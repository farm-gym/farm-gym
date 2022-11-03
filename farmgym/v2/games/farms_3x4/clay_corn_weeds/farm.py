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
    entities1.append((Weather,"lille"))
    entities1.append((Soil,"clay"))
    entities1.append((Plant, 'corn'))

    entities1.append((Weeds,"base_weed"))
    entities1.append((Cide,"herbicide"))

    field1 = Field(localization={'latitude#°':43, 'longitude#°':4, 'altitude#m':150},
                  shape={'length#nb':4, 'width#nb':3, 'scale#m': 1.}, entity_managers=entities1)

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
    var.append(("Field-0", "Cide-0", "amount#kg", lambda x:sum_value(x), "Amount Cide (kg)", 'range_auto'))
    var.append(("Field-0", "Weeds-0", "grow#nb", lambda x:sum_value(x), "Weeds  grow (nb)", 'range_auto'))



    farm.add_monitoring(var)

    return farm


if __name__ == "__main__":
    from farmgym.v2.games.rungame import run_randomactions
    run_randomactions(env(), max_steps=100, render=True, monitoring=False)