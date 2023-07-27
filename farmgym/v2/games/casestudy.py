import copy

from farmgym.v2.entities.Cide import Cide
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Pollinators import Pollinators
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.policy_api import Policy_API, Policy_helper, run_policy_xp

from utils import make_basicfarm, plot_coupling_results, plot_watering_results

f1 = make_basicfarm(
    "dry_clay_bean",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean")],
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
f4 = make_basicfarm(
    "dry_sand_corn",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "sand"), (Plant, "corn")],
)

f5 = make_basicfarm(
    "dry_clay_tomato",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato")],
)
f6 = make_basicfarm(
    "dry_sand_tomato",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "sand"), (Plant, "tomato")],
)
f7 = make_basicfarm(
    "dry_clay_bean_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean"), (Pollinators, "bee")],
)


f8 = make_basicfarm(
    "dry_clay_corn_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn"), (Pollinators, "bee")],
)
f9 = make_basicfarm(
    "dry_clay_tomato_pollinator",
    {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    },
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato"), (Pollinators, "bee")],
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
    ],
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
    ],
)


def make_policy_water_harvest(farm, amounts):
    helper = Policy_helper(farm)
    observe_plant = helper.create_plant_observe()
    water_soil_day1_5l = helper.create_water_soil_continious(amount=amounts, delay=0)
    harvest_ripe = helper.create_harvest_ripe(delay=1)
    harvest_fruit = helper.create_harvest_fruit(delay=18)
    policies = [observe_plant, water_soil_day1_5l, harvest_ripe, harvest_fruit]
    combined_policy = Policy_API.combine_policies([policy.api for policy in policies])
    return combined_policy


def make_policy_herbicide(farm, amount_herbicide, frequency, amount_water):
    helper = Policy_helper(farm)
    observe_plant = helper.create_plant_observe()
    weed_observe = helper.create_weed_observe()
    water_soil = helper.create_water_soil_continious(amount=amount_water, delay=0)
    scatter_cide = helper.create_scatter_cide(amount=amount_herbicide, frequency=frequency, threshold=0)
    harvest_ripe = helper.create_harvest_ripe(delay=1)
    harvest_fruit = helper.create_harvest_fruit(delay=18)
    policies = [observe_plant, weed_observe, water_soil, scatter_cide, harvest_ripe, harvest_fruit]
    combined_policy = Policy_API.combine_policies([policy.api for policy in policies])
    return combined_policy


def xp_coupling(cide_amount, water_amount):
    farms = [ff1, ff2]

    policy_parameters = [2.0, 4.0, 6.0, 10.0, 12.0, 15.0, 20.0]
    scale = 12.5
    nb_replicate = 100

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            policy = make_policy_herbicide(f, cide_amount, policy_parameters[p], water_amount)
            cumrewards = []
            for n in range(nb_replicate):
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                cr /= scale
                cumrewards.append(cr)
            results.append({"farm": f.name, "r": cumrewards})
    return farms, policy_parameters, results


def xp_watering():
    farms = [f1, f2, f3, f4, f5, f6, f7, f8, f9]
    policy_parameters = [0.0, 0.25, 0.5, 1.0, 2, 5]
    scale = 15
    nb_replicate = 100

    results = []
    for idx, f in enumerate(farms):
        for p in range(len(policy_parameters)):
            policy = make_policy_water_harvest(farm=f, amounts=policy_parameters[p])
            cumrewards = []
            for n in range(nb_replicate):
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                cr /= scale
                cumrewards.append(cr)
            results.append({"farm": f.name, "r": cumrewards})
    return farms, policy_parameters, results


farms, policy_parameters, results = xp_watering()
plot_watering_results(farms, policy_parameters, results, "Watering policy (daily input in L)")

farms, policy_parameters, results = xp_coupling(0.0015, 5)
plot_coupling_results(farms, policy_parameters, results, "Herbicide policy (every x day)", "fname")