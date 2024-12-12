MAIN_PROMT = """
You are an humanitarian analyst. Extract the desired information from the following passage.
Only extract the properties mentioned in the {} function. It's a multi-label text classification task, try to assign a boolean value for each label considering the content of the passage
"""  # noqa

DESCRIPTION_PILLARS = """Those are the {} labels that you will use to classify text. Each element can be selected as True or False. It's a multi-label classification task, so not just one label can be inferred as True. If the passage is not enough clear to be associated to some label, also none of them can be selected. Be sure to not over-classify the passage, but just select what you're sure about."""  # noqa
DESCRIPTION_MATRIX = """Those are the {} labels that you will use to classify text. Each label is a combination of a column label (Column category) and a row label (Row category). Each element can be selected as True or False. It's a multi-label classification task, so not just one label can be inferred as True. If the passage can't clearly be associated to some label, none of them must be selected. Be sure to not over-classify the passage, but just select what you're sure about."""  # noqa

MULTI_DESCRIPTION = """Column category: {}. Row category: {}."""

INPUT_PASSAGE = "\nPassage:\n{input}"

EXTRACTION_PROMPT = f"""
Act as an expert humanitarian analyst. Please extract the most relevant pieces of text from the following document, without changing or paraphrasing the original text. Focus on information that would be most important for humanitarian analysis.
The extracted fragments should be comprehensive and can range from a single sentence to a whole paragraph, but no fragment should exceed the length of a single paragraph but can be a subset of them. Choose pieces of text that provide a complete and coherent thought or idea.
The ideal length is whatever is necessary to capture the full context and significance of the information, while staying within the one-paragraph limit. Remember to extract the text verbatim, without altering any words.
Please provide only the extracted text fragments, without any additional commentary. Just select what is actually informative from an humanitarian point of view. It's a extractive summarization task, that must contain all important information.
"""  # noqa
