
import farmgym

from farmgym.v2.farm import Farm
from farmgym.v2.field import Field
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.scorings.BasicScore import BasicScore
from farmgym.v2.rules.BasicRule import BasicRule
#from farmgym.v2.policy_api import Policy_API
import inspect

import yaml
import sys


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
    name_score = name + "_" + farm_yaml["score"]
    name_init = name + "_" + farm_yaml["initialization"]
    name_actions = name + "_" + farm_yaml["actions"]

    scoring = BasicScore(score_configuration=name_score)


    rules = BasicRule(
        init_configuration=name_init,
        actions_configuration=name_actions
    )

    farm = Farm(fields=fields, farmers=farmers, scoring=scoring, rules=rules, policies=[], interaction_mode=interaction_mode)
    return farm



