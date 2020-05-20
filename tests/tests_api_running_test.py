import unittest
import json
import logging

from Api import app
from tests import expected_output, payload


class ApiRunningTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_successful_response(self):
        # Given
        data = json.dumps(payload)
        logging.basicConfig(filename="./log_file.log",
                            level=logging.ERROR,
                            format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

        logging.error(data)
        # When
        response = self.app.post('/power', headers={"Content-Type": "application/json"}, data=data)

        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual(list, type(response.json))
        self.assertCountEqual(response.json, expected_output)


if __name__ == '__main__':
    unittest.main()