from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.policy_api import Policy_API

from farmgym.v2.rendering.monitoring import mat2d_value, sum_value


from gym.envs.registration import register

import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent


def env():
    ##########################################################################
    entities1 = []
    entities1.append((Weather, "lille"))
    entities1.append((Soil, "clay"))
    entities1.append((Plant, "bean"))
    # entities1.append((Weeds,"base_weed"))

    field1 = Field(
        localization={"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        shape={"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        entity_managers=entities1,
    )

    farmer1 = BasicFarmer(max_daily_interventions=1)
    scoring = BasicScore(score_configuration=CURRENT_DIR / "farm_score.yaml")

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
        init_configuration=CURRENT_DIR / "farm_init.yaml",
        actions_configuration=CURRENT_DIR / "farm_actions.yaml",
        terminal_CNF_conditions=terminal_CNF_conditions,
        free_observations=free_observations,
    )

    # DEFINE one policy:
    policies = []
    for i in range(10):
        triggered_observations = []
        trigger_constant = [[]]
        action_schedule_observe = [
            ("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)])
        ]
        triggered_observations.append((trigger_constant, action_schedule_observe))

        triggered_interventions = []
        # trigger_water = [[(("Field-0", "Plant-0", "stage", [(0, 0)]), lambda x: x, "in", ["entered_grow","entered_bloom","entered_fruit","entered_ripe"])]]

        trigger_harvest = [
            [
                (
                    ("Field-0", "Plant-0", "stage", [(0, 0)]),
                    lambda x: x,
                    "in",
                    ["fruit", "entered_ripe", "ripe"],
                )
            ]
        ]
        # or age_ripe#day =  3
        action_harvest = [("BasicFarmer-0", "Field-0", "Plant-0", "harvest", {})]
        triggered_interventions.append((trigger_harvest, action_harvest))

        trigger_water = [[]]
        action_water = []
        if i > 0:
            action_water = [
                (
                    "BasicFarmer-0",
                    "Field-0",
                    "Soil-0",
                    "water_discrete",
                    {"plot": (0, 0), "amount#L": i, "duration#min": 60},
                )
            ]
        triggered_interventions.append((trigger_water, action_water))

        policies.append(Policy_API("", triggered_observations, triggered_interventions))

    farm = Farm(
        fields=[field1],
        farmers=[farmer1],
        scoring=scoring,
        rules=rules,
        policies=policies,
    )

    ##########################################################################

    var = []
    # var.append(("Field-0", "Soil-0", "available_N#g", lambda x:mat2d_value(x,field1.shape['length#nb'],field1.shape['width#nb']), "Available N (g)", 'range_auto'))
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
    # var.append(("Field-0", "Weeds-0", "seeds#nb", lambda x:sum_value(x), "Weeds  grow (nb)", 'range_auto'))
    # var.append(("Field-0", "Weeds-0", "grow#nb", lambda x:sum_value(x), "Weeds  grow (nb)", 'range_auto'))
    farm.add_monitoring(var)
    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions

    # run_randomactions(env(),max_steps=100,render=False, monitoring=True)
    run_randomactions(env(), max_steps=60, render=True, monitoring=False)
