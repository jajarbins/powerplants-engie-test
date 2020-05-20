import logging
from flask import Flask, request
from flask_restful import Resource, Api

from useful_functions_and_class.error_catcher_functions import find_powerplants_production, extract_json_from_request, \
    sanity_check


app = Flask(__name__)
api = Api(app)


class Power(Resource):
    def post(self):
        data = extract_json_from_request(request)
        sanity_check(data)
        return find_powerplants_production(data)


api.add_resource(Power, '/')


if __name__ == '__main__':
    logging.basicConfig(filename="./log_file.log",
                        level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

    app.run(host='0.0.0.0', port=8888)
