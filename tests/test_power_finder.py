import unittest
import random

from useful_functions_and_class.custom_exceptions import AlgorithmError
from useful_functions_and_class.power_finder import PowerFinder
from . import payload


class SortByMeritOrderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_sort_by_merit_order_ListOfPowerplants_NoException(self):
        powerfinder = PowerFinder(payload)
        powerfinder.sort_by_merit_order()
        all_costs = [pp.cost for pp in powerfinder.powerplants]
        self.assertEqual(all_costs, sorted(all_costs))

    def test_sort_by_merit_order_UnknownPowerplantsType_TypeError(self):
        powerfinder = PowerFinder(payload)
        powerfinder.powerplants[0].type = "anUnknownType"
        self.assertRaises(TypeError, powerfinder.sort_by_merit_order)

    def test_sort_by_merit_order_ListOfPowerplantsUnknown_TypeError(self):
        powerfinder = PowerFinder(payload)
        powerfinder.fuels.co2 = "42"
        self.assertRaises(TypeError, powerfinder.sort_by_merit_order)


class UpdatePowerplantsProductionTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_update_powerplants_production_NormalData_NoException(self):
        data = payload
        power_finder = PowerFinder(data)
        power_finder.sort_by_merit_order()
        try:
            power_finder.update_powerplants_production()
        except Exception:
            self.fail("interval_checking raised Exception unexpectedly!")

    def test_update_powerplants_production_LoadTooHigh_TypeError(self):
        data = payload
        power_finder = PowerFinder(data)
        power_finder.load = 100000
        power_finder.sort_by_merit_order()
        self.assertRaises(AlgorithmError, power_finder.update_powerplants_production)

    def test_update_powerplants_production_NegativeLoad_AlgorithmError(self):
        data = payload
        power_finder = PowerFinder(data)
        power_finder.load = -1
        power_finder.sort_by_merit_order()
        self.assertRaises(AlgorithmError, power_finder.update_powerplants_production)

    def test_update_powerplants_production_WrongTypeLoad_TypeError(self):
        data = payload
        power_finder = PowerFinder(data)
        power_finder.load = "42"
        power_finder.sort_by_merit_order()
        self.assertRaises(TypeError, power_finder.update_powerplants_production)

    def test_update_powerplants_production_NoPowerPlants_AlgorithmError(self):
        data = payload
        power_finder = PowerFinder(data)
        power_finder.powerplants = []
        power_finder.sort_by_merit_order()
        self.assertRaises(AlgorithmError, power_finder.update_powerplants_production)


class InsortPowerplantsByCostTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_insort_powerplants_by_cost_NoPowerPlants_AlgorithmError(self):
        data = payload
        sorted_powerplants = []
        powerplants = PowerFinder(data).powerplants
        for pp in powerplants:
            pp.cost = random.randint(1, 101)
        costs = [pp.cost for pp in powerplants]
        for pp in powerplants:
            PowerFinder.insort_powerplants_by_cost(sorted_powerplants, pp)
        sorted_costs = [pp.cost for pp in sorted_powerplants]
        costs.sort()
        self.assertEqual(sorted_costs, costs)








if __name__ == '__main__':
    unittest.main()