import itertools

import gymnasium as gym
import numpy as np
from gymnasium.spaces import Box, Discrete
from PIL import Image

from farmgym.v2.specifications.specification_manager import load_yaml


def checkissubclass(class_object, class_name):
    name = class_object.__name__
    if name == class_name:
        return True
    else:
        for base in class_object.__bases__:
            checkissubclass(base, class_name)
        return False


def kappa(x, range):
    a, b = range
    xx = x - b if x > b else 0
    yy = x - a if x < a else 0
    return xx - yy


def glm(theta0, params):
    v = theta0
    for p in params:
        k = kappa(p[1], (p[2], p[3]))
        if k > 0:
            v += p[0] * k
    return v


def expglm(theta0, params):
    return np.exp(-glm(theta0, params))


def expglmnoisy(theta0, params, sigma2, np_random=np.random):
    return expglm(theta0, params) + np_random.normal() * sigma2


class Range:
    def __init__(self, range, value):
        self.default_value = value
        self.range = range
        if type(range) == tuple:
            self.min, self.max = range
            self.value = max(self.min, min(self.max, value))
        else:
            if value in self.range:
                self.value = value
            else:
                if len(self.range) > 0:
                    self.value = self.range[0]
                else:
                    self.value = None

    def set_value(self, value):
        if type(self.range) == tuple:
            self.value = max(self.min, min(self.max, value))
        elif value in self.range:
            self.value = value

    def get_default_value(self):
        return self.default_value
        # if type(self.range) == tuple:
        #    m, M = self.range
        #    if m > -np.infty:
        #        if M < np.infty:
        #            return (m + M) / 2.0
        #        return m
        #    else:
        #        if M < np.infty:
        #            return M
        #        return 0.0
        # else:
        #    if len(self.range) > 0:
        #        return self.range[0]
        #    return None

    def random_value(self, np_random=np.random):
        if type(self.range) == tuple:
            m, M = self.range
            return m + np_random.random() * (M - m)
        else:
            if len(self.range) > 0:
                return np_random.choice(list(self.range))
            return None

    def to_gym_space(self):
        if type(self.range) == tuple:
            m, M = self.range
            return Box(
                low=np.array([np.float32(m)]),
                high=np.array([np.float32(M)]),
                dtype=np.float32,
            )
        else:
            return Discrete(len(self.range))

    def gym_value(self):
        if type(self.range) == tuple:
            # TODO: should be [self.value] for observation to be part of observation space, but creates spurious [][] elsewhere !
            return [self.value]
        else:
            return self.range.index(self.value)

    def __str__(self):
        s = "(range: "
        if type(self.range) == tuple:
            m, M = self.range
            s += str(m) + ", " + str(M)
        else:
            s += str(list(self.range))
        s += "; value: "
        s += str(self.value) + ")"
        return s

    def __repr__(self):
        s = "(range: "
        if type(self.range) == tuple:
            m, M = self.range
            s += str(m) + ", " + str(M)
        else:
            s += str(list(self.range))
        s += "; value: "
        s += str(self.value) + ")"
        return s


def fillarray(x, y, myrange, value):
    ar = np.empty((x, y), dtype=Range)
    for xx in range(x):
        for yy in range(y):
            ar[xx, yy] = Range(myrange, value)
    return ar


