from enum import Enum

from langchain import OpenAI, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from langchain.chains.summarize import load_summarize_chain

class ChainTypes(Enum):
    """ Chain Types """
    STUFF = 0
    MAP_REDUCE = 1
    REFINE = 2

class Summarization:
    """ Summarization Module """
    def __init__(
        self,
        temperature: float = 0.1,
        max_tokens: int = 512,
        model_name: str = "gpt-3.5-turbo"
    ):
        #self.llm = OpenAI(
        #    temperature=temperature,
        #    model=model_name,
        #    max_tokens=max_tokens,
        #)

        self.llm = ChatOpenAI(
            temperature=temperature,
            model=model_name,
            max_tokens=max_tokens,            
        )

    def textsplitter(self):
        """ Text Splitter """
        return RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=25,
            separators=["\n\n", "\n", "\t"]
        )

    def create_docs(self, texts: str):
        """ Create Docs """
        text_splitter = self.textsplitter()
        texts = text_splitter.split_text(texts)
        docs = [Document(page_content=t) for t in texts]
        return docs

    def generate_prompt(self):
        """ Generate Prompts """
        prompt_template = """You are a humanitarian analyst and has a strong domain knowledge.
        Write a concise summary of the following including key points:

        {text}

        CONCISE SUMMARY:
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        return prompt

    def generate_refine_prompt(self):
        """ Generate Refine Prompt """
        refine_template = (
            "Your job is to produce a final summary\n"
            "We have provided an existing summary up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing summary\n"
            "(only if needed) with some more context below.\n"
            "----------------\n"
            "{text}\n"
            "----------------\n"
            "Given the new context, refine the original summary\n"
            "If the context isn't useful, return the original summary"
        )
        refine_prompt = PromptTemplate(
            template=refine_template,
            input_variables=["existing_answer", "text"]
        )
        return refine_prompt

    def generate_summary(
        self,
        docs,
        prompt,
        chain_type=ChainTypes.MAP_REDUCE,
        verbose=False
    ):
        """ Generate Summary """
        if chain_type==ChainTypes.MAP_REDUCE:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                verbose=verbose,
                map_prompt=prompt,
                combine_prompt=prompt
            )
        elif chain_type==ChainTypes.REFINE:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type="refine",
                verbose=verbose,
                question_prompt=prompt,
                refine_prompt=self.generate_refine_prompt()
            )
        else:
            chain = load_summarize_chain(
                llm=self.llm,
                chain_type=chain_type,
                verbose=verbose
            )
        return chain.run(docs) # summary
