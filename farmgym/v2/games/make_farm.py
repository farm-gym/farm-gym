import copy

from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.policy_api import Policy_API

from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Cide import Cide
from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Facilities import Facility
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Pollinators import Pollinators

from farmgym.v2.rendering.monitoring import mat2d_value, sum_value

import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent


def make_farm(name, field, entities, init_values=None):

    name_score = name + "_score.yaml"
    name_init = name + "_init.yaml"
    name_actions = name + "_actions.yaml"
    entities1 = []
    for e, i in entities:
        entities1.append((e, i))

    field1 = Field(
        localization=field["localization"],
        shape=field["shape"],
        entity_managers=entities1,
    )

    farmer1 = BasicFarmer(max_daily_interventions=1)
    scoring = BasicScore(score_configuration=CURRENT_DIR / name_score)

    free_observations = []
    free_observations.append(("Field-0", "Weather-0", "day#int365", []))
    free_observations.append(("Field-0", "Weather-0", "air_temperature", []))

    terminal_CNF_conditions = [
        [(("Field-0", "Weather-0", "day#int365", []), lambda x: x.value, ">=", 360)],
        [
            (
                ("Field-0", "Plant-0", "global_stage", []),
                lambda x: x.value,
                "in",
                ["dead", "harvested"],
            )
        ],
    ]
    rules = BasicRule(
        init_configuration=CURRENT_DIR / name_init,
        actions_configuration=CURRENT_DIR / name_actions,
        terminal_CNF_conditions=terminal_CNF_conditions,
        free_observations=free_observations,
        initial_conditions_values=init_values,
    )

    # DEFINE one policy:
    policies = []

    farm = Farm(
        fields=[field1],
        farmers=[farmer1],
        scoring=scoring,
        rules=rules,
        policies=policies,
    )
    farm.name = name
    return farm


