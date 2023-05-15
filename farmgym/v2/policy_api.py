import yaml
import copy

class Policy_API:
    """
    Class used to define an expert policy. Expert policies can then be attached to a farm.
    """

    def __init__(self, triggered_observations, triggered_interventions):

        self.triggered_observations = triggered_observations
        self.triggered_interventions = triggered_interventions

        self.delayed_actions = []

    def reset(self):
        self.delayed_actions = []

    # def setup(self, farm):
    #    with open(self.policy_configuration, "r", encoding="utf8") as file:
    #        self.policy_parameters = yaml.safe_load(file)

    # def available_ations(self,farm):
    #     #TODO: Under construction, Output in gym format.
    #     self.available_actions =[]
    #     for fi_key in self.policy_parameters['actions']:
    #         fi= self.policy_parameters['actions'][fi_key]
    #         for e_key in fi:
    #             e = fi[e_key]
    #             for a_name in e:
    #                 a = e[a_name]
    #                 for i in it.product(*list(a[p] for p in a)):
    #                     print(i)
    #                     x={}
    #                     pj=0
    #                     for p in a:
    #                         x[p]=i[pj]
    #                         pj+=1
    #
    #                 # a: {p1: range1, p2:range2, etc}
    #
    #                     # if (type(range) == tuple):
    #                     #     m, M = range
    #                     #     Box(m, M, shape=(1,))
    #                     # else:
    #                     #     if (len(range) > 0):
    #                     #         Discrete(len(range))
    #                     #     pass
    #                 for fa_key in farm.farmers:
    #                     self.available_actions.append((fa_key, fi_key,e_key,a_name,x))

    def observation_schedule(self, observations):
        # observations: list of (farmer,field,entity,variable,path,value)
        # contains all free observations, hence current day as minimum info.
        action_schedule = []
        for trigger, actions in self.triggered_observations:
            # Trigger is CNF
            trigger_on = any([self.is_trigger_on(trigger, obs) for obs in observations]) or trigger == [[]]
            if trigger_on:
                [action_schedule.append(action) for action in actions]
        return action_schedule

    def intervention_schedule(self, observations):
        # observations: list of (farmer,field,entity,variable,path,value)
        # contains all free observations, hence current day as minimum info.
        action_schedule = []
        for trigger, actions in self.triggered_interventions:
            # Trigger is CNF
            trigger_on = any([self.is_trigger_on(trigger, obs) for obs in observations]) or trigger == [[]]
            if trigger_on:
                # [action_schedule.append(action) for action in actions]
                [self.delayed_actions.append(action) for action in actions]

        for action in self.delayed_actions:
            if action["delay"] == 0:
                action_schedule.append(action["action"])
                self.delayed_actions.remove(action)
            else:
                action["delay"] = action["delay"] - 1

        return action_schedule

    def is_trigger_on(self, trigger, var):
        farm, field, entity, variable, path, v = var
        for and_conditions in trigger:
            bool_cond = True
            for condition in and_conditions:
                variable_path, fun, operator, value = condition
                # field,entity,variable,path = variable_path
                # v = self.farm.fields[field].entities[entity].variables[variable]
                if variable_path == (field, entity, variable, path):
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
            if bool_cond:
                return True
        return False
    
    def __add__(self, other):
        combined_obs = self.triggered_observations + other.triggered_observations
        combined_interv = self.triggered_interventions + other.triggered_interventions

        combined = Policy_API(combined_obs, combined_interv)
        combined.reset = lambda: (
            self.reset(),
            other.reset()
        )
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
        combined.observation_schedule = lambda obs: [a for p in policies for a in p.observation_schedule(obs)]
        combined.intervention_schedule = lambda obs: [a for p in policies for a in p.intervention_schedule(obs)]

        return combined

