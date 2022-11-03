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
    entities1.append((Weather,"montpellier"))
    entities1.append((Soil,"clay"))
    entities1.append((Plant, 'corn'))

    field1 = Field(localization={'latitude#°':43, 'longitude#°':4, 'altitude#m':150},
                  shape={'length#nb':3, 'width#nb':4, 'scale#m': 1.}, entity_managers=entities1)

    entities2 = []
    entities2.append((Weather, "montpellier"))
    entities2.append((Soil, "sand"))
    entities2.append((Plant, 'tomato'))

    field2 = Field(localization={'latitude#°': 43, 'longitude#°': 4, 'altitude#m': 150},
                   shape={'length#nb': 2, 'width#nb': 4, 'scale#m': 0.8}, entity_managers=entities2)

    farmer1 = BasicFarmer(max_daily_interventions=3)
    farmer2 = BasicFarmer(max_daily_interventions=1)
    scoring = BasicScore(score_configuration= CURRENT_DIR / 'farm_score.yaml')

    free_observations = []
    free_observations.append( ("Field-0", "Weather-0", "day#int365", []))
    free_observations.append(("Field-0", "Weather-0", "air_temperature", []))

    terminal_CNF_conditions = [[(("Field-0", "Weather-0", "day#int365", []), lambda x: x.value, ">=", 360)], [(("Field-0","Plant-0","global_stage",[]),lambda x:x.value,"in",["dead", "harvested"])]]
    rules = BasicRule(init_configuration=CURRENT_DIR/'farm_init.yaml',
                      actions_configuration=CURRENT_DIR/'farm_actions.yaml',
                      terminal_CNF_conditions=terminal_CNF_conditions,
                      free_observations=free_observations)

    farm = Farm(fields=[field1,field2], farmers=[farmer1,farmer2], scoring=scoring, rules=rules)
    ##########################################################################

    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions
    run_randomactions(env(), max_steps=5, render=True, monitoring=False)