def make_monitor(variables):

    var = []

    for v in variables:
        if v == "soil.available_N#g":
            var.append(
                (
                    "Field-0",
                    "Soil-0",
                    "available_N#g",
                    lambda x: sum_value(x),
                    "Available Nitrogen (g)",
                    "range_auto",
                )
            )
        # if (v=="soil.available_N#g.mat"):
        #    var.append(("Field-0", "Soil-0", "available_N#g", lambda x:mat2d_value(x,field1.shape['length#nb'],field1.shape['width#nb']), "Available N (g)", 'range_auto'))
        if v == "soil.available_Water#L":
            var.append(
                (
                    "Field-0",
                    "Soil-0",
                    "available_Water#L",
                    lambda x: sum_value(x),
                    "Available Water (g)",
                    "range_auto",
                )
            )
        if v == "soil.microlife_health_index#%":
            var.append(
                (
                    "Field-0",
                    "Soil-0",
                    "microlife_health_index#%",
                    lambda x: sum_value(x),
                    "Microlife Health  (%)",
                    "range_auto",
                )
            )
        if v == "plant.size#cm":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "size#cm",
                    lambda x: sum_value(x),
                    "Size (cm)",
                    "range_auto",
                )
            )
        if v == "plant.cumulated_water#L":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "cumulated_water#L",
                    lambda x: sum_value(x),
                    "Cumulated water (L)",
                    "range_auto",
                )
            )
        if v == "plant.cumulated_stress_water#L":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "cumulated_stress_water#L",
                    lambda x: sum_value(x),
                    "Cumulated stress water (L)",
                    "range_auto",
                )
            )
        if v == "plant.cumulated_nutrients_N#g":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "cumulated_nutrients_N#g",
                    lambda x: sum_value(x),
                    "Cumulated  N (g)",
                    "range_auto",
                )
            )
        if v == "plant.cumulated_stress_nutrients_N#g":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "cumulated_stress_nutrients_N#g",
                    lambda x: sum_value(x),
                    "Cumulated stress N (g)",
                    "range_auto",
                )
            )
        if v == "plant.flowers_per_plant#nb":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "flowers_per_plant#nb",
                    lambda x: sum_value(x),
                    "Flowers (nb)",
                    "range_auto",
                )
            )
        if v == "plant.pollinator_visits#nb":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "pollinator_visits#nb",
                    lambda x: sum_value(x),
                    "Pollinator visits (nb)",
                    "range_auto",
                )
            )
        if v == "plant.flowers_pollinated_per_plant#nb":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "flowers_pollinated_per_plant#nb",
                    lambda x: sum_value(x),
                    "Flowers pollinated (nb)",
                    "range_auto",
                )
            )
        if v == "plant.fruits_per_plant#nb":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "fruits_per_plant#nb",
                    lambda x: sum_value(x),
                    "Fruits (nb)",
                    "range_auto",
                )
            )
        if v == "plant.fruit_weight#g":
            var.append(
                (
                    "Field-0",
                    "Plant-0",
                    "fruit_weight#g",
                    lambda x: sum_value(x),
                    "Fruit weight (g)",
                    "range_auto",
                )
            )
        if v == "weeds.grow#nb":
            var.append(
                (
                    "Field-0",
                    "Weeds-0",
                    "grow#nb",
                    lambda x: sum_value(x),
                    "Weeds grow (nb)",
                    "range_auto",
                )
            )
        if v == "weeds.seeds#nb":
            var.append(
                (
                    "Field-0",
                    "Weeds-0",
                    "seeds#nb",
                    lambda x: sum_value(x),
                    "Weeds seeds (nb)",
                    "range_auto",
                )
            )
        if v == "weeds.flowers#nb":
            var.append(
                (
                    "Field-0",
                    "Weeds-0",
                    "flowers#nb",
                    lambda x: sum_value(x),
                    "Weeds flowers (nb)",
                    "range_auto",
                )
            )

        if v == "pests.plot_population#nb":
            var.append(
                (
                    "Field-0",
                    "Pests-0",
                    "plot_population#nb",
                    lambda x: sum_value(x),
                    "Pest population (nb)",
                    "range_auto",
                )
            )
        if v == "pests.onplant_population#nb.plant":
            var.append(
                (
                    "Field-0",
                    "Pests-0",
                    "onplant_population#nb",
                    lambda x: sum_value(x["Plant-0"]),
                    "Pest on plant (nb)",
                    "range_auto",
                )
            )
        if v == "pests.onplant_population#nb.weeds":
            var.append(
                (
                    "Field-0",
                    "Pests-0",
                    "onplant_population#nb",
                    lambda x: sum_value(x["Weeds-0"]),
                    "Pest on weeds (nb)",
                    "range_auto",
                )
            )
        if v == "cides.amount#kg":
            var.append(
                (
                    "Field-0",
                    "Cide-0",
                    "amount#kg",
                    lambda x: sum_value(x),
                    "Cide Amount (kg)",
                    "range_auto",
                )
            )
        if v == "fertilizer.amount#kg":
            var.append(
                (
                    "Field-0",
                    "Fertilizer-0",
                    "amount#kg",
                    lambda x: sum_value(x),
                    "Fertilizer Amount (kg)",
                    "range_auto",
                )
            )

    return var


