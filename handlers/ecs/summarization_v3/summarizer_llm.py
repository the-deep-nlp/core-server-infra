import os

from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback

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

    def define_prompt_template(self):
        """ Define the prompt template """

        map_template = """
        Act as a humanitarian evaluation analyst or journalist. Your main objective is to generate a concise summary,
        capturing the main points, key facts, issues and main takeaways. Incorporate relevant details and maintaining coherence.
        If possible provide the summary which includes context, needs and response. Do not include quotes.
        Please generate the summary as in the input text. If the input language is English, provide the summary in English.
        If the input language is Spanish, provide the summary in Spanish, and so on for French, Arabic etc.
        Try to maintain the length of that generated summary to be around {tokens_count} words.

        TEXT: {text}

        SUMMARY:
        """

        # map_template = """
        #     Article: {text}

        #     You will generate an increasingly concise, entity-dense summaries of the above Article.

        #     Repeat the following 2 steps 5 times.

        #     Step 1. Identify 1-3 informative Entities ("; " delimited) from the Article which are missing from the previously generated summary.
        #     Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.

        #     A Missing Entity is:
        #     - Relevant: to the main story.
        #     - Specific: descriptive yet concise (5 words or fewer).
        #     - Novel: not in the previous summary.
        #     - Faithful: present in the Article.
        #     - Anywhere: located anywhere in the Article.

        #     Guidelines:
        #     - The first summary should be long ({tokens_count} words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach ~80 words.
        #     - Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
        #     - Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
        #     - The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the Article.
        #     - Missing entities can appear anywhere in the new summary.
        #     - Never drop entities from the previous summary. If space cannot be made, add fewer new entities.

        #     Remember, use the exact same number of words for each summary.

        #     Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".
        # """

        return map_template

    def summarizer(self, min_tokens: int=20):
        """ Summarization using Chain of Density prompt """
        generated_summary = None
        tokens_count = max(int(self.get_tokens_size()/2), min_tokens)

        map_template = self.define_prompt_template()

        template_prompt = PromptTemplate.from_template(map_template)

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
