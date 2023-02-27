import os
import json
import logging
import psycopg2
from huggingface_hub import snapshot_download
from enum import Enum
from reports_generator import ReportsGenerator

logging.getLogger().setLevel(logging.INFO)

class ReportStatus(Enum):
    INITIATE = 1
    SUCCESS = 2
    FAILED = 3

class Database:
    def __init__(
        self,
        endpoint: str,
        database: str,
        username: str,
        password: str,
        port: int=5432,
    ):
        try:
            conn = psycopg2.connect(
                host=endpoint,
                port=port,
                database=database,
                user=username,
                password=password
            )
            cur = conn.cursor()
            return cur
        except Exception as e:
            logging.error(f"Database connection failed {e}")
            return None


class ReportsGeneratorHandler:
    def __init__(self):
        test_entry = '''
        “Since the start of the full-scale war we, along with our humanitarian partners in Ukraine, have made every effort to ramp up operations to provide life-saving support to those who need it most,” UN Spokesperson Stéphane Dujarric told journalists in New York. Last year, thousands of convoys delivered vital supplies to people in all regions of the country, he said, and humanitarians reached nearly 16 million with aid, including water, medicines, heating appliances, and other supplies, as well as support for home repairs. Some six million people received cash assistance totalling $1.2 billion – the largest such programme in history, he added. As the war enters a second year, the UN and partners are calling for nearly $4 billion to support more than 11 million people. The appeal is just over 14 per cent funded, Mr. Dujarric said.  **Young lives lost ** UN agencies have been taking stock of the death, destruction, devastation, and displacement that have occurred in Ukraine over the past 12 months. Nearly 500 children have been killed and almost 1,000 injured, UN humanitarians said on Friday in Geneva. In addition to that terrible human toll, the UN Children’s Fund (UNICEF) said that more than 800 health facilities had been damaged or destroyed by shelling. Education under fire The fighting has also disrupted access to education, and thousands of pre-schools and secondary schools have been damaged. In total, 7.8 million children have been impacted and more than five million have no access to schooling in Ukraine at all, UNICEF warned. Toxic legacy looms. The war will have a toxic legacy for generations to come, the UN Environment Programme (UNEP) said earlier in the week, reporting on a preliminary monitoring of the conflict conducted last year together with partners. While UNEP will verify the full range and severity, the agency noted that “thousands of possible incidents of air, water, and land pollution and the degradation of ecosystems, including risks to neighbouring countries, have already been identified.” UNEP is supporting the Ukrainian Government on remote environmental impact monitoring and is preparing to undertake field-level impact assessments – expected to be a colossal task, due to the scale and geographical spread of reported incidents. “The mapping and initial screening of environmental hazards only serves to confirm that war is quite literally toxic,” said UNEP Executive Director Inger Andersen. “Ukraine will then need huge international support to assess, mitigate, and remediate the damage across the country, and alleviate risks to the wider region,” she added.  Air and waters polluted. The data showed that the conflict has resulted in damage across many regions of the country, with incidents at nuclear power plants and facilities; energy infrastructure, including oil storage tankers, oil refineries, and drilling platforms; and other locations as well as distribution pipelines, mines, industrial sites, and agro-processing facilities.  The result has been multiple incidents of air pollution and potentially serious contamination of ground and surface waters, UNEP said.  Significant damage has also occurred to such water infrastructure as pumping stations, purification plants, and sewage facilities. Clean-up challenges  UNEP added that hazardous substances have also been released from explosions in agro-industrial storage facilities, including fertilizer and nitric acid plants. Damage also extends to urban areas, where the clean-up of destroyed housing could lead to debris being mixed with hazardous chemicals, particularly asbestos. Furthermore, satellite imagery has also revealed a significant increase of fires in various nature reserves, protected areas, and forests. Additionally, pollution from weapons use, and the large volumes of military waste, also creates a major clean-up challenge, the UN agency said. Averting nuclear disaster. The conflict has also marked the first time in history that a war is being fought amid the facilities of a major nuclear power programme. The International Atomic Energy Agency (IAEA) issued a report this week highlighting its activities to reduce the likelihood of a nuclear accident during the fighting. IAEA has been working to implement a nuclear safety and security protection zone at the Zaporizhzhya Nuclear Power Plant, the largest in Europe, which has been occupied by Russian forces since the early weeks of the war. The plant has repeatedly come under fire, sparking fears of a nuclear disaster.
        '''
        self.entries = test_entry #os.environ.get("ENTRIES", [])
        self.callback_url = os.environ.get("CALLBACK_URL", None)
        self.unique_id = os.environ.get("UNIQUE_ID", 0)
        self.database_url = os.environ.get("DATABASE_URL", None)
    
    def download_models(
            self,
            summ_model: str="csebuetnlp/mT5_multilingual_XLSum",
            sent_embedding_model: str="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        model_info = {}
        if not any(os.listdir("/models")):
            summarization_model_local_path = snapshot_download(
                repo_id=summ_model,
                cache_dir="/models"
            )
            summarization_embedding_model_local_path = snapshot_download(
                repo_id=sent_embedding_model,
                cache_dir="/models"
            )
            model_info = {
                "summarization_model_path": summarization_model_local_path,
                "summarization_embedding_model_path": summarization_embedding_model_local_path
            }
            with open("/models/model_info.json", "w", encoding="utf-8") as f:
                json.dump(model_info, f)
        else:
            model_info_path = "/models/model_info.json"
            if os.path.exists(model_info_path):
                with open(model_info_path, "r") as f:
                    model_info = json.load(f)
            else:
                return {}
        return model_info

    def summary_store_s3(self):
        pass

    def status_update_db(self):
        pass

    
    def __call__(self, model_info):
        if ("summarization_model_path" and 
            "summarization_embedding_model_path" in model_info):
            self.repgen = ReportsGenerator(
                summarization_model_name=model_info["summarization_model_path"],
                sentence_embedding_model_name=model_info["summarization_embedding_model_path"],
                device="cpu"
            )
            summary = self.repgen(self.entries)
            return summary
        else:
            return "Summarization models could not be loaded."


reports_generator_handler = ReportsGeneratorHandler()
model_info = reports_generator_handler.download_models()
result = reports_generator_handler(model_info=model_info)
logging.info(f"Result generated: {result}")
#summarized_texts = reports_generator_handler()

