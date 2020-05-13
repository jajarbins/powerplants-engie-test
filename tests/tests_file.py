import unittest
import json

from find_prooduction_plan_api.Api import app


class ApiRunningTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_successful_response(self):
        # Given
        payload = json.dumps({
            "load": 480,
            "fuels": {
                "gas(euro/MWh)": 13.4,
                "kerosine(euro/MWh)": 50.8,
                "co2(euro/ton)": 20,
                "wind(%)": 60
            },
            "powerplants": [{
                    "name": "gasfiredbig1",
                    "type": "gasfired",
                    "efficiency": 0.53,
                    "pmin": 100,
                    "pmax": 460},
                {
                    "name": "gasfiredbig2",
                    "type": "gasfired",
                    "efficiency": 0.53,
                    "pmin": 100,
                    "pmax": 460
                },
                {
                    "name": "gasfiredsomewhatsmaller",
                    "type": "gasfired",
                    "efficiency": 0.37,
                    "pmin": 40,
                    "pmax": 210
                },
                {
                    "name": "tj1",
                    "type": "turbojet",
                    "efficiency": 0.3,
                    "pmin": 0,
                    "pmax": 16
                },
                {
                    "name": "windpark1",
                    "type": "windturbine",
                    "efficiency": 1,
                    "pmin": 0,
                    "pmax": 150
                },
                {
                    "name": "windpark2",
                    "type": "windturbine",
                    "efficiency": 1,
                    "pmin": 0,
                    "pmax": 36
                }
            ]
        })

        expected_output = [{
            "name": "windpark1",
            "p": 90
        },
        {
            "name": "windpark2",
            "p": 21
        },
        {
            "name": "gasfiredsomewhatsmaller",
            "p": 210
        },
        {
            "name": "gasfiredbig1",
            "p": 159
        },
        {
            "name": "gasfiredbig2",
            "p": 0
        },
        {
            "name": "tj1",
            "p": 0
        }]

        # When
        response = self.app.post('/power', headers={"Content-Type": "application/json"}, data=payload)

        # Then
        self.assertEqual(list, type(response.json))
        self.assertCountEqual(response.json, expected_output)
        self.assertEqual(200, response.status_code)