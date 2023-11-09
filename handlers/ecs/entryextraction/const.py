
HIGH_LEVEL_TAG_GROUPS = [
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
    ]

# This parameters were optimized in a hyperparamenters bayesian optimization process 
# A continuous learning and research is needed in order to improve the results. 
OPTIMIZED_PARAMETERS = {
    "selected_tags": ['sectors', 
                      'pillars_1d', 
                      'pillars_2d', 
                      'subpillars_1d', 
                      'Not displaced',
                      'Gender',
                      'severity'],
    "method": "standard_deviation",
    "length_weight": 0,
    "std_multiplier": 0.727764
}