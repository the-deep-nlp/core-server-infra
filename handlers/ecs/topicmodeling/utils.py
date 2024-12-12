import re

import numpy as np


def preprocess_text(text: str) -> str:
    """Preprocess the texts"""
    text = np.str_(text)
    text = text.replace("\\n", "")
    text = text.replace("\\", "")
    text = re.sub(r"\[(.*?)\]", "", text)  # removes [this one]
    url_pattern = "((https?|ftp|smtp)://)?(www.)?[a-z0-9]+\\.[a-z]+(/[a-zA-Z0-9#]+/?)*"
    text = re.sub(url_pattern, "", text)  # remove urls
    # text = re.sub('\'','',text)
    # text = re.sub(r'\d+', ' __number__ ', text) #replaces numbers
    # text = re.sub('\W', ' ', text)
    text = re.sub(" +", " ", text)
    text = text.replace("\t", "")
    text = text.replace("\n", "")

    return text.strip()
