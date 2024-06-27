def summary_generation_prompt():
    """ Define the prompt template """

    prompt = """
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

    return prompt

def analytical_statement_prompt():
    """ Generate Analytical Statement based on the Summary """
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
    """ Generate Information gaps from the excerpts """
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
