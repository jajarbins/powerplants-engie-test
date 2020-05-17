import unittest
import json

from Api import app
from tests import expected_output, payload


class ApiRunningTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_successful_response(self):
        # Given
        data = json.dumps(payload)

        # When
        response = self.app.post('/power', headers={"Content-Type": "application/json"}, data=data)

        # Then
        self.assertEqual(list, type(response.json))
        self.assertCountEqual(response.json, expected_output)
        self.assertEqual(200, response.status_code)