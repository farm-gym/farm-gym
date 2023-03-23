from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant

from farmgym.v2.rendering.monitoring import mat2d_value, sum_value

import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
CURRENT_DIR = file_path.parent


def env():
    ##########################################################################
    entities1 = []
    entities1.append((Weather, "montpellier"))
    entities1.append((Soil, "sand"))
    entities1.append((Plant, "bean"))

    field1 = Field(
        localization={"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        shape={"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
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

    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions

    run_randomactions(env(), max_steps=100, render=True, monitoring=False)
