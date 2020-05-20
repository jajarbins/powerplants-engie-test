from useful_functions_and_class.custom_exceptions import AlgorithmError


class Payload:
    def __init__(self, data):
        self.load = data["load"]
        self.fuels = Fuels(data["fuels"])
        self.powerplants = [Powerplant(powerplant) for powerplant in data["powerplants"]]
        self.emissions = 0.3  # ton of co2 per Mwh (for both Gaz and Kerosine ?)


class Powerplant:
    def __init__(self, powerplant):
        self.name = powerplant["name"]
        self.type = powerplant["type"]
        self.efficiency = powerplant["efficiency"]
        self.pmin = powerplant["pmin"]
        self.pmax = powerplant["pmax"]
        self.production = None
        self.cost = None

    def set_cost(self, cost):
        self.cost = cost

    def set_production(self, production):
        self.production = production


class Fuels:
    def __init__(self, fuels):
        self.gas = fuels["gas(euro/MWh)"]
        self.kerosine = fuels["kerosine(euro/MWh)"]
        self.co2 = fuels["co2(euro/ton)"]
        self.wind = fuels["wind(%)"]



class PowerFinder(Payload):
    """The class that will find the production plan."""

    def __init__(self, data):
        super().__init__(data)

    def run(self):
        """
        Method to process the data to find the production plan. Also create the response to send

        Returns:
            message (list): a list containing of dict containing the name and production for each
            of the different powerplants.
        """
        self.sort_by_merit_order()
        self.update_powerplants_production()
        return self.generate_response()

    def sort_by_merit_order(self):
        """iterate through powerplants, estimate the cost for generating power for each powerplants and sort
        powerplants in the cost order."""
        powerplants_sorted = []

        for pp in self.powerplants:
            cost = 0
            if pp.type == "windturbine":
                pp.pmax = int(pp.pmax * self.fuels.wind / 100)
            elif pp.type == "turbojet" or pp.type == "gasfired":
                cost = self.__estimate_cost(pp)
            else:
                raise TypeError(f"unknown powerplant type: {pp.type}. Should be: windturbine, turbojet or gasfired")
            pp.set_cost(cost)
            self.insort_powerplants_by_cost(powerplants_sorted, pp)

        self.powerplants = powerplants_sorted

    def update_powerplants_production(self):
        """The algorithm which take the powerplant in the merit order and set the production plan"""
        total_production = 0

        for i, pp in enumerate(self.powerplants):

            if self.__is_load_already_satisfied(total_production):
                pp.set_production(0)

            elif self.__is_load_unsatisfied_by_adding_powerplant_max_production(total_production, pp.pmax):
                total_production += self.__update_current_powerplant_production(pp, pp.pmax)

            elif self.__is_powerplant_pmin_too_high_to_fill_the_load(total_production, pp.pmin):
                total_production += self.__update_previous_and_current_powerplant_production(total_production, pp, i)

            elif self.__is_needed_power_to_fill_the_load_in_current_powerplant_production_interval(total_production, pp):
                total_production += self.__update_current_powerplant_production(pp, self.load - total_production)

        if self.load != total_production:
            raise AlgorithmError("production does not fill the load")

    def generate_response(self):
        """create a new list of dictionary for the request response.
        It is based on powerplants one with only the name and production."""
        return [{"name": pp.name, "p": pp.production} for pp in self.powerplants]

    @staticmethod
    def insort_powerplants_by_cost(a, x):
        """
        a custum insert_right function from bisect module.
        insert "x" in "a" assuming "x" is a Powerplant, "a" a list of Powerplants, "x" and "cost" parameter is set in
        every Powerplant in "a".

        Parameters:
            a (list): a list of PowerPlants, the dictionaries must contain "cost" as key
            x (Powerplant): the dict to insert in the "cost" value order.
        """
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if x.cost < a[mid].cost:
                hi = mid
            else:
                lo = mid + 1
        a.insert(lo, x)

    def __estimate_cost(self, powerplant):
        """
        Estimate the cost of producing electricity with a powerplant.

        Parameters:
            powerplant (Powerplant): The current powerplant
        Returns:
            cost (float): The cost of generating power with a powerplant
        """
        return powerplant.efficiency * (self.__set_fuel(powerplant) + self.fuels.co2 * self.emissions)

    def __set_fuel(self, powerplant):
        """
        Given a powerplant, returns its fuel cost.

        Parameters:
            powerplant (Powerplant): The current powerplant
        Returns:
            fuel (float): the cost of the fuel
        """
        if powerplant.type == "gasfired":
            return self.fuels.gas
        elif powerplant.type == "turbojet":
            return self.fuels.kerosine
        elif powerplant.type == "windturbine":
            return 0
        else:
            raise TypeError(f"Unknown powerplant type: {powerplant.type}")

    def __is_load_already_satisfied(self, total_production):
        """
        Return True if load already satisfied, False otherwise.

        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
        Returns:
            (bool): True if load already satisfied, False otherwise.
        """
        return total_production - self.load == 0

    def __is_load_unsatisfied_by_adding_powerplant_max_production(self, total_production, powerplant_max_production):
        """
        If the current powerplant pmax is not enough to fill the load, it's production is set to pmax.

        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
            powerplant_max_production (int): The powerplant maximum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        return total_production + powerplant_max_production - self.load < 0

    def __is_powerplant_pmin_too_high_to_fill_the_load(self, total_production, powerplant_min_production):
        """
        If the minimum production of the current powerplant is too low to fill the load.

        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
            powerplant_min_production (int): The powerplant maximum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        return total_production + powerplant_min_production - self.load > 0

    @staticmethod
    def __previous_powerplant_production_interval_higher_than_needed_production_offset(
            previous_powerplant, previous_powerplant_power_needed_offset):
        """
        Check if we can subtract to previous powerplant the needed production for the current powerplant to fill the
        load with it's minimum production.

        Parameters:
            previous_powerplant (Powerplant): The previous powerplant in the merit order.
            previous_powerplant_power_needed_offset (int): The needed offset we must remove from previous powerplant for
                the current one being able to fill the load with it's minimum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        power_production_interval = previous_powerplant.pmax - previous_powerplant.pmin
        return power_production_interval - previous_powerplant_power_needed_offset > 0

    def __is_needed_power_to_fill_the_load_in_current_powerplant_production_interval(self, total_production, powerplant):
        """
        If the current powerplant max production is enough to fill the load, but pmin is higher, we set the production
        to what we need to fill the load.

        Parameters:
            total_production (int):
            powerplant (Powerplant):
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        return total_production + powerplant.pmax >= self.load >= total_production + powerplant.pmin

    @staticmethod
    def __update_current_powerplant_production(powerplant, powerplant_production,
                                               previous_powerplant_production_offset=0):
        """
        Update an item of the given powerplant.

        Parameters:
            powerplant (Powerplant): The current powerplant
            powerplant_production (int): the current powerplant production
            previous_powerplant_production_offset (int): deduction of the total production coming from previous powerplant
        Returns:
            (int): The offset of the total production
        """
        powerplant.set_production(powerplant_production)
        return powerplant.production - previous_powerplant_production_offset

    def __perform_previous_and_current_powerplant_production_adjustment(self,
                                                                        powerplant,
                                                                        previous_powerplant,
                                                                        previous_powerplant_production_offset):
        """
        Sutract the right amount of production of previous powerplant for the current one to fill the load with it's
        minimum production.
        Parameters:
            powerplant (Powerplant): The current powerplant
            previous_powerplant (Powerplant): The previous powerplant in the merit order.
            previous_powerplant_production_offset (int): The needed offset we must remove from previous powerplant for
                the current one being able to fill the load with it's minimum production.
        """
        if self.__previous_powerplant_production_interval_higher_than_needed_production_offset(
                previous_powerplant, previous_powerplant_production_offset):

            # decrease prodction of previous powerplant for next one to be turned on.
            previous_powerplant.set_production(previous_powerplant.production - previous_powerplant_production_offset)

            # set production of current powerplant to pmin
            return self.__update_current_powerplant_production(powerplant, powerplant.pmin,
                                                               previous_powerplant_production_offset)
        else:
            raise AlgorithmError("this algorithm is not robust enough, it can't subtract the production of "
                                 "enough powerplant for the current one to be able to fill the load")

    def __update_previous_and_current_powerplant_production(self, total_production, powerplant,
                                                            current_powerplant_index):
        """
        Calculate how much we need to subtract from previous powerplant for current one to fill the load, remove this
        production value from previous powerplant and set the current powerplant production to it's minimum production.
        Parameters:
            total_pruduction (int): The combined production of all the powerplant delivering power.
            powerplant (Powerplant): The current powerplant
            current_powerplant_index (int): The index of the current powerplant in the merit order.
        """
        # calculate how much we need to subtract from previous powerplant for current one to fill the load
        previous_powerplant_production_offset = total_production + powerplant.pmin - self.load

        # check if there is a previous powerplant in the stack
        if current_powerplant_index > 0:

            previous_powerplant = self.powerplants[current_powerplant_index - 1]

            # Remove from previous powerplant the overfull production and set pmin to the current one
            return self.__perform_previous_and_current_powerplant_production_adjustment(
                powerplant, previous_powerplant, previous_powerplant_production_offset)
        else:
            raise AlgorithmError("this algorithm can't fill the load if the load is "
                                 "lower than pmin of the first powerplant in the merit-order")
