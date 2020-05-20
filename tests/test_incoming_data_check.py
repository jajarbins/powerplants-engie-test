import unittest

from . import payload
from power_plan.custom_exceptions import SanityCheckInternalError
from power_plan.incoming_data_check import type_checking, values_checking, interval_checking, \
    convert_interval_value, check_json_layer, perform_sanity_check


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

    def test_type_checking_IntWithOptionalArgs_NoException(self):
        try:
            type_checking(2, int, "data_name")
        except Exception:
            self.fail("type_checking(2, int) raised Exception unexpectedly!")

    def test_type_checking_StrWithOptionalArgsNnoException(self):
        try:
            type_checking("", str, "data_name")
        except Exception:
            self.fail("type_checking('', str) raised Exception unexpectedly!")

    def test_type_checking_TypeDoesNotFitWithOptionalArgs_TypeError(self):
        self.assertRaises(TypeError, type_checking, {"data_to_check": 0, "type_to_check": str, "data_name": "a"})


class ValuesCheckingTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_values_checking_List_NoException(self):
        a = [1, 2, "a", "b"]
        b = [1, "a"]
        try:
            values_checking(a, b)
        except Exception:
            self.fail("values_checking raised Exception unexpectedly!")

    def test_values_checking_Tuples_NoException(self):
        a = [1, 2, "a", "b"]
        b = [2, "b"]
        try:
            values_checking(a, b)
        except Exception:
            self.fail("values_checking raised Exception unexpectedly!")

    def test_values_checking_DictKeys_NoException(self):
        a = {"a": 1, "b": 2, "c": 3}
        b = {"a": 4, "b": 5}
        try:
            values_checking(a.keys(), b.keys())
        except Exception:
            self.fail("values_checking raised Exception unexpectedly!")

    def test_values_checking_List_ValueError(self):
        a = ["a", "b", "c"]
        b = ["a", "b", "d"]
        self.assertRaises(ValueError, values_checking, **{"values_list": a, "expected_values": b})


class IntervalCheckingTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_interval_checking_OneElement_NoException(self):
        json_layer = {"a": 1}
        layer_key = "a"
        interval = (0,)
        try:
            interval_checking(json_layer, layer_key, interval)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_interval_checking_TwoElements_NoException(self):
        json_layer = {"a": 1}
        layer_key = "a"
        interval = (0, 2)
        try:
            interval_checking(json_layer, layer_key, interval)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_interval_checking_OneElementAtLimit_NoException(self):
        json_layer = {"a": 1}
        layer_key = "a"
        interval = (1,)
        try:
            interval_checking(json_layer, layer_key, interval)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_interval_checking_TwoElementsAtLimit1_NoException(self):
        json_layer = {"a": 1}
        layer_key = "a"
        interval = (0, 1)
        try:
            interval_checking(json_layer, layer_key, interval)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_interval_checking_TwoElementsAtLimit2_NoException(self):
        json_layer = {"a": 0}
        layer_key = "a"
        interval = (0, 1)
        try:
            interval_checking(json_layer, layer_key, interval)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_interval_checking_ElementNotInDict_KeyError(self):
        json_layer = {"a": 1.1}
        layer_key = "b"
        interval = (0, 1)
        self.assertRaises(KeyError, interval_checking, **{"json_layer": json_layer,
                                                            "layer_key": layer_key,
                                                            "interval": interval})

    def test_interval_checking_OneElement_ValueError(self):
        json_layer = {"a": 1}
        layer_key = "a"
        interval = (2,)
        self.assertRaises(ValueError, interval_checking, **{"json_layer": json_layer,
                                                            "layer_key": layer_key,
                                                            "interval": interval})

    def test_interval_checking_TwoElements1_ValueError(self):
        json_layer = {"a": 0}
        layer_key = "a"
        interval = (0.1, 1)
        self.assertRaises(ValueError, interval_checking, **{"json_layer": json_layer,
                                                            "layer_key": layer_key,
                                                            "interval": interval})

    def test_interval_checking_TwoElements2_ValueError(self):
        json_layer = {"a": 1.1}
        layer_key = "a"
        interval = (0, 1)
        self.assertRaises(ValueError, interval_checking, **{"json_layer": json_layer,
                                                            "layer_key": layer_key,
                                                            "interval": interval})

    def test_interval_checking_TooManyIntervalElements1_SanityCheckInternalError(self):
        json_layer = {"a": 1.1}
        layer_key = "a"
        interval = ()
        self.assertRaises(SanityCheckInternalError, interval_checking, **{"json_layer": json_layer,
                                                                          "layer_key": layer_key,
                                                                          "interval": interval})

    def test_interval_checking_TooManyIntervalElements2_SanityCheckInternalError(self):
        json_layer = {"a": 1.1}
        layer_key = "a"
        interval = (0, 1, 12)
        self.assertRaises(SanityCheckInternalError, interval_checking, **{"json_layer": json_layer,
                                                                          "layer_key": layer_key,
                                                                          "interval": interval})


class ConvertIntervalValueTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_convert_interval_value_Int_Equal(self):
        self.assertEqual(convert_interval_value(1), 1)

    def test_convert_interval_value_Float_Equal(self):
        self.assertEqual(convert_interval_value(1.0), 1.0)

    def test_convert_interval_value_IntWithJsonLayer_Equal(self):
        self.assertEqual(convert_interval_value(1, {"a": 1}), 1)

    def test_convert_interval_value_StrWithJsonLayer_Equal(self):
        self.assertEqual(convert_interval_value("a", {"a": 1}), 1)

    def test_convert_interval_value_StrWrongKeyWithJsonLayer_KeyError(self):
        self.assertRaises(KeyError, convert_interval_value, **{"interval_bound": "b", "json_layer": {"a": 1}})

    def test_convert_interval_value_StrWithoutJsonLayer_SanityCheckInternalError(self):
        self.assertRaises(SanityCheckInternalError, convert_interval_value, **{"interval_bound": "b"})


class CheckJsonLayerTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_check_json_layer_IntDict_NoException(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", int, (0,)),
            ("b", dict, None)
        ]
        try:
            check_json_layer(a, b)
        except Exception:
            self.fail("check_json_layer raised Exception unexpectedly!")

    def test_check_json_layer_IntervalAsStrAndValueHigherThanInterval_NoException(self):
        a = {"a": 2, "b": 1}
        b = [
            ("a", int, ("b",)),
            ("b", int, None)
        ]
        try:
            check_json_layer(a, b)
        except Exception:
            self.fail("check_json_layer raised Exception unexpectedly!")

    def test_check_json_layer_WrongKey_ValueError(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", int, (0,)),
            ("c", dict, None)
        ]
        self.assertRaises(ValueError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_WrongValueType_TypeError(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", str, (0,)),
            ("b", dict, None)
        ]
        self.assertRaises(TypeError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_ValueLowerThanInterval_ValueError(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", int, (2,)),
            ("b", dict, None)
        ]
        self.assertRaises(ValueError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_ValueOutOfInterval_ValueError(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", int, (2, 3)),
            ("b", dict, None)
        ]
        self.assertRaises(ValueError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_IntervalSetWhereItShouldNot_TypeError(self):
        a = {"a": 1, "b": {"x": 1}}
        b = [
            ("a", int, (0,)),
            ("b", dict, (1,))
        ]
        self.assertRaises(TypeError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_IntervalAsStrButStrNotInJsonKey_KeyError(self):
        a = {"a": 1, "b": 2}
        b = [
            ("a", int, ("c",)),
            ("b", int, None)
        ]
        self.assertRaises(KeyError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})

    def test_check_json_layer_IntervalAsStrAndValueTooLow_ValueError(self):
        a = {"a": 1, "b": 2}
        b = [
            ("a", int, ("b",)),
            ("b", int, None)
        ]
        self.assertRaises(ValueError, check_json_layer, **{"json_layer": a, "key_value_type_and_interval": b})


# perform_sanity_check
class PerformSanityCheckTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_perform_sanity_check_ExpectedDict_NoException(self):
        data = payload
        try:
            perform_sanity_check(data)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_perform_sanity_check_DictWithMoreElements_NoException(self):
        data = payload
        data.update({"a": 1})
        try:
            perform_sanity_check(data)
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_perform_sanity_check_WrongValue_ValueError(self):
        data = payload.copy()
        data["load"] = -1
        self.assertRaises(ValueError, perform_sanity_check, **{"data": data})

    def test_perform_sanity_check_WrongKey_KeyError(self):
        data = payload.copy()
        data["daol"] = data.pop("load")
        self.assertRaises(KeyError, perform_sanity_check, **{"data": data})

    def test_perform_sanity_check_MissingKey_KeyError(self):
        data = payload.copy()
        del data["load"]
        self.assertRaises(KeyError, perform_sanity_check, **{"data": data})


if __name__ == '__main__':
    unittest.main()