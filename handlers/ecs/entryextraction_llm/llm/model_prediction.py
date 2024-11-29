import os
import json
import redis

from box import Box
from dataclasses import make_dataclass, field, dataclass
from pydantic import BaseModel, Field, create_model
from concurrent.futures import ThreadPoolExecutor
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

from prompt_utils import *
from utils import (process_primary_tags, 
                   combine_properties, 
                   connect_db,
                   af_widget_by_id)
#from utils.db import connect_db
#from core_server.env import env
#from core.tasks.queries import af_widget_by_id

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

class WidgetsMappings:
    
    def __init__(self, selected_widgets: list):

        self.mappings = {}
        self.selected_widgets = selected_widgets
        self.WidgetTypes = make_dataclass(
            'WidgetTypes', 
            [(widget, str, field(default=widget))for widget in list(set([element.widget_id 
                                                                         for element in self.selected_widgets]))]
        )
        self.create_mappings()

    def __update(self, key: str, value: dict, version: int, widget_type: str):
        
        self.mappings.update({key: value})
        self.mappings[key].update({
            "version": version,
            "widget_id": widget_type
            })

    def __process_widget_1d(self, key: str, properties: dict, version: int):

        _, rows = process_primary_tags(properties, order="rows", type_="1d")
        self.__update(
            key=key,
            value=rows,
            version=version,
            widget_type=self.WidgetTypes.matrix1dWidget
        )

    def __process_widget_2d(self, key: str, properties: dict, version: int):

        _, rows = process_primary_tags(properties, order="rows")
        _, columns = process_primary_tags(properties, order="columns")
        rows.update(columns)

        self.__update(
            key=key,
            value=rows,
            version=version,
            widget_type=self.WidgetTypes.matrix2dWidget
        )

    def __process_widget_multiselect(self, key: str, properties: dict, version: int):
        raise NotImplementedError
    
    def __process_widget_organigram(self, key: str, properties: dict, version: int):
        raise NotImplementedError

    def __process_widget_daterange(self, key: str, properties: dict, version: int):
        raise NotImplementedError

    def __process_widget_scale(self, key: str, properties: dict, version: int):
        raise NotImplementedError

    def create_mappings(self):
    
        for d in self.selected_widgets:
            
            if d.widget_id == self.WidgetTypes.matrix1dWidget:
                self.__process_widget_1d(d.key, d.properties, d.version)
            
            elif d.widget_id == self.WidgetTypes.matrix2dWidget:
                self.__process_widget_2d(d.key, d.properties, d.version)

            elif d.widget_id == self.WidgetTypes.multiselectWidget:
                self.__process_widget_multiselect(d.key, d.properties, d.version)
            
            elif d.widget_id == self.WidgetTypes.organigramWidget:
                self.__process_widget_organigram(d.key, d.properties, d.version)
            
            elif d.widget_id == self.WidgetTypes.dateRangeWidget:
                self.__process_widget_daterange(d.key, d.properties, d.version)

            elif d.widget_id == self.WidgetTypes.scaleWidget:
                self.__process_widget_scale(d.key, d.properties, d.version)


