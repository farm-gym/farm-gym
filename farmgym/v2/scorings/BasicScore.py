from farmgym.v2.specifications.specification_manager import load_yaml

from farmgym.v2.scoring_api import Scoring_API
from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Facilities import Facility
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Pollinators import Pollinators
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Weeds import Weeds

import numpy as np


def compute_sizeobservation(variable):
    if type(variable) not in [dict, np.ndarray]:
        return 1
    if type(variable) == dict:
        return sum([compute_sizeobservation(variable[a]) for a in variable.keys()])
    if type(variable) == np.ndarray:
        return sum(1 for x in np.nditer(variable, flags=["multi_index", "refs_ok"]))


# def compute_allinterventioncost(action,unitcost,field):
#    return unitcost*field.shape['width']*field.shape['length']
# c= compute_allobservationcost( {'bla': np.zeros((2,3)), 'bli': np.zeros((1,4)) }, 1)
# print(c)

import yaml


def sum_value(value_array):
    sum = 0
    it = np.nditer(value_array, flags=["multi_index", "refs_ok"])
    for x in it:
        sum += value_array[it.multi_index].value
    return sum


class BasicScore(Scoring_API):
    def __init__(self, score_configuration=""):
        Scoring_API.__init__(self, score_configuration=score_configuration)
        # self.default_action_cost = default_action_cost

    # TODO: Define a "default_cost" in the yaml file, so that each missing entry is given this value!

    def intervention_cost(self, farmer, field_key, entity_key, action_key, params):
        return self.score_parameters["intervention-cost"][field_key][entity_key][
            action_key
        ]
        # action_cost=0
        # return action_cost
        # e= field.entities[entity]
        # cost =    self.cost_parameters['default']
        # for cl in [Birds, Facility, Fertilizer, Pests, Plant, Pollinators, Soil, Weather, Weeds]:
        #     if (issubclass(e.__class__, cl)):
        #        c= self.cost_parameters[cl.__name__][action]
        #        cost=c
        #        #if (isinstance(c,dict)):
        #        #    cost = c[value]
        #        #else:
        #        #    cost = c
        # action_cost += cost
        # return action_cost

    def observation_cost(
        self, farmer, field, field_key, entity_key, variable_key, path
    ):
        var = field.entities[entity_key].variables[variable_key]
        for p in path:
            var = var[p]
        # return 0
        return (
            compute_sizeobservation(var)
            * self.score_parameters["observation-cost"][field_key][entity_key][
                variable_key
            ]
        )

    def reward(self, entities_list: list):
        r_stage = 0
        for e in entities_list:
            if issubclass(e.__class__, Plant):
                ## Do we need to make reward depend on transitions (s,s')? No
                ## To avoid that we keep accumulating 1 when still in stage sprouting: use transition_states !!
                # print("GLOBAL_S
                # TAGE",e.variables["global_stage"])
                if "entered_" in e.variables["global_stage"].value:
                    if e.variables["global_stage"].value != "entered_death":
                        r_stage += 1

        mix = self.score_parameters["reward-mix"]
        r = r_stage * mix["alpha_stage"]
        return r

    def final_reward(self, entities_list: list):
        # print("FINAL REWARD")

        # birds =  [entities_list[e] for e in entities_list if checkissubclass(entities_list[e].__class__, 'Birds')]

        birds = [e for e in entities_list if issubclass(e.__class__, Birds)]
        pests = [e for e in entities_list if issubclass(e.__class__, Pests)]
        pollinators = [e for e in entities_list if issubclass(e.__class__, Pollinators)]
        weeds = [e for e in entities_list if issubclass(e.__class__, Weeds)]

        r_bio = 0
        for b in birds:
            r_bio += b.variables["total_cumulated_birds#nb"].value
        for p in pests:
            r_bio += p.variables["total_cumulated_plot_population#nb"].value * 0.01
        for p in pollinators:
            r_bio += p.variables["total_cumulated_occurrence#nb"].value * 0.5
        for w in weeds:
            r_bio += w.variables["total_cumulated_plot_population#nb"].value * 0.1

        ferts = [e for e in entities_list if issubclass(e.__class__, Fertilizer)]
        soil = [e for e in entities_list if issubclass(e.__class__, Soil)]

        r_resource = 0
        for f in ferts:
            r_resource += f.variables["total_cumulated_scattered_amount#kg"].value
        for s in soil:
            r_resource += s.variables["total_cumulated_added_water#L"].value
            r_resource += (
                s.variables["total_cumulated_added_cide#g"]["pollinators"].value * 0.001
            )
            r_resource += (
                s.variables["total_cumulated_added_cide#g"]["pests"].value * 0.001
            )
            r_resource += (
                s.variables["total_cumulated_added_cide#g"]["soil"].value * 0.001
            )
            r_resource += (
                s.variables["total_cumulated_added_cide#g"]["weeds"].value * 0.001
            )

        r_soil = sum_value(soil[0].variables["microlife_health_index#%"]) / 100

        plants = [e for e in entities_list if issubclass(e.__class__, Plant)]
        r_harvest = 0.0
        for p in plants:
            r_harvest += p.variables["harvest_weight#kg"].value * 1000

        r_stage = 0
        for p in plants:
            rr = 0
            for x in range(p.field.X):
                for y in range(p.field.Y):
                    if p.variables["stage"][x, y].value == "sprout":
                        rr += 2.0
                    elif p.variables["stage"][x, y].value == "grow":
                        rr += (
                            p.variables["size#cm"][x, y].value
                            / p.parameters["size_max#cm"]
                        )

                    elif p.variables["stage"][x, y].value == "flower":
                        rr += (
                            p.variables["nb_pollinated_flowers"][x, y].value
                            / p.parameters["nb_flowers"]
                        )
                    elif p.variables["stage"][x, y].value == "fruit":
                        rr += (
                            p.variables["fruit_weight#g"][x, y].value
                            / p.parameters["fruit_weight_max#g"]
                        )

            r_stage += rr / (p.field.X * p.field.Y)

        mix = self.score_parameters["reward-mix"]
        r = (
            r_bio * mix["alpha_bio"]
            - r_resource * mix["alpha_resource"]
            + r_soil * mix["alpha_soil"]
            + r_harvest * mix["alpha_harvest"]
            + r_stage * mix["alpha_stage"]
        )
        return r
