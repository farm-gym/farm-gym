from farmgym.v2.games.rungame import run_policy, run_policy_xp
import numpy as np
from farmgym.v2.games.rungame import run_xps
import copy

#from farmgym.v2.games.make_farm import make_policy_water_harvest, make_policy_herbicide, make_policy_fertilize

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


import inspect


import yaml
import sys
# env_list=register_all()
# print(env_list)

# env = gym.make(env_list[2],100)
# farm = env.unwrapped

# TODO: We want these farms in dry weather !
# 1. Monitor water in soil: it should decay fast.
# 2. Stop evaporation in clay, not in sand.
# 3. Check that water neeeds are not reached/water stress increases in plant (monitor water stress).
# farm1 = gym.make('farms_1x1_clay_bean-v0').unwrapped
# farm4 = gym.make('farms_1x1_sand_bean-v0').unwrapped
# farm2 = gym.make('farms_1x1_clay_corn-v0').unwrapped
# farm5 = gym.make('farms_1x1_sand_corn-v0').unwrapped
# farm3 = gym.make('farms_1x1_clay_tomato-v0').unwrapped
# farm6 = gym.make('farms_1x1_sand_tomato-v0').unwrapped
# farms = [farm1,farm2,farm3,farm4,farm5,farm6]


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
        # terminal_CNF_conditions=terminal_CNF_conditions,
        # initial_conditions_values=init_values,
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

f1 = make_basicfarm(
    "dry_clay_bean",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean")]
)
f7 = make_basicfarm(
    "dry_clay_bean_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean"), (Pollinators, "bee")]
)
f2 = make_basicfarm(
    "dry_sand_bean",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "sand"), (Plant, "bean")],
)


f3 = make_basicfarm(
    "dry_clay_corn",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn")],
)
f8 = make_basicfarm(
    "dry_clay_corn_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn"), (Pollinators, "bee")],
)
f4 = make_basicfarm(
    "dry_sand_corn",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "sand"), (Plant, "corn")],
    # init_values=[
    #     ("Field-0", "Weather-0", "day#int365", 120),
    #     ("Field-0", "Plant-0", "stage", "seed"),
    #     ("Field-0", "Soil-0", "available_N#g", 2500),
    #     ("Field-0", "Soil-0", "available_P#g", 2500),
    #     ("Field-0", "Soil-0", "available_K#g", 2500),
    #     ("Field-0", "Soil-0", "available_C#g", 2500),
    # ],
)



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
                        lambda x: x,
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
                        lambda x: x,  # TODO: rather x??
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

        policies.append(Policy_API(triggered_observations, triggered_interventions))

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
    p = Policy_API(triggered_observations, triggered_interventions)
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
    p = Policy_API(triggered_observations, triggered_interventions)
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
    p = Policy_API(triggered_observations, triggered_interventions)
    p.reset()
    return p




f5 = make_basicfarm(
    "dry_clay_tomato",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato")],
)
f9 = make_basicfarm(
    "dry_clay_tomato_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato"), (Pollinators, "bee")],
)
f6 = make_basicfarm(
    "dry_sand_tomato",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "sand"), (Plant, "tomato")],
)


ff1 = make_basicfarm(
    "coupling_weeds_pests",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "tomato"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Pests, "basic"),
        (Cide, "herbicide_slow"),
    ]
)

ff2 = make_basicfarm(
    "coupling_weeds_nopests",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "tomato"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Cide, "herbicide_slow"),
    ]
)


def xp_watering():
    farms = [f2, f1, f7, f4, f3, f8, f6, f5, f9]
    # farms = [f5,f9]
    # farms=[ff1,ff2]
    nb_f = len(farms)

    # policy_parameters= [0.,0.25,0.5,1.,2,5, 10, 20]
    policy_parameters = [0.0, 0.25, 0.5, 1.0, 2, 5]
    # policy_herbicide_parameters= [0.,0.1,0.5,2,4]
    # policy_herbicide_parameters= [1,2,3,4,5]
    nb_pol = len(policy_parameters)

    nb_replicate = 100

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            policy = make_policy_water_harvest(p)
            # policy = make_policy_herbicide(8.,p,0.2)
            cumrewards = []
            for n in range(nb_replicate):
                # policies = make_policies_water_harvest(policy_parameters)
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                # print(n,":", cr)
                cumrewards.append(cr)
            # print("Mean:", np.mean(cumrewards), "Rewards:", cumrewards)
            results.append({"farm": f.name, "r": cumrewards})
    return farms, policy_parameters, results

    # policies = make_policies_water_harvest([0., 0.5, 1., 2, 4, 8])
    # for policy in policies:
    #  cumrewards, cumcosts = run_xps(f, policy, max_steps=200, nb_replicate=40)
    #  #print("Mean:",np.mean(cumrewards), "Rewards:", cumrewards)
    #  results.append({"farm":f.name, "r":cumrewards})

    # print(results)


