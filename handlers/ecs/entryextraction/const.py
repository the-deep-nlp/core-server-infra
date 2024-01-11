
HIGH_LEVEL_TAG_GROUPS = {
    "main-model-cpu-new-test": [
        "sectors",
        "subsectors",
        "pillars_1d",
        "pillars_2d",
        "subpillars_1d",
        "subpillars_2d",
        "specific_needs_groups",
        "Displaced",
        "Not displaced",
        "Gender",
        "severity",
        "Age"
    ],
    "main-model-cpu": [
        "sectors",
        "pillars_1d",
        "pillars_2d",
        "affected_groups",
        "age",
        "gender",
        "severity",
        "specific_needs_groups",
        "subpillars_1d",
        "subpillars_2d"
    ]
}

MAP_OLD_SUBPILLARS = {
 'Casualties': 'subpillars_1d',
 'Context': 'subpillars_1d',
 'Covid-19': 'subpillars_1d',
 'Displacement': 'subpillars_1d',
 'Humanitarian Access': 'subpillars_1d',
 'Information And Communication': 'subpillars_1d',
 'Shock/Event': 'subpillars_1d',
 'At Risk': 'subpillars_2d',
 'Capacities & Response': 'subpillars_2d',
 'Humanitarian Conditions': 'subpillars_2d',
 'Impact': 'subpillars_2d',
 'Priority Interventions': 'subpillars_2d',
 'Priority Needs': 'subpillars_2d'
}

# This parameters were optimized in a hyperparamenters bayesian optimization process 
# A continuous learning and research is needed in order to improve the results. 
OPTIMIZED_PARAMETERS = {
    "main-model-cpu-new-test": {
        "selected_tags": [
            'sectors', 
            'pillars_1d', 
            'pillars_2d', 
            'subpillars_1d', 
            'Not displaced',
            'Gender',
            'severity'
            ],
        "method": "standard_deviation",
        "length_weight": 0,
        "std_multiplier": 0.727764,
        "min_sentence_length": 15
        },
    "main-model-cpu": {
        "selected_tags": [
            'affected_groups',
            'age',
            'gender',
            'severity',
            'subpillars_2d',
            'subpillars_1d'
            ],
        "method": "standard_deviation",
        "length_weight": 0,
        "std_multiplier": 0.4407837873398228,
        "min_sentence_length": 15
    }   
}


CLASSIFICATION_MODEL_NAME = "all_tags_model_24112023"
CLASSIFICATION_MODEL_VERSION = "1.0.0"
