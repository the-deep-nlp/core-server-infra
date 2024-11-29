
MAIN_PROMT = """
You are an humanitarian analyst. Extract the desired information from the following passage.
Only extract the properties mentioned in the {} function. It's a multi-label text classification task, try to assign a boolean value for each label considering the content of the passage
"""

DESCRIPTION_PILLARS = """Those are the {} labels that you will use to classify text. Each element can be selected as True or False. It's a multi-label classification task, so not just one label can be inferred as True. If the passage is not enough clear to be associated to some label, also none of them can be selected. Be sure to not over-classify the passage, but just select what you're sure about."""
DESCRIPTION_MATRIX = """Those are the {} labels that you will use to classify text. Each label is a combination of a column label (Column category) and a row label (Row category). Each element can be selected as True or False. It's a multi-label classification task, so not just one label can be inferred as True. If the passage can't clearly be associated to some label, none of them must be selected. Be sure to not over-classify the passage, but just select what you're sure about."""

MULTI_DESCRIPTION = """Column category: {}. Row category: {}."""

INPUT_PASSAGE = "\nPassage:\n{input}"