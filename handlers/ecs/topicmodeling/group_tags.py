import os
import ast
import boto3
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback

from nlp_modules_utils import add_metric_data

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

cloudwatch_client = boto3.client(
    "cloudwatch",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)

class GroupTags:
    """ Group tags based on contextual similarity using using OpenAI gpt-3.5
        Url: https://platform.openai.com/docs/models/gpt-3-5
    """
    def __init__(
        self,
        model_name: str="gpt-3.5-turbo-1106",
        temperature: float=0.1,
        max_tokens: int=4096,
        max_retries: int=2,
        req_timeout: int=60
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            request_timeout=req_timeout
        )
        self.excerpt_tags = []

    def set_excerpts(self, excerpt_tags: list):
        """ Set excerpt tags """
        self.excerpt_tags = excerpt_tags

    def define_prompt_template(self):
        """ Define the prompt template """

        map_template = """
        Group the following list of keywords  as list of list of keywords based on their contextual similarity.
        {tags}
        Make sure to only return that list of list of keywords  and nothing more .
        """
        return map_template

    def generate_tag_groups(self):
        """ Group tags based on similarity """
        generated_tags = None

        map_template = self.define_prompt_template()

        template_prompt = PromptTemplate.from_template(map_template)

        llm_chain = LLMChain(
            llm=self.llm,
            prompt=template_prompt
        )

        with get_openai_callback() as cb:
            generated_tags = llm_chain.invoke({
                "tags": self.excerpt_tags,
            })
            summary_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4),
                "request_count": cb.successful_requests
            }

            for metric_name, metric_value in summary_info.items():
                add_metric_data(
                    cw_client=cloudwatch_client,
                    metric_name=metric_name,
                    metric_value=metric_value,
                    dimension_name="Module",
                    dimension_value="TopicModel",
                    environment=ENVIRONMENT
                )
        grouped_tags = generated_tags["text"] if "text" in generated_tags else []
        try:
            return ast.literal_eval(grouped_tags)
        except SyntaxError:
            return [[tag_item] for tag_item in self.excerpt_tags]
