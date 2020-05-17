import unittest

from useful_functions_and_class.incoming_data_check import type_checking, values_checking


class TypeCheckingTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_type_checking_Int_NoException(self):
        try:
            type_checking(2, int)
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")

    def test_type_checking_Str_NoException(self):
        try:
            type_checking("", str)
        except Exception:
            self.fail("type_checking('', str) raised Exception unexpectedly!")

    def test_type_checking_TypeDoesNotFit_TypeError(self):
        self.assertRaises(TypeError, type_checking, {"data_to_check": 0, "type_to_check": str})

    def test_type_checking_IntWithOptionalArgs_noException(self):
        try:
            type_checking(2, int, "data_name")
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")

    def test_type_checking_StrWithOptionalArgs_noException(self):
        try:
            type_checking("", str, "data_name")
        except Exception:
            self.fail("type_checking('', str) raised Exception unexpectedly!")

    def test_type_checking_TypeDoesNotFitWithOptionalArgs_TypeError(self):
        self.assertRaises(TypeError, type_checking, {"data_to_check": 0, "type_to_check": str, "data_name": "a"})


class ValuesCheckingTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_values_checking_(self):
        try:
            type_checking(2, int)
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")






if __name__ == '__main__':
    unittest.main()