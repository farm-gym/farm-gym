import numpy as np

import farmgym.v2.scorings.reward_functions as rf
from farmgym.v2.score_api import Score_API


def compute_sizeobservation(variable):
    if type(variable) not in [dict, np.ndarray]:
        return 1
    if isinstance(variable, dict()):
        return sum([compute_sizeobservation(variable[a]) for a in variable.keys()])
    if type(variable) == np.ndarray:
        return sum(1 for x in np.nditer(variable, flags=["multi_index", "refs_ok"]))


class BasicScore(Score_API):
    def __init__(self, score_configuration=""):
        Score_API.__init__(self, score_configuration=score_configuration)
        # self.default_action_cost = default_action_cost

    # TODO: Define a "default_cost" in the yaml file, so that each missing entry is given this value!

    def intervention_cost(self, farmer, field_key, entity_key, action_key, params):
        return self.score_parameters["intervention-cost"][field_key][entity_key][
            action_key
        ]

    def observation_cost(
        self, farmer, field, field_key, entity_key, variable_key, path
    ):
        var = field.entities[entity_key].variables[variable_key]
        for p in path:
            var = var[p]
        return (
            compute_sizeobservation(var)
            * self.score_parameters["observation-cost"][field_key][entity_key][
                variable_key
            ]
        )

    def reward(self, entities_list: list):
        r_bio = rf.reward_biodiversitycounts(entities_list)
        r_resource = rf.reward_resourceadded(entities_list)
        r_soil = rf.reward_soilmicrolife(entities_list)
        r_harvest = rf.reward_harvest(entities_list)
        r_stagecount = rf.reward_stagecount(entities_list)
        r_stagetransition = rf.reward_stagetransition(entities_list)

        mix = self.score_parameters["reward-mix"]
        r = (
            r_bio * mix["weight_biodiversitycounts"]
            + r_resource * mix["weight_resourceadded"]
            + r_soil * mix["weight_soilmicrolife"]
            + r_harvest * mix["weight_harvest"]
            + r_stagecount * mix["weight_stagecount"]
            + r_stagetransition * mix["weight_stagetransition"]
        )
        return r

    def final_reward(self, entities_list: list):
        r_bio = rf.reward_biodiversitycounts(entities_list)
        r_resource = rf.reward_resourceadded(entities_list)
        r_soil = rf.reward_soilmicrolife(entities_list)
        r_harvest = rf.reward_harvest(entities_list)
        r_stagecount = rf.reward_stagecount(entities_list)
        r_stagetransition = rf.reward_stagetransition(entities_list)

        mix = self.score_parameters["final-reward-mix"]
        r = (
            r_bio * mix["weight_biodiversitycounts"]
            + r_resource * mix["weight_resourceadded"]
            + r_soil * mix["weight_soilmicrolife"]
            + r_harvest * mix["weight_harvest"]
            + r_stagecount * mix["weight_stagecount"]
            + r_stagetransition * mix["weight_stagetransition"]
        )
        return r
