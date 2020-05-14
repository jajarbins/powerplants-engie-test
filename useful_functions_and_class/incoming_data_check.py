first_layer_keys_and_values_type = [
    ("load", int),
    ("fuels", dict),
    ("powerplants", list)
]

fuels_layer_keys_and_values_type = [
    ("gas(euro/MWh)", (int, float)),
    ("kerosine(euro/MWh)", (int, float)),
    ("co2(euro/ton)", (int, float)),
    ("wind(%)", (int, float)),
]

powerplants_layer_keys_and_values_type = [
    ("name", str),
    ("type", str),
    ("efficiency", (int, float)),
    ("pmin", int),
    ("pmax", int),
]



def perform_sanity_check(data):
    """
    Check keys and value type for received json from the post request.

    Parameters:
        data (dict): a dictionary containing load, fuels and powerplants as keys.

    Returns:
        message: (True, '') if the incoming dict is correct, (False, 'an error message') otherwise.
    """
    type_checking(data, dict)
    type_checking(data["load"], (int, float))
    check_json_layer(data, first_layer_keys_and_values_type)
    check_json_layer(data["fuels"], fuels_layer_keys_and_values_type)
    type_checking(data["powerplants"], list)
    for pp_dict in data["powerplants"]:
        check_json_layer(pp_dict, powerplants_layer_keys_and_values_type)


def type_checking(data_to_check, type_to_check, key=None):
    if not isinstance(data_to_check, type_to_check):
        if key:
            error_message = f"{data_to_check} should be {type_to_check} instead of {type(data_to_check)}: {type_to_check}"
        else:
            error_message = f"{key} value should be {type_to_check} instead of {type(data_to_check)}: {data_to_check}"
        raise TypeError(error_message)


def values_checking(values_list, expected_values):
    if not all(key in values_list for key in expected_values):
        error_message = f"wrong json keys received. It should be:" \
                        f"{[str(expected_value) for expected_value in expected_values]}. Instead we have: {values_list}"
        raise ValueError(error_message)


def check_json_layer(json_layer, pairs_of_key_and_value_type):
    values_checking(json_layer, [item[0] for item in pairs_of_key_and_value_type])
    for dict_key, value_type in pairs_of_key_and_value_type:
        type_checking(json_layer[dict_key], value_type, dict_key)