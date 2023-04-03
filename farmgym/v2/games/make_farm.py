import copy

from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.policy_api import Policy_API


## The following importe lines are import for the make_farm function that uses inspection module!

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

from farmgym.v2.rendering.monitoring import mat2d_value, sum_value, make_variables_to_be_monitored


import inspect


import yaml
import sys


def make_farm(yamlfile):
    with open(yamlfile, "r", encoding="utf8") as file:
        farm_yaml = yaml.safe_load(file)

    farm = farm_yaml["Farm"]

    fields = []
    farmers = []
    for fi in farm:
        if "Field" in fi:
            entities = farm[fi]["entities"]
            ent = []
            for e in entities:
                k = (list(e.keys()))[0]
                c = getattr(sys.modules[__name__], k)
                # print("E",e, list(e.keys()), k,c)
                ent.append((c, str(e[k])))
            fields.append(Field(localization=farm[fi]["localization"], shape=farm[fi]["shape"], entities_specifications=ent))
        if "Farmer" in fi:
            if farm[fi]["type"] == "basic":
                farmers.append(
                    BasicFarmer(
                        max_daily_interventions=farm[fi]["parameters"]["max_daily_interventions"],
                        max_daily_observations=farm[fi]["parameters"]["max_daily_observations"],
                    )
                )

    interaction_mode = farm_yaml["interaction_mode"]
    name = yamlfile[:-5]
    # TODO: Perhaps these names could be defined automatically? or actually remove the initailization file entirely, and proceed with init_values only.
    name_score = name+"_"+farm_yaml["score"]
    name_init = name+"_"+farm_yaml["initialization"]
    name_actions = name+"_"+farm_yaml["actions"]

    scoring = BasicScore(score_configuration=name_score)

    # if (terminal_conditions==None):
    #    terminal_CNF_conditions = [
    #        [(("Field-0", "Weather-0", "day#int365", []), lambda x: x.value, ">=", 360)],
    #        [
    #            (
    #                ("Field-0", "Plant-0", "global_stage", []),
    #                lambda x: x.value, "in", ["dead", "harvested"],
    #            )
    #        ]
    #    ]
    # else:
    #    terminal_CNF_conditions = terminal_conditions

    rules = BasicRule(
        init_configuration=name_init,
        actions_configuration=name_actions
        # terminal_CNF_conditions=terminal_CNF_conditions,
        # initial_conditions_values=init_values
    )

    # [print("FIELDS",f) for f in fields]
    farm = Farm(fields=fields, farmers=farmers, scoring=scoring, rules=rules, policies=[], interaction_mode=interaction_mode)
    return farm


