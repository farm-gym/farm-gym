import gym
from gym.spaces import Discrete, Box, Dict, Tuple
from gym.utils import seeding
from farmgym.v2.gymUnion import Union, MultiUnion, Sequence
import numpy as np
from farmgym.v2.rendering.monitoring import Monitor


from gym.spaces.utils import flatdim, flatten_space, flatten

######################################
import inspect
from textwrap import indent


import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent

## Here is the reason why you should use dictionaries instead of lists as much as possible: https://towardsdatascience.com/faster-lookups-in-python-1d7503e9cd38


def yml_tuple_constructor(v, f=float):
    w = v[1:-1]
    tup = tuple(map(lambda x: f(x), w.split(",")))
    return tup


from farmgym.v2.specifications.specification_manager import (
    build_inityaml,
    build_scoreyaml,
    build_actionsyaml,
)


class Farm(gym.Env):
    """
    Instantiates a Farm environment.
    Constructed from one or several fields (:class:`~farmgym.v2.field.Field`), farmers (:class:`~farmgym.v2.farmer_api.Farmer_API`), a score (:class:`~farmgym.v2.scoring_api.Scoring_API`) and  a set of rules (:class:`~farmgym.v2.rules_api.Rules_API`). The farm can then be constructed through ``farm=Farm(fields,farmers,scoring,rules)``.

    Parameters
    ----------
    fields : a list of fields, that is instances of the class :class:`~farmgym.v2.field.Field`
        Field used to define the farm.

    farmers: a list of farmers, that is instances of a class implementing the :class:`~farmgym.v2.farmer_api.Farmer_API`
        Farmers used to define the farm.

    scoring: an instance of the :class:`~farmgym.v2.scoring_api.Scoring_API`
        Scoring function used to generate the reward of the farm.

    rules: an instance of the   :class:`~farmgym.v2.rules_api.Rules_API`
        Rules used to define the farm (i.e. allowed actions, how to filter actions...)

    policies: a list of policies, that is instances of a class implementing the :class:`~farmgym.v2.policy_api.Policy_API`
        Expert policies defined in the farm

    seed: an integer,
        seed used by the random-number generator.

    Notes
    -----
    At creation, automatically generates yaml configuration files to help customize the farm. One file to specify the list of allowed actions, one file to initialize state variables, and one file to specify the score.


    """

    def __init__(self, fields, farmers, scoring, rules,  policies=None, interaction_mode="AOMDP",seed=None):
        self.interaction_mode = interaction_mode
        # Name fields uniquely:
        cpt = {}
        for f in fields:
            if f.__class__.__name__ in cpt.keys():
                cpt[f.__class__.__name__] += 1
                f.name = f.__class__.__name__ + "-" + str(cpt[f.__class__.__name__])
            else:
                cpt[f.__class__.__name__] = 0
                f.name = f.__class__.__name__ + "-0"

        self.fields = {}
        for f in fields:
            self.fields[f.name] = f

        # Name farmers uniquely:
        cpt = {}
        for f in farmers:
            if f.__class__.__name__ in cpt.keys():
                cpt[f.__class__.__name__] += 1
                f.name = f.__class__.__name__ + "-" + str(cpt[f.__class__.__name__])
            else:
                cpt[f.__class__.__name__] = 0
                f.name = f.__class__.__name__ + "-0"

        self.farmers = {}
        for f in farmers:
            self.farmers[f.name] = f

        # Assign all fields to all farmers
        for f in farmers:
            [f.assign_field(fi) for fi in fields]

        self.scoring = scoring
        self.rules = rules

        self.last_farmgym_action = None

        farm_call = " ".join(inspect.stack()[1].code_context[0].split("=")[0].split())
        filep = "/".join(inspect.stack()[1].filename.split("/")[0:-1])
        if self.scoring.score_configuration == None:
            print(f"[Farmgym Warning] Missing score configuration file.")
            build_scoreyaml(filep + "/" + farm_call + "_score.yaml", self)
            self.scoring.score_configuration = filep + "/" + farm_call + "_score.yaml"
            print(
                f"[Solution]"
                + " Vanilla score configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_score.yaml")
                + " and used instead. Please, open and modify as wanted."
            )
        else:
            try:
                open(self.scoring.score_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print(f"[Farmgym Warning] Missing score configuration file.")
                build_scoreyaml(self.scoring.score_configuration, self)
                print(
                    f"[Solution]"
                    + " Vanilla score configuration file automatically generated in "
                    + str(self.scoring.score_configuration)
                    + " and used instead. Please, open and modify as wanted."
                )

        if self.rules.init_configuration == None:
            print(f"[Farmgym Warning] Missing initial conditions configuration file.")
            build_inityaml(
                filep + "/" + farm_call + "_init.yaml",
                self,
                mode="default",
                init_values=self.rules.initial_conditions_values,
            )
            self.rules.init_configuration = filep + "/" + farm_call + "_init.yaml"
            print(
                f"[Solution]"
                + " Vanilla initial conditions configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_init.yaml")
                + " and used instead. Please, open and modify as wanted. Deleting a line corresponding to a state variable makes it initialized at default value."
            )
        else:
            try:
                open(self.rules.init_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print(f"[Farmgym Warning] Missing initial conditions configuration file.")
                build_inityaml(
                    self.rules.init_configuration,
                    self,
                    mode="default",
                    init_values=self.rules.initial_conditions_values,
                )
                # print('INIT VALUE', self.rules.initial_conditions_values)
                print(
                    f"[Solution]"
                    + "  Vanilla initial conditions configuration file automatically generated in "
                    + str(self.rules.init_configuration)
                    + " and used instead. Please, open and modify as wanted. Deleting a line corresponding to a state variable makes it initialized at default value."
                )

        if self.rules.actions_configuration == None:
            print(f"[Farmgym Warning] Missing actions configuration file.")
            build_actionsyaml(filep + "/" + farm_call + "_actions.yaml", self)
            self.rules.actions_configuration = filep + "/" + farm_call + "_actions.yaml"
            print(
                f"[Solution]"
                + " Vanilla action configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_actions.yaml")
                + " and used instead. Please, open and remove any line corresponding to an unwanted action."
            )
        else:
            try:
                open(self.rules.actions_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print(f"[Farmgym Warning] Missing actions configuration file.")
                build_actionsyaml(self.rules.actions_configuration, self)
                print(
                    f"[Solution]"
                    + " Vanilla action configuration file automatically generated in "
                    + str(self.rules.actions_configuration)
                    + " and used instead. Please, open and remove any line corresponding to an unwanted action."
                )

        self.scoring.setup(self)
        self.rules.setup(self)
        self.policies = policies

        try:
            self.discretization_nbins = self.rules.actions_allowed["params"]["number_of_bins_to_discretize_continuous_actions"]
        except:
            self.discretization_nbins = 11

        self.farmgym_observation_actions = self.build_farmgym_observation_actions(self.rules.actions_allowed["observations"])
        self.farmgym_intervention_actions = self.build_farmgym_intervention_actions(self.rules.actions_allowed["interventions"])
        self.farmgym_state_space = self.build_gym_state_space()

        # GYM SPACES:
        self.observation_space = self.build_gym_observation_space()
        # self.action_space = self.build_gym_action_space()
        self.action_space = self.build_gym_discretized_action_space()

        self.name = self.build_name()
        self.shortname = self.build_shortname()

        for fi in self.rules.initial_conditions:
            for e in self.rules.initial_conditions[fi]:
                self.fields[fi].entities[e].initial_conditions = self.rules.initial_conditions[fi][e]

        self.is_new_day = True
        self.seed(seed)
        for fi in self.fields:
            for e in self.fields[fi].entities:
                self.fields[fi].entities[e].set_random(self.np_random)

        self.monitor = None

    def build_name(self):
        """
        Builds a standardized name for the farm as a string. example: Farm_Fields[Field-0[Weather-0_Soil-0_Plant-0]]_Farmers[BasicFarmer-0]
        """
        str = "Farm_Fields["
        for fi in self.fields:
            str += fi + "["
            for e in self.fields[fi].entities:
                str += self.fields[fi].entities[e].fullname + "_"
            str = str[:-1]
            str += "]"
        str += "]_Farmers["
        for fa in self.farmers:
            str += fa + "_"
        str = str[:-1]
        str += "]"
        return str

    def build_shortname(self):
        """
        Builds a standardized name for the farm as a string. example: Farm_Fields[Field-0[Weather-0_Soil-0_Plant-0]]_Farmers[BasicFarmer-0]
        """
        short = "farm_"
        for fi in self.fields:
            short += str(self.fields[fi].shape["length#nb"]) + "x" + str(self.fields[fi].shape["width#nb"]) + "("
            for e in self.fields[fi].entities:
                short += self.fields[fi].entities[e].shortname + "_"
            short = short[:-1]
            short += ")"
        return short

    # QUESTION:  Do we add shared entities outside fields ?? (but need to be updated only once /day ). Or do let an entity in a field to be used by a farmer in other field (e.g. water tank).

    def add_monitoring(self, list_of_variables):
        """
        Adds a Monitor to the farm, allowing to observe evolution of some state variables with time.
        list_of_variables: the list of variables to be monitored.
        The format for one variable is (field,entity,variable,function,name,option).
        For instance:
        ("Field-0","Plant-0","fruits_per_plant#nb",lambda x: sum_value(x),"Fruits (nb)","range_auto")
        """
        self.monitor = Monitor(self, list_of_variables)

    def reset(self, seed=None, options=None):
        """
        Resets the environment.
        """
        super().reset(seed=seed, options=options)
        return self.gym_reset(seed, options)

    def gym_reset(self, seed=None, options=None):
        """
        Resets the environment.
        """

        self.last_farmgym_action = None
        farmgym_observations, farmgym_information = self.farmgym_reset(seed, options)

        observations = []
        observation_information = []
        for fo in farmgym_observations:
            fa_key, fi_key, e_key, variable_key, path, value = fo
            gym_value = self.fields[fi_key].entities[e_key].gym_observe_variable(variable_key, path)
            observations.append(gym_value)
            observation_information.append(fo)
        information = farmgym_information
        information["farmgym observations"] = observation_information

        return observations, information

    def farmgym_reset(self, seed=None, options=None):
        """
        Resets the environment.
        """

        self.last_farmgym_action = None
        self.np_random, seed = seeding.np_random(seed)

        self.is_new_day = True

        for f in self.fields.values():
            f.reset()

        observations = []
        # Add free observations if any
        obs_vec = self.rules.get_free_observations(self)
        [observations.append(o) for o in obs_vec]

        # observations, _, _, info = self.farmgym_step([])
        # _, _, _, _ = self.farmgym_step([])

        info = {"intervention cost": 0}
        return observations, info

    def seed(self, seed=None):
        """
        Modifies the seed of the random generators used in the environment.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_free_observations(self):
        """
        Outputs free observations available at the current time.
        """
        return self.rules.get_free_observations(self)

    def step(self, action):
        """
        Performs a step evolution of the system, from current stage to next state given the input action.
        """
        if (self.interaction_mode == "POMDP"):
            return self.gym_step_POMDP(action)
        else: # Assumes it is AOMDP
            return self.gym_step_AOMDP(action)

    # def double_step(self, policy):
    #    info = {}
    #    free_observations = self.get_free_observations()
    #    observation_schedule = policy.observation_schedule(free_observations)
    #    observations, _, _, info1 = self.farmgym_step(observation_schedule)
    #    info["observation cost"] = info1["observation cost"]
    #    intervention_schedule = policy.intervention_schedule(observations)
    #    obs, reward, is_done, info2 = self.farmgym_step(intervention_schedule)
    #    info["intervention cost"] = info2["intervention cost"]
    #    return observations+observations+obs,reward,is_done,info

    def gym_step_POMDP(self, action):
        #info = {}
        observations, _, _, _ = self.farmgym_step([])
        obs, reward, is_done, info = self.farmgym_step(self.gymaction_to_discretized_farmgymaction(action))
        #info["intervention cost"] = info2["intervention cost"]
        # free_observations = self.get_free_observations()
        return self.farmgym_to_gym_observations(observations + obs), reward, is_done, info


    def farmgym_to_gym_observations(self, farmgym_observations):
        gym_observations = []
        for fo in farmgym_observations:
            fa_key, fi_key, e_key, variable_key, path, value = fo
            gym_value = self.fields[fi_key].entities[e_key].gym_observe_variable(variable_key, path)
            g = {}
            g[fa_key] ={}
            g[fa_key][fi_key]={}
            g[fa_key][fi_key][e_key]={}
            g[fa_key][fi_key][e_key][variable_key]={}
            if path != []:
                g[fa_key][fi_key][e_key][variable_key][str(path)]=gym_value
            else:
                g[fa_key][fi_key][e_key][variable_key]=gym_value
            # gym_observations[str(fa_key)+"."+str(fi_key)+"."+str(e_key)+"."+str(variable_key)+"."+str(path)]=gym_value
            gym_observations.append(g)
        return gym_observations

    def gym_step_AOMDP(self, gym_action):
        """
        Performs a step evolution of the system, from current stage to next state given the input action.
        It follows the gym signature, and outputs observations, reward, is_done, information.
        Farmgym observations are added in information["farmgym observations"].
        """
        farmgym_observations, reward, is_done, farmgym_information = self.farmgym_step(
            # self.gymaction_to_farmgymaction(gym_action)
            self.gymaction_to_discretized_farmgymaction(gym_action)
        )

        observations = self.farmgym_to_gym_observations(farmgym_observations)
        information = farmgym_information
        information["farmgym observations"] = farmgym_observations

        return observations, reward, is_done, information

    def farmgym_step(self, action_schedule):
        """
        Performs a step evolution of the system, from current stage to next state given the input action.
        A farm gym step alternates between observation step and action step before moving to next day.
        """
        self.last_farmgym_action = action_schedule
        filtered_action_schedule = self.rules.filter_actions(self, action_schedule, self.is_new_day)
        self.rules.assert_actions(filtered_action_schedule)
        if self.is_new_day:
            output = self.observation_step(filtered_action_schedule)
            self.is_new_day = False
            return output
        else:
            output = self.intervention_step(filtered_action_schedule)
            self.is_new_day = True
            return output

    def observation_step(self, observation_schedule):
        """
        Performs an observation step, one of the two types of farmgym steps.
        """
        observations = []

        # Add free observations if any
        obs_vec = self.rules.get_free_observations(self)
        [observations.append(o) for o in obs_vec]

        # Perform action
        observation_schedule_cost = 0
        # self.rules.assert_actions(action_schedule)
        for observation_item in observation_schedule:
            fa_key, fi_key, entity, variable_key, path = observation_item
            # assert(action_type=='observe')
            # We can change this to policies using:
            # fa_key,fi_key,pos,action = policy_item.action(observations)
            cost = self.scoring.observation_cost(
                self.farmers[fa_key],
                self.fields[fi_key],
                fi_key,
                entity,
                variable_key,
                path,
            )
            # cost = 0
            obs_vec = self.farmers[fa_key].perform_observation(fi_key, entity, variable_key, path)
            [observations.append(o) for o in obs_vec]

        return observations, 0, False, {"observation cost": observation_schedule_cost}
        # return (observation, reward, terminated, truncated, info) or  (observation, reward, done, info)

    def intervention_step(self, action_schedule):
        """
        Performs an intervention step, one of the two types of farmgym steps.
        """
        observations = []

        # Perform action
        intervention_schedule_cost = 0
        for intervention_item in action_schedule:
            fa_key, fi_key, entity_key, action_name, params = intervention_item
            # We can change this to policies using:
            # fa_key,fi_key,pos,action = policy_item.action(observations)
            cost = self.scoring.intervention_cost(fa_key, fi_key, entity_key, action_name, params)
            obs_vec = self.farmers[fa_key].perform_action(fi_key, entity_key, action_name, params)
            [observations.append(o) for o in obs_vec]
            intervention_schedule_cost += cost

        # Update dynamics
        for f in self.fields.values():
            f.update_to_next_day()
        for fa in self.farmers:
            self.farmers[fa].update_to_next_day()

        # Compute reward
        reward = 0
        for f in self.fields:
            entities_list = self.fields[f].entities.values()
            reward += self.scoring.reward(entities_list)

        # Check if terminal
        is_done = self.rules.is_terminal(self.fields)

        if self.monitor != None:
            self.monitor.update_fig()
            if is_done:
                self.monitor.stop()

        # Compute final reward
        if is_done:

            for f in self.fields.values():
                reward += self.scoring.final_reward(f.entities.values())
            if self.monitor != None:
                self.monitor.stop()

        return (
            observations,
            reward,
            is_done,
            {"intervention cost": intervention_schedule_cost},
        )

    def gymaction_to_farmgymaction(self, actions):
        # TODO: Check it on all cases.
        """
        Converts actions given in gym format to actions in farmgym format.
        By construction, this only generates actions in the subset of available actions specified by the configuration file.
        """

        def convert(value, ranges):
            if ranges == None:
                return {}
            if type(ranges) == list:
                if type(ranges[value]) == str and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif type(ranges) == str and "(" in ranges:  # Range of continuous values
                # print("?",value, ranges)
                return (float)(value)
            elif type(ranges) == dict:
                c_v = {}
                for k in ranges:
                    c_v[k] = convert(value[k], ranges[k])
                return c_v

        ll = len(self.farmgym_observation_actions)
        fg_actions = []
        for action in actions:
            index, act = action
            # print("I,A",index,act,len(self.farmgym_observation_actions))
            # if index == 0:
            #    fg_actions.append(self.farmgym_observation_actions[act])
            if index < ll:
                if act == 0:
                    fg_actions.append(self.farmgym_observation_actions[index])
            else:
                fa, fi, e, a, f_a, g, ng = self.farmgym_intervention_actions[index - ll]
                # fa, fi, e, a, f_a, g, ng = self.farmgym_intervention_actions[index - 1]
                farmgym_act = convert(act, f_a)
                # TODO: proper mapping from OrderedDict to Dict when dict parameters, + case of None parameter.
                fg_actions.append((fa, fi, e, a, farmgym_act))
        return fg_actions

    def gymaction_to_discretized_farmgymaction(self, actions):
        def convert(value, ranges):
            if ranges == None:
                return {}
            if type(ranges) == list:
                if type(ranges[value]) == str and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif type(ranges) == str and "(" in ranges:  # Range of continuous values
                # r = ranges.split(",")
                # m=float(r[0][1:])
                # M=float(r[1][:-1])
                # print("?",value, ranges,m,M)
                return (float)(value)
            elif type(ranges) == dict:
                c_v = {}
                for k in ranges:
                    c_v[k] = convert(value[k], ranges[k])
                return c_v

        fg_actions = []
        for action in actions:
            if action < len(self.farmgym_observation_actions):
                fg_actions.append(self.farmgym_observation_actions[action])
            else:
                theindex = action - len(self.farmgym_observation_actions)
                theaction = None
                # print("A",action)
                for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions:
                    if ng > theindex:
                        theaction = (fa, fi, e, a, f_a, g, ng)
                        break
                    else:
                        theindex -= ng
                # print("B",theaction,theindex)

                fa, fi, e, a, f_a, g, ng = theaction

                # print("B1",g,type(g), theindex, ng)

                if type(g) == Discrete:
                    act = theindex
                elif type(g) == Box:
                    m = g.low
                    M = g.high
                    factor = ng // self.discretization_nbins
                    # factor = nbins
                    j = i // factor
                    i = i - j * factor
                    act = m + j / (self.discretization_nbins + 1) * (M - m)

                elif type(g) == Dict:
                    i = theindex
                    factor = ng
                    act = {}
                    for key in g:
                        if type(g[key]) == Discrete:
                            factor = factor // g[key].n
                            # factor = g[key].n
                            j = i // factor
                            i = i - j * factor
                            act[key] = j
                            # print(g[key], i,j, act[key],factor)
                        elif type(g[key]) == Box:
                            # print("B2", g[key], g[key].shape, i, ng)
                            # print(g[key].low, g[key].high)
                            m = g[key].low
                            M = g[key].high
                            factor = factor // self.discretization_nbins
                            # factor = nbins
                            j = i // factor
                            i = i - j * factor
                            act[key] = m + j / (self.discretization_nbins + 1) * (M - m)
                            # print(g[key], i,j, act[key],factor)
                    # print("C",act,i,f_a)
                farmgym_act = convert(act, f_a)
                fg_actions.append((fa, fi, e, a, farmgym_act))
        return fg_actions

    def random_allowed_intervention(self):
        """
        Outputs a randomly generated intervention, as allowed by the yaml file, in farmgym format.
        """
        n = self.np_random.integers(len(self.farmgym_intervention_actions))
        # intervention = self.np_random.choice(list(self.farmgym_intervention_actions))
        fa, fi, e, inter, params, gym_space, len_gym_space = self.farmgym_intervention_actions[n]
        o = gym_space.sample()

        def convert(value, ranges):
            if type(ranges) == list:
                if type(ranges[value]) == str and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif type(ranges) == str and "(" in ranges:  # Range of continuous values
                # print("?",value, ranges)
                return (float)(value)
            elif type(ranges) == dict:
                c_v = {}
                for k in ranges:
                    c_v[k] = convert(value[k], ranges[k])
                return c_v

        farmgym_act = {}
        if type(params) == dict:
            # print("DICT:",f_a,act)
            farmgym_act = {}
            for k in params:
                farmgym_act[k] = convert(o[k], params[k])

        return (fa, fi, e, inter, farmgym_act)

    # def random_intervention(self):
    #     #TODO: Should we restrict to specified inverventions from config file?
    #     fa = self.np_random.choice(list(self.farmers.keys()))
    #     fi = self.np_random.choice(list(self.farmers[fa].fields.keys()))
    #     e = self.np_random.choice(list(self.fields[fi].entities.keys()))
    #
    #     actions =        self.fields[fi].entities[e].actions
    #     while(len(actions)==0):
    #         fa = self.np_random.choice(list(self.farmers.keys()))
    #         fi = self.np_random.choice(list(self.farmers[fa].fields.keys()))
    #         e = self.np_random.choice(list(self.fields[fi].entities.keys()))
    #         actions = self.fields[fi].entities[e].actions
    #     key = self.np_random.choice(list(actions.keys()))
    #     params = actions[key]
    #     #print("CHOICE",fa,fi,e,key,params)
    #     p = {}
    #     for param in params:
    #         if (param == 'plot'):
    #             X = self.fields[fi].X
    #             Y = self.fields[fi].Y
    #             x = self.np_random.randint(0, X)
    #             y = self.np_random.randint(0, Y)
    #             p[param]= (x,y)
    #         else:
    #             range = params[param]
    #             if (isinstance(range, tuple)):
    #                 m, M = range
    #                 p[param] = m + self.np_random.random() * (M - m)
    #             else:
    #                 p[param] = self.np_random.choice(list(range))
    #
    #     return fa, fi, e, key, p

    def random_allowed_observation(self):
        """
        Outputs a randomly generated observation-action (action to collect observation), as allowed by the yaml file, in farmgym format.
        """
        if (len(self.farmgym_observation_actions)>0):
            n = self.np_random.integers(len(self.farmgym_observation_actions))
            return self.farmgym_observation_actions[n]
        return None
    # def random_observation(self):
    #     #TODO: Should we restrict to specified observations from config file?
    #     fa = self.np_random.choice(list(self.farmers.keys()))
    #     fi = self.np_random.choice(list(self.farmers[fa].fields.keys()))
    #     e = self.np_random.choice(list(self.fields[fi].entities.keys()))
    #     vars = self.fields[fi].entities[e].variables
    #     #print("VARS:", vars)
    #     #print("KEYS:", list(vars.keys()))
    #     key= self.np_random.choice(list(vars.keys()))
    #     v = vars[key]
    #     path = []
    #     done = False
    #     while (not done):
    #         if ( type(v) not in { np.ndarray, dict} or  (self.np_random.rand() > 0.5) ):
    #           done = True
    #         else:
    #             if (type(v) == np.ndarray):
    #                 shape = np.shape(v)
    #                 xx= self.np_random.randint(0, shape)
    #                 path.append(tuple(xx))
    #                 done = True
    #             elif (type(v) == dict):
    #                 k = self.np_random.choice(list(v.keys()))
    #                 v = v[k]
    #                 path.append(k)
    #
    #     return fa,fi,e, key, path

    def build_farmgym_intervention_actions(self, action_yaml):
        """
        Generates a list of all possible farmgym intervention-actions allowed by the configuration file action_yaml.
        """

        def make(action):
            #            print("ACTION",action, type(action))
            if type(action) == str:
                tuple = yml_tuple_constructor(action)
                m, M = tuple
                return Box(low=m, high=M, shape=())
            elif type(action) == list:
                ## Need to handle tuples differently.
                # print("KEYY",dictio[key])
                return Discrete(len(action))
            elif action == None:
                return Discrete(1)
            elif type(action) == dict:
                actions = {}
                for key in action:
                    actions[key] = make(action[key])
                return Dict(actions)

        def len_discretized_gym_space(gym_space, nbins=10):
            nactiong = 0
            if type(gym_space) == Dict:
                # print(g)
                nactiong = 1
                for key in gym_space:
                    space = gym_space[key]
                    if isinstance(space, Discrete):
                        nactiong *= space.n
                    elif isinstance(space, Box):
                        nactiong *= nbins ** np.prod(space.shape)
            elif type(gym_space) == Discrete:
                nactiong = gym_space.n
            elif type(gym_space) == Box:  # Assumes it is always dimension 1.
                nactiong = nbins  # ** np.prod(gym_space.shape)
            return int(nactiong)

        actions = []
        for fa in self.farmers:
            if fa in action_yaml.keys():
                for fi in self.fields:
                    if  fi in action_yaml[fa].keys():
                        for e in self.fields[fi].entities:
                            if e in action_yaml[fa][fi].keys():
                                if action_yaml[fa][fi][e] != None:
                                    for action in action_yaml[fa][fi][e]:
                                        gym_a = make(action_yaml[fa][fi][e][action])
                                        # print(gym_a)
                                        actions.append(
                                            (
                                                fa,
                                                fi,
                                                e,
                                                action,
                                                action_yaml[fa][fi][e][action],
                                                gym_a,
                                                len_discretized_gym_space(gym_a, nbins=self.discretization_nbins),
                                            )
                                        )
        return actions

    def build_farmgym_observation_actions(self, action_yaml):
        """
        Generates a list of all possible farmgym observation-actions allowed by the configuration file action_yaml.
        """

        def make(dictio, variables):
            if type(dictio) == list:
                actions = {}
                for key in dictio:
                    if key == "*":
                        actions["*"] = ["'"]
                    elif type(key) == str and "(" in key:
                        id = yml_tuple_constructor(key, int)
                        actions[id] = [id]
                    #    print("KEY2-")
                    #    actions[key]=['\'']
                    else:
                        actions[key] = [key]
                return actions
            elif dictio == None:
                return ["'"]
            elif type(dictio) == dict:
                actions = {}
                for key in dictio:
                    if key == "*":
                        actions["*"] = ["'"]
                    # elif (key=='\'*\''):
                    #    print("KEY2")
                    #    actions[key]=['\'']
                    else:
                        # print("DICTIO", dictio, "key", key, "VAR", variables)
                        p = make(dictio[key], variables[key])
                        actions[key] = p
                return actions

        def unpile(var, paths, prefix):
            actions = []
            if type(paths) == dict:
                for key in paths:
                    if key == "*":
                        acts = unpile(var, paths[key], prefix)
                        [actions.append(o) for o in acts]
                    else:
                        acts = unpile(var, paths[key], prefix + [key])
                        [actions.append(o) for o in acts]
            else:
                actions.append((var[0], var[1], var[2], var[3], prefix))
            return actions

        actions = []
        for fa in self.farmers:
            if fa in action_yaml.keys():
                for fi in self.fields:
                    if  fi in action_yaml[fa].keys():
                        for e in self.fields[fi].entities:
                            if e in action_yaml[fa][fi].keys():
                                if action_yaml[fa][fi][e] != None:
                                    for var in self.fields[fi].entities[e].variables:
                                        if var in action_yaml[fa][fi][e].keys():
                                            paths = make(
                                                action_yaml[fa][fi][e][var],
                                                self.fields[fi].entities[e].variables[var],
                                            )
                                            acts = unpile((fa, fi, e, var), paths, [])
                                            [actions.append(o) for o in acts]

        free_actions = []
        if "Free" in action_yaml.keys():
           for fi in self.fields:
               if  fi in action_yaml["Free"].keys():
                   for e in self.fields[fi].entities:
                       if e in action_yaml["Free"][fi].keys():
                           if action_yaml["Free"][fi][e] != None:
                               for var in self.fields[fi].entities[e].variables:
                                   if var in action_yaml["Free"][fi][e].keys():
                                       paths = make(
                                           action_yaml["Free"][fi][e][var],
                                           self.fields[fi].entities[e].variables[var],
                                       )
                                       acts = unpile(("Free", fi, e, var), paths, [])
                                       [free_actions.append(o) for o in acts]
        self.rules.free_observations = free_actions

        if (self.interaction_mode == "AOMDP"):
            return actions
        return []

    def build_gym_state_space(self):
        """
        Outputs a state space in gym Tuple format built from all state variables.
        """
        ## TODO: flatten? https://github.com/openai/gym/issues/1830

        def to_gym(range):
            if type(range) == tuple:
                m, M = range
                return Box(m, M, (), float)
            else:
                return Discrete(len(range))

        def make_s(x, indent=""):
            if type(x) == dict:
                state = {}
                for k in x:
                    state[k] = make_s(x[k], indent=indent + "  ")
                return Dict(state)
            elif type(x) == np.ndarray:
                it = np.nditer(x, flags=["multi_index", "refs_ok"])
                # s+= str(len(it))+","+str(x.shape) +","+str(len(x.shape))+","+str(len(x))
                if len(x.shape) > 1:
                    state = []
                    state.append(to_gym(x[it.multi_index].range))
                    it.iternext()
                    while not it.finished:
                        state.append(to_gym(x[it.multi_index].range))
                        is_not_finished = it.iternext()
                    return Tuple(state)
                else:
                    state = []
                    for i in range(len(x)):
                        state.append(to_gym(x[i].range))
                    return Tuple(state)
            else:
                return to_gym(x.range)

        state_space = []
        state_space_ = {}
        for fi in self.fields:
            state_space_[fi] = {}
            for e in self.fields[fi].entities:
                state_space_[fi][e] = {}
                for v in self.fields[fi].entities[e].variables:
                    s = make_s(self.fields[fi].entities[e].variables[v])
                    # if type(s) == Union:
                    #    [state_space.append(ss) for ss in s.spaces]
                    # else:
                    state_space.append(s)
                    state_space_[fi][e][v] = self.fields[fi].entities[e].variables[v]

        # print("STATE_SPACE", state_space_)
        return Dict(make_s(state_space_))  # Tuple(state_space)

    def build_gym_observation_space(self):
        """
        Outputs an observation space in gym MultiUnion format from all possible observations.
        """

        # TODO: flatten https://github.com/openai/gym/issues/1830?
        # Number all discrete actions, then discretize continuous ones with param N (nb of elements for each dim). number mutiactions etc.

        def make_space(x):
            if type(x) == dict:
                xspace = {}
                for k in x.keys():
                    xspace[k] = make_space(x[k])
                return Dict(xspace)
            elif type(x) == np.ndarray:
                xspace = []
                for xx in x:
                    xspace.append(make_space(xx))
                return Tuple(xspace)
            else:
                return x.to_gym_space()

        observation_space = []
        # observation_space2 = {}
        # obs_space = {}

        for fo in self.rules.free_observations:
            fa_key, fi_key, e_key, variable_key, path = fo
            var = self.fields[fi_key].entities[e_key].variables[variable_key]
            x = var
            # print("VAR",var)
            # print("PATH",path)
            for p in path:
                x = x[p]
            # print("x",x)
            # observation_space.append(make_space(x))

            o_space = {}
            o_space[fa_key] = {}
            o_space[fa_key][fi_key] = {}
            o_space[fa_key][fi_key][e_key] = {}
            o_space[fa_key][fi_key][e_key][variable_key] = {}
            if path != []:
                o_space[fa_key][fi_key][e_key][variable_key][str(path)] = x
            else:
                o_space[fa_key][fi_key][e_key][variable_key] = x
            observation_space.append(make_space(o_space))

            # if fa_key not in obs_space:
            #    obs_space[fa_key] = {}
            # if fi_key not in obs_space[fa_key]:
            #    obs_space[fa_key][fi_key] = {}
            # if e_key not in obs_space[fa_key][fi_key]:
            #    obs_space[fa_key][fi_key][e_key] = {}
            # if variable_key not in obs_space[fa_key][fi_key][e_key]:
            #    obs_space[fa_key][fi_key][e_key][variable_key] = {}
            # if str(path) not in obs_space[fa_key][fi_key][e_key][variable_key]:
            #    obs_space[fa_key][fi_key][e_key][variable_key][str(path)] = x

            # observation_space2[str(fa_key) + "." + str(fi_key) + "." + str(e_key) + "." + str(variable_key) + "." + str(
            #    path)] = make_space(x)

        for oa in self.farmgym_observation_actions:
            fa_key, fi_key, e_key, variable_key, path = oa
            var = self.fields[fi_key].entities[e_key].variables[variable_key]
            x = var
            for p in path:
                x = x[p]

            # observation_space.append(make_space(x))

            o_space = {}
            o_space[fa_key] = {}
            o_space[fa_key][fi_key] = {}
            o_space[fa_key][fi_key][e_key] = {}
            o_space[fa_key][fi_key][e_key][variable_key] = {}
            if path != []:
                o_space[fa_key][fi_key][e_key][variable_key][str(path)] = x
            else:
                o_space[fa_key][fi_key][e_key][variable_key] = x
            observation_space.append(make_space(o_space))

            # if fa_key not in obs_space:
            #    obs_space[fa_key] = {}
            # if fi_key not in obs_space[fa_key]:
            #    obs_space[fa_key][fi_key] = {}
            # if e_key not in obs_space[fa_key][fi_key]:
            #    obs_space[fa_key][fi_key][e_key] = {}
            # if variable_key not in obs_space[fa_key][fi_key][e_key]:
            #    obs_space[fa_key][fi_key][e_key][variable_key] = {}
            # if str(path) not in obs_space[fa_key][fi_key][e_key][variable_key]:
            #    obs_space[fa_key][fi_key][e_key][variable_key][str(path)] = x
            # observation_space2[str(fa_key) + "." + str(fi_key) + "." + str(e_key) + "." + str(variable_key) + "." + str(
            #    path)] = make_space(x)

        # TODO: Make everything a dictionary?
        # return make_space(obs_space)
        return MultiUnion(observation_space)

    def build_gym_action_space(self):
        return MultiUnion(
            [Discrete(1) for x in range(len(self.farmgym_observation_actions))]
            + [g for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions],
            maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"],
        )

        # return MultiUnion(
        #    [Discrete(len(self.farmgym_observation_actions))]
        #    + [g for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions],
        #    maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"],
        # )

    def build_gym_discretized_action_space(self):
        """Whenever encounters a continuous box, split each dimension into nbins bins"""
        naction = len(self.farmgym_observation_actions)
        for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions:
            naction += ng
        # print("BUILD DISCRETIZED A", naction)
        return Sequence(Discrete(naction), maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"])
        # return MultiUnion([Discrete(naction)],maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"])

    def actions_to_string(self):
        nb_actions = self.action_space.space.n
        nb_observations = len(self.farmgym_observation_actions)

        def variable_to_string(var):
            sva = var.split("#")
            ssva = sva[0].split("_")
            tva = ""
            for s in ssva:
                tva += s[0].upper() + s[1:] + " "
            if len(sva) > 1:
                tva += "(" + sva[1] + ")"
            else:
                tva = tva[:-1]
            return tva

        a = self.gymaction_to_discretized_farmgymaction([])
        s = "-] Do nothing (empty).\n"
        if (self.interaction_mode=="AOMDP"):
            s += "Observation-actions:\n"
            for i in range(nb_observations):
                a = self.gymaction_to_discretized_farmgymaction([i])
                fa, fi, e, a, p = a[0]
                sp = " with parameters " + str(p) if p != [] else ""
                s += (
                    str(i)
                    + "] Farmer "
                    + str(fa)
                    + " observes"
                    + " variable '"
                    + variable_to_string(str(a))
                    + "'"
                    + sp
                    + " on "
                    + str(e)
                    + " in "
                    + str(fi)
                    + ".\n"
                )

            s += "Intervention-actions:\n"
        for i in range(nb_observations, nb_actions):
            a = self.gymaction_to_discretized_farmgymaction([i])
            fa, fi, e, a, p = a[0]
            sp = " with parameters " + str(p) if p != {} else ""
            s += (
                str(i)
                + "] Farmer "
                + str(fa)
                + " performs"
                + " intervention "
                + str(a)
                + sp
                + " on "
                + str(e)
                + " in "
                + str(fi)
                + ".\n"
            )

        return s

    def render(self, mode="human"):
        """
        Renders the farm at current time for human display as an image. The image is stored as a png file. Not everything is displayed, depending on display availability of each entity of the farm.
        The method considerably slows down the code execution hence should only be called for visualization purpose.
        """

        if mode == "human":

            max_display_actions = self.rules.actions_allowed["params"]["max_action_schedule_size"]

            from PIL import Image, ImageDraw, ImageFont

            sprite_width, sprite_height = 64, 64
            scale_factor = 2
            im_width, im_height = sprite_width * scale_factor, sprite_height * scale_factor
            XX = np.sum([self.fields[fi].X + 1 for fi in self.fields])
            YY = np.max(
                [
                    self.fields[fi].Y
                    + (int)(
                        np.ceil(
                            len(
                                [
                                    1
                                    for e in self.fields[fi].entities
                                    if self.fields[fi].entities[e].to_thumbnailimage() != None
                                ]
                            )
                            / self.fields[fi].X
                        )
                    )
                    for fi in self.fields
                ]
            )
            font_size = im_width * XX // (6 * len(self.fields))

            offsetx = im_width // 2
            offset_header = font_size * 2
            offset_sep = font_size // 2
            offset_foot = font_size * 2

            font = ImageFont.truetype(str(CURRENT_DIR) + "/rendering/Gidole-Regular.ttf", size=font_size)
            font_action = ImageFont.truetype(
                str(CURRENT_DIR) + "/rendering/Gidole-Regular.ttf",
                size=im_width * XX // (18 * len(self.fields)),
            )

            left, top, right, bottom = font_action.getbbox("A")
            car_height = np.abs(top - bottom) * 1.33  # font_action.getsize("A")[1]
            # print("FONT:",height,font_action.getsize("A")[1])
            offset_actions = (int)(car_height * max_display_actions + 5 * im_height // 100)

            dashboard_picture = Image.new(
                "RGBA",
                (
                    im_width * XX,
                    im_height * YY + offset_header + offset_sep + offset_foot + offset_actions,
                ),
                (255, 255, 255, 255),
            )
            d = ImageDraw.Draw(dashboard_picture)

            day = (int)(self.fields["Field-0"].entities["Weather-0"].variables["day#int365"].value)
            day_string = "Day {:03d}".format(day)

            d.text(
                (
                    dashboard_picture.width // 2 - len(day_string) * font_size // 4,
                    im_height * YY + offset_header + offset_sep + offset_foot // 4 + offset_actions,
                ),
                day_string,
                font=font,
                fill=(100, 100, 100),
                stroke_width=2,
                stroke_fill="black",
            )

            # offset_field=0
            for fi in self.fields:
                # day_string= 'Day {}'.format( (int) (self.fields[fi].entities['Weather-0'].variables['day#int365'].value))
                text = fi  # "F-"+fi[-1:]
                # print("FFF", font.size,font.getsize("a"),font.getsize(fi))
                left, top, right, bottom = font.getbbox(text)
                width_text = (int)(np.abs(right - left))
                # print("FI size", width_text, font_action.getsize(text))
                # d.text((offsetx+ (self.fields[fi].X+1)*im_width//2  -font.getsize(text)[0] // 2-im_width//2, offset_header//4), text, font=font, fill=(100, 100, 100), stroke_width=2,
                # stroke_fill="black")
                d.text(
                    (
                        offsetx + (self.fields[fi].X) * im_width // 2 - width_text // 2,
                        offset_header // 4,
                    ),
                    text,
                    font=font,
                    fill=(100, 100, 100),
                    stroke_width=2,
                    stroke_fill="black",
                )

                index = 0
                for e in self.fields[fi].entities:
                    image = self.fields[fi].entities[e].to_fieldimage()
                    image = image.resize((image.width * scale_factor, image.height * scale_factor))
                    # image = image.resize((im_width, im_height))
                    dashboard_picture.paste(image, (offsetx, offset_header), image)

                    j = index // self.fields[fi].X
                    i = index - j * self.fields[fi].X
                    image_t = self.fields[fi].entities[e].to_thumbnailimage()
                    if image_t != None:
                        image_t = image_t.resize((image_t.width * scale_factor, image_t.height * scale_factor))
                        dd = ImageDraw.Draw(image_t)
                        # dd.rectangle(((2,2),(im_width-2,im_height-2)), fill="#ff000000", outline="red")
                        xx = offsetx + i * im_width
                        yy = offset_header + self.fields[fi].Y * im_height + offset_sep + j * im_height
                        dashboard_picture.paste(image_t, (xx, yy), image_t)
                        # d.rectangle(((xx,yy),(xx+im_width,yy+im_height)), fill="#ffffff00", outline="red")
                        index += 1

                offset_field_y = (
                    offset_header
                    + self.fields[fi].Y * im_height
                    + offset_sep
                    + ((index - 1) // self.fields[fi].X + 1) * im_height
                )
                d.rectangle(
                    [
                        (offsetx, offset_field_y),
                        (
                            offsetx + self.fields[fi].X * im_width,
                            offset_field_y + offset_actions + im_width // 100,
                        ),
                    ],
                    fill=(255, 255, 255, 255),
                    outline=(0, 0, 0, 255),
                    width=im_width // 100,
                )

                nb_a = 0
                if self.last_farmgym_action:
                    for a in self.last_farmgym_action:
                        fa_key, fi_key, entity_key, action_name, params = a
                        if a[1] == fi and nb_a <= max_display_actions:
                            text = action_name
                            # print("DISPLAY ACTION",action_name, params)
                            if (type(params) == dict) and ("plot" in params.keys()):
                                text += " " + str(params["plot"])
                            xx_a = offsetx + im_width // 100
                            yy_a = offset_field_y + nb_a * car_height + im_width // 100
                            d.text(
                                (xx_a, yy_a),
                                text,
                                font=font_action,
                                fill=(100, 100, 100),
                                stroke_width=1,
                                stroke_fill="black",
                            )
                            nb_a += 1

                offsetx += (self.fields[fi].X + 1) * im_width

                # offset_field+=(self.fields[fi].X+1)*im_width

            dashboard_picture.save("farm-day-" + "{:03d}".format(day) + ".png")
            # plt.pause(0.01)

    def render_step(self, action, observation, reward, is_done, info):
        # Called after a step.
        s = "Farm:\t" + self.shortname + "\t"
        if self.is_new_day:  # Assumes it just switch from False to True
            s += "\tAfternoon phase (interventions)\n"
        else:
            s += "\tMorning phase (observations)\n"
        s += "Actions planned: " + str(action) + "\n"
        s += "Observations:\n"
        for o in observation:
            s += "\t- " + str(o) + "\n"
        s += "Reward: " + str(reward) + "\n"
        s += "Information:\n"
        for i in info:
            s += "\t- " + str(i) + "\n"
        if is_done:
            s += "Done.\n"
        return s

    def __str__(self):
        """
        Outputs a string showing a snapshot of the farm at the given time. All state variables of each entity, farmers information as well ws all free observations, available observations and available interventions.
        """
        s = "Farm: " + self.name + "\nShort name: " + self.shortname + "\n"
        s += "Fields:" + "\n"

        for f in self.fields:
            s += indent(str(self.fields[f]), "\t", lambda line: True) + "\n"

        s += "Farmers:" + "\n"
        for f in self.farmers:
            s += indent(str(self.farmers[f]), "\t", lambda line: True) + "\n"

        s += "Free farmgym observations:" + "\n"
        for o in self.rules.free_observations:
            s += "\t" + str(o) + "\n"

        if (self.interaction_mode == "AOMDP"):
            s += "Available farmgym observations:" + "\n"
            for o in self.farmgym_observation_actions:
                s += "\t" + str(o) + "\n"

        s += "Available farmgym interventions:" + "\n"
        for i in self.farmgym_intervention_actions:
            fa, fi, e, a, f_a, g, ng = i
            s += "\t" + str((fa, fi, e, a, f_a)) + "\n"

        s+= "Available gym actions: (as list [n1 n2 n3] where ni is one of the following)" + "\n"
        s+=self.actions_to_string()
        return s

    def understand_the_farm(self):
        farm=self
        print(farm)

        # PLAY WITH ENVIRONMENT:
        print("#############INTERVENTIONS###############")
        actions = farm.farmgym_intervention_actions
        for ac in actions:
            fa, fi, e, a, f_a, g, ng = ac
            print(ac, ":\t", (fa, fi, e, a, g.sample(), ng))
        print("#############OBSERVATIONS###############")
        actions = farm.farmgym_observation_actions
        for ac in actions:
            # fa,fi,e,a,g = ac
            print(ac)
        print("###########GYM SPACES#################")
        from farmgym.v2.gymUnion import str_pretty
        print("Gym states:\n", str_pretty(farm.farmgym_state_space))
        s = farm.farmgym_state_space.sample()
        print("Random state:", s)
        print("Gym observations:\n", farm.observation_space)
        o = farm.observation_space.sample()
        print("Random observation:", o)
        #print("?", farm.farmgym_state_space.contains(s), farm.observation_space.contains(o))

        print("############RANDOM ACTIONS################")
        print("Random intervention allowed by rules:\t", farm.random_allowed_intervention())
        print("Random observation allowed by rules:\t", farm.random_allowed_observation())
        print("############RANDOM GYM ACTIONS################")
        print("Gym (discretized) actions:", farm.action_space)
        # disc_space= farm.build_gym_discretized_action_space()
        # print("Gym discretized  actions:", disc_space)
        print("Do nothing gym action schedule:", "[]")
        print(" corresponding farmgym action schedule:", farm.gymaction_to_farmgymaction([]))
        for i in range(25):
            a = farm.action_space.sample()
            if len(a) > 0:
                print(
                    "Random gym action schedule:\t\t",
                    a,
                    "\n corresponding discretized farmgym action schedule:",
                    farm.gymaction_to_discretized_farmgymaction(a),
                )

        print("###############################")
        #print(farm.actions_to_string())



#
# def convertImage(imgRGB):
#     imgRGBA = imgRGB.convert("RGBA")
#     datas = imgRGBA.getdata()
#
#     newData = []
#     for item in datas:
#         if item[0] == 255 and item[1] == 255 and item[2] == 255:
#             newData.append((255, 255, 255, 0))
#         else:
#             newData.append(item)
#
#     imgRGBA.putdata(newData)
#     return imgRGB


import cv2


def generate_video(image_folder=".", video_name="farm.avi"):
    """
    Generates an avi video from a collection of png files generated when rendering a farm with farm.render()
    """
    # os.chdir("/home/ganesh/Desktop/video")
    images = [
        img
        for img in os.listdir(image_folder)
        if ("day-" in img) and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith("png"))
    ]

    fourcc = cv2.VideoWriter_fourcc(*"DIVX")

    maxX, maxY = 32 * 6, 32 * 6

    # Array images should only consider
    # the image files ignoring others if any

    frame = cv2.imread(os.path.join(image_folder, images[0]))

    # setting the frame width, height width
    # the width, height of first image
    y, x, layers = frame.shape

    width, height = (x, y)
    if x > maxX:
        x2 = maxX
        y2 = (int)((x2 / x) * y)
        width, height = (x2, y2)
        if y2 > maxY:
            y3 = maxY
            x3 = (int)((y3 / y2) * x2)
            width, height = (x3, y3)
    else:
        if y > maxY:
            y3 = maxY
            x3 = (int)((y3 / y) * x)
            width, height = (x3, y3)

    video = cv2.VideoWriter(video_name, fourcc, 1, (width, height))

    # Appending the images to the video one by one
    for image in images:
        im = cv2.imread(os.path.join(image_folder, image))
        im = cv2.resize(im, (width, height), interpolation=cv2.INTER_AREA)
        video.write(im)

    # Deallocating memories taken for window creation
    cv2.destroyAllWindows()
    video.release()  # releasing the video generated


def generate_gif(image_folder=".", video_name="farm.gif"):
    """
    Generates an animated gif from a collection of png files generated when rendering a farm with farm.render().
    This way of generating gif is very slow, inefficient, and unreliable. An alternative should be found.
    """
    import imageio.v2 as imageio

    # TODO: This way of generating gif is very slow, inefficient, and unreliable. An alternative should be found.

    # os.chdir("/home/ganesh/Desktop/video")
    images = [
        imageio.imread(img)
        for img in os.listdir(image_folder)
        if ("day-" in img) and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith("png"))
    ]

    imageio.mimsave(video_name, images)
