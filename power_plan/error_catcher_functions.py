import logging

from power_plan.custom_exceptions import AlgorithmError, SanityCheckInternalError
from power_plan.incoming_data_check import perform_sanity_check
from power_plan.powerplan import PowerPlan


def find_powerplants_production(payload_data):
    """
    the method to call to find the production plan.
    It instantiates a PowerFinder object and catch errors if some appears.

    Parameters:
        payload_data (dict): a dictionary containing load, fuels and powerplants as keys

    Returns:
        message: False if the incoming dict is correct, an error message otherwise
    """
    try:
        return PowerPlan(payload_data).run()
    except (TypeError, AttributeError, IndexError, KeyError, NameError, ValueError, AlgorithmError) as err:
        logging.error(err)
        return {"error": err.args[0]}


def extract_json_from_request(request):
    try:
        return request.get_json()
    except Exception as err:
        logging.error(err)
        return {"error": err.args[0]}



def sanity_check(data):
    try:
        perform_sanity_check(data)
    except (ValueError, TypeError, SanityCheckInternalError) as err:
        logging.error(err)
        return {"error": err.args[0]}



