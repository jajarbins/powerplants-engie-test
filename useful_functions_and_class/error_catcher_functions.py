import logging

from useful_functions_and_class.custom_exceptions import AlgorithmError, SanityCheckInternalError
from useful_functions_and_class.incoming_data_check import perform_sanity_check
from useful_functions_and_class.power_finder import PowerFinder


def find_powerplants_production(payload_data):
    """
    the method to call to find the production plan.
    It instantiates a PowerFinder object and catch errors if some appears.

    Parameters:
        payload_data (dict): a dictionary containing load, fuels and powerplants as keys

    Returns:
        message: False if the incoming dict is correct, an error message otherwise
    """
    response = None
    try:
        response = PowerFinder(payload_data).run()
    except (TypeError, AttributeError, IndexError, KeyError, NameError, ValueError, AlgorithmError) as err:
        logging.error(err)
        response = {"error": err}
    finally:
        return response


def extract_json_from_request(request):
    try:
        payload_data_dict = request.get_json()
    except Exception as err:
        logging.error(err)
        return False, err
    return True, payload_data_dict


def sanity_check(data):
    try:
        perform_sanity_check(data)
    except (ValueError, TypeError, SanityCheckInternalError) as err:
        logging.error(err)
        return False, err
    return True, ""