class Entity_API:
    """
    class for entity definition

    Naming conventions:
    For variables and parameter names, please use "name_of_the_variable#name_of_the_unit" or "name_of_the_parameter#name_of_the_unit" in case there is a unit.
    """

    def __init__(self, field, parameters):
        self.name = "Entity"
        self.field = field

        if isinstance(parameters, str):
            self.parameters = load_yaml(
                (self.__class__.__name__).lower() + "_specifications.yaml", parameters
            )
        else:
            self.parameters = parameters
            for k in self.get_parameter_keys():
                assert k in self.parameters.keys(), "Parameter " + k + " not specified."

        self.variables = {}  # key:   this  {'range': range, 'value': value } or array of this or dict of variables.

        self.actions = {}  # key:  params, where params is Dict of "key: range", where range is either (m,M), or list (e.g. integer).

        self.dependencies = {}  # List of other entiites on which the entitiy depends.

        self.load_images()

        self.set_random()

        self.initial_conditions = {}

    def set_random(self, np_random=np.random):
        self.np_random = np_random

    def initialize_variables(self, values):
        def set_var(var, value):
            if isinstance(var, dict):
                for k in var:
                    if (type(var[k]) in [dict, np.ndarray]) and k in value.keys():
                        set_var(var[k], value[k])
                    else:
                        if k in value.keys():
                            if type(value[k]) == tuple:
                                m, M = value[k]
                                var[k].set_value(m + self.np_random.random() * (M - m))
                            elif isinstance(value[k], list):
                                var[k].set_value(self.np_random.choice(list(value[k])))
                            else:
                                var[k].set_value(value[k])
            elif type(var) == np.ndarray:
                if type(value) == tuple:
                    m, M = value
                    it = np.nditer(var, flags=["multi_index", "refs_ok"])
                    for x in it:
                        var[it.multi_index].set_value(
                            m + self.np_random.random() * (M - m)
                        )
                elif isinstance(value, list):
                    it = np.nditer(var, flags=["multi_index", "refs_ok"])
                    for x in it:
                        var[it.multi_index].set_value(
                            self.np_random.choice(list(value))
                        )
                else:
                    it = np.nditer(var, flags=["multi_index", "refs_ok"])
                    for x in it:
                        var[it.multi_index].set_value(value)

        # print("SET_VAR:",self.variables,values)
        set_var(self.variables, values)

    def reset(self):
        pass

    def get_parameter_keys(self):
        return []

    def update_variables(self, field, entities: dict):
        # Choice: When an entity update is linked to another entity update, one may ask which of the recevier or emitter should triger the action. Choice: Receiver always triggers action, Emitter never triggers it.

        pass

    def assert_action_(self, action_key, action_value):
        assert action_key in self.actions
        if type(self.actions[action_key]) is tuple:
            assert (
                self.actions[action_key][0]
                <= action_value
                <= self.actions[action_key][1]
            ), (
                "Action value "
                + action_value
                + " for key "
                + action_key
                + " not in range ["
                + str(self.actions[action_key][0])
                + ", "
                + str(self.actions[action_key][1])
                + "]!"
            )
        else:
            assert action_value in self.actions[action_key]

    def assert_action(self, action_name, action_params):
        assert action_name in self.actions
        for p in action_params:
            assert p in self.actions[action_name].keys()
            if type(self.actions[action_name][p]) is tuple:
                # print("ASSERT",action_name, self.actions[action_name], self.actions[action_name][p][0])
                assert (
                    self.actions[action_name][p][0]
                    <= action_params[p]
                    <= self.actions[action_name][p][1]
                ), (
                    "Action value "
                    + str(action_params[p])
                    + " for key "
                    + p
                    + " not in range ["
                    + str(self.actions[action_name][p][0])
                    + ", "
                    + str(self.actions[action_name][p][1])
                    + "]!"
                )
            else:
                # print("ASSERT", action_name, self.actions[action_name], action_params, action_params[p], self.actions[action_name][p])
                if p == "plot":
                    assert str(action_params[p]) in self.actions[action_name][p], (
                        "PLOT"
                        + str(action_params[p])
                        + " not in "
                        + str(self.actions[action_name][p])
                    )
                else:
                    assert action_params[p] in self.actions[action_name][p], (
                        str(action_params[p])
                        + " not in "
                        + str(self.actions[action_name][p])
                    )

    def observe_variable(self, variable_key, path):
        # print("OBSERVE_VARIABLE:",variable_key,path)
        def make_obs(x):
            if type(x) == Range:
                return x.value  # x.gym_value()
            elif isinstance(x, dict):
                ob = {}
                for k in x.keys():
                    ob[k] = make_obs(x[k])
                return ob
            elif type(x) == np.ndarray:
                ob = []
                for xx in x:
                    ob.append(make_obs(xx))
                return ob
            else:
                return x

        obs = self.variables[variable_key]
        for p in path:
            obs = obs[p]
        return make_obs(obs)

    def gym_observe_variable(self, variable_key, path):
        # print("OBSERVE_VARIABLE:",variable_key,path)
        def make_obs(x):
            # print("OBSERVE_VARIABLE:", x)
            if type(x) == Range:
                # TODO : change to [...] ?
                return x.gym_value()
            elif isinstance(x, dict):
                ob = {}
                for k in x.keys():
                    ob[k] = make_obs(x[k])
                return ob
            elif type(x) == np.ndarray:
                # print("OBS VARIABLE", x, " is array")
                ob = []
                for xx in x:
                    ob.append(make_obs(xx))
                return ob
            else:
                # print("OBS VARIABLE", x)
                return x

        obs = self.variables[variable_key]
        for p in path:
            obs = obs[p]
        return make_obs(obs)

    def act_on_variables(self, action_name, action_params) -> None:
        return None

    def load_images(self):
        import os
        from pathlib import Path

        file_path = Path(os.path.realpath(__file__))
        CURRENT_DIR = file_path.parent
        self.images = {}
        if "sprites" in self.parameters:
            for key in self.parameters["sprites"]:
                self.images[key] = Image.open(
                    CURRENT_DIR
                    / ("specifications/sprites/" + self.parameters["sprites"][key])
                )

    def to_fieldimage(self):
        im_width, im_height = 64, 64
        image = Image.new(
            "RGBA",
            (im_width * self.field.X, im_height * self.field.Y),
            (255, 255, 255, 0),
        )
        # for x in range(self.field.X):
        #    for y in range(self.field.Y):
        #        image.paste(images[stages[x, y].value], (im_width * y, im_height * x))
        return image

    def to_thumbnailimage(self):
        im_width, im_height = 64, 64
        image = Image.new("RGBA", (im_width, im_height), (255, 255, 255, 0))  # noqa: F841
        return None

    def __str__(self):
        def make(x, indent=""):
            s = ""
            if isinstance(x, dict):
                s += "\n"
                for k in x:
                    s += indent + ("  " + k + ": ")
                    s += make(x[k], indent=indent + "  ")
            elif type(x) == np.ndarray:
                it = np.nditer(x, flags=["multi_index", "refs_ok"])
                s += "["
                for xx in it:
                    s += str(x[it.multi_index]) + ","
                s = s[:-1]
                s += "]\n"
            elif type(x) in [Range]:
                s += str(x) + "\n"
            else:
                s += "???\n"
            return s

        s = self.name + ":"
        s += make(self.variables, "")
        return s


