from tags_mapping import get_all_mappings, get_categories
from utils import convert_to_lowercase

categories = get_categories()
mappings = get_all_mappings()

def get_model_tags_mappings(pred_data, thresholds, selected_tags=None):
    """ Maps the tags to ids """
    def get_threshold_primary_value(pt_key, t_key):
        return thresholds['primary_tags'][pt_key][t_key]

    def get_threshold_secondary_value(st_key, t_key):
        return thresholds['secondary_tags'][st_key][t_key]

    def check_demo_grp_selected_tag(gender, age):
        return False
        #return True if gender in selected_tags["gender"][0] and age in selected_tags["age"][0] else False

    all_tags_pred = {}

    pred_data = convert_to_lowercase(pred_data)
    thresholds = convert_to_lowercase(thresholds)

    pred_data = [pred_data]
    for prim_tags_key, prim_key_val in pred_data[0]["primary_tags"].items():
        prim_tags_key = prim_tags_key.lower()
        tags = {}
        if prim_tags_key in categories:
            category = categories[prim_tags_key][0]
            tags[category] = {}

            for tag_key, tag_val in prim_key_val.items():
                tag_key = tag_key.lower()
                try:
                    tag = mappings[tag_key][0].lower()
                except KeyError:
                    continue
                tags[category][tag] = {}
                tags[category][tag]["prediction"] = round(tag_val, 3)
                tags[category][tag]["threshold"] = round(get_threshold_primary_value(prim_tags_key, tag_key), 3)
                tags[category][tag]["is_selected"] = tags[category][tag]["prediction"] >= tags[category][tag]["threshold"] #check_selected_tag(prim_tags_key, tag_key)
        all_tags_pred.update(tags)

    for sec_tags_key, sec_tags_val in pred_data[0]["secondary_tags"].items():
        tags = {}
        if sec_tags_key in categories:
            category = categories[sec_tags_key][0]
            tags[category] = {}

            for tag_key, tag_val in sec_tags_val.items():
                tag = mappings[tag_key][0]
                tags[category][tag] = {}
                tags[category][tag]["prediction"] = round(tag_val, 15)
                tags[category][tag]["threshold"] = round(get_threshold_secondary_value(sec_tags_key, tag_key), 15)
                tags[category][tag]["is_selected"] = tags[category][tag]["prediction"] >= tags[category][tag]["threshold"]
        all_tags_pred.update(tags)

    demographic_grp_id = categories['demographic_group'][0]
    tags = {}
    tags[demographic_grp_id] = {}
    for age_key, age_val in pred_data[0]["secondary_tags"]["age"].items():
        for gender_key, gender_val in pred_data[0]["secondary_tags"]["gender"].items():
            demographic_key = f"{gender_key} {age_key}"

            if demographic_key in mappings:
                tag = mappings[demographic_key][0]
                tags[demographic_grp_id][tag] = {}
                tags[demographic_grp_id][tag]["prediction"] = -1  # ignore the prediction value
                tags[demographic_grp_id][tag]["threshold"] = -1   # ignore the threshold value
                tags[demographic_grp_id][tag]["is_selected"] = check_demo_grp_selected_tag(gender_key, age_key)
    all_tags_pred.update(tags)

    return all_tags_pred