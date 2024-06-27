import os

from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback

from prompts import (
    summary_generation_prompt,
    analytical_statement_prompt,
    information_gaps_prompt
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class SummarizerBase:
    """ Summarizer base class """
    def __init__(self,
        texts: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        max_retries: int,
        req_timeout: int=60
    ):
        """ Summarizer initializations """
        self.texts = texts
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            request_timeout=req_timeout
        )

    def get_tokens_size(self):
        """ Get the tokens size """
        return self.llm.get_num_tokens(self.texts)

class LLMSummarization(SummarizerBase):
    """ Summarization using LLM Chain
        Note: https://platform.openai.com/docs/models/gpt-3-5
    """
    def __init__(self,
        texts: str,
        model_name: str="gpt-3.5-turbo-1106",
        temperature: float=0.2,
        max_tokens: int=4096,
        max_retries: int=2
    ):
        super().__init__(texts, model_name, temperature, max_tokens, max_retries)

    def summarizer(self, min_tokens: int=20):
        """ Summarization using Chain of Density prompt """
        generated_summary = None
        tokens_count = max(int(self.get_tokens_size()/2), min_tokens)

        prompt = summary_generation_prompt()

        template_prompt = PromptTemplate.from_template(prompt)

        summarize_chain = LLMChain(
            llm=self.llm,
            prompt=template_prompt
        )

        with get_openai_callback() as cb:
            generated_summary = summarize_chain.invoke({
                "text": self.texts,
                "tokens_count": tokens_count
            })
            summary_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4),
                "request_count": cb.successful_requests
            }

        final_summary = generated_summary["text"]
        return final_summary, summary_info
        # final_summary = json.loads(generated_summary["text"])
        # return final_summary[-1]["Denser_Summary"], summary_info

    def generate_analytical_statement(self, summary: str):
        """ Generate Analytical Statement from the Summary """
        prompt = analytical_statement_prompt()
        template_prompt = PromptTemplate.from_template(prompt)
        chain = LLMChain(
            llm=self.llm,
            prompt=template_prompt
        )

        with get_openai_callback() as cb:
            generated_analytical_statement = chain.invoke({
                "summary": summary
            })

            analytical_statement_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4),
                "request_count": cb.successful_requests
            }
        return (
            generated_analytical_statement["text"] if "text" in generated_analytical_statement else "",
            analytical_statement_info
        )

    def generate_information_gaps(self, entries: list, topics: list):
        """ Generate Information Gaps based on entries and topics """
        prompt = information_gaps_prompt()
        template_prompt = PromptTemplate.from_template(prompt)
        chain = LLMChain(
            llm=self.llm,
            prompt=template_prompt
        )

        with get_openai_callback() as cb:
            generated_info_gaps = chain.invoke({
                "entries": entries,
                "topics": topics
            })
            information_gaps_info = {
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": round(cb.total_cost, 4),
                "request_count": cb.successful_requests
            }
        return (
            generated_info_gaps["text"] if "text" in generated_info_gaps else "",
            information_gaps_info
        )
