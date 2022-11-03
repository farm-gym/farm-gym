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
    entities1.append((Soil,"loam"))
    entities1.append((Plant, 'tomato'))

    field1 = Field(localization={'latitude#°':43, 'longitude#°':4, 'altitude#m':150},
                  shape={'length#nb':1, 'width#nb':1, 'scale#m': 1.}, entity_managers=entities1)

    farmer1 = BasicFarmer(max_daily_interventions=1)
    scoring = BasicScore(score_configuration= CURRENT_DIR / 'farm_score.yaml')

    free_observations = []
    free_observations.append( ("Field-0", "Weather-0", "day#int365", []))
    free_observations.append(("Field-0", "Weather-0", "air_temperature", []))

    terminal_CNF_conditions = [[(("Field-0", "Weather-0", "day#int365", []), lambda x: x.value, ">=", 360)], [(("Field-0","Plant-0","global_stage",[]),lambda x:x.value,"in",["dead", "harvested"])]]
    rules = BasicRule(init_configuration=CURRENT_DIR/'farm_init.yaml',
                      actions_configuration=CURRENT_DIR/'farm_actions.yaml',
                      terminal_CNF_conditions=terminal_CNF_conditions,
                      free_observations=free_observations)

    farm = Farm(fields=[field1], farmers=[farmer1], scoring=scoring, rules=rules)
    ##########################################################################

    var = []
    #var.append(("Field-0", "Soil-0", "available_N#g", lambda x:mat2d_value(x,field1.shape['length#nb'],field1.shape['width#nb']), "Available N (g)", 'range_auto'))
    var.append(("Field-0", "Weather-0", "air_temperature", lambda x:x["mean#°C"].value, "Air Temperature (°C)", 'range_auto'))
    var.append(("Field-0", "Weather-0", "humidity_index#%", lambda x:x.value, "Humidity index (%)", 'range_auto'))
    var.append(("Field-0", "Weather-0", "rain_intensity", lambda x:x.value, "Rain intensity", 'range_auto'))
    var.append(("Field-0", "Soil-0", "available_N#g", lambda x:sum_value(x), "Available Nitrogen (g)", 'range_auto'))
    var.append(("Field-0", "Soil-0", "available_Water#L", lambda x:sum_value(x), "Available Water (L)", 'range_auto'))
    var.append(("Field-0", "Soil-0", "microlife_health_index#%", lambda x:sum_value(x), "Microlife Health (%)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "size#cm", lambda x:sum_value(x), "Size (cm)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "flowers_per_plant#nb", lambda x:sum_value(x), "Flowers (nb)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "flowers_pollinated_per_plant#nb", lambda x:sum_value(x), "Flowers pollinated (nb)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "fruits_per_plant#nb", lambda x:sum_value(x), "Fruits (nb)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "fruit_weight#g", lambda x:sum_value(x), "Fruit weight (g)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "cumulated_stress_water#L", lambda x:sum_value(x), "Cumulated stress water (L)", 'range_auto'))
    var.append(("Field-0", "Plant-0", "cumulated_stress_nutrients_N#g", lambda x:sum_value(x), "Cumulated stress N (g)", 'range_auto'))



    farm.add_monitoring(var)
    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions
    run_randomactions(env(), max_steps=100, render=False, monitoring=True)