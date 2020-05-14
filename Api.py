import logging
from flask import Flask, request
from flask_restful import Resource, Api

# Create Api
from find_prooduction_plan_api.usefull_functions_and_tools import sanity_check, find_powerplants_production

app = Flask(__name__)
api = Api(app)

# Create Logger
logging.basicConfig(filename="../log_file.log",
                    level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


# Creation of main endpoint classes
class Power(Resource):
    def post(self):

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


# Addition of the endpoint classes as endpoints for the RESTFul API
api.add_resource(Power, '/power')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
