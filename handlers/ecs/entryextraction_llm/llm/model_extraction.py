import os
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from llm.model_prediction import LLMTagsPrediction
from llm.prompt_utils import EXTRACTION_PROMPT, INPUT_PASSAGE
# from langchain_aws import ChatBedrockConverse
from llm.utils import reformat_old_output
from polyfuzz import PolyFuzz
from polyfuzz.models import TFIDF
from pydantic import BaseModel


class LLMExtractionPrediction:

    CLASSIFICATION_MODEL_NAME = "llm_model"
    CLASSIFICATION_MODEL_VERSION = "1.0.0"

    def __init__(self, analysis_framework_id: int, model_family: str = "openai"):

        self.af_id = analysis_framework_id
        self.model_family = model_family
        self.classification_model = LLMTagsPrediction(
            analysis_framework_id=self.af_id, model_family=self.model_family
        )

        self.tfidf = TFIDF(n_gram_range=(1, 5), min_similarity=0, model_id="TF-IDF")

    def __entry_extraction(self, structured_text):

        # in my opinion a different strategy is needed here, due to the fact that most of the costs are related with the
        # input-output token. An extractive summarization task like this one involve an high number of token both sides.
        # This increase the cost dramatically respect to a standard classification that on average is in the cents range (0.05$)  # noqa
        # another issue is the response time, that due to the big prompt slow down the process in a significant way.

        class Extraction(BaseModel):
            excerpts: List[str]

        self.structured_text = structured_text
        joined_plain_text = "\n".join(
            [c.get("text") for c in self.structured_text["blocks"]]
        )
        tag_ex = EXTRACTION_PROMPT + INPUT_PASSAGE
        tagging_prompt_ex = ChatPromptTemplate.from_template(tag_ex)
        if self.model_family == "openai":
            llm_ex = ChatOpenAI(
                model=os.environ.get("OPENAI_SMALL_MODEL"), temperature=0
            ).with_structured_output(Extraction)
        elif self.model_family == "bedrock":
            raise NotImplementedError
            # llm_ex = ChatBedrockConverse(model=os.environ.get("BEDROCK_SMALL_MODEL"), temperature=0).with_structured_output(Extraction)  # noqa
        tagging_chain_ex = tagging_prompt_ex | llm_ex

        extracted_excerpts = tagging_chain_ex.invoke({"input": joined_plain_text})

        return self.__remap_text(extracted_excerpts)

    def __remap_text(self, excerpts: List[str]):

        if not excerpts.excerpts:
            return excerpts.excerpts
        model = (
            PolyFuzz(self.tfidf)
            .match(
                excerpts.excerpts,
                [c.get("text") for c in self.structured_text["blocks"]],
            )
            .get_matches()
        )

        doc = {
            passage.pop("text"): passage for passage in self.structured_text["blocks"]
        }
        return [
            {"text": original, **doc.get(match)}
            for original, match in zip(model.From, model.To)
        ]

    def __build_output(self, entry_extraction, extry_classification, structured_output):

        blocks = []
        for ex, cls in zip(entry_extraction, extry_classification):
            if cls:
                blocks.append(
                    {
                        "type": "text",
                        **ex,
                        "relevant": True,
                        "prediction_status": True,
                        "classification": cls,
                    }
                )

        output = {
            "metadata": {
                "total_pages": structured_output["metadata"]["total_pages"],
                "total_words_count": structured_output["metadata"]["total_words_count"],
            },
            "blocks": blocks,
            "classification_model_info": {
                "name": self.CLASSIFICATION_MODEL_NAME,
                "version": self.CLASSIFICATION_MODEL_VERSION,
            },
        }

        return output

    def predict(self, structured_text):

        if isinstance(structured_text, list):
            structured_text = reformat_old_output(structured_text)

        entry_extraction = self.__entry_extraction(structured_text)
        entry_classification = self.classification_model.predict(
            excerpts=[c["text"] for c in entry_extraction]
        )

        return self.__build_output(
            entry_extraction, entry_classification, structured_text
        )
