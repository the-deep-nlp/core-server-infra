def summary_generation_prompt():
    """Define the prompt template"""

    prompt = """
    Act as a humanitarian evaluation analyst or journalist. You are requested to adhere the following guidelines:
    1. Generate a concise summary, capturing the main points, key facts, issues and main takeaways guided by the following tags {tags}. Incorporate relevant details and maintaining coherence. If possible provide the summary which includes context, needs and response. Do not include quotes.
    2. Always generate the summary in English.
    Try to maintain the length of that generated summary to be around {tokens_count} words.
    TEXT: {text}

    SUMMARY:
    """  # noqa
    return prompt


def analytical_statement_prompt():
    """Generate Analytical Statement based on the Summary"""
    prompt = """
    You are a humanitarian analyst tasked with providing objective, neutral, and evidence-based analytical statements.
    I will provide you with a summary of a series of entries. Your task is to create an analytical statement of no
    more than 45 words based solely on the information provided in the summary. Your statement should be specific,
    detailed, and avoid vagueness or fabrication of data. Remain impartial and rely strictly on the evidence
    presented in the summary.

    SUMMARY: {summary}
    """

    return prompt


def information_gaps_prompt():
    """Generate Information gaps from the excerpts"""
    prompt = """
    You are a humanitarian analyst tasked with identifying gaps and limitations in the information provided.
    I will provide you with a series of entries {entries} containing data, reports, or other information related to this
    particular topics {topics}. Your task is to critically analyze the
    information presented in these entries and create a concise assessment highlighting the information gaps,
    missing pieces, or areas where additional information is needed.

    Your text should be objective, neutral, and evidence-based, relying strictly on the information provided
    in the entries. Avoid making assumptions, speculations, or fabricating data not supported by the evidence.
    Additionally, you should evaluate the diversity and reliability of the sources cited in the entries.

    Your text should not exceed 100 words, and please provide it in bullet points.
    """

    return prompt
