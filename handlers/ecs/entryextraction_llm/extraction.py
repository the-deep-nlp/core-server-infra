import logging
import boto3
import json
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError


logging.getLogger().setLevel(logging.INFO)


def divide_into_batches(data, batch_size: int = 100):
    
    # in order to avoid problems in the sagemaker endpoints,
    # i prefer to split the document text in batches.
    # i noticed that after the 250/300 senteces is very probable to get a ClientError
    
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def rebuild(output_list: list):

    raw_predictions = []
    indexes = []
    for ids, element in output_list:
        raw_predictions.extend(element["raw_predictions"])
        indexes.extend(ids)

    return {"raw_predictions": raw_predictions, 
            "thresholds": element["thresholds"],
            "indexes": indexes}



def reformat_old_output(output: list):
    reformat = {
        "metadata": {
            "total_pages": len(output),
            "total_words_count": get_words_count(" ".join([s for page in output for s in page]))
        },
        "blocks": []}

    for i, page in enumerate(output):
        for j, sentence in enumerate(page):
            reformat["blocks"].append(
                {
                    "type": "text",
                    "page": i,
                    "text": sentence,
                    "textOrder": j
                }
            )
    return reformat


def create_final_output(output: dict, classification_results: dict, min_length: int = 15):
    """ Generate the final output """
    blocks = output["blocks"]
    true_indexes = classification_results["predictions"]==1
    selected = np.array(classification_results["indexes"])[true_indexes]
    pred_vector = np.where(true_indexes)[0]

    for block in output["blocks"]:
        if block.get("type") == "text":
            block.update({
                "relevant": False,
                "prediction_status": False,
                "classification": {}
            })

    for i, j in zip(selected, pred_vector):
        
        block = blocks[i]
        tags_pred = convert_current_dict_to_previous_one(classification_results["raw_predictions"][j])
        tags_threshold = convert_current_dict_to_previous_one(classification_results["thresholds"])
        pred = get_model_tags_mappings(tags_pred, tags_threshold)
        block.update({
            "relevant": True,
            "prediction_status": True,
            "classification": pred
        })

    output["classification_model_info"] = {
        "name": CLASSIFICATION_MODEL_NAME,
        "version": CLASSIFICATION_MODEL_VERSION
    }

    return output


class EntryExtractionModel:
    BLOCKS: str = "blocks"
    TYPE: str = "type"
    TEXT: str = "text"
    RAW_PREDICTIONS: str = "raw_predictions"
    THRESHOLDS: str = "thresholds"
    PERCENTAGE: str = "percentage"
    PERCENTILE: str = "percentile"
    STANDARD_DEVIATION: str = "standard_deviation"

    def __init__(
        self,
        model_endpoint: str = "main-model-cpu",
        selected_tags: list = None,
        method: str = None,
        mean_percentage: float=None,
        mean_percentile: float=None,
        std_multiplier: float=None,
        length_weight: float=None,
        min_length: int = 15
    ):

        self.model_endpoint = model_endpoint
        self.selected_tags = selected_tags
        self.mean_percentage = mean_percentage
        self.mean_percentile = mean_percentile
        self.std_multiplier = std_multiplier
        self.length_weight = length_weight
        self.method = method
        self.min_length = min_length

    def check_length(self, sentence):
        return True if len(sentence.split())>=self.min_length else False
    
    def predict(self, document):

        if isinstance(document, list):
            document = reformat_old_output(document)
        indexes, text = zip(*[(i, c[self.TEXT])
            for i, c in enumerate(document[self.BLOCKS])
            if c[self.TYPE]==self.TEXT and self.check_length(c[self.TEXT])]
        )

        results = []
        for idx, batch in zip(divide_into_batches(indexes),
                                divide_into_batches(text)):
            try:
                batch_results = json.loads(
                    get_outputs_from_endpoint_text(
                        batch,
                        endpoint_name=self.model_endpoint
                    )
                )
                results.append((idx, batch_results))
            except Exception as e:
                logging.warning(e)
                continue

        results = rebuild(results)
        res_for_doc = [get_results_one_row(c,
            thresholds=results[self.THRESHOLDS],
            tags=self.selected_tags)
            for c in results[self.RAW_PREDICTIONS]
        ]

        # get the mean of max (we can try something else too) from each group of selected_tags
        # for each sentence of the document

        means = [np.mean([c.get("max")
                    for c in i.values()]) for i in res_for_doc]
        prediction = np.zeros(len(means))

        if self.method == self.PERCENTAGE:

            thres = np.mean(means) + np.mean(means)*self.mean_percentage

        elif self.method == self.PERCENTILE:

            thres =  np.percentile(means, self.mean_percentile)

        elif self.method == self.STANDARD_DEVIATION:

            thres = np.mean(means)+self.std_multiplier*np.std(means)

        thres = thres+self.length_weight*np.log(len(document))
        prediction[np.where(means>=thres)] = 1
        results.update({"predictions": prediction})

        return create_final_output(
            output=document,
            classification_results=results,
            min_length=self.min_length
        )

parameters = OPTIMIZED_PARAMETERS["main-model-cpu"]
entry_extraction_model = EntryExtractionModel(
    selected_tags=parameters["selected_tags"],
    method=parameters["method"],
    length_weight=parameters["length_weight"],
    std_multiplier=parameters["std_multiplier"],
    min_length=parameters["min_sentence_length"]
)
