import ast
import copy
import random
from typing import NamedTuple


class Policy_API:
    """
    Class used to define an expert policy. Expert policies can then be attached to a farm.
    """

    def __init__(self, triggered_observations, triggered_interventions):
        self.triggered_observations = triggered_observations
        self.triggered_interventions = triggered_interventions
        # TODO: Perhaps use discretized_farmgymaction_to_gymaction to be able to output gymactions (integers)  and not just farmgymactions?

        self.delayed_actions = []

    def reset(self):
        self.delayed_actions = []

    def observation_schedule(self, observations):
        # observations: list of (farmer,field,entity,variable,path,value)
        # contains all free observations, hence current day as minimum info.
        action_schedule = []
        for trigger, actions in self.triggered_observations:
            # Trigger is CNF
            trigger_on = self.is_trigger_on(trigger, observations)
            if trigger_on:
                [action_schedule.append(copy.copy(action)) for action in actions]
        return action_schedule

    def intervention_schedule(self, observations):
        """
        "And" condtions  [(),()]
        "or" conditions  [()],[()]
        """
        # observations: list of (farmer,field,entity,variable,path,value)
        # contains all free observations, hence current day as minimum info.
        action_schedule = []
        for trigger, actions in self.triggered_interventions:
            # Trigger is CNF
            trigger_on = self.is_trigger_on(trigger, observations)
            if trigger_on:
                # [action_schedule.append(action) for action in actions]
                [self.delayed_actions.append(copy.copy(action)) for action in actions]

        for action in reversed(self.delayed_actions):
            if action["delay"] == 0:
                action_schedule.append(action["action"])
                self.delayed_actions.remove(action)
            else:
                action["delay"] = action["delay"] - 1

        return action_schedule

    def is_trigger_on(self, trigger, observations):
        ## Check Breaks
        if trigger == [[]]:
            return True
        for and_conditions in trigger:
            bool_cond = True
            observation_exists = False
            for condition in and_conditions:
                for ob in observations:
                    farm, field, entity, variable, path, v = ob
                    variable_path, fun, operator, value = condition
                    if variable_path == (field, entity, variable, path):
                        observation_exists = True
                        if operator == "==":
                            bool_cond = bool_cond and fun(v) == value
                        elif operator == "!=":
                            bool_cond = bool_cond and fun(v) != value
                        elif operator == "<=":
                            bool_cond = bool_cond and fun(v) <= value
                        elif operator == ">=":
                            bool_cond = bool_cond and fun(v) >= value
                        elif operator == "<":
                            bool_cond = bool_cond and fun(v) < value
                        elif operator == ">":
                            bool_cond = bool_cond and fun(v) > value
                        elif operator == "in":
                            bool_cond = bool_cond and fun(v) in value
                        elif operator == "ni":
                            bool_cond = bool_cond and value in fun(v)
                        elif operator == "not in":
                            bool_cond = bool_cond and fun(v) not in value
                        elif operator == "not ni":
                            bool_cond = bool_cond and value not in fun(v)
                        else:
                            bool_cond = False
            if bool_cond and observation_exists:
                return True
        return False

    def __add__(self, other):
        combined_obs = self.triggered_observations + other.triggered_observations
        combined_interv = self.triggered_interventions + other.triggered_interventions

        combined = Policy_API(combined_obs, combined_interv)
        combined.reset = lambda: (self.reset(), other.reset())
        combined.observation_schedule = lambda obs: (
            self.observation_schedule(obs) + other.observation_schedule(obs)
        )
        combined.intervention_schedule = lambda obs: (
            self.intervention_schedule(obs) + other.intervention_schedule(obs)
        )

        return combined

    @classmethod
    def combine_policies(cls, policies):
        combined_obs = []
        combined_interv = []
        for policy in policies:
            combined_obs.extend(policy.triggered_observations)
            combined_interv.extend(policy.triggered_interventions)

        combined = cls(combined_obs, combined_interv)
        combined.reset = lambda: [p.reset() for p in policies]
        combined.observation_schedule = lambda obs: [
            a for p in policies for a in p.observation_schedule(obs)
        ]
        combined.intervention_schedule = lambda obs: [
            a for p in policies for a in p.intervention_schedule(obs)
        ]

        return combined


