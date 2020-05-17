from useful_functions_and_class.custom_exceptions import AlgorithmError


class Payload:
    def __init__(self, data):
        self.load = data["load"]
        self.fuels = data["fuels"]
        self.powerplants = [Powerplant(powerplant) for powerplant in data["powerplants"]]
        self.emissions = 0.3  # ton of co2 per Mwh (for both Gaz and Kerosine ?)



class Powerplant:
    def __init__(self, powerplant):
        self.name = powerplant["name"]
        self.type = powerplant["type"]
        self.efficiency = powerplant["efficiency"]
        self.pmin = powerplant["pmin"]
        self.pmax = powerplant["pmax"]
        self.p = None
        self.cost = None


class PowerFinder(Payload):
    """The class that will find the production plan."""
    def __init__(self, data):
        super().__init__(data)
        # self.load = data["load"]
        # self.fuels = data["fuels"]
        # self.powerplants = data["powerplants"]
        self.response = None

    def run(self):
        """
        Method to process the data to find the production plan. Also create the response to send

        Returns:
            message (list): a list containing of dict containing the name and production for each
            of the different powerplants.
        """
        self.set_merit_order()
        self.find_power_plan()
        self.generate_response()
        return self.response

    def set_merit_order(self):
        """iterate through powerplants, estimate the cost for generating power for each powerplants and sort
        powerplants in the cost order."""
        powerplants_sorted = []

        for pp in self.powerplants:
            if pp.type == "windturbine":
                pp.pmax = int(pp.pmax * self.fuels["wind(%)"] / 100)
                self.__update_cost_powerplant_and_sort_it(powerplants_sorted, pp)
            elif pp.type == "turbojet":
                self.__estimate_cost_update_powerplant_and_sort_it(powerplants_sorted, pp, "kerosine(euro/MWh)")
            elif pp.type == "gasfired":
                self.__estimate_cost_update_powerplant_and_sort_it(powerplants_sorted, pp, "gas(euro/MWh)")
            else:
                raise TypeError(f"unknown powerplant type: {pp.type}. Should be: windturbine, turbojet or gasfired")
        self.powerplants = powerplants_sorted

    def find_power_plan(self):
        """The algorithm which take the powerplant in the merit order and set the production plan"""
        total_production = 0

        for i, pp in enumerate(self.powerplants):

            if self.__load_already_satisfied(total_production):
                pp.p = 0

            elif self.__load_unsatisfied_by_adding_powerplant_max_production(total_production, pp.pmax):
                total_production += self.__update_powerplant_production_and_returns_total_production(pp, pp.pmax)

            elif self.__powerplant_pmin_too_high_to_fill_the_load(total_production, pp.pmin):
                total_production += self.__perform_adjustment(total_production, pp, i)

            elif self.__needed_power_to_fill_the_load_in_current_powerplant_production_interval(total_production, pp):
                total_production += self.__update_powerplant_production_and_returns_total_production(
                    pp, self.load - total_production)

        if self.load != total_production:
            raise AlgorithmError("production does not fill the load")

    def generate_response(self):
        """create a new list of dictionary for the request response.
        It is based on powerplants one with only the name and production."""
        self.response = [{"name": pp.name, "p": pp.p} for pp in self.powerplants]

    @staticmethod
    def __insort(a, x):
        """
        a custum insert_right function from bisect module.
        insert "x" in "a" assuming "x" is a dict, "a" a list of dict, "x" and every dict
        in "a" contains the key "cost".

        Parameters:
            a (list): a list of dictionary, the dictionaries must contain "cost" as key
            x (Powerplant): the dict to insert in the "cost" value order.
        """
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo+hi)//2
            if x.cost < a[mid].cost:
                hi = mid
            else:
                lo = mid+1
        a.insert(lo, x)

    def __estimate_cost(self, powerplant, fuels_type):
        """
        Estimate the cost of producing electricity with a powerplant.
        Parameters:
            powerplant (Powerplant): A powerplant as dict
            fuels_type (str): The combined production of all the powerplant delivering power
        Returns:
            cost (float): The cost of generating power with a powerplant
        """
        return powerplant.efficiency * (self.fuels[fuels_type] + self.fuels["co2(euro/ton)"] * self.emissions)

    def __update_cost_powerplant_and_sort_it(self,powerplants, powerplant, cost=0):
        """
        Update powerplant cost and insert powerplant in the merit order
        Parameters:
            powerplants (list): A list of powerplant as dict
            powerplant (Powerplant): A powerplant as dict
            cost (float): The cost of generating power with a powerplant
        """
        self.cost = cost
        self.__insort(powerplants, powerplant)

    def __estimate_cost_update_powerplant_and_sort_it(self, powerplants, powerplant, fuels_type):
        """
        Update powerplant cost and insert powerplant in the merit order

        Parameters:
            powerplants (list): A list of powerplant as dict
            powerplant (Powerplant): A powerplant as dict
            fuels_type (str): The combined production of all the powerplant delivering power
        """
        cost = self.__estimate_cost(powerplant, fuels_type)
        self.__update_cost_powerplant_and_sort_it(powerplants, powerplant, cost)

    def __load_already_satisfied(self, total_production):
        """
        Return True if load already satisfied, False otherwise.
        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
        Returns:
            (bool): True if load already satisfied, False otherwise.
        """
        return total_production - self.load == 0

    def __load_unsatisfied_by_adding_powerplant_max_production(self, total_production, powerplant_max_production):
        """
        If the current powerplant pmax is not enough to fill the load, it's production is set to pmax.
        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
            powerplant_max_production (int): The powerplant maximum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        return total_production + powerplant_max_production - self.load < 0

    def __powerplant_pmin_too_high_to_fill_the_load(self, total_production, powerplant_min_production):
        """
        If the minimum production of the current powerplant is too low to fill the load.
        Parameters:
            total_production (int): The combined production of all the powerplant delivering power.
            powerplant_min_production (int): The powerplant maximum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        return total_production + powerplant_min_production - self.load > 0

    def __previous_powerplant_production_interval_higher_than_needed_production_offset(
            self, current_powerplant_index, previous_powerplant_power_needed_offset):
        """
        Check if we can subtract to previous powerplant the needed production for the current powerplant to fill the
        load with it's minimum production.

        Parameters:
            current_powerplant_index (int): The index od the current powerplant in the merit order.
            previous_powerplant_power_needed_offset (int): The needed offset we must remove from previous powerplant for
                the current one being able to fill the load with it's minimum production.
        Returns:
            (bool): True condition satisfied, False otherwise.
        """
        power_production_interval = self.powerplants[current_powerplant_index-1].pmax - \
                                    self.powerplants[current_powerplant_index-1].pmin
        return power_production_interval - previous_powerplant_power_needed_offset > 0

    def __needed_power_to_fill_the_load_in_current_powerplant_production_interval(self, total_production, powerplant):
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
    def __update_powerplant_production_and_returns_total_production(powerplant, powerplant_production,
                                                                    previous_powerplant_power_needed_offset=0):
        """
        Update an item of the given powerplant
        Parameters:
            powerplant (Powerplant): a powerplant as dict
            powerplant_production (int): the current powerplant production
            previous_powerplant_power_needed_offset (int): deduction of the total production coming from previous powerplant
        Returns:
            (int): The offset of the total production
        """
        powerplant.p = powerplant_production
        return powerplant.p - previous_powerplant_power_needed_offset

    def __previous_powerplant_adjustment_and_current_one_setting(self, powerplant,
                                                                 current_powerplant_index,
                                                                 previous_powerplant_power_needed_offset):
        """
        Sutract the right amount of production of previous powerplant for the current one to fill the load with it's
        minimum production.
        Parameters:
            powerplant (Powerplant): a powerplant as dict
            current_powerplant_index (int): The index od the current powerplant in the merit order.
            previous_powerplant_power_needed_offset (int): The needed offset we must remove from previous powerplant for
                the current one being able to fill the load with it's minimum production.
        """
        if self.__previous_powerplant_production_interval_higher_than_needed_production_offset(
                current_powerplant_index, previous_powerplant_power_needed_offset):

            # decrease prrodction of previous powerplant
            self.powerplants[current_powerplant_index - 1].p -= previous_powerplant_power_needed_offset
            return self.__update_powerplant_production_and_returns_total_production(
                powerplant, powerplant.pmin, previous_powerplant_power_needed_offset)
        else:
            raise AlgorithmError("this algorithm is not robust enough, it can't subtract the production of "
                                 "enough powerplant for the current one to be able to fill the load")

    def __perform_adjustment(self, total_production, powerplant, current_powerplant_index):
        """
        Calculate how much we need to subtract from previous powerplant for current one to fill the load, remove this
        production value from previous powerplant and set the current powerplant production to it's minimum production.
        Parameters:
            total_pruduction (int): The combined production of all the powerplant delivering power.
            powerplant (Powerplant): A powerplant as dict
            current_powerplant_index (int): The index of the current powerplant in the merit order.
        """
        # calculate how much we need to subtract from previous powerplant for current one to fill the load
        previous_powerplant_power_needed_offset = total_production + powerplant.pmin - self.load

        # check if there is a previous powerplant in the stack
        if current_powerplant_index > 0:

            # Remove from previous powerplant the overfull production and set to current one the needed one
            return self.__previous_powerplant_adjustment_and_current_one_setting(
                powerplant, current_powerplant_index, previous_powerplant_power_needed_offset)
        else:
            raise AlgorithmError("this algorithm can't fill the load if the load is "
                                 "lower than pmin of the first powerplant in the merit-order")