def get_space_list(space):
    """
    Converts gym `space`, constructed from `types`, to list `space_list`
    """

    # -------------------------------- #

    types = [
        gym.spaces.multi_binary.MultiBinary,
        gym.spaces.discrete.Discrete,
        gym.spaces.multi_discrete.MultiDiscrete,
        gym.spaces.dict.Dict,
        gym.spaces.tuple.Tuple,
    ]

    if type(space) not in types:
        raise ValueError(
            f"input space {space} is not constructed from spaces of types:"
            + "\n"
            + str(types)
        )

    # -------------------------------- #

    if type(space) is gym.spaces.multi_binary.MultiBinary:
        return [
            np.reshape(np.array(element), space.n)
            for element in itertools.product(*[range(2)] * np.prod(space.n))
        ]

    if type(space) is gym.spaces.discrete.Discrete:
        return list(range(space.n))

    if type(space) is gym.spaces.multi_discrete.MultiDiscrete:
        return [
            np.array(element)
            for element in itertools.product(*[range(n) for n in space.nvec])
        ]

    if type(space) is gym.spaces.dict.Dict:
        keys = space.spaces.keys()

        values_list = itertools.product(
            *[get_space_list(sub_space) for sub_space in space.spaces.values()]
        )

        return [
            {key: value for key, value in zip(keys, values)} for values in values_list
        ]

    if type(space) is gym.spaces.tuple.Tuple:
        return [
            list(element)
            for element in itertools.product(
                *[get_space_list(sub_space) for sub_space in space.spaces]
            )
        ]

    # -------------------------------- #


def BoundedNumber(number_class):
    def BoundedNumberClassCreator(class_name, lower_bound, upper_bound):
        if upper_bound and lower_bound and upper_bound < lower_bound:
            raise ValueError(
                f"Upper bound {upper_bound} is lower than the lower bound {lower_bound}"
            )

        def new(cls, number):
            if lower_bound and number < lower_bound:
                raise ValueError(
                    f"{number} is below the lower bound of {lower_bound} for this class"
                )

            if upper_bound and upper_bound < number:
                raise ValueError(
                    f"{number} is above the upper bound of {upper_bound} for this class"
                )

            return number_class(number)

        return type(
            class_name,
            (number_class,),
            {
                "__new__": new,
                "__doc__": f"Class that acts like `{number_class.__name__}` but has an inclusive lower bound of {lower_bound} and an inclusive upper bound of {upper_bound}",
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            },
        )

    return BoundedNumberClassCreator


if __name__ == "__main__":
    BoundedInt = BoundedNumber(int)
    BoundedFloat = BoundedNumber(float)

    IntBetween50And150 = BoundedInt("IntBetween50And150", 50, 150)
    print(IntBetween50And150(100) == 100)  # True
    try:
        IntBetween50And150(200)
    except ValueError as e:
        print(
            f"Caught the ValueError: {e}"
        )  # Caught the value error: 200 is above the upper bound of 150 for this class

    print(IntBetween50And150(50.8))  # 50
    print(
        IntBetween50And150.__doc__
    )  # Class that acts like `int` but has an inclusive lower bound of 50 and an inclusive upper bound of 150

    x = (int)(17)
    print("INT", x, type(x))
    y = (BoundedNumber(int)("int-mM", 50, 150))(53)
    z = (BoundedNumber(int)("int-mM", 20, 127))(47)
    print("Bounded-INT", y, type(y))
    print("Bounded-INT", z, type(z))
    print("Bounded-INT", y - z, type(z))

    x = Range((0, 5), 34)
    print("X:", x.value)
    # y = np.empty((2,3),dtype=Range)
    # print(y)
    z = np.full((2, 3), fill_value=Range((0, 5), 2.0))
    print(z[0, 1].value)
    print(z[1, 1].value)
    y = np.full((2, 3), fill_value=Range(["a", "b", "c"], "b"))
    print(y[0, 1].value)
    print(y[1, 1].value)


# x = Range((2,3), 2.5)
# print({"a": x })
# print(x)