def xp_coupling():
    farms = [ff1, ff2]

    policy_parameters = [2, 3, 4, 6, 10, 12, 15, 20]

    nb_replicate = 100

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            # policy = make_policy_water_harvest(p)
            policy = make_policy_herbicide(0.005, policy_parameters[p], 8)
            cumrewards = []
            for n in range(nb_replicate):
                # policies = make_policies_water_harvest(policy_parameters)
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                # print(n,":", cr)
                cumrewards.append(cr)
            # print("Mean:", np.mean(cumrewards), "Rewards:", cumrewards)
            results.append({"farm": f.name, "r": cumrewards})
    return farms, policy_parameters, results


def plot_results(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    nb_f = len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]
    # names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc = (int)(np.ceil(np.sqrt(nb_f)))
    nr = nb_f // nc
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1))

    axes = mat_axes.flatten()

    i = 0
    bplots = []
    for j in range(nb_f):
        # rectangular box plot
        bplots.append(
            axes[j].boxplot(
                all_data[i : i + nb_pol],
                notch=True,  # notch shape
                vert=True,  # vertical box alignment
                patch_artist=True,  # fill with color
                labels=labels[i : i + nb_pol],
            )
        )  # will be used to label x-ticks
        axes[j].set_title(names[j])
        axes[j].set_ylabel("Rewards")
        axes[j].set_xlabel(title)
        axes[j].yaxis.grid(True)
        axes[j].set_ylim([0, 150])
        i += nb_pol

    # fill with colors
    # colors = ['pink', 'lightblue', 'lightgreen']
    # for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig("fig.pdf")
    plt.savefig("fig.png")


import matplotlib.pyplot as plt


def box_plot(ax, data, labels, edge_color, fill_color, hatch):
    bp = ax.boxplot(data, patch_artist=True, labels=labels, notch=True)

    for element in ["boxes", "whiskers", "fliers", "means", "medians", "caps"]:
        plt.setp(bp[element], color=edge_color)

    for patch in bp["boxes"]:
        patch.set(facecolor=fill_color)
        patch.set(hatch=hatch)

    return bp


def plot_results2(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    nb_f = len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]
    # names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc = 3
    nr = 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1))

    axes = mat_axes.flatten()

    i = 4 * nb_pol
    bp1 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 3 * nb_pol
    bp2 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ["clay", "sand"])
    axes[0].set_title("Sand vs Clay (corn)")
    axes[0].set_ylabel("Rewards")
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 150])

    i = 1 * nb_pol
    bp1 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 2 * nb_pol
    bp2 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[1].legend([bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"])
    axes[1].set_title("Pollinators in beans")
    axes[1].set_ylabel("Rewards")
    axes[1].set_xlabel(title)
    axes[1].yaxis.grid(True)
    axes[1].set_ylim([0, 150])

    i = 4 * nb_pol
    bp1 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 5 * nb_pol
    bp2 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[2].legend([bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"])
    axes[2].set_title("Pollinators in corn")
    axes[2].set_ylabel("Rewards")
    axes[2].set_xlabel(title)
    axes[2].yaxis.grid(True)
    axes[2].set_ylim([0, 150])

    # fill with colors
    # colors = ['pink', 'lightblue', 'lightgreen']
    # for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig("fig.pdf")
    plt.savefig("fig.png")


def plot_results3(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    nb_f = len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]
    # names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc = 2
    nr = 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1))

    axes = mat_axes.flatten()

    i = 0 * nb_pol
    bp1 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 1 * nb_pol
    bp2 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1.0, 0.8),
        ".",
    )

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ["pests", "no pests"])
    axes[0].set_title("Weeds without vs with pests")
    axes[0].set_ylabel("Rewards")
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 150])

    # fill with colors
    # colors = ['pink', 'lightblue', 'lightgreen']
    # for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig("fig.pdf")
    plt.savefig("fig.png")


farms, policy_parameters, results = xp_watering()
plot_results2(farms, policy_parameters, results, "Watering policy (daily input in L)")


# farms,policy_parameters,results = xp_coupling()
# plot_results3(farms,policy_parameters,results,'Herbicide policy (every x day)')


#print(f1)
