import logging
from flask import Flask, request
from flask_restful import Resource, Api
from script_functions import sanity_check, find_powerplants_production

# Create Api
app = Flask(__name__)
api = Api(app)

# Create logger
logging.basicConfig(filename="log_file.log",
                    level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


# Creation Of Main Endpoint Classes
class Power(Resource):
    def post(self):
        app.logger.info("This is an info message")

        # Get POST data as json & read it as a DataFrame
        payload_data_dict = None
        try:
            payload_data_dict = request.get_json()
        except Exception as err:
            logging.error(err)

        false_or_message = sanity_check(payload_data_dict)
        if false_or_message:
            return false_or_message

        res = find_powerplants_production(payload_data_dict)

        return res


# Addition of the Endpoint Classes As Endpoints For The RESTFul API
api.add_resource(Power, '/power')


if __name__ == '__main__':
    app.run(debug=True)