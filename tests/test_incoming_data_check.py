import unittest

from useful_functions_and_class.incoming_data_check import type_checking


class TypeCheckingTest(unittest.TestCase):

    def setUp(self):
        pass

    def run_test_int(self):
        try:
            type_checking(2, int)
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")

    def run_test_str(self):
        try:
            type_checking("", str)
        except Exception:
            self.fail("type_checking('', str) raised Exception unexpectedly!")

    def type_does_not_fit(self):
        self.assertRaises(TypeError, type_checking, {"data_to_check": 0, "type_to_check": str})

    def run_test_int_with_optional_args(self):
        try:
            type_checking(2, int, "data_name")
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")

    def run_test_str_with_optional_args(self):
        try:
            type_checking("", str, "data_name")
        except Exception:
            self.fail("type_checking('', str) raised Exception unexpectedly!")

    def type_does_not_fit_with_optional_args(self):
        self.assertRaises(TypeError, type_checking, {"data_to_check": 0, "type_to_check": str, "data_name": "a"})


if __name__ == '__main__':
    unittest.main()