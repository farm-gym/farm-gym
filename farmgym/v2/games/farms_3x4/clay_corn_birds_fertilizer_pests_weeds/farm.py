from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant


from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Facilities import Facility
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Pollinators import Pollinators
from farmgym.v2.entities.Cide import Cide

from farmgym.v2.rendering.monitoring import mat2d_value, sum_value

import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent


def env():
    ##########################################################################
    entities1 = []
    entities1.append((Weather, "montpellier"))
    entities1.append((Soil, "clay"))
    entities1.append((Plant, "corn"))

    entities1.append((Birds, "base_bird"))
    entities1.append((Facility, "base_facility"))

    entities1.append((Fertilizer, "basic_N"))

    entities1.append((Pests, "basic"))
    entities1.append((Pollinators, "bee"))
    entities1.append((Cide, "pesticide"))

    entities1.append((Weeds, "base_weed"))
    entities1.append((Cide, "herbicide"))

    field1 = Field(
        localization={"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        shape={"length#nb": 4, "width#nb": 3, "scale#m": 1.0},
        entities_specifications=entities1,
    )

    farmer1 = BasicFarmer(max_daily_interventions=1)
    scoring = BasicScore(score_configuration=CURRENT_DIR / "farm_score.yaml")


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
        terminal_CNF_conditions=terminal_CNF_conditions
    )

    farm = Farm(fields=[field1], farmers=[farmer1], scoring=scoring, rules=rules)
    ##########################################################################

    var = []
    var.append(
        (
            "Field-0",
            "Weather-0",
            "air_temperature",
            lambda x: x["min#°C"].value,
            "Min air temperature (°C)",
            "range_auto",
        )
    )
    var.append(
        (
            "Field-0",
            "Weather-0",
            "air_temperature",
            lambda x: x["mean#°C"].value,
            "Mean air temperature (°C)",
            "range_auto",
        )
    )
    var.append(
        (
            "Field-0",
            "Weather-0",
            "air_temperature",
            lambda x: x["max#°C"].value,
            "Max air temperature (°C)",
            "range_auto",
        )
    )
    var.append(
        (
            "Field-0",
            "Pests-0",
            "plot_population#nb",
            lambda x: x[(0, 0)].value,
            "Insects (nb)",
            "range_auto",
        )
    )
    var.append(
        (
            "Field-0",
            "Plant-0",
            "stage",
            lambda x: x[(0, 0)].gym_value(),
            "Stage",
            "range_auto",
        )
    )
    farm.add_monitoring(var)
    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions

    run_randomactions(env(), max_steps=100, render=True, monitoring=False)