def make_policies_water_harvest(amounts):
    policies = []
    for amount in amounts:
        triggered_observations = []
        policy_observe = (
            [[]],
            [("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)])],
        )
        triggered_observations.append(policy_observe)

        triggered_interventions = []
        policy_harvest = (
            [
                [
                    (
                        ("Field-0", "Plant-0", "stage", [(0, 0)]),lambda x: x,"in",["ripe"],
                    )
                ]
            ],
            [
                {
                    "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                    "delay": 0,
                }
            ],
        )
        triggered_interventions.append(policy_harvest)
        policy_harvest = (
            [
                [
                    (
                        ("Field-0", "Plant-0", "stage", [(0, 0)]),
                        lambda x: x,
                        "in",
                        ["fruit"],
                    )
                ]
            ],
            [
                {
                    "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                    "delay": 18,
                }
            ],
        )
        triggered_interventions.append(policy_harvest)

        if amount > 0.0:
            policy_water = (
                [[]],
                [
                    {
                        "action": (
                            "BasicFarmer-0",
                            "Field-0",
                            "Soil-0",
                            "water_continuous",
                            {"plot": (0, 0), "amount#L": amount, "duration#min": 60},
                        ),
                        "delay": 0,
                    }
                ],
            )
            triggered_interventions.append(policy_water)

        policies.append(Policy_API("", triggered_observations, triggered_interventions))

    return policies


def make_policy_water_harvest(amount):
    triggered_observations = []
    policy_observe = (
        [[]],
        [("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)])],
    )
    triggered_observations.append(policy_observe)

    triggered_interventions = []
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["fruit"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 18,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)

    if amount > 0.0:
        policy_water = (
            [[]],
            [
                {
                    "action": (
                        "BasicFarmer-0",
                        "Field-0",
                        "Soil-0",
                        "water_continuous",
                        {"plot": (0, 0), "amount#L": amount, "duration#min": 60},
                    ),
                    "delay": 0,
                }
            ],
        )
        triggered_interventions.append(policy_water)
    p = Policy_API("", triggered_observations, triggered_interventions)
    p.reset()
    return p


def make_policy_herbicide(amount_herbicide, frequency, amount_water):
    triggered_observations = []
    policy_observe = (
        [[]],
        [
            ("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)]),
            ("BasicFarmer-0", "Field-0", "Weeds-0", "grow#nb", [(0, 0)]),
        ],
    )
    triggered_observations.append(policy_observe)

    triggered_interventions = []
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["fruit"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 18,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    if amount_herbicide > 0.0:
        policy_herbicide = (
            [
                [
                    (
                        ("Field-0", "Weather-0", "day#int365", []),
                        lambda x: x % frequency,
                        "==",
                        0,
                    )
                ]
            ],
            [
                {
                    "action": (
                        "BasicFarmer-0",
                        "Field-0",
                        "Cide-0",
                        "scatter",
                        {"plot": (0, 0), "amount#kg": amount_herbicide},
                    ),
                    "delay": 0,
                }
            ],
        )

        # policy_herbicide= ([[(("Field-0", 'Weeds-0', 'grow#nb', [(0, 0)]), lambda x: x, ">=", 2.),(("Field-0", 'Weather-0', 'day#int365', []), lambda x: x%f, "==", 0)]], [{'action':('BasicFarmer-0', 'Field-0', 'Cide-0', 'scatter', {'plot': (0,0), 'amount#kg':amount_herbicide}),'delay':2}])
        triggered_interventions.append(policy_herbicide)

    if amount_water > 0.0:
        policy_water = (
            [[]],
            [
                {
                    "action": (
                        "BasicFarmer-0",
                        "Field-0",
                        "Soil-0",
                        "water_continuous",
                        {"plot": (0, 0), "amount#L": amount_water, "duration#min": 60},
                    ),
                    "delay": 0,
                }
            ],
        )
        triggered_interventions.append(policy_water)
    p = Policy_API("", triggered_observations, triggered_interventions)
    p.reset()
    return p


def make_policy_fertilize(amount_fertilizer, frequency, amount_water):
    triggered_observations = []
    policy_observe = (
        [[]],
        [
            ("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)]),
            ("BasicFarmer-0", "Field-0", "Weeds-0", "grow#nb", [(0, 0)]),
        ],
    )
    triggered_observations.append(policy_observe)

    triggered_interventions = []
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["fruit"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 18,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    if amount_fertilizer > 0.0:
        policy_fertilize = (
            [
                [
                    (
                        ("Field-0", "Weather-0", "day#int365", []),
                        lambda x: x % frequency,
                        "==",
                        0,
                    )
                ]
            ],
            [
                {
                    "action": (
                        "BasicFarmer-0",
                        "Field-0",
                        "Fertilizer-0",
                        "scatter",
                        {"plot": (0, 0), "amount#kg": amount_fertilizer},
                    ),
                    "delay": 0,
                }
            ],
        )

        # policy_herbicide= ([[(("Field-0", 'Weeds-0', 'grow#nb', [(0, 0)]), lambda x: x, ">=", 2.),(("Field-0", 'Weather-0', 'day#int365', []), lambda x: x%f, "==", 0)]], [{'action':('BasicFarmer-0', 'Field-0', 'Cide-0', 'scatter', {'plot': (0,0), 'amount#kg':amount_herbicide}),'delay':2}])
        triggered_interventions.append(policy_fertilize)

    if amount_water > 0.0:
        policy_water = (
            [[]],
            [
                {
                    "action": (
                        "BasicFarmer-0",
                        "Field-0",
                        "Soil-0",
                        "water_continuous",
                        {"plot": (0, 0), "amount#L": amount_water, "duration#min": 60},
                    ),
                    "delay": 0,
                }
            ],
        )
        triggered_interventions.append(policy_water)
    p = Policy_API("", triggered_observations, triggered_interventions)
    p.reset()
    return p


if __name__ == "__main__":
    from farmgym.v2.games.rungame import (
        run_xps,
        run_policy_xp,
        run_randomactions,
        run_policy,
    )

    # policies = make_policies_water_harvest([0.,8.,2.])
    # f1 = make_farm("blatest",
    #                {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
    #                [(Weather,"dry"),(Soil,"clay"),(Plant, 'tomato'),(Pollinators,'bee')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),
    #                                                                                                 ('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
    #                                                                                                 ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
    #
    # f1.add_monitoring(make_monitor(["soil.available_Water#L","soil.available_N#g", "soil.microlife_health_index#%",
    #                                 "plant.pollinator_visits#nb", "plant.size#cm","plant.flowers_per_plant#nb","plant.flowers_pollinated_per_plant#nb",
    #                                 "plant.cumulated_water#L", "plant.cumulated_stress_water#L","plant.cumulated_nutrients_N#g", "plant.cumulated_stress_nutrients_N#g","plant.fruits_per_plant#nb","plant.fruit_weight#g"]))
    # #cumrewards, cumcosts= run_policy(f1, policies[1], max_steps=150, render=False, monitoring=False)
    # print("Rewards:",cumrewards[-1])

    # cumrewards, cumcosts = run_xps(f1, policies[1], max_steps=150, nb_replicate=40)
    # print("Rewards:",cumrewards)

    # nb_replicate = 10
    # cum_rewards = []
    # farms = []
    # for n in range(nb_replicate):
    #     farms.append(make_farm("blatest"+str(n),
    #                    {'localization': {'latitude#°': 43, 'longitude#°': 4, 'altitude#m': 150},
    #                     'shape': {'length#nb': 1, 'width#nb': 1, 'scale#m': 1.}},
    #                    [(Weather, "dry"), (Soil, "clay"), (Plant, 'tomato'), (Pollinators, 'bee')],
    #                    init_values=[('Field-0', 'Weather-0', 'day#int365', 120),
    #                                 ('Field-0', 'Plant-0', 'stage', 'seed'),
    #                                 ('Field-0', 'Soil-0', 'available_N#g', 2500),
    #                                 ('Field-0', 'Soil-0', 'available_P#g', 2500),
    #                                 ('Field-0', 'Soil-0', 'available_K#g', 2500),
    #                                 ('Field-0', 'Soil-0', 'available_C#g', 2500)]))
    #     farms[-1].add_monitoring(make_monitor(["soil.available_Water#L", "soil.available_N#g", "soil.microlife_health_index#%",
    #                                     "plant.pollinator_visits#nb", "plant.size#cm", "plant.flowers_per_plant#nb",
    #                                     "plant.flowers_pollinated_per_plant#nb",
    #                                     "plant.cumulated_water#L", "plant.cumulated_stress_water#L",
    #                                     "plant.cumulated_nutrients_N#g", "plant.cumulated_stress_nutrients_N#g",
    #                                     "plant.fruits_per_plant#nb", "plant.fruit_weight#g"]))
    #     policies = make_policies_water_harvest([0., 8., 2.])
    #     cr, _ = run_policy(farms[-1], policies[1], max_steps=150, render=False, monitoring=False)
    #     #print(n,":", cr)
    #     cum_rewards.append(cr[-1])
    # print("Rewards:",cum_rewards)
    #
    # nb_replicate = 10
    # cum_rewards = []
    #
    # f1 = make_farm("blatest",
    #                {'localization': {'latitude#°': 43, 'longitude#°': 4, 'altitude#m': 150},
    #                 'shape': {'length#nb': 1, 'width#nb': 1, 'scale#m': 1.}},
    #                [(Weather, "dry"), (Soil, "clay"), (Plant, 'tomato'), (Pollinators, 'bee')],
    #                init_values=[('Field-0', 'Weather-0', 'day#int365', 120),
    #                             ('Field-0', 'Plant-0', 'stage', 'seed'),
    #                             ('Field-0', 'Soil-0', 'available_N#g', 2500),
    #                             ('Field-0', 'Soil-0', 'available_P#g', 2500),
    #                             ('Field-0', 'Soil-0', 'available_K#g', 2500),
    #                             ('Field-0', 'Soil-0', 'available_C#g', 2500)])
    #
    # policy = make_policy_water_harvest(8.)
    # for n in range(nb_replicate):
    #     #policies = make_policies_water_harvest([0., 8., 2.])
    #     cr, _ = run_policy_xp(f1, copy.deepcopy(policy), max_steps=150)
    #     #cr, _ = run_policy_xp(f1, policy, max_steps=150)
    #     # print(n,":", cr)
    #     cum_rewards.append(cr)
    # print("Rewards:", cum_rewards)

    ###
    # Herbicides
    f2 = make_farm(
        "herbtest",
        {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        },
        [
            (Weather, "rainy"),
            (Soil, "clay"),
            (Plant, "corn"),
            (Pollinators, "bee"),
            (Weeds, "base_weed"),
            (Cide, "herbicide"),
            (Pests, "basic"),
        ],
        init_values=[
            ("Field-0", "Weather-0", "day#int365", 120),
            ("Field-0", "Plant-0", "stage", "seed"),
            ("Field-0", "Soil-0", "available_N#g", 2500),
            ("Field-0", "Soil-0", "available_P#g", 2500),
            ("Field-0", "Soil-0", "available_K#g", 2500),
            ("Field-0", "Soil-0", "available_C#g", 2500),
        ],
    )
    f2.add_monitoring(
        make_monitor(
            [
                "soil.available_Water#L",
                "soil.available_N#g",
                "soil.microlife_health_index#%",
                "plant.pollinator_visits#nb",
                "plant.size#cm",
                "plant.flowers_per_plant#nb",
                "plant.flowers_pollinated_per_plant#nb",
                "plant.cumulated_water#L",
                "plant.cumulated_stress_water#L",
                "plant.cumulated_nutrients_N#g",
                "plant.cumulated_stress_nutrients_N#g",
                "plant.fruits_per_plant#nb",
                "plant.fruit_weight#g",
                "weeds.seeds#nb",
                "weeds.grow#nb",
                "weeds.flowers#nb",
                "cides.amount#kg",
                "pests.plot_population#nb",
                "pests.onplant_population#nb.plant",
                "pests.onplant_population#nb.weeds",
            ]
        )
    )

    f3 = make_farm(
        "ferttest",
        {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        },
        [
            (Weather, "rainy"),
            (Soil, "clay"),
            (Plant, "corn"),
            (Pollinators, "bee"),
            (Weeds, "base_weed"),
            (Fertilizer, "fast_all"),
        ],
        init_values=[
            ("Field-0", "Weather-0", "day#int365", 120),
            ("Field-0", "Plant-0", "stage", "seed"),
            ("Field-0", "Soil-0", "available_N#g", 500),
            ("Field-0", "Soil-0", "available_P#g", 500),
            ("Field-0", "Soil-0", "available_K#g", 500),
            ("Field-0", "Soil-0", "available_C#g", 500),
        ],
    )
    f3.add_monitoring(
        make_monitor(
            [
                "soil.available_Water#L",
                "soil.available_N#g",
                "soil.microlife_health_index#%",
                "plant.pollinator_visits#nb",
                "plant.size#cm",
                "plant.flowers_per_plant#nb",
                "plant.flowers_pollinated_per_plant#nb",
                "plant.cumulated_water#L",
                "plant.cumulated_stress_water#L",
                "plant.cumulated_nutrients_N#g",
                "plant.cumulated_stress_nutrients_N#g",
                "plant.fruits_per_plant#nb",
                "plant.fruit_weight#g",
                "weeds.seeds#nb",
                "weeds.grow#nb",
                "weeds.flowers#nb",
                "fertilizer.amount#kg",
            ]
        )
    )

    # policy = make_policy_herbicide(0.005, 10, 8)
    # run_policy(f2, policy, max_steps=60, render=True, monitoring=True)

    policy = make_policy_fertilize(0.5, 10, 2)
    run_policy(f3, policy, max_steps=60, render=True, monitoring=True)