class WidgetSchema:

    @dataclass
    class Schema:
        type : str
        prompt: str
        model: str
        properties: dict
        pyd_class: BaseModel

    def __init__(self, selected_widgets: list, model_family: str = "openai"):

        self.schemas = {}
        self.max_widget_length = 50
        self.selected_widgets = selected_widgets
        self.model_family = model_family
        self.mappings_instance = WidgetsMappings(self.selected_widgets)
        self.mappings = self.mappings_instance.mappings
        self.create_schemas()

    def __foundation_model_id_selection(self, 
                                        schema: BaseModel = None, 
                                        ln_threshold: int = 30):
    
        length = len(schema.model_json_schema()["properties"].keys())
        
        if self.model_family == "bedrock":
            
            model_id_main = os.environ.get("BEDROCK_MAIN_MODEL")
            model_id_small = os.environ.get("BEDROCK_SMALL_MODEL") # haiku model overclassify a lot for some reason
            
            return model_id_main if length<=ln_threshold else model_id_main
            
        elif self.model_family == "openai":
            
            model_id_main = os.environ.get("OPENAI_MAIN_MODEL")
            model_id_small = os.environ.get("OPENAI_SMALL_MODEL")

            return model_id_small if length<=ln_threshold else model_id_main
        
        # other foundation model families can be added here

    def __update(self, key: str, value: Schema):
        self.schemas.update({key: value})

    def __process_widget_1d(self, key: str, properties: dict, class_name: str = "Pillars"):
        
        properties, _ = process_primary_tags(properties, order="rows", type_="1d")
        # dynamic pydantic class creation
        pillars = create_model(
                    class_name,
                    __base__=BaseModel,
                    __doc__=DESCRIPTION_PILLARS.format(class_name.lower()),
                    **{k: (bool, Field(title=k, 
                                       description=v['description'], 
                                       default=False)) 
                    for k, v in properties.items()}
                )
        self.__update(key, self.Schema(
            type=self.mappings_instance.WidgetTypes.matrix1dWidget,
            prompt=MAIN_PROMT.format(class_name)+INPUT_PASSAGE,
            model=self.__foundation_model_id_selection(schema=pillars),
            properties=properties,
            pyd_class=pillars
        ))
        
    def __process_widget_2d(self, key: str, properties: dict, class_name: str = "Matrix"):
        
        properties_row, _ = process_primary_tags(properties, order="rows")
        properties_columns, _ = process_primary_tags(properties, order="columns")
        properties = combine_properties(properties_columns=properties_columns,
                                        properties_row=properties_row,
                                        max_length=self.max_widget_length,
                                        reduce_on_length=True) # setting the description reduction
        # dynamic pydantic class creation
        matrix = create_model(
                    class_name,
                    __base__=BaseModel,
                    __doc__=DESCRIPTION_MATRIX.format(class_name.lower()),
                    **{k: (bool, Field(title=k, 
                                       description=v['description'], 
                                       default=False)) 
                    for k, v in properties.items()}
                )
        
        self.__update(key, self.Schema(
            type=self.mappings_instance.WidgetTypes.matrix2dWidget,
            prompt=MAIN_PROMT.format(class_name)+INPUT_PASSAGE,
            model=self.__foundation_model_id_selection(schema=matrix),
            properties=properties,
            pyd_class=matrix
        ))

    def __process_widget_multiselect(self, key: str, properties: dict, class_name: str):
        raise NotImplementedError
    
    def __process_widget_organigram(self, key: str, properties: dict, class_name: str):
        raise NotImplementedError

    def __process_widget_daterange(self, key: str, properties: dict, class_name: str):
        raise NotImplementedError

    def __process_widget_scale(self, key: str, properties: dict, class_name: str):
        raise NotImplementedError

    def create_schemas(self):

        for d in self.selected_widgets:
            
            if d.widget_id == self.mappings_instance.WidgetTypes.matrix1dWidget:
                self.__process_widget_1d(d.key, d.properties, "Pillar")
            
            elif d.widget_id == self.mappings_instance.WidgetTypes.matrix2dWidget:
                self.__process_widget_2d(d.key, d.properties, "Matrix")

            elif d.widget_id == self.mappings_instance.WidgetTypes.multiselectWidget:
                self.__process_widget_multiselect(d.key, d.properties, "Multiselect")
            
            elif d.widget_id == self.mappings_instance.WidgetTypes.organigramWidget:
                self.__process_widget_organigram(d.key, d.properties, "Organigram")
            
            elif d.widget_id == self.mappings_instance.WidgetTypes.dateRangeWidget:
                self.__process_widget_daterange(d.key, d.properties, "Date")

            elif d.widget_id == self.mappings_instance.WidgetTypes.scaleWidget:
                self.__process_widget_scale(d.key, d.properties, "Scale")


