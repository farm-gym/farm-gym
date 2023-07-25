from farmgym.v2.farm import Farm
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.field import Field

from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Cide import Cide
from farmgym.v2.entities.Pollinators import Pollinators

from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule


from farmgym.v2.policy_api import Policy_API, Policy_helper, run_policy_xp
import copy
import numpy as np

from plot_utils import plot_results2, plot_results3

# Daily interventios is set to 2 otherwise farmer 
# does not harvest on days where it has another action
def make_basicfarm(name, field, entities, farmers=[{"max_daily_interventions": 2}]):
    # farm_call = " ".join(inspect.stack()[1].code_context[0].split("=")[0].split())
    name = "casestudy/" + name
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


field0 = {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    }

f1 = make_basicfarm(
    "dry_clay_bean", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean")])
f2 = make_basicfarm(
    "dry_sand_bean", field0,
    [(Weather, "dry"), (Soil, "sand"), (Plant, "bean")],
)
f3 = make_basicfarm(
    "dry_clay_corn", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn")],
)
f4 = make_basicfarm(
    "dry_sand_corn", field0,
    [(Weather, "dry"), (Soil, "sand"), (Plant, "corn")],
)
f5 = make_basicfarm(
    "dry_clay_tomato", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato")],
)
f6 = make_basicfarm(
    "dry_sand_tomato", field0,
    [(Weather, "dry"), (Soil, "sand"), (Plant, "tomato")],
)
f7 = make_basicfarm(
    "dry_clay_bean_pollinator", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "bean"), (Pollinators, "bee")]
)
f8 = make_basicfarm(
    "dry_clay_corn_pollinator", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn"), (Pollinators, "bee")],
)
f9 = make_basicfarm(
    "dry_clay_tomato_pollinator", field0,
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato"), (Pollinators, "bee")],
)

ff1 = make_basicfarm(
    "coupling_weeds_pests", field0,
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
    "coupling_weeds_nopests", field0,
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "tomato"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Cide, "herbicide_slow"),
    ]
)

def make_policy_water_harvest(farm, amount_water):
    helper = Policy_helper(farm)
    observe_plant = helper.create_plant_observe()
    water_soil_day1_5l = helper.create_water_soil(amount=amount_water, delay=0)
    harvest_fruit_delay4 = helper.create_harvest_fruit(delay=0)
    policies = [observe_plant, water_soil_day1_5l, harvest_fruit_delay4]
    combined_policy = Policy_API.combine_policies([policy.api for policy in policies])
    return combined_policy 

def make_policy_herbicide(farm, amount_herbicide, frequency, amount_water):
    helper = Policy_helper(farm)
    observe_plant = helper.create_plant_observe()
    weed_observe = helper.create_weed_observe()
    water_soil = helper.create_water_soil(amount=amount_water, delay=0)
    scatter_cide = helper.create_scatter_cide(amount=amount_herbicide,frequency=frequency)
    harvest_ripe = helper.create_harvest_ripe(delay=1)
    harvest_fruit = helper.create_harvest_fruit(delay=18)
    policies = [
        observe_plant,
        weed_observe,
        water_soil,
        scatter_cide,
        harvest_ripe,
        harvest_fruit
    ]
    combined_policy = Policy_API.combine_policies([policy.api for policy in policies])
    return combined_policy 

def xp_coupling():
    farms = [ff1, ff2]

    policy_parameters = [1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0]

    nb_replicate = 10

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            # policy = make_policy_water_harvest(p)
            policy = make_policy_herbicide(f, 1, policy_parameters[p], 8)
            cumrewards = []
            for n in range(nb_replicate):
                # policies = make_policies_water_harvest(policy_parameters)
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                # print(n,":", cr)
                cumrewards.append(cr)
            # print("Mean:", np.mean(cumrewards), "Rewards:", cumrewards)
            results.append({"farm": f.name, "r": cumrewards})
    return farms, policy_parameters, results

def xp_watering():
    farms = [f2, f1, f7, f4, f3, f8, f6, f5, f9]
    policy_parameters = [3.0, 5.0, 8.0, 10.0, 13.0, 15.0]
    nb_replicate = 100
    
    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            policy = make_policy_water_harvest(farm=f, amount_water=policy_parameters[p])
            cumrewards = []
            for n in range(nb_replicate):
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                cumrewards.append(cr)
            results.append({"farm": f.name, "r": cumrewards})
    print(results)
    return farms, policy_parameters, results



#farms, policy_parameters, results = xp_watering()
#plot_results2(farms, policy_parameters, results, "Watering policy (daily input in L)")

# farms,policy_parameters,results = xp_coupling()
# plot_results3(farms,policy_parameters,results,'Herbicide policy (every x day)')


from farmgym.v2.rendering.monitoring import make_variables_to_be_monitored
f1.add_monitoring(make_variables_to_be_monitored(["f0.soil.available_Water#L"]))
policy = make_policy_water_harvest(farm=f1, amount_water=5.)
cr, _ = run_policy_xp(f1, copy.deepcopy(policy), max_steps=150)