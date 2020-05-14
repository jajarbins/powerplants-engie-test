import logging
from flask import Flask, request
from flask_restful import Resource, Api

# Create Api
from find_prooduction_plan_api.error_catcher_functions import find_powerplants_production
from find_prooduction_plan_api.extract_data import extract_data

app = Flask(__name__)
api = Api(app)

# Config Logger
logging.basicConfig(filename="../log_file.log",
                    level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


# Creation of main endpoint classes
class Power(Resource):
    def post(self):

        request_body_content = extract_data(request)
        if "error" in request_body_content and len(request_body_content) == 1:
            return request_body_content
        return find_powerplants_production(request_body_content)


# Addition of the endpoint classes as endpoints for the RESTFul API
api.add_resource(Power, '/power')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
