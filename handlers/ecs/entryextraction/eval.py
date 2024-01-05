import pandas as pd
import numpy as np
import random
from datasets import load_dataset
from eval_helpers import process
from extraction import entry_extraction_model
from sklearn.metrics import accuracy_score

def sample(dataset, sample_size=1000):
    ids = dataset["lead_id"].unique()
    groups = dataset.groupby("lead_id")
    random.shuffle(ids)
    docs = []
    current_sample = 0
    for _id in ids:
        c = groups.get_group(_id)
        if current_sample + len(c.excerpt) <= sample_size:
            docs.append((c.excerpt.to_list(), c.lead_id.values[0], c.document.values[0],
                          c.project_title.values[0]))
            current_sample += len(c.excerpt)
    return docs

def convert_output(predictions, data):

    nlp_relevant = []
    current_page = -1

    for p in predictions["blocks"]:
        page = p["page"]
        lead_id = data[page][1]
        lead_url = data[page][2]
        project_title = data[page][3]
        if page!=current_page:
            nlp_relevant.append(([], lead_id, lead_url, project_title))
            current_page = page
        relevant = p.get("relevant", False)
        if relevant:
            nlp_relevant[page][0].append(1)
        else:
            nlp_relevant[page][0].append(0)
    
    return nlp_relevant

class entryeval:

    def __init__(self) -> None:
        self.nlp_dataset = pd.DataFrame(load_dataset("nlp-thedeep/humset", split="test"))
        self.general_dataset = pd.read_csv("/home/mogady/Desktop/core-server-infra/handlers/ecs/entryextraction/general_docs.csv")


    
    def _eval(self, prediction_func, approx_precision=False, sample_size=2000):
        nlp_docs = sample(self.nlp_dataset)
        general_docs = sample(self.general_dataset)

        self.nlp_dataset = self.nlp_dataset[self.nlp_dataset["document"]!="Unknown"]
        self.general_dataset = self.general_dataset[~self.general_dataset["excerpt"].isna()]
        
        nlp_docs = sample(self.nlp_dataset, sample_size=sample_size)
        general_docs = sample(self.general_dataset, sample_size=sample_size)

        ### Assuming paragraphs of one lead construct a document
        ### Assuming each lead to be a page for fast batch prediction
        predictions_nlp = prediction_func([x[0] for x in nlp_docs])
        predictions_general = prediction_func([x[0] for x in general_docs])

        nlp_relevant = convert_output(predictions_nlp, nlp_docs)
        general_relevant = convert_output(predictions_general, general_docs)

        results_nlp = pd.DataFrame([[c[0], [1]*len(c[0]), c[1], c[2], c[3]] for c in nlp_relevant], 
                            columns=["predictions", "labels", "lead_id", "lead_url", "project_title"])
        results_nlp["accuracy"] = results_nlp[["predictions", "labels"]].apply(lambda x: accuracy_score(x[1], x[0]), axis = 1)
        
        results_general = pd.DataFrame([[c[0], [1]*len(c[0]), c[1], c[2], c[3]] for c in general_relevant], 
                    columns=["predictions", "labels", "lead_id", "lead_url", "project_title"])
        results_general["accuracy"] = results_general[["predictions", "labels"]].apply(lambda x: accuracy_score(x[1], x[0]), axis = 1)

        print("NLP data avg accuracy: ", results_nlp["accuracy"].mean())
        print("General data avg accuracy: ", results_general["accuracy"].mean())

        results_nlp.to_csv("results_nlp.csv")
        results_general.to_csv("results_general.csv")
        if approx_precision:
            results_general["full_document"]
            

        return
    

if __name__ == "__main__":
    obj = entryeval()
    obj._eval(prediction_func=entry_extraction_model.predict)