import unittest

from useful_functions_and_class.incoming_data_check import type_checking



class TypeChecking(unittest.TestCase):

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
        self.assertRaises(TypeError, type_checking, *args, **kwds)

        type_checking()

