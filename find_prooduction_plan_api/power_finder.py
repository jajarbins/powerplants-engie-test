from find_prooduction_plan_api.custom_exceptions import AlgorithmError


class PowerFinder:
    """The class that will find the production plan."""
    def __init__(self, data):
        self.load = data["load"]
        self.fuels = data["fuels"]
        self.powerplants = data["powerplants"]
        self.emissions = 0.3  # ton of co2 per Mwh (for both Gaz and Kerosine ?)
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

    @staticmethod
    def insort(a, x):
        """
        a custum insert_right function from bisect module.
        insert "x" in "a" assuming "x" is a dict, "a" a list of dict, "x" and every dict
        in "a" contains the key "cost".

        Parameters:
            a (list): a list of dictionary, the dictionaries must contain "cost" as key
            x (dict): the dict to insert in the "cost" value order.
        """
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo+hi)//2
            if x["cost"] < a[mid]["cost"]:
                hi = mid
            else:
                lo = mid+1
        a.insert(lo, x)

    def set_merit_order(self):
        """iterate through powerplants, estimate the cost for generating power for each powerplants and sort
        powerplants in the cost order."""

        powerplants_sorted = []

        for pp in self.powerplants:
            if pp["type"] == "windturbine":
                pp["pmax"] = int(pp["pmax"] * self.fuels["wind(%)"] / 100)
                pp.update({"cost": 0})
                self.insort(powerplants_sorted, pp)

            elif pp["type"] == "turbojet":
                pp.update({"cost": pp["efficiency"] * (self.fuels["kerosine(euro/MWh)"] +
                                                       self.fuels["co2(euro/ton)"] * self.emissions)})
                self.insort(powerplants_sorted, pp)

            elif pp["type"] == "gasfired":
                pp.update({"cost": pp["efficiency"] * (self.fuels["gas(euro/MWh)"] +
                                                       self.fuels["co2(euro/ton)"] * self.emissions)})
                self.insort(powerplants_sorted, pp)

            else:
                raise TypeError(f"unknown powerplant type: {pp['type']}. Should be: windturbine, turbojet or gasfired")

        self.powerplants = powerplants_sorted

    def find_power_plan(self):
        """The algorithm which take the powerplant in the merit order and set the"""
        prod = 0

        for i, pp in enumerate(self.powerplants):

            # if load already supplied, we set the production of the current powerplant to 0
            if prod == self.load:
                pp.update({"p": 0})

            # if the current powerplant pmax is not enough to fill the load, it's production is set to pmax
            elif prod + pp["pmax"] < self.load:
                pp.update({"p": pp["pmax"]})
                prod += pp["p"]

            # if pmin of current powerplant is too high to fill the load
            elif prod + pp["pmin"] > self.load:
                previous_powerplant_power_offset = prod + pp["pmin"] - self.load

                # check if there is a previous powerplant in the stack
                if i > 0:

                    # check if we can subtract to previous powerplant the needed production for the current powerplant
                    # to fill the load
                    if self.powerplants[i - 1]["pmax"] - self.powerplants[i - 1]["pmin"] >= previous_powerplant_power_offset:
                        self.powerplants[i - 1]["p"] -= previous_powerplant_power_offset
                        pp.update({"p": pp["pmin"]})
                        prod += pp["p"] - previous_powerplant_power_offset

                    else:
                        raise AlgorithmError("this algorithm is not robust enough, it can't subtract the production of "
                                             "enough powerplant for the current one to be able to fill the load")

                else:
                    raise AlgorithmError("this algorithm can't fill the load if the load is "
                                         "lower than pmin of the first powerplant in the merit-order")

            # if the current powerplant max production is enough to fill the load, but pmin is higher, we set
            # the production to what we need to fill the load.
            elif prod + pp["pmax"] >= self.load >= prod + pp["pmin"]:
                pp.update({"p": self.load - prod})
                prod += pp["p"]

    def generate_response(self):
        """create a new list of dictionary for the request response.
        It is based on powerplants one with only the name and production."""
        self.response = [{"name": pp["name"], "p": pp["p"]} for pp in self.powerplants]

