from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Pollinators import Pollinators
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Weeds import Weeds


def reward_stagetransition(entities_list: list):
    r_stage = 0
    for e in entities_list:
        if issubclass(e.__class__, Plant):
            if "entered_" in e.variables["global_stage"].value:
                if e.variables["global_stage"].value != "entered_death":
                    r_stage += 1

    return r_stage


def reward_stagecount(entities_list: list):
    plants = [e for e in entities_list if issubclass(e.__class__, Plant)]
    r_stage = 0
    for p in plants:
        rr = 0
        for x in range(p.field.X):
            for y in range(p.field.Y):
                if p.variables["stage"][x, y].value == "sprout":
                    rr += 2.0
                elif p.variables["stage"][x, y].value == "grow":
                    rr += (
                        p.variables["size#cm"][x, y].value / p.parameters["size_max#cm"]
                    )

                elif p.variables["stage"][x, y].value == "flower":
                    rr += (
                        p.variables["nb_pollinated_flowers"][x, y].value
                        / p.parameters["nb_flowers"]
                    )
                elif p.variables["stage"][x, y].value == "fruit":
                    rr += (
                        p.variables["fruit_weight#g"][x, y].value
                        / p.parameters["fruit_weight_max#g"]
                    )

        r_stage += rr / (p.field.X * p.field.Y)

    return r_stage


def reward_soilmicrolife(entities_list: list):
    soils = [e for e in entities_list if issubclass(e.__class__, Soil)]
    r = 0
    for s in soils:
        # from farmgym.v2.rendering.monitoring import sum_value
        # ml = sum_value(e.variables["microlife_health_index#%"]) / 100.
        X, Y = s.variables["microlife_health_index#%"].shape
        for x in range(X):
            for y in range(Y):
                if s.variables["microlife_health_index#%"][x, y].value < 10:
                    r -= 2
    return r


def reward_biodiversitycounts(entities_list: list):
    birds = [e for e in entities_list if issubclass(e.__class__, Birds)]
    pests = [e for e in entities_list if issubclass(e.__class__, Pests)]
    pollinators = [e for e in entities_list if issubclass(e.__class__, Pollinators)]
    weeds = [e for e in entities_list if issubclass(e.__class__, Weeds)]

    r_bio = 0
    for b in birds:
        r_bio += b.variables["total_cumulated_birds#nb"].value
    for p in pests:
        r_bio += p.variables["total_cumulated_plot_population#nb"].value * 0.01
    for p in pollinators:
        r_bio += p.variables["total_cumulated_occurrence#nb"].value * 0.5
    for w in weeds:
        r_bio += w.variables["total_cumulated_plot_population#nb"].value * 0.1
    return r_bio


def reward_resourceadded(entities_list: list):
    ferts = [e for e in entities_list if issubclass(e.__class__, Fertilizer)]
    soil = [e for e in entities_list if issubclass(e.__class__, Soil)]

    r_resource = 0
    for f in ferts:
        r_resource -= f.variables["total_cumulated_scattered_amount#kg"].value
    for s in soil:
        r_resource -= s.variables["total_cumulated_added_water#L"].value
        r_resource -= (
            s.variables["total_cumulated_added_cide#g"]["pollinators"].value * 0.001
        )
        r_resource -= s.variables["total_cumulated_added_cide#g"]["pests"].value * 0.001
        r_resource -= s.variables["total_cumulated_added_cide#g"]["soil"].value * 0.001
        r_resource -= s.variables["total_cumulated_added_cide#g"]["weeds"].value * 0.001
    return r_resource


def reward_harvest(entities_list: list):
    plants = [e for e in entities_list if issubclass(e.__class__, Plant)]
    r_harvest = 0.0
    for p in plants:
        r_harvest += p.variables["harvest_weight#kg"].value * 1000
    return r_harvest
