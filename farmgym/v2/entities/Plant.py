import logging

import numpy as np
from PIL import Image

from farmgym.v2.entities.Weather import irradiance_perday

from farmgym.v2.entity_api import (
    Entity_API,
    Range,
    checkissubclass,
    expglm,
    expglmnoisy,
    fillarray,
)

logger = logging.getLogger()


def increase(value, rate, valuemax):
    return min(value + rate * (1.0 - value / valuemax) * np.sqrt(value), valuemax)


class Plant(Entity_API):
    stages = [
        "none",
        "seed",
        "entered_grow",
        "grow",
        "entered_bloom",
        "bloom",
        "entered_fruit",
        "fruit",
        "entered_ripe",
        "ripe",
        "entered_seed",
        "harvested",
        "dead",
    ]

    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y
        # TODO: Make sure that we consider a population of plants on each plot, not just one plent: Check that flowers/fruits/etc is coherent. some plants die or all die exact same state?
        self.variables = {}

        # TODO : Strange, it seems all values in array get assigned same value = ref (hence changing (0,0) change all values): We  should initialize differently to indeed have different ojects, not same ref. IS IT STILL THE CASE?
        self.variables["stage"] = fillarray(X, Y, self.stages, "none")
        self.variables["global_stage"] = Range(self.stages + ["undefined"], "none")
        self.variables["population#nb"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["size#cm"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["flowers_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["pollinator_visits#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["flowers_pollinated_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["fruits_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["fruit_weight#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["harvest_weight#kg"] = Range((0, 1000000), 0.0)
        # TODO: ADD day_afer_planting#day
        self.variables["age_seed#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["consecutive_nogrow#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["age_bloom#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["consecutive_noweight#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["age_ripe#day"] = fillarray(X, Y, (0, 100), 0.0)

        self.variables["cumulated_nutrients_N#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_nutrients_P#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_nutrients_K#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["cumulated_nutrients_C#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["cumulated_stress_nutrients_N#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_P#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_K#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_C#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_water#L"] = fillarray(X, Y, (0, 10000), 0.0)

        self.variables["grow_size_threshold#cm"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["fruit_weight_threshold#g"] = fillarray(X, Y, (0, 100000), 0.0)

        self.debug_death_info = np.empty((X, Y), dtype=dict)
        for xx in range(X):
            for yy in range(Y):
                self.debug_death_info[xx, yy] = {}

        # Actions
        self.actions = {
            "sow": {
                "plot": field.plots,
                "amount#seed": [1, 3, 5, 10, 15, 20, 25, 30],
                "spacing#cm": [5, 10, 15, 20],
            },
            "harvest": {},
            "micro_harvest": {"plot": field.plots},
            "remove": {"plot": field.plots},
        }

        # Dependencies
        self.dependencies = {"Weather", "Soil", "Birds", "Pests", "Pollinators"}

    def get_parameter_keys(self):
        return [
            "initial_stage",
            "size_max#cm",
            "flowers_max#nb",
            "fruit_weight_max#g",
            "pest_repulsive_effect#float",
            "shadow_coeff#%",
            "seed_conditions",
            "grow_conditions",
            "bloom_conditions",
            "fruit_conditions",
            "ripe_conditions",
            "death_conditions",
        ]

    def reset(self):
        X = self.field.X
        Y = self.field.Y

        self.variables["stage"] = fillarray(X, Y, self.stages, "none")
        self.variables["global_stage"] = Range(self.stages + ["undefined"], "none")
        self.variables["population#nb"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["size#cm"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["flowers_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["pollinator_visits#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["flowers_pollinated_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["fruits_per_plant#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["fruit_weight#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["harvest_weight#kg"] = Range((0, 1000000), 0.0)

        self.variables["age_seed#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["consecutive_nogrow#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["age_bloom#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["consecutive_noweight#day"] = fillarray(X, Y, (0, 100), 0.0)
        self.variables["age_ripe#day"] = fillarray(X, Y, (0, 100), 0.0)

        self.variables["cumulated_nutrients_N#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_nutrients_P#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_nutrients_K#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["cumulated_nutrients_C#g"] = fillarray(X, Y, (0, 100000), 0.0)
        self.variables["cumulated_stress_nutrients_N#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_P#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_K#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_nutrients_C#g"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["cumulated_stress_water#L"] = fillarray(X, Y, (0, 10000), 0.0)

        self.variables["grow_size_threshold#cm"] = fillarray(X, Y, (0, 10000), 0.0)
        self.variables["fruit_weight_threshold#g"] = fillarray(X, Y, (0, 100000), 0.0)

        ## Init stage:
        for x in range(X):
            for y in range(Y):
                if self.parameters["initial_stage"] in Plant.stages:
                    self.variables["stage"][x, y].set_value(self.parameters["initial_stage"])
                elif self.parameters["initial_stage"] == "random":
                    self.variables["stage"][x, y].set_value(self.np_random.choice(Plant.stages))
                else:
                    self.variables["stage"][x, y].set_value("none")

                if self.variables["stage"][x, y].value == "none":
                    self.variables["population#nb"][x, y].set_value(0)
                    self.variables["size#cm"][x, y].set_value(0)
                elif self.variables["stage"][x, y].value == "seed":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(0)
                elif self.variables["stage"][x, y].value == "entered_grow":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(0.1)
                elif self.variables["stage"][x, y].value == "grow":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.np_random.random() * self.parameters["size_max#cm"]
                    )
                elif self.variables["stage"][x, y].value == "entered_bloom":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(self.parameters["size_max#cm"])
                    self.variables["flowers_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )
                elif self.variables["stage"][x, y].value == "bloom":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                    self.variables["flowers_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )
                elif self.variables["stage"][x, y].value == "entered_fruit":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                    self.variables["flowers_pollinated_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )
                    self.variables["fruits_per_plant#nb"][x, y].set_value(
                        self.variables["flowers_pollinated_per_plant#nb"][x, y]
                    )
                    self.variables["fruit_weight#g"][x, y].set_value(1)
                elif self.variables["stage"][x, y].value == "fruit":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                    self.variables["fruits_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )

                    self.variables["fruit_weight#g"][x, y].set_value(
                        self.np_random.random() * self.parameters["fruit_weight_max#g"]
                    )
                elif self.variables["stage"][x, y].value == "entered_ripe":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                    self.variables["fruits_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )
                    self.variables["fruit_weight#g"][x, y].set_value(
                        self.parameters["fruit_weight_max#g"]
                    )
                elif self.variables["stage"][x, y].value == "ripe":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                    self.variables["fruits_per_plant#nb"][x, y].set_value(
                        self.np_random.binomial(
                            self.parameters["flowers_max#nb"],
                            self.variables["size#cm"][x, y].value
                            / self.parameters["size_max#cm"],
                            1,
                        )[0]
                    )

                    self.variables["fruit_weight#g"][x, y].set_value(
                        self.parameters["fruit_weight_max#g"]
                    )
                elif self.variables["stage"][x, y].value == "entered_seed":
                    self.variables["population#nb"][x, y].set_value(1)
                    self.variables["size#cm"][x, y].set_value(
                        self.parameters["size_max#cm"]
                    )
                elif self.variables["stage"][x, y].value == "dead":
                    self.variables["population#nb"][x, y].set_value(0)

                self.variables["cumulated_nutrients_N#g"][x, y].set_value(
                    self.variables["size#cm"][x, y].value
                    * self.parameters["grow_conditions"]["N_grow_consumption#g.mm-1"]
                    * 10
                )
                self.variables["cumulated_nutrients_P#g"][x, y].set_value(
                    self.variables["size#cm"][x, y].value
                    * self.parameters["grow_conditions"]["P_grow_consumption#g.mm-1"]
                    * 10
                )
                self.variables["cumulated_nutrients_K#g"][x, y].set_value(
                    self.variables["size#cm"][x, y].value
                    * self.parameters["grow_conditions"]["K_grow_consumption#g.mm-1"]
                    * 10
                )
                self.variables["cumulated_nutrients_C#g"][x, y].set_value(
                    self.variables["size#cm"][x, y].value
                    * self.parameters["grow_conditions"]["C_grow_consumption#g.mm-1"]
                    * 10
                )

        self.initialize_variables(self.initial_conditions)
        ## Init global stage:
        self.compute_globalstage()

    def is_active(self, position):
        return self.variables["stage"][position].value not in [
            "none",
            "seed",
            "harvested",
            "dead",
        ]

    def compute_globalstage(self):
        ## Init global stage:
        X = self.field.X
        Y = self.field.Y
        unique, counts = np.unique(
            [self.variables["stage"][x, y].value for x in range(X) for y in range(Y)],
            return_counts=True,
        )
        d = dict(zip(unique, counts))
        stage = max(d, key=d.get)
        if d[stage] > 0.75 * X * Y:
            self.variables["global_stage"].set_value(stage)
        else:
            self.variables["global_stage"].set_value("undefined")

    def update_variables(self, field, entities):
        ######################################

        # TODO: Add that plant stores Nitrogen into soil?

        weather = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Weather")
        ][0]
        soil = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Soil")
        ][0]
        birds = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Birds")
        ]
        nb_birds_eating_seeds = np.sum(
            [
                b.variables["population#nb"].value
                for b in birds
                if b.parameters["seed_eater"]
            ]
        )
        pests = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Pests")
        ]
        pollinators = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Pollinators")
        ]
        for x in range(self.field.X):
            for y in range(self.field.Y):
                if self.variables["population#nb"][x, y].value > 0:
                    # if (self.is_active((x,y))):

                    total_stress = 0
                    total_stress += self.variables["cumulated_stress_nutrients_N#g"][x, y].value
                    total_stress += self.variables["cumulated_stress_nutrients_P#g"][x, y].value
                    total_stress += self.variables["cumulated_stress_nutrients_K#g"][x, y].value
                    total_stress += self.variables["cumulated_stress_nutrients_C#g"][x, y].value
                    total_stress += (self.variables["cumulated_stress_water#L"][x, y].value * 1000)

                    for n in ["N", "K", "P", "C"]:
                        self.variables["cumulated_stress_nutrients_"+n+"#g"][x, y].set_value(
                            self.variables["cumulated_stress_nutrients_"+n+"#g"][x, y].value*(1-self.parameters["stress_healing#%"])
                        )
                    self.variables["cumulated_stress_water#L"][x, y].set_value(
                        self.variables["cumulated_stress_water#L"][x, y].value * (1 - self.parameters["stress_healing#%"])
                    )

                    if self.variables["stage"][x, y].value == "entered_grow":
                        self.variables["size#cm"][x, y].set_value(0.1)
                        self.variables["consecutive_nogrow#day"][x, y].set_value(0.0)
                        self.variables["stage"][x, y].set_value("grow")
                    elif self.variables["stage"][x, y].value == "entered_bloom":

                        p = self.parameters["bloom_conditions"]
                        q = []
                        q.append(
                            (
                                p["sensitivity_stress"],
                                total_stress,
                                -np.infty,
                                0,
                            )
                        )
                        p_boost = 1.-expglm(0, q)

                        self.variables["flowers_per_plant#nb"][x, y].set_value(
                            self.np_random.binomial(
                                self.parameters["flowers_max#nb"]*(1+p["stress_boost#%"]*p_boost),
                                self.variables["size#cm"][x, y].value
                                / self.parameters["size_max#cm"],
                                1,
                            )[0]
                        )
                        self.variables["age_bloom#day"][x, y].set_value(0.0)
                        self.variables["pollinator_visits#nb"][x, y].set_value(0.0)
                        self.variables["stage"][x, y].set_value("bloom")
                    elif self.variables["stage"][x, y].value == "entered_fruit":
                        self.variables["consecutive_noweight#day"][x, y].set_value(0.0)
                        self.variables["fruits_per_plant#nb"][x, y].set_value(
                            self.variables["flowers_pollinated_per_plant#nb"][x, y].value
                        )
                        self.variables["flowers_per_plant#nb"][x, y].set_value(0)
                        self.variables["flowers_pollinated_per_plant#nb"][x, y].set_value(0)
                        self.variables["fruit_weight#g"][x, y].set_value(1)
                        self.variables["stage"][x, y].set_value("fruit")
                    elif self.variables["stage"][x, y].value == "entered_ripe":
                        self.variables["age_ripe#day"][x, y].set_value(0.0)
                        self.variables["stage"][x, y].set_value("ripe")

                    elif self.variables["stage"][x, y].value in ["seed"]:
                        self.debug_death_info[x, y] = {}
                        total_stress = 0
                        for n in ["N", "K", "P", "C"]:
                            self.variables["cumulated_nutrients_" + n + "#g"][x, y].set_value(0)
                            self.variables["cumulated_stress_nutrients_" + n + "#g"][x, y].set_value(0)

                            self.variables["cumulated_stress_water#L"][x, y].set_value(0)
                            p = self.parameters["seed_conditions"]

                            q = []
                            q.append(
                                (
                                    p["sensitivity_death_birds"],
                                    nb_birds_eating_seeds,
                                    0,
                                    p["death_birds_max#nb"],
                                )
                            )
                            q.append(
                                (
                                    p["sensitivity_death_ageseed"],
                                    self.variables["age_seed#day"][x, y].value,
                                    0,
                                    p["death_ageseed_max#day"],
                                )
                            )
                            p_stayalive = expglm(p["sensitivity_death_0"], q)
                            # print("SEED STAY ALIVE",p_stayalive,q)
                            # w_stayalive = np.exp( -glm([p['sensitivity_death_0'],p['sensitivity_death_birds_max'],p['sensitivity_death_ageseed_max']],[nb_birds_eating_seeds,age_seed],[(0,p['death_birds_max']),(0,p['death_ageseed_max'])])) # in [0,1] : proba_death = 1-w_life

                            is_dead = self.np_random.binomial(1, p_stayalive, 1)[0] == 0
                            if is_dead:
                                self.debug_death_info[x, y] = {"stage": self.variables["stage"][x, y].value, "p": p_stayalive, "q": q}
                                logger.debug(
                                    "[FarmGym] DEATH CAUSE:"
                                    + str((x, y))
                                    + str(self.debug_death_info[x, y])
                                )
                                self.variables["stage"][x, y].set_value("dead")

                            else:
                                q = []
                                q.append(
                                    (
                                        p["sensitivity_sprout_air_temperature"],
                                        weather.variables["air_temperature"][
                                            "mean#°C"
                                        ].value,
                                        p["sprout_air_temperature_min#°C"],
                                        p["sprout_air_temperature_max#°C"],
                                    )
                                )
                                q.append(
                                    (
                                        p["sensitivity_sprout_humidity"],
                                        weather.variables["humidity#%"].value,
                                        p["sprout_humidity_min#%"],
                                        p["sprout_humidity_max#%"],
                                    )
                                )
                                q.append(
                                    (
                                        p["sensitivity_sprout_age"],
                                        self.variables["age_seed#day"][x, y].value,
                                        p["sprout_age_min#day"],
                                        np.infty,
                                    )
                                )

                                p_sprout = expglm(p["sensitivity_sprout_0"], q)
                                # w_sprout = np.exp(- glm([p['sensitivity_sprout_0'], p['sensitivity_sprout_T'], p['sensitivity_sprout_RH']], [T, RH], [(p['sprout_T_min'], p['sprout_T_max']), (
                                # p['sprout_RH_min'], p['sprout_RH_max'])]))  # \in [0,1] proba_sprout = w_sprout.
                                # print("P_SPROUT", p_sprout, q)

                                is_sprouting = (self.np_random.binomial(1, p_sprout, 1)[0] == 1)
                                if is_sprouting:
                                    self.variables["stage"][x, y].set_value("entered_grow")
                                else:
                                    self.variables["age_seed#day"][x, y].set_value(self.variables["age_seed#day"][x, y].value + 1)

                    elif self.variables["stage"][x, y].value in ["grow"]:
                        # TODO: Add that plants turn atmospheric N2 into soil, injecting N in it and C in their body, hence release C when dead.
                        p = self.parameters["grow_conditions"]

                        # Sun power in kWh/m2:
                        sun_power = irradiance_perday(field.localization["longitude#°"], weather.variables["day#int365"].value) * (1.-weather.variables["clouds#%"].value / 100)
                        # sun power received by plant in kWh:
                        # sun_power *= self.parameters["grow_conditions"]["grow_leaf_surface#m2.cm-1"]* self.variables["size#cm"][(x,y)].value

                        q = []
                        q.append(
                            (
                                p["sensitivity_grow_Energy"],
                                sun_power,
                                p["grow_Energy_opt#kWh.m-2"],
                                np.infty,
                            )
                        )
                        #print("SUN POWER", sun_power, p["grow_Energy_opt#kWh.m-2"])
                        q.append(
                            (
                                p["sensitivity_grow_air_temperature"],
                                weather.variables["air_temperature"]["mean#°C"].value,
                                p["grow_air_temperature_min#°C"],
                                p["grow_air_temperature_max#°C"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_grow_N"],
                                self.variables["cumulated_stress_nutrients_N#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_grow_K"],
                                self.variables["cumulated_stress_nutrients_K#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_grow_P"],
                                self.variables["cumulated_stress_nutrients_P#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_grow_C"],
                                self.variables["cumulated_stress_nutrients_C#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_grow_Water"],
                                self.variables["cumulated_stress_water#L"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        draught = p["sensitivity_draught#%"]
                        w = (
                            (
                                (1.0 - draught) * soil.parameters["wilting_point#L.m-3"]
                                + draught * soil.parameters["max_water_capacity#L.m-3"]
                            )
                            * soil.parameters["depth#m"]
                            * self.field.plotsurface
                        )
                        q.append(
                            (
                                p["sensitivity_grow_Water"],
                                soil.variables["available_Water#L"][(x, y)].value,
                                w,
                                np.infty,
                            )
                        )
                        #print("DRAUGHT", soil.variables["available_Water#L"][(x, y)].value, w)

                        rate = max(
                            0.0,
                            expglmnoisy(
                                p["sensitivity_grow_0"],
                                q,
                                p["grow_rate_sigma2"],
                                np_random=self.np_random,
                            ),
                        )

                        is_growing = rate >= p["grow_rate_min#"]
                        if is_growing:
                            newsize = increase(
                                self.variables["size#cm"][x, y].value,
                                rate,
                                self.parameters["size_max#cm"],
                            )

                            self.variables["size#cm"][x, y].set_value(newsize)
                            self.variables["consecutive_nogrow#day"][x, y].set_value(0)
                        else:
                            self.variables["consecutive_nogrow#day"][x, y].set_value(
                                self.variables["consecutive_nogrow#day"][x, y].value + 1
                            )


                        self.variables["grow_size_threshold#cm"][x, y].set_value(
                            self.parameters["size_max#cm"]
                            * (1 + np.exp(-total_stress / 1000))
                            / 2.0
                        )

                        # Grow-Bloom
                        q = []
                        q.append(
                            (
                                1.0,
                                self.variables["size#cm"][x, y].value,
                                self.variables["grow_size_threshold#cm"][x, y].value,
                                np.infty,
                            )
                        )
                        p_bloom = expglm(0.0, q)
                        is_blooming = self.np_random.binomial(1, p_bloom, 1)[0] == 1
                        if is_blooming:
                            self.variables["stage"][x, y].set_value("entered_bloom")

                        # Grow-Death
                        q = []
                        nb_pests = np.sum(
                            [
                                p.variables["onplant_population#nb"][self.name][
                                    x, y
                                ].value
                                for p in pests
                                if self.name
                                in p.variables["onplant_population#nb"].keys()
                            ]
                        )
                        q.append(
                            (
                                p["sensitivity_death_pests"],
                                nb_pests,
                                0,
                                p["death_pests_max#nb"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_death_nogrow"],
                                self.variables["consecutive_nogrow#day"][x, y].value,
                                0,
                                p["death_nogrow_max#day"],
                            )
                        )
                        p_stayalive = expglm(p["sensitivity_death_0"], q)

                        is_dead = self.np_random.binomial(1, p_stayalive, 1)[0] == 0
                        if is_dead:
                            self.debug_death_info[x, y] = {"stage": self.variables["stage"][x, y].value,
                                                           "p": p_stayalive, "q": q}
                            logger.debug(
                                "[FarmGym] DEATH CAUSE:"
                                + str((x, y))
                                + str(self.debug_death_info[x, y])
                            )
                            self.variables["stage"][x, y].set_value("dead")

                    elif self.variables["stage"][x, y].value in ["bloom"]:
                        p = self.parameters["bloom_conditions"]


                        #TODO: Add growth probability? to decide if growth day or not-growth day, hence decide death proba.





                        non_pollinated = max(
                            self.variables["flowers_per_plant#nb"][x, y].value
                            - self.variables["flowers_pollinated_per_plant#nb"][x, y].value,
                            0,
                        )

                        w = []
                        w.append(p["auto_pollination_rate#%"])
                        w.append(p["wind_pollination_rate#%"])
                        w.append(p["insect_pollination_rate#%"])
                        W = np.sum(w)
                        w = w / W

                        # Wind conditions:
                        q = []
                        q.append(
                            (
                                p["sensitivity_wind_air_temperature"],
                                weather.variables["air_temperature"]["mean#°C"].value,
                                p["wind_air_temperature_min#°C"],
                                p["wind_air_temperature_max#°C"],
                            )
                        )

                        q.append(
                            (
                                p["sensitivity_wind_speed"],
                                weather.variables["wind"]["speed#km.h-1"].value,
                                p["wind_speed_min#km.h-1"],
                                p["wind_speed_max#km.h-1"],
                            )
                        )
                        wind_pollination_success = expglm(p["sensitivity_wind_0"], q)

                        # Pollinator conditions:
                        for po in pollinators:
                            if po.variables["occurrence#bin"][x, y].value == "True":
                                self.variables["pollinator_visits#nb"][x, y].set_value(
                                    self.variables["pollinator_visits#nb"][x, y].value + 1
                                )
                        q = []
                        q.append(
                            (
                                p["sensitivity_pollinator_visits"],
                                self.variables["pollinator_visits#nb"][x, y].value,
                                p["pollinator_visits_min#nb"],
                                np.infty,
                            )
                        )
                        insect_pollination_success = expglm(p["sensitivity_pollinator_0"], q)

                        pp = (
                            w[0] * p["auto_pollination_success#%"]
                            + w[1] * wind_pollination_success
                            + w[2] * insect_pollination_success
                        )
                        # print("POLLINATION INSECT",insect_pollination_success, pp)
                        self.variables["flowers_pollinated_per_plant#nb"][x, y].set_value(
                            self.variables["flowers_pollinated_per_plant#nb"][x, y].value
                            + np.floor(
                                self.np_random.binomial(non_pollinated, pp, 1)[0]
                            )
                        )
                        #                                                                + np.floor(
                        # w[0]*self.np_random.binomial(non_pollinated, p['auto_pollination_success#%'],1)[0] + w[1] *
                        # self.np_random.binomial(non_pollinated, wind_pollination_success, 1)[0]
                        # + w[2] * self.np_random.binomial(non_pollinated, insect_pollination_success, 1)[0]))

                        self.variables["age_bloom#day"][x, y].set_value(
                            self.variables["age_bloom#day"][x, y].value + 1
                        )


                        # Bloom-Fruit
                        q = []
                        q.append(
                            (
                                1.0,
                                self.variables["age_bloom#day"][x, y].value,
                                p["bloom_duration#day"],
                                np.infty,
                            )
                        )
                        p_fruit = expglm(0.0, q)
                        is_fruiting = self.np_random.binomial(1, p_fruit, 1)[0] == 1
                        if is_fruiting:
                            self.variables["stage"][x, y].set_value("entered_fruit")

                        # Bloom-Death
                        q = []
                        q.append(
                            (
                                p["sensitivity_death_frost"],
                                weather.variables["consecutive_frost#day"].value,
                                0,
                                p["death_frost_max#day"],
                            )
                        )
                        p_stayalive = expglm(p["sensitivity_death_0"], q)

                        is_dead = self.np_random.binomial(1, p_stayalive, 1)[0] == 0
                        if is_dead:
                            self.debug_death_info[x, y] = {"stage": self.variables["stage"][x, y].value,
                                                           "p": p_stayalive, "q": q}
                            logger.debug(
                                "[FarmGym] DEATH CAUSE:"
                                + str((x, y))
                                + str(self.debug_death_info[x, y])
                            )
                            self.variables["stage"][x, y].set_value("dead")

                    elif self.variables["stage"][x, y].value in ["fruit"]:
                        p = self.parameters["fruit_conditions"]


                        # Sun power in kWh/m2:
                        sun_power = irradiance_perday(field.localization["longitude#°"], weather.variables["day#int365"].value) * (1.-weather.variables["clouds#%"].value / 100)
                        # sun power received by plant in kWh:
                        # sun_power *= self.parameters["grow_conditions"]["grow_leaf_surface#m2.cm-1"]* self.variables["size#cm"][(x,y)].value

                        q = []
                        q.append(
                            (
                                p["sensitivity_fruit_Energy"],
                                sun_power,
                                p["fruit_Energy_opt#kWh.m-2"],
                                np.infty,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_air_temperature"],
                                weather.variables["air_temperature"]["mean#°C"].value,
                                p["fruit_air_temperature_min#°C"],
                                p["fruit_air_temperature_max#°C"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_N"],
                                self.variables["cumulated_stress_nutrients_N#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_K"],
                                self.variables["cumulated_stress_nutrients_K#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_P"],
                                self.variables["cumulated_stress_nutrients_P#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_C"],
                                self.variables["cumulated_stress_nutrients_C#g"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_Water"],
                                self.variables["cumulated_stress_water#L"][(x, y)].value,
                                -np.infty,
                                0,
                            )
                        )
                        draught = p["sensitivity_draught#%"]
                        w = (
                            (
                                (1.0 - draught) * soil.parameters["wilting_point#L.m-3"]
                                + draught * soil.parameters["max_water_capacity#L.m-3"]
                            )
                            * soil.parameters["depth#m"]
                            * self.field.plotsurface
                        )
                        q.append(
                            (
                                p["sensitivity_fruit_Water"],
                                soil.variables["available_Water#L"][(x, y)].value,
                                w,
                                np.infty,
                            )
                        )
                        rate = max(
                            0.0,
                            expglmnoisy(
                                p["sensitivity_fruit_0"],
                                q,
                                p["fruit_rate_sigma2"],
                                np_random=self.np_random,
                            ),
                        )
                        #print("Fruit rate", rate, q)

                        qq = []
                        qq.append(
                            (
                                p["sensitivity_fruit_pollinators"],
                                self.variables["pollinator_visits#nb"][x, y].value,
                                p["fruit_pollinators_min#nb"],
                                np.infty,
                            )
                        )
                        qq.append(
                            (
                                p["sensitivity_fruit_stress"],
                                total_stress / 1000,
                                -np.infty,
                                0.0,
                            )
                        )
                        self.variables["fruit_weight_threshold#g"][x, y].set_value(
                            self.parameters["fruit_weight_max#g"] * expglm(0, qq)
                        )

                        is_weighting = rate >= p["weight_rate_min#"]
                        if is_weighting:
                            newweigth = increase(
                                self.variables["fruit_weight#g"][x, y].value,
                                rate,
                                self.parameters["fruit_weight_max#g"],
                            )
                            self.variables["fruit_weight#g"][x, y].set_value(newweigth)
                            self.variables["consecutive_noweight#day"][x, y].set_value(
                                0
                            )
                        else:
                            self.variables["consecutive_noweight#day"][x, y].set_value(
                                self.variables["consecutive_noweight#day"][x, y].value
                                + 1
                            )

                        # Fruit-Ripe
                        q = []
                        q.append(
                            (
                                1.0,
                                self.variables["fruit_weight#g"][x, y].value,
                                self.variables["fruit_weight_threshold#g"][x, y].value,
                                np.infty,
                            )
                        )
                        p_ripe = expglm(0.0, q)
                        is_ripe = self.np_random.binomial(1, p_ripe, 1)[0] == 1
                        if is_ripe:
                            self.variables["stage"][x, y].set_value("entered_ripe")

                        # Fruit-Death
                        q = []
                        # print("PESTS",[p for p in pests])
                        nb_pests = np.sum(
                            [
                                p.variables["onplant_population#nb"][self.name][
                                    x, y
                                ].value
                                for p in pests
                                if self.name
                                in p.variables["onplant_population#nb"].keys()
                            ]
                        )
                        # print("PESTS",nb_pests)
                        q.append(
                            (
                                p["sensitivity_death_pests"],
                                nb_pests,
                                0,
                                p["death_pests_max#nb"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_death_humidity"],
                                weather.variables["humidity#%"].value,
                                p["death_humidity_min#%"],
                                p["death_humidity_max#%"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_death_noweight"],
                                self.variables["consecutive_noweight#day"][x, y].value,
                                -np.infty,
                                p["death_noweight_max#day"],
                            )
                        )
                        p_stayalive = expglm(p["sensitivity_death_0"], q)
                        is_dead = self.np_random.binomial(1, p_stayalive, 1)[0] == 0
                        if is_dead:
                            self.debug_death_info[x, y] = {"stage": self.variables["stage"][x, y].value,
                                                           "p": p_stayalive, "q": q}
                            logger.debug(
                                "[FarmGym] DEATH CAUSE:"
                                + str((x, y))
                                + str(self.debug_death_info[x, y])
                            )
                            self.variables["stage"][x, y].set_value("dead")

                    elif self.variables["stage"][x, y].value in ["ripe"]:
                        p = self.parameters["ripe_conditions"]

                        q = []
                        q.append(
                            (
                                p["sensitivity_ripe_air_temperature"],
                                weather.variables["air_temperature"]["mean#°C"].value,
                                p["ripe_air_temperature_min#°C"],
                                p["ripe_air_temperature_max#°C"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_ripe_rain"],
                                weather.variables["rain_amount#mm.day-1"].value,
                                -np.infty,
                                0.0,
                            )
                        )
                        # [print("PESTS",p) for p in pests]
                        nb_pests = np.sum(
                            [
                                p.variables["onplant_population#nb"][self.name][
                                    x, y
                                ].value
                                for p in pests
                                if self.name
                                in p.variables["onplant_population#nb"].keys()
                            ]
                        )

                        q.append(
                            (p["sensitivity_ripe_pests"], nb_pests, -np.infty, 0.0)
                        )
                        q.append(
                            (
                                p["sensitivity_ripe_frost"],
                                weather.variables["consecutive_frost#day"].value,
                                0,
                                p["ripe_frost_max#day"],
                            )
                        )
                        q.append(
                            (
                                p["sensitivity_ripe_age"],
                                self.variables["age_ripe#day"][x, y].value,
                                0,
                                p["ripe_age_max#day"],
                            )
                        )
                        # q.append((p['sensitivity_death_humidity'], weather.variables['humidity#%'].value, p['death_humidity_min'], p['death_humidity_max']))
                        rate = min(
                            max(
                                0.0,
                                expglmnoisy(
                                    p["sensitivity_ripe_0"],
                                    q,
                                    p["ripe_rate_sigma2"],
                                    np_random=self.np_random,
                                ),
                            ),
                            1.0,
                        )
                        # print(q,rate)

                        # TODO: generate seeds?
                        self.variables["fruits_per_plant#nb"][x, y].set_value(
                            np.floor(
                                rate * self.variables["fruits_per_plant#nb"][x, y].value
                            )
                        )
                        self.variables["age_ripe#day"][x, y].set_value(
                            self.variables["age_ripe#day"][x, y].value + 1
                        )

                        # Ripe-Death
                        if self.variables["fruits_per_plant#nb"][x, y].value == 0:
                            self.debug_death_info[x, y] = {"stage": self.variables["stage"][x, y].value,
                                                           "fruits": self.variables["fruits_per_plant#nb"][x, y].value}
                            logger.debug(
                                "[FarmGym] DEATH CAUSE:" 
                                + str((x, y)) 
                                + str(self.debug_death_info[x, y])
                            )
                            self.variables["stage"][x, y].set_value("dead")

                    elif self.variables["stage"][x, y].value in ["harvested"]:
                        for n in ["N", "K", "P", "C"]:
                            self.variables["cumulated_nutrients_" + n + "#g"][x, y].set_value(0)
                            self.variables["cumulated_stress_nutrients_" + n + "#g"][x, y].set_value(0)

                        self.variables["cumulated_stress_water#L"][x, y].set_value(0)

                    elif self.variables["stage"][x, y].value in ["dead"]:
                        self.variables["fruits_per_plant#nb"][x, y].set_value(0)
                        threshold = 0.1
                        # Dead-None
                        if (
                            (self.variables["cumulated_nutrients_N#g"][x, y].value <= threshold)
                            and (
                                self.variables["cumulated_nutrients_P#g"][x, y].value
                                <= threshold
                            )
                            and (
                                self.variables["cumulated_nutrients_K#g"][x, y].value
                                <= threshold
                            )
                            and (
                                self.variables["cumulated_nutrients_C#g"][x, y].value
                                <= threshold
                            )
                        ):
                            self.variables["stage"][x, y].set_value("none")

        # Update global_stage as being most present stage
        self.compute_globalstage()

    def act_on_variables(self, action_name, action_params):
        def act_on_variables(self, action_name, action_params):
            """
            Apply a specific action to plant variables.

            Parameters:
            - action_name (str): The name of the action to be applied.
            - action_params (dict): Parameters specific to the action.

            Actions and their effects:
            - "harvest":
                - Harvest all ripe fruits from the entire field.
                - Effects:
                    - Updates the harvest weight based on the fruits harvested.
                    - Resets the number of fruits per plant and sets their stage to "harvested".

            - "micro_harvest":
                - Harvest ripe fruits from a specific plot.
                - Parameters:
                    - "plot" (tuple): Coordinates (x, y) of the plot.
                - Effects:
                    - Updates the harvest weight based on the fruits harvested.
                    - Resets the number of fruits per plant and sets their stage to "harvested".

            - "sow":
                - Sow seeds in a specific plot.
                - Parameters:
                    - "plot" (tuple): Coordinates (x, y) of the plot.
                    - "amount#seed" (float): Amount of seeds to sow.
                - Effects:
                    - Sets the population, stage, and age of the seed in the specified plot.
                    - Only has effects if the plant is absent or in seed stage.

            - "remove":
                - Remove a plant from a specific plot.
                - Parameters:
                    - "plot" (tuple): Coordinates (x, y) of the plot.
                - Effects:
                    - Resets all plant variables in the specified plot to initial values.

            - Updates the global stage based on the most present stage in the entire field.

            Raises:
            - AssertionError: If the action or its parameters are invalid.
            """
            # Method implementation goes here

        self.assert_action(action_name, action_params)
        if action_name == "harvest":
            self.variables["harvest_weight#kg"].set_value(0)
            for x in range(self.field.X):
                for y in range(self.field.Y):
                    if self.variables["stage"][x, y].value in [
                        "entered_fruit",
                        "fruit",
                        "ripe",
                        "entered_ripe",
                    ]:
                        # if (self.variables['stage'][x,y].value in ['ripe','entered_ripe']):
                        self.variables["harvest_weight#kg"].set_value(
                            self.variables["harvest_weight#kg"].value
                            + self.variables["fruits_per_plant#nb"][x, y].value
                            * self.variables["fruit_weight#g"][x, y].value
                            / 1000.0
                        )
                        self.variables["fruits_per_plant#nb"][x, y].set_value(0.0)
                        self.variables["stage"][x, y].set_value("harvested")

        elif action_name == "micro_harvest":
            position = action_params["plot"]

            if self.variables["stage"][position].value in [
                "entered_fruit",
                "fruit",
                "ripe",
                "entered_ripe",
            ]:
                value = (
                    self.variables["fruits_per_plant#nb"][position].value
                    * self.variables["fruit_weight#g"][position].value
                    / 1000.0
                )
                self.variables["fruits_per_plant#nb"][position].set_value(0.0)
                self.variables["stage"][position].set_value("harvested")
                self.variables["harvest_weight#kg"].set_value(
                    self.variables["harvest_weight#kg"].value + value
                )
        elif action_name == "sow":
            position = action_params["plot"]
            if self.variables["stage"][position].value in ["none", "seed"]:
                self.variables["population#nb"][position].set_value(
                    action_params["amount#seed"]
                )
                self.variables["stage"][position].set_value("seed")
                self.variables["age_seed#day"][position].set_value(0)

        elif action_name == "remove":
            position = action_params["plot"]
            self.variables["stage"][position].set_value("none")
            self.variables["population#nb"][position].set_value(0)
            self.variables["size#cm"][position].set_value(0)
            self.variables["flowers_per_plant#nb"][position].set_value(0)
            self.variables["pollinator_visits#nb"][position].set_value(0)
            self.variables["flowers_pollinated_per_plant#nb"][position].set_value(0)
            self.variables["fruits_per_plant#nb"][position].set_value(0)
            self.variables["fruit_weight#g"][position].set_value(0)

            self.variables["age_seed#day"][position].set_value(0)
            self.variables["consecutive_nogrow#day"][position].set_value(0)
            self.variables["age_bloom#day"][position].set_value(0)
            self.variables["consecutive_noweight#day"][position].set_value(0)
            self.variables["age_ripe#day"][position].set_value(0)

            self.variables["cumulated_nutrients_N#g"][position].set_value(0)
            self.variables["cumulated_nutrients_P#g"][position].set_value(0)
            self.variables["cumulated_nutrients_K#g"][position].set_value(0)
            self.variables["cumulated_nutrients_C#g"][position].set_value(0)
            self.variables["cumulated_stress_nutrients_N#g"][position].set_value(0)
            self.variables["cumulated_stress_nutrients_P#g"][position].set_value(0)
            self.variables["cumulated_stress_nutrients_K#g"][position].set_value(0)
            self.variables["cumulated_stress_nutrients_C#g"][position].set_value(0)
            self.variables["cumulated_stress_water#L"][position].set_value(0)

            self.variables["grow_size_threshold#cm"][position].set_value(0)
            self.variables["fruit_weight_threshold#g"][position].set_value(0)

        # Update global_stage as being most present stage
        self.compute_globalstage()

    def requirement_nutrients(self, position):
        """
        return nutrients requirement in g
        """
        r = {"N": 0.0, "K": 0.0, "P": 0.0, "C": 0.0}  #'Water':(0.,1.)}
        if not self.is_active(position):
            return r
        for n in ["N", "K", "P", "C"]:
            if self.variables["stage"][position].value in [
                "entered_grow",
                "grow",
                "entered_bloom",
                "bloom",
                "entered_fruit",
                "fruit",
            ]:
                r[n] += (
                    self.variables["size#cm"][position].value* 10
                    * self.parameters["grow_conditions"][n + "_grow_consumption#g.mm-1"]
                )
            if self.variables["stage"][position].value in ["entered_bloom", "bloom"]:
                r[n] += (
                    self.variables["flowers_per_plant#nb"][position].value
                    * self.parameters["bloom_conditions"][n + "_flower_consumption#g"]
                )
            if self.variables["stage"][position].value in ["entered_fruit", "fruit"]:
                r[n] += (
                    self.variables["fruits_per_plant#nb"][position].value
                    * self.variables["fruit_weight#g"][position].value
                    * self.parameters["fruit_conditions"][n + "_fruit_consumption#g.g-1"]
                )
            r[n] *= self.variables["population#nb"][position].value
        return r

    def requirement_water(self, position, weather, field):
        """
        return water requirement in mL
        """
        if not self.is_active(position):
            return 0
        w = (
            weather.evaporation(field) # Evaporation in mL.m-2.day-1
            * self.parameters["grow_conditions"]["grow_leaf_surface#m2.cm-1"]
            * self.variables["size#cm"][position].value
        )
        if self.variables["stage"][position].value in ["entered_grow", "grow"]:
            w += self.parameters["grow_conditions"]["Water_grow_consumption#mL"]
        if self.variables["stage"][position].value in ["entered_bloom", "bloom"]:
            w += (self.variables["flowers_per_plant#nb"][position].value
                * self.parameters["bloom_conditions"]["Water_flower_consumption#mL"]
            )

        if self.variables["stage"][position].value in ["entered_fruit", "fruit"]:
            w += (self.variables["fruits_per_plant#nb"][position].value
                * self.parameters["fruit_conditions"]["Water_fruit_consumption#mL.g-1"]
                * self.variables["fruit_weight#g"][position].value
            )

        w = w * self.variables["population#nb"][position].value
        return w


    def receive_nutrients(self, position, nutrients, stress):
        if self.is_active(position):
            self.variables["cumulated_nutrients_C#g"][position].set_value(
                self.variables["cumulated_nutrients_C#g"][position].value
                + nutrients["C#g"]
            )
            self.variables["cumulated_nutrients_N#g"][position].set_value(
                self.variables["cumulated_nutrients_N#g"][position].value
                + nutrients["N#g"]
            )
            self.variables["cumulated_nutrients_P#g"][position].set_value(
                self.variables["cumulated_nutrients_P#g"][position].value
                + nutrients["P#g"]
            )
            self.variables["cumulated_nutrients_K#g"][position].set_value(
                self.variables["cumulated_nutrients_K#g"][position].value
                + nutrients["K#g"]
            )
            self.variables["cumulated_stress_nutrients_C#g"][position].set_value(
                self.variables["cumulated_stress_nutrients_C#g"][position].value
                + stress["C#g"]
            )
            self.variables["cumulated_stress_nutrients_N#g"][position].set_value(
                self.variables["cumulated_stress_nutrients_N#g"][position].value
                + stress["N#g"]
            )
            self.variables["cumulated_stress_nutrients_P#g"][position].set_value(
                self.variables["cumulated_stress_nutrients_P#g"][position].value
                + stress["P#g"]
            )
            self.variables["cumulated_stress_nutrients_K#g"][position].set_value(
                self.variables["cumulated_stress_nutrients_K#g"][position].value
                + stress["K#g"]
            )

    def receive_water(self, position, water, stress):
        if self.is_active(position):
            # print("WATER RECEIVED", water, stress)
            self.variables["cumulated_stress_water#L"][position].set_value(
                self.variables["cumulated_stress_water#L"][position].value + stress
            )

    def release_nutrients(self, position, soil):
        r = {"N#g": 0.0, "K#g": 0.0, "P#g": 0.0, "C#g": 0.0}  # 'Water':(0.,1.)}
        if self.variables["stage"][position].value in ["dead"]:
            for n in ["N", "K", "P", "C"]:
                # TODO: Use total nutrients received and release as function of soil_microlife_health_index in [0,1]?
                r[n + "#g"] = (
                    self.variables["cumulated_nutrients_" + n + "#g"][position].value
                    * self.parameters["death_conditions"][
                        n + "_release_speed#g.g-1.day-1"
                    ]
                    * (soil.variables["microlife_health_index#%"][position].value / 100)
                    * self.variables["population#nb"][position].value
                )
                self.variables["cumulated_nutrients_" + n + "#g"][position].set_value(
                    max(
                        0,
                        self.variables["cumulated_nutrients_" + n + "#g"][
                            position
                        ].value
                        - r[n + "#g"],
                    )
                )
        elif self.is_active(position):
            p = self.parameters["grow_conditions"]
            nb = self.variables["population#nb"][position].value
            r["N#g"] = (
                nb
                * p["N_air_storage#g.mm-1"]
                * self.variables["size#cm"][position].value
                * 10
            )
            r["C#g"] = (
                nb
                * p["C_air_storage#g.mm-1"]
                * self.variables["size#cm"][position].value
                * 10
            )
        return r

    def compute_shadowsurface(self, position):
        # returns shadow effective size in m2
        if self.is_active(position):
            # Consider a plant is a ball of diameter size#cm
            r = self.variables["size#cm"][position].value * 0.01 / 2.0
            return (
                np.pi * r * r * self.variables["population#nb"][position].value
            )  * self.parameters['shadow_coeff#%']
        return 0

    def to_fieldimage(self):
        im_width, im_height = 64, 64
        image = Image.new(
            "RGBA",
            (im_width * self.field.X, im_height * self.field.Y),
            (255, 255, 255, 0),
        )
        for x in range(self.field.X):
            for y in range(self.field.Y):
                if self.variables["population#nb"][x, y].value > 0:
                    image.paste(
                        self.images[self.variables["stage"][x, y].value],
                        (im_width * x, im_height * y),
                    )
        return image


def to_image(stages, images):
    X, Y = np.shape(stages)
    im_width, im_height = 64, 64
    image = Image.new("RGBA", (im_width * X, im_height * Y), (255, 255, 255, 0))
    for x in range(X):
        for y in range(Y):
            image.paste(
                images[stages[x, y].value],
                (im_width * x, im_height * y),
                mask=images[stages[x, y].value],
            )
    return image
