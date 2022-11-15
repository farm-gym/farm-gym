import yaml

import itertools as it
from gym.spaces import Discrete, Box, Dict, Tuple


class Policy_API:
    def __init__(self, policy, triggered_observations, triggered_interventions):

        self.policy_configuration = policy

        self.triggered_observations = triggered_observations
        self.triggered_interventions = triggered_interventions

        self.delayed_actions = []

    def reset(self):
        self.delayed_actions = []

    def setup(self, farm):
        with open(self.policy_configuration, "r", encoding="utf8") as file:
            self.policy_parameters = yaml.safe_load(file)

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
            trigger_on = any(
                [self.is_trigger_on(trigger, obs) for obs in observations]
            ) or trigger == [[]]
            if trigger_on:
                [action_schedule.append(action) for action in actions]
        return action_schedule

    def intervention_schedule(self, observations):
        # observations: list of (farmer,field,entity,variable,path,value)
        # contains all free observations, hence current day as minimum info.
        action_schedule = []
        for trigger, actions in self.triggered_interventions:
            # Trigger is CNF
            trigger_on = any(
                [self.is_trigger_on(trigger, obs) for obs in observations]
            ) or trigger == [[]]
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


#
#
# x = {'p1': [0,3,5], 'p2': [(1,1),(4,5)]}
# for i in it.product(    x['p1'], x['p2']):
#  print(i)
#
# print('\n\n')
# for i in it.product(  *list(x[k] for k in x) ):
#  print(i)
#
# print('\n\n')
# for i in it.product(    range(1, 3), range(5, 8)):
#     print(i)
#
#     #((x, y) for x in A for y in B)
