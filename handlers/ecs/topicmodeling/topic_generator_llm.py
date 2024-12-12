import os
import re

import boto3
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain_openai.chat_models import ChatOpenAI
from nlp_modules_utils import add_metric_data

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

cloudwatch_client = boto3.client(
    "cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1")
)


class TopicGenerationLLM:
    """Topic Generation using using OpenAI gpt-3.5
    Url: https://platform.openai.com/docs/models/gpt-3-5
    """

    def __init__(
        self,
        texts: list,
        keywords: str,
        model_name: str = "gpt-3.5-turbo-1106",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 2,
        req_timeout: int = 60,
    ):
        self.texts = texts
        self.keywords = keywords
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            request_timeout=req_timeout,
        )

    def define_prompt_template(self):
        """Define the prompt template"""

        map_template = """
        I have a topic that contains the following documents in a List.
        {documents}
        The topic is described by the following keywords: {keywords}
        Based on the information about the topic above, please create a short label of this topic.
        Make sure to only return the label and nothing more.
        """

        return map_template

    def topic_generator_handler(self):
        """Topic generator"""
        generated_summary = None

        map_template = self.define_prompt_template()

        template_prompt = PromptTemplate.from_template(map_template)

        summarize_chain = LLMChain(llm=self.llm, prompt=template_prompt)

        with get_openai_callback() as cb:
            generated_summary = summarize_chain.invoke(
                {"documents": self.texts, "keywords": self.keywords}
            )
            summary_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4),
                "request_count": cb.successful_requests,
            }
            for metric_name, metric_value in summary_info.items():
                add_metric_data(
                    cw_client=cloudwatch_client,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    dimension_name="Module",
                    dimension_value="TopicModel",
                    environment=ENVIRONMENT,
                )
        return self.postprocess(generated_summary["text"])

    def postprocess(self, texts: str):
        """Postprocess the generated text"""
        return re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", texts)
