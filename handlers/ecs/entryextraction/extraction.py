import logging
import boto3
import json
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError

from tags import total_tags
from utils import get_words_count
from const import (
    HIGH_LEVEL_TAG_GROUPS,
    OPTIMIZED_PARAMETERS,
    CLASSIFICATION_MODEL_NAME,
    CLASSIFICATION_MODEL_VERSION
)


logging.getLogger().setLevel(logging.INFO)
client = boto3.session.Session().client("sagemaker-runtime", region_name="us-east-1")


def get_outputs_from_endpoint_text(document: str, endpoint_name: str):
    
    inputs = pd.DataFrame(document, columns=["excerpt"])
    inputs["return_type"] = "default_analyis"
    inputs["analyis_framework_id"] = "all"

    # kw for interpretability
    inputs["interpretability"] = False
    # minimum ratio between proba and threshold to perform interpretability
    inputs["ratio_interpreted_labels"] = 0.5
    inputs["attribution_type"] = "Layer DeepLift"

    # predictions
    inputs["return_prediction_labels"] = True

    # kw for embeddings
    inputs["output_backbone_embeddings"] = False
    inputs["pooling_type"] = "['cls', 'mean_pooling']"
    inputs["finetuned_task"] = "['first_level_tags', 'secondary_tags', 'subpillars']"
    inputs["embeddings_return_type"] = "array"

    backbone_inputs_json = inputs.to_json(orient="split")
    try:
        response = client.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=backbone_inputs_json,
            ContentType="application/json; format=pandas-split",
        )
        output = response["Body"].read().decode("ascii")
    except ClientError as cexc:
        logging.error("Error occurred while invoking the sagemaker endpoint. %s", str(cexc))
        raise cexc

    return output



def get_results_one_row(ss, thresholds, tags):
    
    results = {}
    for k, v in ss.items():

        s = k.split("->")
        main_group = s[0] if s[0] in HIGH_LEVEL_TAG_GROUPS else s[1]
        if not main_group in results.keys():
            results[main_group] = {"tags": [], "o_tags": [], "pred": [], "clf_thres": []}

        if not s[-1] in results[main_group]["tags"]:
            results[main_group]["tags"].append(s[-1])
            results[main_group]["o_tags"].append(k)
            results[main_group]["pred"].append(v)
            results[main_group]["clf_thres"].append(thresholds.get(k))

    for k, v in results.items():
        results[k].update({"max": max(v["pred"])})
        results[k].update({"max_tag": v["tags"][v["pred"].index(max(v["pred"]))]})
        results[k].update({"avg": np.mean(v["pred"])})
        results[k].update({"accepted": [c for c, i in zip(v["o_tags"], v["pred"]) if i>=thresholds.get(c)]})
    
    results = {k: v for k, v in results.items() if k in tags}
    return results


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


def get_tag_ids(total_tags, taglist, idx=0):
    """
    Retrieves the tag IDs
    """
    for tag in total_tags[idx]:
        if tag["key"] == taglist[idx]:
            if idx >= len(total_tags) - 1:
                return [tag.get("id", None)]
            else:
                return [tag.get("id", None)] + get_tag_ids(
                    total_tags, taglist, idx=idx + 1
                )
    return [None]



def convert_prediction(pred, thresholds):
    
    tag_preds = {}
    for label, prob in pred.items():
        firstlabel, secondlabel, thirdlabel = get_tag_ids(
            total_tags, label.split("->")
        )
        if not (firstlabel and secondlabel and thirdlabel):
            continue
        if firstlabel not in tag_preds:
            tag_preds[firstlabel] = {}
        if secondlabel not in tag_preds[firstlabel]:
            tag_preds[firstlabel][secondlabel] = {}
        if thirdlabel not in tag_preds[firstlabel][secondlabel]:
            tag_preds[firstlabel][secondlabel][thirdlabel] = {
                "prediction": prob,
                "threshold": thresholds[label],
                "is_selected": prob > thresholds[label],
            }
    
    return tag_preds



def create_final_output(output: dict, classification_results: dict):
    
    blocks = output["blocks"]
    true_indexes = classification_results["predictions"]==1
    selected = np.array(classification_results["indexes"])[true_indexes]
    pred_vector = np.where(true_indexes)[0]

    for block in output["blocks"]:
        if block.get("type") == "text":
            block.update({
                "relevant": False,
                "classification": None
            })

    for i, j in zip(selected, pred_vector):

        block = blocks[i]
        pred = convert_prediction(classification_results["raw_predictions"][j], 
                                  classification_results["thresholds"])
        block.update({
            "relevant": True,
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
        model_endpoint: str = "main-model-cpu-new-test",
        selected_tags: list = None,
        method: str = None,
        mean_percentage: float=None,
        mean_percentile: float=None,
        std_multiplier: float=None,
        length_weight: float=None,
    ):
        
        self.model_endpoint = model_endpoint
        self.selected_tags = selected_tags
        self.mean_percentage = mean_percentage
        self.mean_percentile = mean_percentile
        self.std_multiplier = std_multiplier
        self.length_weight = length_weight
        self.method = method

    def predict(self, document):
        if isinstance(document, list):
            document = reformat_old_output(document)
        indexes, text = zip(*[(i, c[self.TEXT])
            for i, c in enumerate(document[self.BLOCKS])
            if c[self.TYPE]==self.TEXT]
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
            classification_results=results
        )

entry_extraction_model = EntryExtractionModel(
    selected_tags=OPTIMIZED_PARAMETERS["selected_tags"],
    method=OPTIMIZED_PARAMETERS["method"],
    length_weight=OPTIMIZED_PARAMETERS["length_weight"],
    std_multiplier=OPTIMIZED_PARAMETERS["std_multiplier"]
)
