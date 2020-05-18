from useful_functions_and_class.custom_exceptions import SanityCheckInternalError

first_layer_keys_and_values_type_and_interval = [
    ("load", int, (0,)),
    ("fuels", dict, None),
    ("powerplants", list, None)
]

fuels_layer_keys_values_type_and_interval = [
    ("gas(euro/MWh)", (int, float), None),
    ("kerosine(euro/MWh)", (int, float), None),
    ("co2(euro/ton)", (int, float), (0,)),
    ("wind(%)", (int, float), (0, 100)),
]

powerplants_layer_keys_and_values_type_and_interval = [
    ("name", str, None),
    ("type", str, None),
    ("efficiency", (int, float), (0, 1)),
    ("pmin", int, (0, "pmax")),
    ("pmax", int, ("pmin",)),
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
    check_json_layer(data, first_layer_keys_and_values_type_and_interval)

    check_json_layer(data["fuels"], fuels_layer_keys_values_type_and_interval)
    type_checking(data["powerplants"], list)
    for pp_dict in data["powerplants"]:
        check_json_layer(pp_dict, powerplants_layer_keys_and_values_type_and_interval)


def type_checking(data_to_check, type_to_check, data_name=None):
    """
    Check if data_to_check is of type: type_to_check
    Raise a TypeError with a custom message if not the case.

    Parameters:
        data_to_check: a value
        type_to_check (type): a python type
        data_name (str: The data_to_check name in order to write an error message
    """
    if not isinstance(data_to_check, type_to_check):
        if data_name:
            error_message = f"{data_name} value should be {type_to_check} instead of {type(data_to_check)}: {data_to_check}"
        else:
            error_message = f"{data_to_check} should be {type_to_check} instead of {type(data_to_check)}: {type_to_check}"
        raise TypeError(error_message)


def values_checking(values_list, expected_values):
    """
    Check if all items in values_list are in expected_values

    Parameters:
        values_list (list, tuples, dict_keys):
        expected_values (list, tuples, dict_keys):
    """
    if not all(key in values_list for key in expected_values):
        error_message = f"wrong json keys received. It should be:" \
                        f"{[str(expected_value) for expected_value in expected_values]}. Instead we have: {values_list}"
        raise ValueError(error_message)


def interval_checking(json_layer, layer_key, interval):
    """
    Check if layer_key of json_layer is in interval
    If interval contains one value, layer_key value must be higher,
    If interval contains two values, mayer_key value must be betwwen those values

    Parameters:
        json_layer (dict): the current json layer to test
        layer_key (str): the current dict item's key to test
        interval (tuple):
    """
    if len(interval) == 1:
        minimum_value = convert_interval_value(interval[0], json_layer)

        if json_layer[layer_key] - minimum_value < 0:
            raise ValueError(f"{layer_key} value: {json_layer[layer_key]} must be higher than {minimum_value}")
    elif len(interval) == 2:
        minimum_value = convert_interval_value(interval[0], json_layer)
        maximum_value = convert_interval_value(interval[1], json_layer)

        if not minimum_value <= json_layer[layer_key] <= maximum_value:
            raise ValueError(f"{layer_key} value of {json_layer[layer_key]} is not in the interval "
                             f"[{minimum_value}, {maximum_value}] for dict {json_layer} ")
    else:
        raise SanityCheckInternalError("Incorrect number of element in interval parameter.")


def convert_interval_value(interval_bound, json_layer=None):
    if isinstance(interval_bound, str):
        if json_layer is not None:
            return json_layer[interval_bound]
        else:
            raise SanityCheckInternalError(
                "You should provide the dictionary you are analysing as parameters to the current function")
    else:
        return interval_bound


def check_json_layer(json_layer, pairs_of_key_and_value_type):
    values_checking(json_layer, [item[0] for item in pairs_of_key_and_value_type])

    for layer_key, value_type, interval in pairs_of_key_and_value_type:

        type_checking(json_layer[layer_key], value_type, layer_key)
        if interval is not None:
            interval_checking(json_layer, layer_key, interval)