from typing import NamedTuple

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

    #### ADD FREQUENCY 
    #### ADD VALUE FOR PARAMETERS SUCH AS ( )
    ### TENSORBOARD MONITORING; simplexps

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
        self.interventions = set()
        for field in farm.fields:
            for entity in farm.fields[field].entities.keys():
                self.entities.add((entity, farm.fields[field].entities[entity]))
        
        for action in farm.farmgym_intervention_actions:
            fa, fi, e, inter, params, gym_space, len_gym_space = action
            self.interventions.add(inter)

    # Single policies

    def create_plant_observe(self):
        """
        Define policy to observe the stage of Plant-0 in Field-0
        """
        observation_conditions = [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["ripe"])]]
        observation_actions = [("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)])]
        observe_plant_stage = (observation_conditions, observation_actions)
        policy_plant_observe = Policy_API([observe_plant_stage], [])
        policy_plant_observe = Policy("plant_observe",policy_plant_observe)
        return policy_plant_observe
    
    def create_harvest_ripe(self, delay=1):
        """
        Define policy to harvest Plant-0 if its stage is 'ripe'
        """
        harvest_conditions = [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["ripe"])]]
        harvest_actions = [{"action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}), "delay": delay}]
        harvest_ripe = (harvest_conditions, harvest_actions)
        policy_harvest_ripe = Policy_API([], [harvest_ripe])
        policy_harvest_ripe = Policy("harvest_ripe",policy_harvest_ripe, delay=delay)
        return policy_harvest_ripe
    
    def create_harvest_fruit(self, delay=18):
        """
        Define policy to harvest Plant-0 if its stage is 'fruit'
        """
        harvest_conditions = [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["fruit"])]]
        harvest_actions = [{"action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}), "delay": delay}]
        harvest_fruit = (harvest_conditions, harvest_actions)
        policy_harvest_fruit = Policy_API([], [harvest_fruit])
        policy_harvest_fruit = Policy("harvest_fruit",policy_harvest_fruit, delay=delay)
        return policy_harvest_fruit

    def create_observe_weeds(self):
        """
        Define policy to observe Weeds growth in Field-0
        """
        observation_conditions = []
        observation_actions = [("BasicFarmer-0", "Field-0", "Weeds-0", "grow#nb", [(0, 0)])]
        observe_weeds_growht = (observation_conditions, observation_actions)
        policy_observe_weeds = Policy_API(observe_weeds_growht, [])
        policy_observe_weeds = Policy("observe_weeds",policy_observe_weeds)
        return policy_observe_weeds
    
    def create_scatter_cide(self, delay=2, amount=5, frequency=5, threshold=2.0):
        """
        Define policy to scatter herbicide every few days if number of weeds is greater than a threshold
        Args : 
            - delay : days before taking the action
            - amount : herbicide amount in kg
            - frequency : frequency in days 
            - threshold : threshold for taking the action
        """
        scatter_conditions = [
        (("Field-0", 'Weeds-0', 'grow#nb', [(0, 0)]), lambda x: x, ">=", float(threshold)),
        (("Field-0", 'Weather-0', 'day#int365', []), lambda x: x%frequency, "==", 0)]
        scatter_actions = [{'action':('BasicFarmer-0', 'Field-0', 'Cide-0', 'scatter',
         {'plot': (0,0), 'amount#kg':amount}),'delay':delay}]
        scatter_cide = (scatter_conditions, scatter_actions)
        policy_scatter_cide = Policy_API([], scatter_cide)
        policy_scatter_cide = Policy("scatter_cide",policy_scatter_cide, delay=delay, amount=amount, frequency=frequency, threshold=threshold)
        return policy_scatter_cide

    def create_remove_weeds(self, delay=2, frequency=5, threshold=2.0):
        """
        Define policy to remove herbs every few days if number of weeds is greater than a threshold
        Args : 
            - frequency : frequency in days 
            - threshold : threshold for taking the action
        """
        remove_conditions = [
        (("Field-0", 'Weeds-0', 'grow#nb', [(0, 0)]), lambda x: x, ">=", float(threshold)),
        (("Field-0", 'Weather-0', 'day#int365', []), lambda x: x % frequency, "==", 0)]
        remove_actions = [{'action':('BasicFarmer-0', 'Field-0', 'Weeds-0', 'remove', {}),'delay':delay}]
        remove_weeds = (remove_conditions, remove_actions)
        policy_remove_weeds = Policy_API([], remove_weeds)
        policy_remove_weeds = Policy("remove_weeds",policy_remove_weeds, delay=delay, frequency=frequency, threshold=threshold)
        return policy_remove_weeds

    def create_water_soil(self, delay=0, amount=8):
        """
        Define policy to water Soil-0 
        """
        water_conditions = [[]]
        water_actions = [{"action": ("BasicFarmer-0", "Field-0", "Soil-0", "water_continuous", {"plot": (0, 0), "amount#L": amount, "duration#min": 60}), "delay": 0}]
        water_soil = (water_conditions, water_actions)
        policy_water_soil = Policy_API([], [water_soil])
        policy_water_soil = Policy("water_soil",policy_water_soil, delay=delay, amount=amount)
        return policy_water_soil

    def create_scatter_fert(self, delay=0, amount=5):
        """
        Define policy to scatter Fertilizer-0
        """
        scatter_conditions = []
        scatter_actions = {"action": ("BasicFarmer-0", "Field-0", "Fertilizer-0", "scatter", {"plot": (0, 0), "amount#kg": amount, "duration#min": 60}), "delay": 0}
        scatter_fert = (scatter_conditions, scatter_actions)
        policy_scatter_fert = Policy_API([], [scatter_fert])
        policy_scatter_fert = Policy("scatter_fert",policy_scatter_fert, delay=delay, amount=amount)
        return policy_scatter_fert

    def create_put_scarecrow(self, delay=0):
        """
        Define policy to put scarecrow 
        """
        scarecrow_conditions = []
        scarecrow_actions = {"action": ("BasicFarmer-0", "Field-0", "Facility-0", "put_scarecrow", {}), "delay": delay}
        put_scarecrow = (scarecrow_conditions, scarecrow_actions)
        policy_put_scarecrow = Policy_API([], [put_scarecrow])
        policy_put_scarecrow = Policy("put_scarecrow",policy_put_scarecrow, delay=delay)
        return policy_put_scarecrow

    # Entity policies

    def get_plant_policies(self):
        policies = []
        # Define policy to observe the stage of Plant-0 in Field-0
        policy_plant_observe = self.create_plant_observe()
        policies.append(policy_plant_observe)
        # Define policy to harvest Plant-0 if its stage is 'ripe'
        policy_harvest_ripe = self.create_harvest_ripe()
        if "harvest" in self.interventions:
            policies.append(policy_harvest_ripe)
        # Define policy to harvest Plant-0 if its stage is 'fruit'
        policy_harvest_fruit = self.create_harvest_fruit()
        if "harvest" in self.interventions:
            policies.append(policy_harvest_fruit)
        return policies

    def get_weeds_policies(self):
        policies = []
        # Define policy to observe Weeds growth in Field-0
        policy_observe_weeds = self.create_observe_weeds()
        policies.append(policy_observe_weeds)
        # Define policy to scatter herbicide every few days if number of weeds is greater than a threshold
        policy_scatter_cide = self.create_scatter_cide(amount=5)
        if "scatter" in self.interventions:
            policies.append(policy_scatter_cide)
        # Define policy to remove herbs every few days if number of weeds is greater than a threshold
        policy_remove_weeds = self.create_remove_weeds()
        if "remove" in self.interventions:
            policies.append(policy_remove_weeds)
        return policies

    def get_soil_policies(self):
        policies = []
        # Define policy to water Soil-0 
        policy_water_soil = self.create_water_soil(amount=8)
        policies.append(policy_water_soil)
        return policies
    
    def get_fertilizer_policies(self):
        policies = []
        # Define policy to scatter Fertilizer-0
        policy_scatter_fert = self.create_scatter_fert(amount=5)
        policies.append(policy_scatter_fert)
        return policies

    def get_facility_policies(self):
        policies = []
        # Define policy to put scarecrow 
        policy_put_scarecrow = self.create_put_scarecrow()
        policies.append(policy_put_scarecrow)
        return policies
    
    def get_policies(self):
        policies = []
        entities = [e[0] for e in self.entities]
        #print(entities)
        if "Plant-0" in entities:
            policies += self.get_plant_policies()
        if "Soil-0" in entities:
            policies += self.get_soil_policies()
        if "Weeds-0" in entities:
            policies += self.get_weeds_policies()
        if "Fertilizer-0" in entities:
            policies += self.get_facility_policies()
        if "Facility-0" in entities:
            policies += self.get_facility_policies()
        return policies


if __name__ == "__main__":
    from farmgym.v2.games.make_farm import make_farm
    farm = make_farm("games/farms_1x1/farm_lille_clay_bean.yaml")
    
    helper = Policy_helper(farm)
    policies = helper.get_policies()
    print(policies)    
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


    ## COMBINING EXAMPLE
    import numpy as np
    def run_policy_xp(farm, policy, max_steps=np.infty):
        if farm.monitor != None:
            farm.monitor = None
        cumreward = 0.0
        cumcost = 0.0
        policy.reset()
        observation = farm.reset()
        terminated = False
        i = 0
        while (not terminated) and i <= max_steps:
            observations = farm.get_free_observations()
            observation_schedule = policy.observation_schedule(observations)
            observation, _, _,_, info = farm.farmgym_step(observation_schedule)
            obs_cost = info["observation cost"]
            intervention_schedule = policy.intervention_schedule(observation)
            obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
            int_cost = info["intervention cost"]
            cumreward += reward
            cumcost += obs_cost + int_cost
        return cumreward, cumcost

    combined = Policy_API.combine_policies([policies[0].api, policies[1].api, policies[2].api, policies[3].api])
    # OR
    combined = policies[0].api + policies[1].api + policies[2].api + policies[3].api
    
    run_policy_xp(farm, copy.deepcopy(combined), max_steps=150)