class Policy(NamedTuple):
    name: str
    api: Policy_API
    delay: int = 0
    amount: int = None
    frequency: int = None
    threshold: float = None

    def __repr__(self):
        return self.name

    def infos(self):
        name = f"Name = {self.name}"
        delay = f"Delay = {self.delay}"
        amount = f"Amount = {self.amount}"
        frequency = f"Frequency = {self.frequency}"
        threshold = f"Threshold = {self.threshold}"
        infos = ", ".join([name, delay, amount, frequency, threshold])
        return infos


class Policy_helper:
    """
    A class that generates a set of policies for the different entities in a farm.

    Attributes:
        farm (Farm): A Farm object representing the farm environment.
        entities (set): A set containing all the entities present in the farm.
        interventions (set): A set containing all the interventions available in the farm.

    Methods:
        Entity policies :
            get_plant_policies(): Generates all possible single policies for the plants in the farm.
            get_weeds_policies(): Generates all possible single policies for the weeds in the farm.
            get_soil_policies(): Generates all possible single policies for the soil in the farm.
            get_fertilizer_policies(): Generates all possible single policies for the fertilizer in the farm.
            get_facility_policies(): Generates all possible single policies for the facilities in the farm.
            get_policies(): Generates all possible single policies for all the different entities in the farm.
        Single policies :
            Plant:
                create_plant_observe()
                create_harvest_ripe(delay)
                create_harvest_fruit(delay)
            Weeds:
                create_observe_weeds()
                create_scatter_cide(delay, amount, frequency, threshold)
                create_remove_weeds(delay, frequency, threshold)
            Soil:
                create_water_soil(delay, amount)
            Fertilizer:
                create_scatter_fert(delay, amount)
            Facility:
                create_put_scarecrow()
    """

    def __init__(self, farm):
        self.farm = farm
        self.entities = set()
        self.interventions = {}
        for field in farm.fields:
            for entity in farm.fields[field].entities.keys():
                self.entities.add((entity, farm.fields[field].entities[entity]))
        self.entities = [e[0] for e in self.entities]

        for action in farm.farmgym_intervention_actions:
            fa, fi, e, inter, params, gym_space, len_gym_space = action
            self.interventions[(e, inter)] = params
        ## TODO check if value from create policy is permitted in farm actions

    # Single policies

    def create_policyfromaction(self, action, frequency, delay):
        policy_condition = [
            [
                (
                    ("Field-0", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                )
            ]
        ]
        policy_action = [{"action": action, "delay": delay}]
        policy = Policy_API(policy_condition, policy_action)
        return policy

    def create_plant_observe(self, field=0, index=0, location=(0, 0)):
        """
        Define policy to observe the stage of Plant-0 in Field-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        observation_conditions = [[]]
        observation_actions = [
            ("BasicFarmer-0", f"Field-{fi}", f"Plant-{idx}", "stage", [loc])
        ]
        observe_plant_stage = (observation_conditions, observation_actions)
        policy_plant_observe = Policy_API([observe_plant_stage], [])
        policy_plant_observe = Policy("plant_observe", policy_plant_observe)
        return policy_plant_observe

    def create_weed_observe(self, field=0, index=0, location=(0, 0)):
        """
        Define policy to observe the number of Weeds-0 in Field-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        observation_conditions = [[]]
        observation_actions = [
            ("BasicFarmer-0", f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc])
        ]
        observe_weed_nb = (observation_conditions, observation_actions)
        policy_weed_observe = Policy_API([observe_weed_nb], [])
        policy_weed_observe = Policy("plant_observe", policy_weed_observe)
        return policy_weed_observe

    def create_harvest_ripe(
        self, field=0, index=0, location=(0, 0), delay=1, frequency=1
    ):
        """
        Define policy to harvest Plant-0 if its stage is 'ripe'
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        harvest_conditions = [
            [
                (
                    (f"Field-{fi}", f"Plant-{idx}", "stage", [loc]),
                    lambda x: x,
                    "in",
                    ["ripe"],
                ),
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        harvest_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Plant-{idx}",
                    "harvest",
                    {},
                ),
                "delay": delay,
            }
        ]
        harvest_ripe = (harvest_conditions, harvest_actions)
        policy_harvest_ripe = Policy_API([], [harvest_ripe])
        policy_harvest_ripe = Policy("harvest_ripe", policy_harvest_ripe, delay=delay)
        return policy_harvest_ripe

    def create_harvest_fruit(
        self, field=0, index=0, location=(0, 0), delay=18, frequency=1
    ):
        """
        Define policy to harvest Plant-0 if its stage is 'fruit'
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        harvest_conditions = [
            [
                (
                    (f"Field-{fi}", f"Plant-{idx}", "stage", [loc]),
                    lambda x: x,
                    "in",
                    ["fruit"],
                ),
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        harvest_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Plant-{idx}",
                    "harvest",
                    {},
                ),
                "delay": delay,
            }
        ]
        harvest_fruit = (harvest_conditions, harvest_actions)
        policy_harvest_fruit = Policy_API([], [harvest_fruit])
        policy_harvest_fruit = Policy(
            "harvest_fruit", policy_harvest_fruit, delay=delay
        )
        return policy_harvest_fruit

    def create_observe_weeds(self, field=0, index=0, location=(0, 0)):
        """
        Define policy to observe Weeds growth in Field-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        observation_conditions = [[]]
        observation_actions = [
            ("BasicFarmer-0", f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc])
        ]
        observe_weeds_growth = (observation_conditions, observation_actions)
        policy_observe_weeds = Policy_API([observe_weeds_growth], [])
        policy_observe_weeds = Policy("observe_weeds", policy_observe_weeds)
        return policy_observe_weeds

    def create_scatter_cide(
        self,
        field=0,
        index=0,
        location=(0, 0),
        delay=2,
        amount=5,
        frequency=5,
        threshold=2.0,
        day=-1,
        bag=False,
    ):
        """
        Define policy to scatter herbicide every few days if number of weeds is greater
        than a threshold
        Args :
            - delay : days before taking the action
            - amount : herbicide amount in bags
            - frequency : frequency in days
            - threshold : threshold for taking the action
        """
        ## TODO : weather, cide can be different than 0 ?
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        # Check if amount is specified in rules :
        # TODO : renable this
        # possible_amounts = self.interventions["scatter_bag"].get("amount#bag", [1])
        # if amount not in possible_amounts:
        #     amount = possible_amounts[-1]
        #     print(f"Specified amount not defined in farm rules, setting default amount ({amount})")
        fi, idx, loc = field, index, location
        scatter_conditions = [
            [
                (
                    (f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc]),
                    lambda x: x,
                    ">=",
                    float(threshold),
                ),
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        if day >= 0:
            scatter_conditions[0].append(
                ((f"Field-{fi}", "Weather-0", "day#int365", []), lambda x: x, "==", day)
            )
        if bag:
            scatter_actions = [
                {
                    "action": (
                        "BasicFarmer-0",
                        f"Field-{fi}",
                        "Cide-0",
                        "scatter_bag",
                        {"plot": loc, "amount#bag": amount},
                    ),
                    "delay": delay,
                }
            ]
        else:
            scatter_actions = [
                {
                    "action": (
                        "BasicFarmer-0",
                        f"Field-{fi}",
                        "Cide-0",
                        "scatter",
                        {"plot": loc, "amount#kg": amount},
                    ),
                    "delay": delay,
                }
            ]

        scatter_cide = (scatter_conditions, scatter_actions)
        policy_scatter_cide = Policy_API([], [scatter_cide])
        policy_scatter_cide = Policy(
            "scatter_cide",
            policy_scatter_cide,
            delay=delay,
            amount=amount,
            frequency=frequency,
            threshold=threshold,
        )
        return policy_scatter_cide

    def create_remove_weeds(
        self, field=0, index=0, location=(0, 0), delay=2, frequency=5, threshold=2.0
    ):
        """
        Define policy to remove herbs every few days if number of weeds is greater than a threshold
        Args :
            - frequency : frequency in days
            - threshold : threshold for taking the action
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        remove_conditions = [
            [
                (
                    (f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc]),
                    lambda x: x,
                    ">=",
                    float(threshold),
                ),
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]

        remove_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Weeds-{idx}",
                    "remove",
                    {"plot": loc},
                ),
                "delay": delay,
            }
        ]
        remove_weeds = (remove_conditions, remove_actions)
        policy_remove_weeds = Policy_API([], [remove_weeds])
        policy_remove_weeds = Policy(
            "remove_weeds",
            policy_remove_weeds,
            delay=delay,
            frequency=frequency,
            threshold=threshold,
        )
        return policy_remove_weeds

    def create_water_soil(
        self, field=0, index=0, location=(0, 0), delay=0, amount=5, frequency=1, day=-1
    ):
        """
        Define policy to water Soil-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        # Check if amount is specified in rules :
        possible_amounts = self.interventions[(f"Soil-{idx}", "water_discrete")].get(
            "amount#L", [1]
        )
        if amount not in possible_amounts:
            amount = possible_amounts[-1]
            print(
                f"Specified amount not defined in farm rules, setting default amount ({amount})"
            )
        water_conditions = [
            [
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                )
            ]
        ]
        if day >= 0:
            water_conditions = [
                [
                    (
                        (f"Field-{fi}", "Weather-0", "day#int365", []),
                        lambda x: x,
                        "==",
                        day,
                    )
                ]
            ]

        water_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Soil-{idx}",
                    "water_discrete",
                    {"plot": loc, "amount#L": amount, "duration#min": 60},
                ),
                "delay": delay,
            }
        ]
        water_soil = (water_conditions, water_actions)
        policy_water_soil = Policy_API([], [water_soil])
        policy_water_soil = Policy(
            "water_soil", policy_water_soil, delay=delay, amount=amount
        )
        return policy_water_soil

    def create_water_soil_continious(
        self,
        field=0,
        index=0,
        location=(0, 0),
        delay=0,
        amount=5.0,
        frequency=1,
        day=-1,
    ):
        """
        Define policy to water Soil-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        # Check if amount is specified in ru.les :
        possible_range = self.interventions[(f"Soil-{idx}", "water_continuous")].get(
            "amount#L", [1]
        )
        possible_range = ast.literal_eval(possible_range)
        min_amount, max_amount = possible_range[0], possible_range[1]
        if not min_amount <= amount <= max_amount:
            amount = max_amount
            print(
                f"Specified amount not defined in farm rules, setting default amount ({max_amount})"
            )

        water_conditions = [
            [
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        if day >= 0:
            water_conditions = [
                [
                    (
                        (f"Field-{fi}", "Weather-0", "day#int365", []),
                        lambda x: x,
                        "==",
                        day,
                    )
                ]
            ]

        water_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Soil-{idx}",
                    "water_continuous",
                    {"plot": loc, "amount#L": amount, "duration#min": 60},
                ),
                "delay": delay,
            }
        ]
        water_soil = (water_conditions, water_actions)
        policy_water_soil = Policy_API([], [water_soil])
        policy_water_soil = Policy(
            "water_soil", policy_water_soil, delay=delay, amount=amount
        )
        return policy_water_soil

    def create_scatter_fert(
        self,
        field=0,
        index=0,
        location=(0, 0),
        delay=0,
        amount=5,
        frequency=1,
        day=-1,
        bag=True,
    ):
        """
        Define policy to scatter Fertilizer-0
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx, loc = field, index, location
        # Check if amount is specified in rules :
        possible_amounts = self.interventions[(f"Fertilizer-{idx}", "scatter_bag")].get(
            "amount#bag", [1]
        )
        if amount not in possible_amounts:
            amount = possible_amounts[-1]
            print(
                f"Specified amount not defined in farm rules, setting default amount ({amount})"
            )
        scatter_conditions = [
            [
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        if day >= 0:
            scatter_conditions = [
                [
                    (
                        (
                            (f"Field-{fi}", "Weather-0", "day#int365", []),
                            lambda x: x,
                            "==",
                            day,
                        )
                    )
                ]
            ]
        if bag:
            scatter_actions = [
                {
                    "action": (
                        "BasicFarmer-0",
                        f"Field-{fi}",
                        f"Fertilizer-{idx}",
                        "scatter_bag",
                        {"plot": loc, "amount#bag": amount},
                    ),
                    "delay": delay,
                }
            ]
        else:
            scatter_actions = [
                {
                    "action": (
                        "BasicFarmer-0",
                        f"Field-{fi}",
                        f"Fertilizer-{idx}",
                        "scatter",
                        {"plot": loc, "amount#kg": amount},
                    ),
                    "delay": delay,
                }
            ]
        scatter_fert = (scatter_conditions, scatter_actions)
        policy_scatter_fert = Policy_API([], [scatter_fert])
        policy_scatter_fert = Policy(
            "scatter_fert", policy_scatter_fert, delay=delay, amount=amount
        )
        return policy_scatter_fert

    def create_put_scarecrow(
        self, field=0, index=0, location=(0, 0), frequency=1, delay=0
    ):
        """
        Define policy to put scarecrow
        """
        assert isinstance(field, int) and isinstance(
            index, int
        ), "Field, index must be integers."
        assert isinstance(location, tuple), "Location must be a tuple, i.e : (0, 0)."
        fi, idx = field, index
        scarecrow_conditions = [
            [
                (
                    (f"Field-{fi}", "Weather-0", "day#int365", []),
                    lambda x: x % frequency,
                    "==",
                    0,
                ),
            ]
        ]
        scarecrow_actions = [
            {
                "action": (
                    "BasicFarmer-0",
                    f"Field-{fi}",
                    f"Facility-{idx}",
                    "put_scarecrow",
                    {},
                ),
                "delay": delay,
            }
        ]
        put_scarecrow = (scarecrow_conditions, scarecrow_actions)
        policy_put_scarecrow = Policy_API([], [put_scarecrow])
        policy_put_scarecrow = Policy(
            "put_scarecrow", policy_put_scarecrow, delay=delay
        )
        return policy_put_scarecrow

    # Entity policies
    def get_plant_policies(self, frequency=1, amount=None, delay=1):
        policies = []
        # Define policy to observe the stage of Plant-0 in Field-0
        policy_plant_observe = self.create_plant_observe()
        policies.append(policy_plant_observe)
        # Define policy to harvest Plant-0 if its stage is 'ripe'
        if ("Plant-0", "harvest") in self.interventions.keys():
            policy_harvest_ripe = self.create_harvest_ripe(
                frequency=frequency, delay=delay
            )
            policies.append(policy_harvest_ripe)
        # Define policy to harvest Plant-0 if its stage is 'fruit'
        if ("Plant-0", "harvest") in self.interventions.keys():
            policy_harvest_fruit = self.create_harvest_fruit(
                frequency=frequency, delay=delay
            )
            policies.append(policy_harvest_fruit)
        return policies

    def get_weeds_policies(self, frequency=1, amount=1, delay=1):
        policies = []
        # Define policy to observe Weeds growth in Field-0
        if "Weeds-0" in self.entities:
            policy_observe_weeds = self.create_observe_weeds()
            policies.append(policy_observe_weeds)
        # Define policy to scatter herbicide every few days if number of weeds is greater than a threshold
        if ("Cide-0", "scatter_bag") in self.interventions.keys():
            policy_scatter_cide = self.create_scatter_cide(
                amount=amount, frequency=frequency, delay=delay, bag=True
            )
            policies.append(policy_scatter_cide)
        if ("Cide-0", "scatter") in self.interventions.keys():
            policy_scatter_cide = self.create_scatter_cide(
                amount=amount, frequency=frequency, delay=delay, bag=False
            )
            policies.append(policy_scatter_cide)
        # Define policy to remove herbs every few days if number of weeds is greater than a threshold
        if ("Weeds-0", "remove") in self.interventions.keys():
            policy_remove_weeds = self.create_remove_weeds(
                frequency=frequency, delay=delay
            )
            policies.append(policy_remove_weeds)
        return policies

    def get_weeds_params(self):
        if ("Cide-0", "scatter") in self.interventions.keys():
            return self.interventions[("Cide-0", "scatter")]["amount#kg"]
        if ("Cide-0", "scatter_bag") in self.interventions.keys():
            return self.interventions[("Cide-0", "scatter_bag")]["amount#bag"]

    def get_soil_policies(self, frequency=1, amount=5.0, delay=1):
        policies = []
        # Define policy to water Soil-0
        if ("Soil-0", "water_discrete") in self.interventions.keys():
            policy_water_soil = self.create_water_soil(
                amount=amount, frequency=frequency, delay=delay
            )
            policies.append(policy_water_soil)
        if ("Soil-0", "water_continuous") in self.interventions.keys():
            policy_water_soil = self.create_water_soil_continious(
                amount=amount, frequency=frequency, delay=delay
            )
            policies.append(policy_water_soil)
        return policies

    def get_soil_params(self):
        return self.interventions[("Soil-0", "water_discrete")]["amount#L"]

    def get_fertilizer_policies(self, frequency=1, amount=1, delay=1):
        policies = []
        # Define policy to scatter Fertilizer-0*
        if (
            "Fertilizer-0",
            "scatter_bag",
        ) in self.interventions.keys() and "Fertilizer-0" in self.entities:
            policy_scatter_fert = self.create_scatter_fert(
                amount=amount, frequency=frequency, delay=delay, bag=True
            )
            policies.append(policy_scatter_fert)
        if (
            "Fertilizer-0",
            "scatter",
        ) in self.interventions.keys() and "Fertilizer-0" in self.entities:
            policy_scatter_fert = self.create_scatter_fert(
                amount=amount, frequency=frequency, delay=delay, bag=False
            )
            policies.append(policy_scatter_fert)
        return policies

    def get_fertilizer_params(self):
        if ("Fertilizer-0", "scatter_bag") in self.interventions.keys():
            return self.interventions[("Fertilizer-0", "scatter_bag")]["amount#bag"]
        if ("Fertilizer-0", "scatter") in self.interventions.keys():
            return self.interventions[("Fertilizer-0", "scatter")]["amount#kg"]

    def get_facility_policies(self, frequency=1):
        policies = []
        # Define policy to put scarecrow
        policy_put_scarecrow = self.create_put_scarecrow(frequency=frequency)
        policies.append(policy_put_scarecrow)
        return policies

    def get_policies(self, frequency=1):
        """
        Possible frequencies = {1,3,5,10}
        Possible delay = {1,3,5,10}
        Possible params = {., ., ., .}
        """
        policies = []
        entities = self.entities
        if "Plant-0" in entities:
            policies += self.get_plant_policies(frequency=frequency)
        if "Soil-0" in entities:
            # params = self.get_soil_params()
            policies += self.get_soil_policies(frequency=frequency)
        if "Weeds-0" in entities:
            # params = self.get_weeds_params()
            policies += self.get_weeds_policies(frequency=frequency)
        if "Fertilizer-0" in entities:
            policies += self.get_fertilizer_policies(frequency=frequency)
        if "Facility-0" in entities:
            policies += self.get_facility_policies(frequency=frequency)
        return policies

    def get_random_policies(self, n):
        """
        Possible frequencies = {1,3,5,10}
        Possible delay = {1,3,5,10}
        Possible params = {., ., ., .}
        """
        freqs = [1, 3, 5, 7]
        delays = [0, 2, 5, 10]

        soil_params = self.get_soil_params()
        weeds_params = self.get_weeds_params()
        fertilizer_params = self.get_fertilizer_params()

        policies = []
        # n policies
        for i in range(n):
            name = ""
            # Soil
            param = random.choice(soil_params)
            freq = random.choice(freqs)
            delay = random.choice(delays)
            soil_policies = self.get_soil_policies(freq, param, delay)
            name += f"f{freq}a{int(param)}d{delay}_"
            # Weeds
            param = random.choice(weeds_params)
            freq = random.choice(freqs)
            delay = random.choice(delays)
            weeds_policies = self.get_weeds_policies(freq, param, delay)
            name += f"f{freq}a{param}d{delay}_"
            # Fertilizer
            param = random.choice(fertilizer_params)
            freq = random.choice(freqs)
            delay = random.choice(delays)
            fertilizer_policies = self.get_fertilizer_policies(freq, param, delay)
            name += f"f{freq}a{param}d{delay}_"
            # Plant
            freq = random.choice(freqs)
            delay = random.choice(delays)
            plant_policies = self.get_plant_policies(freq, None, delay)
            name += f"f{freq}a0d{delay}"

            apis = soil_policies + weeds_policies + fertilizer_policies + plant_policies
            apis = [i.api for i in apis]
            combined = Policy_API.combine_policies(apis)
            policies.append((name, combined))

        return policies


def run_policy_xp(farm, policy, max_steps=10000, show_actions=False):
    #    if farm.monitor is not None:
    #        farm.monitor = None
    cumreward = 0.0
    cumcost = 0.0
    policy.reset()
    observation = farm.reset()
    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:
        i += 1
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]
        intervention_schedule = policy.intervention_schedule(observation)
        if show_actions:
            print(f"Day = {i}, Actions : {intervention_schedule}")
        obs, reward, terminated, truncated, info = farm.farmgym_step(
            intervention_schedule
        )
        int_cost = info["intervention cost"]
        cumreward += reward
        cumcost += obs_cost + int_cost
    return cumreward, cumcost


if __name__ == "__main__":
    from farmgym.v2.make_farm import make_farm

    farm = make_farm("games/farms_1x1/farm_lille_clay_bean.yaml")

    # Policy helper example
    helper = Policy_helper(farm)
    print(helper.entities)

    policies = helper.get_policies()
    print(f"All policies : {policies}")
    plant_policies = helper.get_plant_policies()
    weeds_policies = helper.get_weeds_policies()
    soil_policies = helper.get_soil_policies()
    fertilizer_policies = helper.get_fertilizer_policies()
    facility_policies = helper.get_facility_policies()
    print(f"plant_policies = {plant_policies}")
    print(f"weeds_policies = {weeds_policies}")
    print(f"soil_policies = {soil_policies}")
    print(f"fertilizer_policies = {fertilizer_policies}")
    print(f"facility_policies = {facility_policies}")
    print(f"{facility_policies[0]}.api : {facility_policies[0].api}")
    print(f"{facility_policies[0]}.infos() : {facility_policies[0].infos()}")
    water_soil = helper.create_water_soil(amount=8, delay=0)

    # Combining policies example

    # It is possible to combine policy_apis with the combine method
    combined = Policy_API.combine_policies(
        [policies[0].api, policies[1].api, policies[2].api, policies[3].api]
    )
    # or using addition operator
    combined = policies[0].api + policies[1].api + policies[2].api + policies[3].api

    run_policy_xp(farm, copy.deepcopy(combined), max_steps=150)
