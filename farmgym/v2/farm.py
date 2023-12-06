######################################
# ruff: noqa: F841, F821
import inspect
import os
from pathlib import Path
from textwrap import indent

import gymnasium as gym
import numpy as np
from gymnasium.spaces import Box, Dict, Discrete, Tuple
from gymnasium.spaces.utils import flatdim, flatten, flatten_space
from gymnasium.utils import seeding

from farmgym.v2.gymUnion import MultiUnion, Sequence, Union
from farmgym.v2.rendering.monitoring import MonitorPlt, MonitorTensorBoard

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent

## Here is the reason why you should use dictionaries instead of lists as much as possible: https://towardsdatascience.com/faster-lookups-in-python-1d7503e9cd38


def yml_tuple_constructor(v, f=float):
    w = v[1:-1]
    tup = tuple(map(lambda x: f(x), w.split(",")))
    return tup


from farmgym.v2.specifications.specification_manager import (  # noqa: E402
    build_actionsyaml,
    build_inityaml,
    build_scoreyaml,
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

    def __init__(
        self,
        fields,
        farmers,
        scoring,
        rules,
        policies=None,
        interaction_mode="AOMDP",
        seed=None,
    ):
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
        if self.scoring.score_configuration is None:
            print("[Farmgym Warning] Missing score configuration file.")
            build_scoreyaml(filep + "/" + farm_call + "_score_vanilla.yaml", self)
            self.scoring.score_configuration = (
                filep + "/" + farm_call + "_score_vanilla.yaml"
            )
            print(
                "[Solution]"
                + " Vanilla score configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_score_vanilla.yaml")
                + " and used instead. Please, open and modify as wanted."
            )
        else:
            try:
                open(self.scoring.score_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print("[Farmgym Warning] Missing score configuration file.")
                build_scoreyaml(self.scoring.score_configuration, self)
                print(
                    "[Solution]"
                    + " Vanilla score configuration file automatically generated in "
                    + str(self.scoring.score_configuration)
                    + " and used instead. Please, open and modify as wanted."
                )

        # TODO : Double check the behavior when empty init file, or nor empty with or without init_values as parameter.
        if self.rules.init_configuration is None:
            print("[Farmgym Warning] Missing initial conditions configuration file.")
            build_inityaml(
                filep + "/" + farm_call + "_init_vanilla.yaml",
                self,
                mode="default",
                init_values=self.rules.initial_conditions_values,
            )
            self.rules.init_configuration = (
                filep + "/" + farm_call + "_init_vanilla.yaml"
            )
            print(
                "[Solution]"
                + " Vanilla initial conditions configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_init_vanilla.yaml")
                + " and used instead. Please, open and modify as wanted. Deleting a line corresponding to a state variable makes it initialized at default value."
            )
        else:
            try:
                open(self.rules.init_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print(
                    "[Farmgym Warning] Missing initial conditions configuration file."
                )
                build_inityaml(
                    self.rules.init_configuration,
                    self,
                    mode="default",
                    init_values=None,  # self.rules.initial_conditions_values,
                )
                # print('INIT VALUE', self.rules.initial_conditions_values)
                print(
                    "[Solution]"
                    + "  Vanilla initial conditions configuration file automatically generated in "
                    + str(self.rules.init_configuration)
                    + " and used instead. Please, open and modify as wanted. Deleting a line corresponding to a state variable makes it initialized at default value."
                )

        if self.rules.actions_configuration is None:
            print("[Farmgym Warning] Missing actions configuration file.")
            build_actionsyaml(filep + "/" + farm_call + "_actions_vanilla.yaml", self)
            self.rules.actions_configuration = (
                filep + "/" + farm_call + "_actions_vanilla.yaml"
            )
            print(
                "[Solution]"
                + " Vanilla action configuration file automatically generated in "
                + str(filep + "/" + farm_call + "_actions_vanilla.yaml")
                + " and used instead. Please, open and remove any line corresponding to an unwanted action."
            )
        else:
            try:
                open(self.rules.actions_configuration, "r", encoding="utf8")
            except FileNotFoundError as err:
                print("[Farmgym Warning] Missing actions configuration file.")
                build_actionsyaml(self.rules.actions_configuration, self)
                print(
                    "[Solution]"
                    + " Vanilla action configuration file automatically generated in "
                    + str(self.rules.actions_configuration)
                    + " and used instead. Please, open and remove any line corresponding to an unwanted action."
                )

        self.scoring.setup(self)
        self.rules.setup(self)
        self.policies = policies

        try:
            self.discretization_nbins = self.rules.actions_allowed["params"][
                "number_of_bins_to_discretize_continuous_actions"
            ]
        except:
            self.discretization_nbins = 11

        self.farmgym_observation_actions = self.build_farmgym_observation_actions(
            self.rules.actions_allowed["observations"]
        )
        self.farmgym_intervention_actions = self.build_farmgym_intervention_actions(
            self.rules.actions_allowed["interventions"]
        )
        self.farmgym_state_space = self.build_gym_state_space()

        # GYM SPACES:
        self.observation_space = self.build_gym_observation_space(seed)
        # self.action_space = self.build_gym_action_space()
        self.action_space = self.build_gym_discretized_action_space(seed)

        self.name = self.build_name()
        self.shortname = self.build_shortname()

        for fi in self.rules.initial_conditions:
            for e in self.rules.initial_conditions[fi]:
                self.fields[fi].entities[
                    e
                ].initial_conditions = self.rules.initial_conditions[fi][e]

        self.day_path = {
            "field": "Field-0",
            "entity": "Weather-0",
            "variable": "day#int365",
        }
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
            short += (
                str(self.fields[fi].shape["length#nb"])
                + "x"
                + str(self.fields[fi].shape["width#nb"])
                + "("
            )
            for e in self.fields[fi].entities:
                short += self.fields[fi].entities[e].shortname + "_"
            short = short[:-1]
            short += ")"
        return short

    # QUESTION:  Do we add shared entities outside fields ?? (but need to be updated only once /day ). Or do let an entity in a field to be used by a farmer in other field (e.g. water tank).

    def add_monitoring(
        self, list_of_variables, tensorboard=True, matview=True, launch=True
    ):
        """
        Adds a Monitor to the farm, allowing to observe evolution of some state variables with time.
        list_of_variables: the list of variables to be monitored.
        The format for one variable is (field,entity,variable,function,name,option).
        For instance:
        ("Field-0","Plant-0","fruits_per_plant#nb",lambda x: sum_value(x),"Fruits (nb)","range_auto")
        """
        if tensorboard:
            self.monitor = MonitorTensorBoard(
                self, list_of_variables, matview=matview, launch=launch
            )
        else:
            self.monitor = MonitorPlt(self, list_of_variables)

    def reset(self, seed=None, options=None):
        """
        Resets the environment.
        """
        super().reset(seed=seed, options=options)
        if self.interaction_mode == "POMDP":
            return self.gym_reset_POMDP(seed, options)
        else:
            return self.gym_reset_AOMDP(seed, options)

    def gym_reset_AOMDP(self, seed=None, options=None):
        """
        Resets the environment.
        """
        self.last_farmgym_action = None
        farmgym_observations, farmgym_information = self.farmgym_reset(seed, options)

        observations = self.farmgym_to_gym_observations(farmgym_observations)
        information = farmgym_information
        information["farmgym observations"] = farmgym_observations

        # print("RESET",observations,information)
        return (observations, information)

    def gym_reset_POMDP(self, seed=None, options=None):
        """
        Resets the environment.
        """
        self.last_farmgym_action = None
        farmgym_observations, farmgym_information = self.farmgym_reset(seed, options)

        observations = self.farmgym_to_gym_observations(farmgym_observations)
        # print("RESET",observations,farmgym_information)
        # print("OBSERVATION",self.observation_space)
        # print("IS",observations in self.observation_space)
        # print("IS", self.observation_space.contains(observations))

        return (observations, farmgym_information)

    def farmgym_reset(self, seed=None, options=None):
        """
        Resets the environment.
        """

        self.last_farmgym_action = None
        self.np_random, seed = seeding.np_random(seed)
        self.is_new_day = True
        for f in self.fields.values():
            f.np_random = self.np_random
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
        if self.interaction_mode == "POMDP":
            # print("POMDP step")
            return self.gym_step_POMDP(action)
        else:  # Assumes it is AOMDP
            return self.gym_step_AOMDP(action)

    def gym_step_POMDP(self, action):
        # info = {}
        observations, _, _, _, _ = self.farmgym_step([])
        obs, reward, terminated, truncated, info = self.farmgym_step(
            self.gymaction_to_discretized_farmgymaction(action)
        )
        # info["intervention cost"] = info2["intervention cost"]
        # free_observations = self.get_free_observations()
        # print("O1",observations)
        # print("O2",obs)
        # print("O3", self.farmgym_to_gym_observations(observations + obs))
        return self.farmgym_to_gym_observations(
            observations + obs
        ), reward, terminated, truncated, info

    def farmgym_to_gym_observations(self, farmgym_observations):
        gym_observations = []
        for fo in farmgym_observations:
            fa_key, fi_key, e_key, variable_key, path, value = fo
            gym_value = (
                self.fields[fi_key]
                .entities[e_key]
                .gym_observe_variable(variable_key, path)
            )
            g = {}
            g[fa_key] = {}
            g[fa_key][fi_key] = {}
            g[fa_key][fi_key][e_key] = {}
            g[fa_key][fi_key][e_key][variable_key] = {}
            if path != []:
                # print("PATH",str(path))
                # TODO UPDATE for path=['min#°C',2]?
                g[fa_key][fi_key][e_key][variable_key][str(path)] = gym_value
            else:
                g[fa_key][fi_key][e_key][variable_key] = gym_value
            # gym_observations[str(fa_key)+"."+str(fi_key)+"."+str(e_key)+"."+str(variable_key)+"."+str(path)]=gym_value
            gym_observations.append(g)
        return gym_observations

    def gym_step_AOMDP(self, gym_action):
        """
        Performs a step evolution of the system, from current stage to next state given the input action.
        It follows the gym signature, and outputs observations, reward, is_done, information.
        Farmgym observations are added in information["farmgym observations"].
        """
        (
            farmgym_observations,
            reward,
            terminated,
            truncated,
            farmgym_information,
        ) = self.farmgym_step(
            # self.gymaction_to_farmgymaction(gym_action)
            self.gymaction_to_discretized_farmgymaction(gym_action)
        )

        observations = self.farmgym_to_gym_observations(farmgym_observations)
        information = farmgym_information
        information["farmgym observations"] = farmgym_observations

        return observations, reward, terminated, truncated, information

    def farmgym_step(self, action_schedule):
        """
        Performs a step evolution of the system, from current stage to next state given the input action.
        A farm gym step alternates between observation step and action step before moving to next day.
        """
        # print("AS",action_schedule)
        filtered_action_schedule = self.rules.filter_actions(
            self, action_schedule, self.is_new_day
        )
        self.rules.assert_actions(filtered_action_schedule)
        if self.is_new_day:
            self.last_farmgym_action = (filtered_action_schedule, None)
            output = self.observation_step(filtered_action_schedule)
            self.is_new_day = False
            return output
        else:
            self.last_farmgym_action = (
                self.last_farmgym_action[0],
                filtered_action_schedule,
            )
            output = self.intervention_step(filtered_action_schedule)
            self.is_new_day = True
            return output

    def _get_day(self):
        return (int)(
            self.fields[self.day_path["field"]]
            .entities[self.day_path["entity"]]
            .variables[self.day_path["variable"]]
            .value
        )

    def _set_day_path(self, path):
        self.day_path = path

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
            day = self._get_day()
            obs_vec = self.farmers[fa_key].perform_observation(
                fi_key, entity, variable_key, path, day
            )
            [observations.append(o) for o in obs_vec]
            # print("OV",obs_vec)
            # print("O",observations)

        return observations, 0, False, False, {
            "observation cost": observation_schedule_cost
        }
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
            cost = self.scoring.intervention_cost(
                fa_key, fi_key, entity_key, action_name, params
            )
            day = self._get_day()
            obs_vec = self.farmers[fa_key].perform_intervention(
                fi_key, entity_key, action_name, params, day
            )
            # print("OBSVEC", obs_vec)
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
        terminated = self.rules.is_terminal(self.fields)

        if self.monitor is not None:
            self.monitor.update_fig()

        # Compute final reward
        if terminated:
            for f in self.fields.values():
                reward += self.scoring.final_reward(f.entities.values())
            if self.monitor is not None:
                self.monitor.stop()

        return (
            observations,
            reward,
            terminated,
            False,
            {"intervention cost": intervention_schedule_cost},
        )

    def gymaction_to_farmgymaction(self, actions):
        # TODO: Check it on all cases. Is it still working?
        """
        Converts actions given in gym format to actions in farmgym format.
        By construction, this only generates actions in the subset of available actions specified by the configuration file.
        """

        def convert(value, ranges):
            if ranges is None:
                return {}
            if isinstance(ranges, list):
                if isinstance(ranges[value], str) and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif (
                isinstance(ranges, str) and "(" in ranges
            ):  # Range of continuous values
                # print("?",value, ranges)
                return (float)(value)
            elif isinstance(ranges, dict):
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
        """
        Input:
            actions = [4, 8 ...]
        Output:
            fg_actions = [('BasicFarmer-0', 'Field-0', 'Plant-0', 'stage', [(0, 0)]), ...]
        """

        def convert(value, ranges):
            if ranges is None:
                return {}
            if isinstance(ranges, list):
                if isinstance(ranges[value], str) and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif (
                isinstance(ranges, str) and "(" in ranges
            ):  # Range of continuous values
                # r = ranges.split(",")
                # m=float(r[0][1:])
                # M=float(r[1][:-1])
                # print("?",value, ranges,m,M)
                return (float)(value)
            elif isinstance(ranges, dict):
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
                # print("A", action)
                # print("gymtodiscre", theindex, self.farmgym_intervention_actions,actions)
                for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions:
                    if ng > theindex:
                        theaction = (fa, fi, e, a, f_a, g, ng)
                        break
                    else:
                        theindex -= ng
                # print("gymtodiscre", theindex, theaction)
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

    def discretized_farmgymaction_to_gymaction(self, actions):
        """
        Input:
            actions = [('BasicFarmer-0', 'Field-0', 'Plant-0', 'stage', [(0, 0)]), ...]
        Output:
            ii = [4,5, etc]
        """
        ii = []
        nb_tot_actions = self.action_space.space.n + len(
            self.farmgym_observation_actions
        )
        for action in actions:
            for i in range(nb_tot_actions):
                a = self.farm.gymaction_to_discretized_farmgymaction([i])
                fa, fi, e, a, p = a[0]
                if action == a[0]:
                    ii.append(i)
        return ii

    def random_allowed_intervention(self):
        """
        Outputs a randomly generated intervention, as allowed by the yaml file, in farmgym format.
        """
        n = self.np_random.integers(len(self.farmgym_intervention_actions))
        # intervention = self.np_random.choice(list(self.farmgym_intervention_actions))
        (
            fa,
            fi,
            e,
            inter,
            params,
            gym_space,
            len_gym_space,
        ) = self.farmgym_intervention_actions[n]
        o = gym_space.sample()

        def convert(value, ranges):
            if isinstance(ranges, list):
                if isinstance(ranges[value], str) and "(" in ranges[value]:  # Plots.
                    return yml_tuple_constructor(ranges[value], int)
                return ranges[value]
            elif (
                isinstance(ranges, str) and "(" in ranges
            ):  # Range of continuous values
                # print("?",value, ranges)
                return (float)(value)
            elif isinstance(ranges, dict):
                c_v = {}
                for k in ranges:
                    c_v[k] = convert(value[k], ranges[k])
                return c_v

        farmgym_act = {}
        if isinstance(params, dict):
            # print("DICT:",f_a,act)
            farmgym_act = {}
            for k in params:
                farmgym_act[k] = convert(o[k], params[k])

        return (fa, fi, e, inter, farmgym_act)

    def random_allowed_observation(self):
        """
        Outputs a randomly generated observation-action (action to collect observation), as allowed by the yaml file, in farmgym format.
        """
        if len(self.farmgym_observation_actions) > 0:
            n = self.np_random.integers(len(self.farmgym_observation_actions))
            return self.farmgym_observation_actions[n]
        return None

    def build_farmgym_intervention_actions(self, action_yaml):
        """
        Generates a list of all possible farmgym intervention-actions allowed by the configuration file action_yaml.
        """

        def make(action):
            #            print("ACTION",action, type(action))
            if isinstance(action, str):
                tuple = yml_tuple_constructor(action)
                m, M = tuple
                return Box(low=m, high=M, shape=())
            elif isinstance(action, list):
                ## Need to handle tuples differently.
                # print("KEYY",dictio[key])
                return Discrete(len(action))
            elif action is None:
                return Discrete(1)
            elif isinstance(action, dict):
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
                    if fi in action_yaml[fa].keys():
                        for e in self.fields[fi].entities:
                            if e in action_yaml[fa][fi].keys():
                                if action_yaml[fa][fi][e] is not None:
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
                                                len_discretized_gym_space(
                                                    gym_a,
                                                    nbins=self.discretization_nbins,
                                                ),
                                            )
                                        )
        return actions

    def count_farmgym_intervention_actions(self):
        n = 0
        for i in self.farmgym_intervention_actions:
            n += i[6]
        return n

    def build_farmgym_observation_actions(self, action_yaml):
        """
        Generates a list of all possible farmgym observation-actions allowed by the configuration file action_yaml.
        """

        def make(dictio, variables):
            if isinstance(dictio, list):
                actions = {}
                for key in dictio:
                    if key == "*":
                        actions["*"] = ["'"]
                    elif isinstance(key, str) and "(" in key:
                        id = yml_tuple_constructor(key, int)
                        actions[id] = [id]
                    #    print("KEY2-")
                    #    actions[key]=['\'']
                    else:
                        actions[key] = [key]
                return actions
            elif dictio is None:
                return ["'"]
            elif isinstance(dictio, dict):
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
            if isinstance(paths, dict):
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
                    if fi in action_yaml[fa].keys():
                        for e in self.fields[fi].entities:
                            if e in action_yaml[fa][fi].keys():
                                if action_yaml[fa][fi][e] is not None:
                                    for var in self.fields[fi].entities[e].variables:
                                        if var in action_yaml[fa][fi][e].keys():
                                            paths = make(
                                                action_yaml[fa][fi][e][var],
                                                self.fields[fi]
                                                .entities[e]
                                                .variables[var],
                                            )
                                            acts = unpile((fa, fi, e, var), paths, [])
                                            [actions.append(o) for o in acts]

        free_actions = []
        if "Free" in action_yaml.keys():
            for fi in self.fields:
                if fi in action_yaml["Free"].keys():
                    for e in self.fields[fi].entities:
                        if e in action_yaml["Free"][fi].keys():
                            if action_yaml["Free"][fi][e] is not None:
                                for var in self.fields[fi].entities[e].variables:
                                    if var in action_yaml["Free"][fi][e].keys():
                                        paths = make(
                                            action_yaml["Free"][fi][e][var],
                                            self.fields[fi].entities[e].variables[var],
                                        )
                                        acts = unpile(("Free", fi, e, var), paths, [])
                                        [free_actions.append(o) for o in acts]
        self.rules.free_observations = free_actions

        if self.interaction_mode == "AOMDP":
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
            if isinstance(x, dict):
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

        return Dict(make_s(state_space_))  # Tuple(state_space)

    def build_gym_observation_space(self, seed):
        """
        Outputs an observation space in gym MultiUnion format from all possible observations.
        """

        # TODO: flatten https://github.com/openai/gym/issues/1830?
        # Number all discrete actions, then discretize continuous ones with param N (nb of elements for each dim). number mutiactions etc.

        def make_space(x):
            if isinstance(x, dict):
                xspace = {}
                for k in x.keys():
                    xspace[k] = make_space(x[k])
                # print("MS",x.keys(),"\n\t",xspace,"\n\t",Dict(xspace))
                # TODO: THe following does not keep the keys from x.keys() in the correct order !! This is a gymnasium (and gym) issue !! It seems to sort them by alphabetic order !!
                return Dict(xspace)
            elif type(x) == np.ndarray:
                xspace = []
                for xx in x:
                    xspace.append(make_space(xx))
                return Tuple(xspace)
            else:
                return x.to_gym_space()

        observation_space = []

        for fo in self.rules.free_observations:
            fa_key, fi_key, e_key, variable_key, path = fo
            var = self.fields[fi_key].entities[e_key].variables[variable_key]
            x = var
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
                # oo ={}
                # for p in path:
                #    oo[p]={}

                o_space[fa_key][fi_key][e_key][variable_key][str(path)] = x
            else:
                o_space[fa_key][fi_key][e_key][variable_key] = x
            # print("MAKE SPACE",make_space(o_space))
            observation_space.append(make_space(o_space))

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

        multi_union = MultiUnion(observation_space)
        multi_union.seed(seed)
        return multi_union

    def build_gym_action_space(self, seed):
        multi_union = MultiUnion(
            [Discrete(1) for x in range(len(self.farmgym_observation_actions))]
            + [g for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions],
            maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"],
            np_random=self.np_random,
        )
        multi_union.seed(seed)
        return multi_union

        # return MultiUnion(
        #    [Discrete(len(self.farmgym_observation_actions))]
        #    + [g for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions],
        #    maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"],
        # )

    def build_gym_discretized_action_space(self, seed):
        """Whenever encounters a continuous box, split each dimension into nbins bins"""
        naction = len(self.farmgym_observation_actions)
        for fa, fi, e, a, f_a, g, ng in self.farmgym_intervention_actions:
            naction += ng
        # print("BUILD DISCRETIZED A", naction)
        sequence = Sequence(
            Discrete(naction),
            maxnonzero=self.rules.actions_allowed["params"]["max_action_schedule_size"],
        )
        sequence.seed(seed)
        return sequence
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
        if self.interaction_mode == "AOMDP":
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
            image = self.make_rendering_image()
            day = (int)(
                self.fields["Field-0"]
                .entities["Weather-0"]
                .variables["day#int365"]
                .value
            )
            if self.interaction_mode == "AOMDP":
                if self.is_new_day:  # Assumes it just switch from False to True
                    image.save("farm-day-" + "{:03d}".format(day) + "-2.png")
                else:
                    image.save("farm-day-" + "{:03d}".format(day) + "-1.png")
            else:
                image.save("farm-day-" + "{:03d}".format(day) + ".png")

    def make_rendering_image(self):
        max_display_actions = self.rules.actions_allowed["params"][
            "max_action_schedule_size"
        ]

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
                                if self.fields[fi].entities[e].to_thumbnailimage()
                                is not None
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

        font = ImageFont.truetype(
            str(CURRENT_DIR) + "/rendering/Gidole-Regular.ttf", size=font_size
        )
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
                im_height * YY
                + offset_header
                + offset_sep
                + offset_foot
                + offset_actions,
            ),
            (255, 255, 255, 255),
        )
        d = ImageDraw.Draw(dashboard_picture)

        day = (int)(
            self.fields["Field-0"].entities["Weather-0"].variables["day#int365"].value
        )
        day_string = "Day {:03d}".format(day)

        d.text(
            (
                dashboard_picture.width // 2 - len(day_string) * font_size // 4,
                im_height * YY
                + offset_header
                + offset_sep
                + offset_foot // 4
                + offset_actions,
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
                image = image.resize(
                    (image.width * scale_factor, image.height * scale_factor)
                )
                # image = image.resize((im_width, im_height))
                dashboard_picture.paste(image, (offsetx, offset_header), image)

                j = index // self.fields[fi].X
                i = index - j * self.fields[fi].X
                image_t = self.fields[fi].entities[e].to_thumbnailimage()
                if image_t is not None:
                    image_t = image_t.resize(
                        (image_t.width * scale_factor, image_t.height * scale_factor)
                    )
                    dd = ImageDraw.Draw(image_t)
                    # dd.rectangle(((2,2),(im_width-2,im_height-2)), fill="#ff000000", outline="red")
                    xx = offsetx + i * im_width
                    yy = (
                        offset_header
                        + self.fields[fi].Y * im_height
                        + offset_sep
                        + j * im_height
                    )
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
                (
                    (offsetx, offset_field_y),
                    (
                        offsetx + self.fields[fi].X * im_width,
                        offset_field_y + offset_actions + im_width // 100,
                    ),
                ),
                fill=(255, 255, 255, 255),
                outline=(0, 0, 0, 255),
                width=im_width // 100,
            )

            nb_a = 0
            if self.last_farmgym_action:
                # print("LAST ACTION", self.is_new_day, self.last_farmgym_action)
                mor, aft = self.last_farmgym_action
                if self.is_new_day:
                    actions = aft
                else:
                    actions = mor
                if actions:
                    for a in actions:
                        # print("A", a)
                        fa_key, fi_key, entity_key, action_name, params = a
                        if a[1] == fi and nb_a <= max_display_actions:
                            text = action_name
                            # print("DISPLAY ACTION",action_name, params)
                            if isinstance(params, dict):
                                for p in params:
                                    text += " " + str(params[p])
                            # if (type(params) == dict) and ("plot" in params.keys()):
                            #    text += " " + str(params["plot"])
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

        # dashboard_picture.save("farm-day-" + "{:03d}".format(day) + ".png")
        return dashboard_picture

    def render_step(self, action, observation, reward, terminated, truncated, info):
        # Called after a step.
        s = "Farm:\t" + self.shortname + "\t"
        if self.is_new_day:  # Assumes it just switch from False to True
            s += "\tAfternoon phase (interventions)\n"
        else:
            s += "\tMorning phase (observations)\n"
        s += "Actions planned: " + str(action) + "\n"
        for a in self.gymaction_to_discretized_farmgymaction(action):
            s += "\t- " + str(a) + "\n"
        s += "Observations received:\n"
        for o in observation:
            s += "\t- " + str(o) + "\n"
        s += "Reward received: " + str(reward) + "\n"
        s += "Information:\n"
        for i in info:
            s += "\t- " + str(i) + ": " + str(info[i]) + "\n"
        if terminated:
            s += "Terminated.\n"
        if truncated:
            s += "Truncated.\n"
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

        if self.interaction_mode == "AOMDP":
            s += "Available farmgym observations:" + "\n"
            for o in self.farmgym_observation_actions:
                s += "\t" + str(o) + "\n"

        s += "Available farmgym interventions:" + "\n"
        for i in self.farmgym_intervention_actions:
            fa, fi, e, a, f_a, g, ng = i
            s += "\t" + str((fa, fi, e, a, f_a)) + "\n"

        s += (
            "Available gym actions: (as list [n1 n2 n3] where ni is one of the following)"
            + "\n"
        )
        s += self.actions_to_string()
        return s

    def understand_the_farm(self):
        farm = self
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
        # print("?", farm.farmgym_state_space.contains(s), farm.observation_space.contains(o))

        print("############RANDOM ACTIONS################")
        print(
            "Random intervention allowed by rules:\t",
            farm.random_allowed_intervention(),
        )
        print(
            "Random observation allowed by rules:\t", farm.random_allowed_observation()
        )
        print("############RANDOM GYM ACTIONS################")
        print("Gym (discretized) actions:", farm.action_space)
        # disc_space= farm.build_gym_discretized_action_space()
        # print("Gym discretized  actions:", disc_space)
        print("Do nothing gym action schedule:", "[]")
        print(
            " corresponding farmgym action schedule:",
            farm.gymaction_to_farmgymaction([]),
        )
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
        # print(farm.actions_to_string())


import cv2  # noqa: E402


def generate_video(image_folder=".", video_name="farm.avi"):
    """
    Generates an avi video from a collection of png files generated when rendering a farm with farm.render()
    """
    # os.chdir("/home/ganesh/Desktop/video")
    images = [
        img
        for img in os.listdir(image_folder)
        if ("day-" in img)
        and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith("png"))
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
        if ("day-" in img)
        and (img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith("png"))
    ]

    imageio.mimsave(video_name, images)