def make_basicfarm(name, field, entities, farmers=[{"max_daily_interventions": 1}]):
    # farm_call = " ".join(inspect.stack()[1].code_context[0].split("=")[0].split())
    filep = "/".join(inspect.stack()[1].filename.split("/")[0:-1])

    name_score = name + "_score.yaml"
    name_init = name + "_init.yaml"
    name_actions = name + "_actions.yaml"
    entities1 = []
    for e, i in entities:
        entities1.append((e, i))

    field1 = Field(
        localization=field["localization"],
        shape=field["shape"],
        entities_specifications=entities1,
    )

    # farmer1 = BasicFarmer(max_daily_interventions=1)
    ffarmers = [BasicFarmer(max_daily_interventions=f["max_daily_interventions"]) for f in farmers]
    # scoring = BasicScore(score_configuration=filep + "/" + name_score)
    scoring = BasicScore(score_configuration=name_score)
    # scoring = BasicScore(score_configuration=CURRENT_DIR / name_score)

    rules = BasicRule(
        init_configuration=name_init,
        actions_configuration=name_actions,
        #terminal_CNF_conditions=terminal_CNF_conditions,
        #initial_conditions_values=init_values,
    )

    # DEFINE one policy:
    policies = []

    farm = Farm(
        fields=[field1],
        farmers=ffarmers,
        scoring=scoring,
        rules=rules,
        policies=policies,
    )
    farm.name = name
    return farm


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
                        ("Field-0", "Plant-0", "stage", [(0, 0)]),
                        lambda x: x.value,
                        "in",
                        ["ripe"],
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
                        lambda x: x.value,  # TODO: rather x.value??
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
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["fruit"])]],
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
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["fruit"])]],
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
                        lambda x: x.value % frequency,
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
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["ripe"])]],
        [
            {
                "action": ("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {}),
                "delay": 1,
            }
        ],
    )
    triggered_interventions.append(policy_harvest)
    policy_harvest = (
        [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x.value, "in", ["fruit"])]],
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
                        lambda x: x.value % frequency,
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

    f = make_farm("farm.yaml")
    print(f)
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
    f2 = make_basicfarm(
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
        make_variables_to_be_monitored(
            [
                "f0.soil.available_Water#L",
                "f0.soil.available_N#g",
                "f0.soil.microlife_health_index#%",
                "f0.plant.pollinator_visits#nb",
                "f0.plant.size#cm",
                "f0.plant.flowers_per_plant#nb",
                "f0.plant.flowers_pollinated_per_plant#nb",
                "f0.plant.cumulated_water#L",
                "f0.plant.cumulated_stress_water#L",
                "f0.plant.cumulated_nutrients_N#g",
                "f0.plant.cumulated_stress_nutrients_N#g",
                "f0.plant.fruits_per_plant#nb",
                "f0.plant.fruit_weight#g",
                "f0.weeds.seeds#nb",
                "f0.weeds.grow#nb",
                "f0.weeds.flowers#nb",
                "f0.cide.amount#kg",
                "f0.pests.plot_population#nb",
                "f0.pests.onplant_population#nb[plant]",
                "f0.pests.onplant_population#nb[weeds]",
            ]
        )
    )

    f3 = make_basicfarm(
        "ferttest",
        {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 2, "scale#m": 1.0},
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
    # f3.add_monitoring(
    #     make_monitor(
    #         [
    #             "soil.available_Water#L",
    #             #    "soil.available_N#g",
    #             #    "soil.microlife_health_index#%",
    #             #    "plant.pollinator_visits#nb",
    #             #    "plant.size#cm",
    #             #    "plant.flowers_per_plant#nb",
    #             #    "plant.flowers_pollinated_per_plant#nb",
    #             #    "plant.cumulated_water#L",
    #             #    "plant.cumulated_stress_water#L",
    #             #    "plant.cumulated_nutrients_N#g",
    #             #    "plant.cumulated_stress_nutrients_N#g",
    #             #    "plant.fruits_per_plant#nb",
    #             #    "plant.fruit_weight#g",
    #             #    "weeds.seeds#nb",
    #             #    "weeds.grow#nb",
    #             #    "weeds.flowers#nb",
    #             "weeds.flowers#nb_mat",
    #             "fertilizer.amount#kg",
    #         ]
    #     )
    # )
    f3.add_monitoring(
        make_variables_to_be_monitored(
            [
                "f0.soil.available_Water#L",
                #    "soil.available_N#g",
                #    "soil.microlife_health_index#%",
                #    "plant.pollinator_visits#nb",
                #    "plant.size#cm",
                #    "plant.flowers_per_plant#nb",
                #    "plant.flowers_pollinated_per_plant#nb",
                #    "plant.cumulated_water#L",
                #    "plant.cumulated_stress_water#L",
                #    "plant.cumulated_nutrients_N#g",
                #    "plant.cumulated_stress_nutrients_N#g",
                #    "plant.fruits_per_plant#nb",
                #    "plant.fruit_weight#g",
                #    "weeds.seeds#nb",
                #    "weeds.grow#nb",
                #    "weeds.flowers#nb",
                "f0.weeds.flowers#nb",
                "f0.weeds.flowers#nb.mat",
                "f0.fertilizer.amount#kg.mat",
            ]
        )
    )

    # policy = make_policy_herbicide(0.005, 10, 8)
    # run_policy(f2, policy, max_steps=60, render=True, monitoring=True)

    # policy = make_policy_fertilize(0.5, 10, 2)
    # run_policy(f3, policy, max_steps=60, render=False, monitoring=True)