class LLMTagsPrediction:

    AVAILABLE_WIDGETS: list = ["matrix2dWidget", "matrix1dWidget"] # it'll be extended to all widget types
    AVAILABLE_FOUNDATION_MODELS: list = ["bedrock", "openai"]

    def __init__(self, analysis_framework_id: int, model_family: str = "openai"):

        self.af_id = analysis_framework_id
        self.model_family = model_family

        assert self.model_family in self.AVAILABLE_FOUNDATION_MODELS, ValueError("Selected model family not implemented")

        # self.cursor = self.__get_deep_db_connection().cursor
        self.selected_widgets = self.__get_framework_widgets()
        self.widgets = WidgetSchema(self.selected_widgets, self.model_family)

    def __get_deep_db_connection(self):
        return connect_db()

    def __get_elasticache(self, port: int = 6379):
        return redis.Redis(host=os.environ.get("REDIS_HOST"), 
                           port=port, 
                           decode_responses=True)

    def __get_framework_widgets(self, expire_time: int = 1200): 
        
        # let's get or save the af_id widget original data on elasticache for 20 minutes
        # avoiding multiple db connection and executions on the same analysis framework id. 

        self.redis = self.__get_elasticache()
        cached_afw = self.redis.get(f"af_id:{self.af_id}")
        if cached_afw:
            afw = [Box(element) for element in json.loads(cached_afw)]
        else:
            self.cursor = self.__get_deep_db_connection().cursor
            self.cursor.execute(af_widget_by_id.format(self.af_id))
            fetch = self.cursor.fetchall()
            if not fetch:
                raise ValueError(f"Not possible to retrieve framework widgets: {self.af_id}")
            else:
                afw = [Box(dict(zip([c.name for c in self.cursor.description], row))) for row in fetch]
                afw = [element for element in afw if afw.widget_id in self.AVAILABLE_WIDGETS]
                self.redis.set(
                    name=f"af_id:{self.af_id}", 
                    ex=expire_time, 
                    value=json.dumps(afw)
                )

        return afw

    def __predict_entry(self, excerpt: str):

        # this method run a parallel predition across all the selected widgets 
        results_dict = {}    

        def select_model_instance(model_name: str):
            
            if self.model_family == "bedrock": model = ChatBedrock(model_id=model_name, temperature=0)
            elif self.model_family == "openai": model = ChatOpenAI(model=model_name, temperature=0)
            
            return model
    
        def create_chain(prompt: str, llm: str, pydantic_model: BaseModel):
            
            tagging_prompt = ChatPromptTemplate.from_template(prompt)
            _llm = select_model_instance(model_name=llm).with_structured_output(pydantic_model)
            return tagging_prompt | _llm

        # running the excerpt tagging in a parallel way across all the widgets of the framework
        parallel_tasks = RunnableParallel(**{k: 
                                             create_chain(v.prompt, 
                                                          v.model, 
                                                          v.pyd_class) for k, v in self.widgets.schemas.items()})

        results = parallel_tasks.invoke({"input": excerpt})
        
        # here we select just the alias keys tagged as True
        for k, v in results.items():
            results_dict.update({k: []})
            for i, j in v.dict(by_alias=True).items():
                if j: results_dict[k].append(i)
        
        return self.__convert_result(results_dict)
    
    def predict(self, excerpts: list):
        
        excerpts = [text.get("entry") for text in excerpts]
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.__predict_entry, excerpts))

        return results    

    def __convert_result(self, prediction: dict):

        results = {}
        for k, v in prediction.items():
            # don't add nothing to the result if no tags are predicted
            if not v: continue

            type_ = self.widgets.schemas[k].type
            schema = self.widgets.schemas[k].properties
            
            if type_ == self.widgets.mappings_instance.WidgetTypes.matrix1dWidget:

                if k not in results.keys(): results.update({k: {}})
                for c in v:
                    alias = schema[c]["alias"]
                    pillar, subpillar = alias.split("->")
                    if pillar not in results[k].keys(): results[k].update({pillar: {}})
                    results[k][pillar].update({subpillar: True})

            elif type_ == self.widgets.mappings_instance.WidgetTypes.matrix2dWidget:

                if k not in results.keys(): results.update({k: {}})
                for c in v:
                    alias = schema[c]["alias"]
                    elements = alias.split("->")
                    if len(elements) == 3: # prediction without subcolumn
                        sector, pillar, subpillar = elements
                        if pillar not in results[k].keys(): results[k].update({pillar: {}})
                        if not subpillar in results[k][pillar].keys(): results[k][pillar].update({subpillar: {}})
                        results[k][pillar][subpillar].update({sector: []})
                    elif len(elements) == 4: # prediction with subcolumn
                        sector, subsector, pillar, subpillar = elements
                        if pillar not in results[k].keys(): results[k].update({pillar: {}})
                        if not subpillar in results[k][pillar].keys(): results[k][pillar].update({subpillar: {}})
                        if not sector in results[k][pillar][subpillar].keys(): results[k][pillar][subpillar].update({sector: []})
                        results[k][pillar][subpillar][sector].append(subsector)

            elif type_ == self.widgets.mappings_instance.WidgetTypes.multiselectWidget:
                raise NotImplementedError
            
            elif type_ == self.widgets.mappings_instance.WidgetTypes.organigramWidget:
                raise NotImplementedError
            
            elif type_ == self.widgets.mappings_instance.WidgetTypes.dateRangeWidget:
                raise NotImplementedError
            
            elif type_ == self.widgets.mappings_instance.WidgetTypes.scaleWidget:
                raise NotImplementedError
        
        return results
