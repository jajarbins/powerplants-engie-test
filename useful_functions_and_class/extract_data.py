from useful_functions_and_class.error_catcher_functions import extract_json_from_request, sanity_check
import logging


def extract_data(request):
    """
    Check if the request contains the expected data

    Parameters:
        request:
    :return:
    """

    # Check if request contains data and if it is extractable
    if request.data:
        is_data_extracted, request_body_content_or_error = extract_json_from_request(request)
        if not is_data_extracted:
            logging.error(request_body_content_or_error)
            return {"error": request_body_content_or_error}
    else:
        msg = "no data in request"
        logging.error(msg)
        return {"error": msg}

    # Check if the received data is in the expected shape
    is_data_clean, error_message = sanity_check(request_body_content_or_error)
    if not is_data_clean:
        logging.error(error_message)
        return {"error": error_message}
    return request_body_content_or_error
