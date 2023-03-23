import yaml


class Rules_API:
    """
    class for rules definition

    Parameters
    ----------
    first_day: int

    last_day: int

    terminal_CNF_conditions:
        This is a boolean formula in CNF. E.g. [ [a1,a2],[a3],[a4,a5]]] means (a1 & a2) & (a3) or (a4 & a5) Each condition is a copmarison between a variable value and a target value.

    max_action_schedule_cost:
    """

    def __init__(
        self,
        init_configuration,
        actions_configuration,
        terminal_CNF_conditions,
        initial_conditions_values=None,
    ):

        self.init_configuration = init_configuration
        self.initial_conditions_values = initial_conditions_values

        self.terminal_CNF_conditions = terminal_CNF_conditions

        self.free_observations = []
        #for fo in free_observations:
        #    fi_key, e_key, variable_key, path = fo
        #    self.free_observations.append(("Free", fi_key, e_key, variable_key, path))

        self.actions_configuration = actions_configuration

    def setup(self, farm):
        with open(self.init_configuration, "r", encoding="utf8") as file:
            self.initial_conditions = yaml.safe_load(file)

        with open(self.actions_configuration, "r", encoding="utf8") as file:
            self.actions_allowed = yaml.safe_load(file)  # Note the safe_load

        #self.actions_allowed['observations']['Free']


    def is_terminal(self, fields):
        for and_conditions in self.terminal_CNF_conditions:
            bool_cond = True
            for condition in and_conditions:
                variable_path, fun, operator, value = condition
                field, entity, variable, path = variable_path
                v = fields[field].entities[entity].variables[variable]
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
            if bool_cond:
                return True
        return False

    def get_free_observations(self, farm):
        """
        :param field:
        :return:  list of (field-key,position, entity-key, variable, value)
        """
        # Give all information
        # entities_list = field.entities.values()
        observations = []

        for fo in self.free_observations:
            fa_key, fi_key, e_key, variable_key, path = fo
            value = farm.fields[fi_key].entities[e_key].observe_variable(variable_key, path)
            observations.append((fa_key, fi_key, e_key, variable_key, path, value))

        return observations

    def is_allowed_action(self, action, is_observation_time):
        allowed_actions = self.actions_allowed

        def check(dic, param):
            if dic == None:
                return True
            if len(param) > 0:
                if type(dic) == dict:
                    if str(param[0]) not in dic.keys():
                        return False
                    return check(dic[param[0]], param[1:])
                else:
                    if str(param[0]) not in dic:
                        return False
                    else:
                        return True
            else:
                if ("*" in dic) or ("*" in dic.keys()):
                    return True
                return dic == {}

        #print("ACTION",action)
        fa, fi, e, a, p = action
        if type(p) != list:  # Intervention
            if is_observation_time:
                return False
            env_space = allowed_actions["interventions"]
            if fa in env_space.keys():
                farmer = env_space[fa]
                if fi in farmer.keys():
                    field = farmer[fi]
                    # print("FIELD",field)
                    if e in field.keys():
                        ent = field[e]
                        # print("ENT",ent)
                        if a in ent.keys():
                            act = ent[a]
                            # print("ACT",act)
                            return True
        else:
            env_space = allowed_actions["observations"]
            if not is_observation_time:
                return False
            if fa in env_space.keys():
                farmer = env_space[fa]
                if fi in farmer.keys():
                    field = farmer[fi]
                    if e in field.keys():
                        ent = field[e]
                        # print("ENT", ent)
                        if a in ent.keys():
                            act = ent[a]
                            # print("ACT", act, p)
                            return check(act, p)
                        # for j in range(len(p)):
                        #     if (type(act) == dict):
                        #         if (str(p[j]) not in act.keys()):
                        #             return False
                        #         act = act[p[j]]
                        #     else:
                        #         if (str(p[j]) not in act):
                        #             return False
                        #         else:
                        #             return True
                        # if (act is None):
                        #     #if len(p) == 0:
                        #         return True
                        #     #else:
                        #      #print(field,ent,act,"\n\t",p)
                        #      #raise Exception("Malformed action request " + str(action))
                        # if ('*' in act) or ('*' in act.keys()):
                        #     return True
        return False

    def assert_actions(self, actions):
        ()

    def filter_actions(self, farm, actions, is_observation_time):
        return actions
