import numpy as np
from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, checkissubclass, expglm, fillarray


class Soil(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["available_N#g"] = fillarray(
            X, Y, (0, 10000), 100 * self.field.plotsurface
        )  # 100 g/m3
        self.variables["available_P#g"] = fillarray(
            X, Y, (0, 10000), 100 * self.field.plotsurface
        )
        self.variables["available_K#g"] = fillarray(
            X, Y, (0, 10000), 100 * self.field.plotsurface
        )
        self.variables["available_C#g"] = fillarray(
            X, Y, (0, 10000), 100 * self.field.plotsurface
        )
        self.variables["available_Water#L"] = fillarray(
            X, Y, (0, 10000), 1 * self.field.plotsurface
        )  # 1 L/m3

        self.variables["wet_surface#m2.day-1"] = fillarray(X, Y, (0, 1000), 0.0)

        self.variables["microlife_health_index#%"] = fillarray(X, Y, (0, 100), 75)

        self.variables["amount_cide#g"] = {
            "pollinators": fillarray(X, Y, (0, 10000), 0.0),
            "pests": fillarray(X, Y, (0, 10000), 0.0),
            "soil": fillarray(X, Y, (0, 10000), 0.0),
            "weeds": fillarray(X, Y, (0, 10000), 0.0),
        }

        #
        self.variables["total_cumulated_added_water#L"] = Range((0, 100000), 0.0)
        self.variables["total_cumulated_added_cide#g"] = {
            "pollinators": Range((0, 100000), 0.0),
            "pests": Range((0, 100000), 0.0),
            "soil": Range((0, 100000), 0.0),
            "weeds": Range((0, 100000), 0.0),
        }

        # Actions
        self.actions = {
            "water_discrete": {
                "plot": field.plots,
                "amount#L": list(np.linspace(1, 15, 15)),
                "duration#min": [30, 60],
            },
            "water_continuous": {
                "plot": field.plots,
                "amount#L": (0.0, 20.0),
                "duration#min": [30, 60],
            },
        }

        # Dependencies
        self.dependencies = {"Plant", "Weather"}

    def get_parameter_keys(self):
        return [
            "max_water_capacity#L.m-3",
            "depth#m",
            "wilting_point#L.m-3",
            "water_surface_absorption_speed#m2.day-1",
            "bedrocks_release_N#mg.day-1",
            "bedrocks_release_K#mg.day-1",
            "bedrocks_release_P#mg.day-1",
            "bedrocks_release_C#mg.day-1",
        ]

    def reset(self):
        # Generate a random soil
        for x in range(self.field.X):
            for y in range(self.field.Y):
                self.variables["available_N#g"][x, y].set_value(
                    self.np_random.random() * 100 * self.field.plotsurface
                )
                self.variables["available_P#g"][x, y].set_value(
                    self.np_random.random() * 100 * self.field.plotsurface
                )
                self.variables["available_K#g"][x, y].set_value(
                    self.np_random.random() * 100 * self.field.plotsurface
                )
                self.variables["available_C#g"][x, y].set_value(
                    self.np_random.random() * 100 * self.field.plotsurface
                )
                self.variables["available_Water#L"][x, y].set_value(
                    (0.5 + 0.5 * self.np_random.random())
                    * self.parameters["max_water_capacity#L.m-3"]
                    * self.field.plotsurface
                    * self.parameters["depth#m"]
                )
                self.variables["wet_surface#m2.day-1"][x, y].set_value(
                    0
                )  # self.np_random.rand()*self.field.plotsurface
                self.variables["microlife_health_index#%"][x, y].set_value(100)
                self.variables["amount_cide#g"]["pollinators"][x, y].set_value(0)
                self.variables["amount_cide#g"]["pests"][x, y].set_value(0)
                self.variables["amount_cide#g"]["soil"][x, y].set_value(0)
                self.variables["amount_cide#g"]["weeds"][x, y].set_value(0)
        self.variables["total_cumulated_added_water#L"].set_value(0.0)
        # self.variables["total_cumulated_added_pesticide#g"] = 0.
        # self.variables["total_cumulated_added_herbicide#g"] = 0.
        self.variables["total_cumulated_added_cide#g"]["pollinators"].set_value(0.0)
        self.variables["total_cumulated_added_cide#g"]["pests"].set_value(0.0)
        self.variables["total_cumulated_added_cide#g"]["soil"].set_value(0.0)
        self.variables["total_cumulated_added_cide#g"]["weeds"].set_value(0.0)
        self.initialize_variables(self.initial_conditions)

    def update_variables(self, field, entities):
        max_water_plot_capacity = (
            self.parameters["max_water_capacity#L.m-3"]
            * self.field.plotsurface
            * self.parameters["depth#m"]
        )

        # plants = [entities[e] for e in entities if issubclass(entities[e].__class__,Plant)]
        plants = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Plant")
        ]
        weather = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Weather")
        ][0]
        fertilizers = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Fertilizer")
        ]
        weeds = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Weeds")
        ]
        cides = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Cide")
        ]

        for x in range(self.field.X):
            for y in range(self.field.Y):
                water_surplus = 0
                # Natural water input (rain)
                if weather.variables["rain_amount"].value == "Light":
                    # TODO : Water afte rinput = actuel + precipation
                    water_after_input = (
                        self.variables["available_Water#L"][x, y].value
                        + 0.5 * self.np_random.random() * max_water_plot_capacity
                    )
                    self.variables["available_Water#L"][x, y].set_value(
                        min(max_water_plot_capacity, water_after_input)
                    )
                    water_surplus = (
                        water_after_input
                        - self.variables["available_Water#L"][x, y].value
                    )
                    self.variables["wet_surface#m2.day-1"][x, y].set_value(
                        self.field.plotsurface
                    )
                elif weather.variables["rain_amount"].value == "Heavy":
                    water_after_input = (
                        self.variables["available_Water#L"][x, y].value
                        + max_water_plot_capacity
                    )
                    self.variables["available_Water#L"][x, y].set_value(
                        max_water_plot_capacity
                    )
                    water_surplus = (
                        water_after_input
                        - self.variables["available_Water#L"][x, y].value
                    )
                    self.variables["wet_surface#m2.day-1"][x, y].set_value(
                        self.field.plotsurface
                    )

                # Natural nutrients input (earth)
                for n in ["N", "K", "P", "C"]:
                    self.variables["available_" + n + "#g"][x, y].set_value(
                        self.variables["available_" + n + "#g"][x, y].value
                        + self.variables["microlife_health_index#%"][x, y].value
                        / 100.0
                        * self.parameters["bedrocks_release_" + n + "#mg.day-1"]
                        / 1000.0
                    )

                # Other nutrients input (fertilizers)
                for f in fertilizers:
                    # Q: Here, should we trigger update of f entity or simply compute amount? [f is updated later or earlier]
                    # Answer: Receiver always triggers action, Emitter never triggers it.
                    release = f.release_nutrients((x, y), self)  # in kg
                    for n in ["N", "K", "P", "C"]:
                        self.variables["available_" + n + "#g"][x, y].set_value(
                            self.variables["available_" + n + "#g"][x, y].value
                            + release[n] * 1000
                        )

                for c in cides:
                    release = c.release((x, y))  # in kg

                    for n in ["pollinators", "pests", "soil", "weeds"]:
                        self.variables["amount_cide#g"][n][x, y].set_value(
                            self.variables["amount_cide#g"][n][x, y].value
                            + release * 1000 * c.parameters[n]
                        )

                # Weed nutrients and water consumption:
                for w in weeds:
                    requirements = w.requirement((x, y))
                    release = w.release_nutrients((x, y), self)  # in g
                    for n in ["N", "K", "P", "C"]:
                        self.variables["available_" + n + "#g"][x, y].set_value(
                            max(
                                0.0,
                                self.variables["available_" + n + "#g"][x, y].value
                                - requirements[n + "#g"]
                                + release[n + "#g"],
                            )
                        )

                    self.variables["available_Water#L"][x, y].set_value(
                        max(
                            0.0,
                            self.variables["available_Water#L"][x, y].value
                            - requirements["Water#L"],
                        )
                    )

                # Plant nutrients consumption or release:
                milife = self.variables["microlife_health_index#%"][x, y].value / 100.0
                for p in plants:
                    requirements = p.requirement_nutrients((x, y))
                    release = p.release_nutrients((x, y), self)  # in g
                    v = {}
                    stress = {}
                    for n in ["N", "K", "P", "C"]:
                        v[n + "#g"] = min(
                            self.variables["available_" + n + "#g"][x, y].value,
                            milife * requirements[n],
                        )
                        stress[n + "#g"] = requirements[n] - v[n + "#g"]
                        self.variables["available_" + n + "#g"][x, y].set_value(
                            self.variables["available_" + n + "#g"][x, y].value
                            - v[n + "#g"]
                            + release[n + "#g"]
                        )
                    p.receive_nutrients((x, y), v, stress)

                    # Plant water requirement
                    requirement_water = p.requirement_water((x, y), weather, field)
                    # print("PLANT WATER REQUIRES", requirement_water)
                    wp = (
                        self.parameters["wilting_point#L.m-3"]
                        * self.parameters["depth#m"]
                        * self.field.plotsurface
                    )

                    w = min(
                        requirement_water,
                        max(self.variables["available_Water#L"][x, y].value - wp, 0),
                    )
                    stress_water = requirement_water - w

                    self.variables["available_Water#L"][x, y].set_value(
                        self.variables["available_Water#L"][x, y].value - w
                    )
                    # print("SOIL ",requirement_water, w, stress_water)
                    p.receive_water((x, y), w, stress_water)

                # Soil water evaporation (depend on shadows and what is not wet...)
                soil_evaporated_water = (
                    self.ground_evaporation((x, y), weather, plants, weeds, field)
                    / 1000
                )
                water_evaporation_threshold = (
                    self.parameters["max_water_capacity#L.m-3"]
                    * self.field.plotsurface
                    * (
                        self.parameters["depth#m"]
                        - self.parameters["total_evaporable_water#mm"] / 1000
                    )
                )
                # print("SOIL", soil_evaporated_water)
                soil_evaporated_water = min(
                    soil_evaporated_water,
                    max(
                        self.variables["available_Water#L"][x, y].value
                        - water_evaporation_threshold,
                        0,
                    ),
                )
                # print("SOIL", soil_evaporated_water, water_evaporation_threshold)
                # if (self.variables['available_Water#L'][x,y].value  - soil_evaporated_water<water_evaporation_threshold):

                self.variables["available_Water#L"][x, y].set_value(
                    max(
                        0,
                        self.variables["available_Water#L"][x, y].value
                        - soil_evaporated_water,
                    )
                )
                # print("WET",self.variables["wet_surface#m2.day-1"][x, y].value)
                self.variables["wet_surface#m2.day-1"][x, y].set_value(
                    max(
                        self.variables["wet_surface#m2.day-1"][x, y].value
                        - self.parameters["water_surface_absorption_speed#m2.day-1"],
                        0,
                    )
                )
                # print("WET update", self.variables["wet_surface#m2.day-1"][x, y].value)

                # Microlife health index:
                q = []
                q.append(
                    (
                        1.0,
                        self.variables["amount_cide#g"]["soil"][x, y].value / 100,
                        0,
                        0,
                    )
                )
                q.append((0.5, water_surplus / max_water_plot_capacity, 0, 0))
                p_stayalive = expglm(0.0, q)
                # print("STAYALIVE",p_stayalive,self.variables['amount_cide#g']['soil'][x,y].value,water_surplus/max_water_plot_capacity)
                # is_dead = (self.np_random.binomial(1, p_stayalive, 1)[0] == 0)
                # if (is_dead):
                #    self.variables['microlife_health_index#%'][x, y].set_value(
                #        self.variables['microlife_health_index#%'][x, y].value * p_stayalive)
                # else:
                #    self.variables['microlife_health_index#%'][x, y].set_value(min(100,
                #        self.variables['microlife_health_index#%'][x, y].value * (1+0.1*p_stayalive)))
                self.variables["microlife_health_index#%"][x, y].set_value(
                    (
                        (
                            p_stayalive * (1 + 0.1 * p_stayalive)
                            + (1 - p_stayalive) * (p_stayalive)
                        )
                        * self.variables["microlife_health_index#%"][x, y].value
                    )
                )

                # Soil nutrients/water/pesticide/herbicide leakage due to rain.
                rain_intensity = weather.variables["rain_intensity"].value
                if rain_intensity > 0 or water_surplus > 0:
                    milife = (
                        self.variables["microlife_health_index#%"][x, y].value / 100.0
                    )
                    surf = self.field.plotsurface
                    for n in ["N", "K", "P", "C"]:
                        self.variables["available_" + n + "#g"][x, y].set_value(
                            max(
                                0,
                                self.variables["available_" + n + "#g"][x, y].value
                                - (
                                    rain_intensity * surf
                                    + water_surplus / max_water_plot_capacity
                                )
                                * (1 - milife),
                            )
                        )
                    for n in ["pollinators", "pests", "soil", "weeds"]:
                        self.variables["amount_cide#g"][n][x, y].set_value(
                            max(
                                0,
                                self.variables["amount_cide#g"][n][x, y].value
                                * np.exp(
                                    -(
                                        rain_intensity * surf
                                        + water_surplus / max_water_plot_capacity
                                    )
                                ),
                            )
                        )

    def ground_evaporation(self, position, weather, plants, weeds, field):
        ET_0 = weather.evapo_coefficient(field)  # ml/m2/day

        # Compute % of ground covered by shadow:
        plantshadow = np.sum(
            [
                p.compute_shadowsurface(position) * p.parameters["shadow_coeff#%"]
                for p in plants
            ]
        )
        weedshadow = np.sum([w.compute_shadowsurface(position) for w in weeds])
        shadow_proportion = min(
            (plantshadow + weedshadow) / self.field.plotsurface, 1.0
        )
        wet_proportion = (
            self.variables["wet_surface#m2.day-1"][position].value
            / self.field.plotsurface
        )
        evapo_prop = min(1.0 - shadow_proportion, wet_proportion)

        # print("EVAPO_prop",evapo_prop,  shadow_proportion, wet_proportion)
        drop_proportion = (
            (1.1 - self.variables["microlife_health_index#%"][position].value / 100)
            * self.field.plotsurface
            * self.parameters["depth#m"]
            * self.parameters["water_leakage_max#L.m-3.day-1"]
            * 1000
        )

        return ET_0 * evapo_prop * self.field.plotsurface + drop_proportion

    def act_on_variables(self, action_name, action_params):
        self.assert_action(action_name, action_params)
        if action_name == "water_discrete" or "water_continuous":
            x, y = action_params["plot"]
            max_water_plot_capacity = (
                self.parameters["max_water_capacity#L.m-3"]
                * self.field.plotsurface
                * self.parameters["depth#m"]
            )
            water_after_input = (
                self.variables["available_Water#L"][x, y].value
                + action_params["amount#L"]
            )
            new_value = min(max_water_plot_capacity, water_after_input)
            water_surplus = water_after_input - new_value
            self.variables["wet_surface#m2.day-1"][x, y].set_value(
                self.variables["wet_surface#m2.day-1"][x, y].value
                + self.field.plotsurface * (action_params["duration#min"] / 60.0) / 24.0
            )  # watering for 30minutes over 24h.
            self.variables["total_cumulated_added_water#L"].set_value(
                self.variables["total_cumulated_added_water#L"].value
                + (new_value - self.variables["available_Water#L"][x, y].value)
            )
            self.variables["available_Water#L"][x, y].set_value(new_value)
            if water_surplus > 0:
                milife = self.variables["microlife_health_index#%"][x, y].value / 100.0
                for n in ["N", "K", "P", "C"]:
                    self.variables["available_" + n + "#g"][x, y].set_value(
                        max(
                            0,
                            self.variables["available_" + n + "#g"][x, y].value
                            - water_surplus * (1 - milife),
                        )
                    )
                for n in ["pollinators", "pests", "soil", "weeds"]:
                    self.variables["amount_cide#g"][n][x, y].set_value(
                        max(
                            0,
                            self.variables["amount_cide#g"][n][x, y].value
                            * np.exp(-water_surplus / max_water_plot_capacity),
                        )
                    )

                q = []
                q.append(
                    (2.0, self.variables["amount_cide#g"]["soil"][x, y].value, 0, 0)
                )
                q.append((0.5, water_surplus / max_water_plot_capacity, 0, 0))
                p_stayalive = expglm(0.0, q)
                self.variables["microlife_health_index#%"][x, y].set_value(
                    (
                        (
                            p_stayalive * (1 + 0.1 * p_stayalive)
                            + (1 - p_stayalive) * (p_stayalive)
                        )
                        * self.variables["microlife_health_index#%"][x, y].value
                    )
                )

    def to_fieldimage(self):
        im_width, im_height = 64, 64
        image = Image.new(
            "RGBA",
            (im_width * self.field.X, im_height * self.field.Y),
            (255, 255, 255, 0),
        )
        for x in range(self.field.X):
            for y in range(self.field.Y):
                # print("XY",x,y,self.variables['wet_surface#m2.day-1'][x,y].value)
                if (
                    self.variables["wet_surface#m2.day-1"][x, y].value
                    > 0.5 * self.field.plotsurface
                ):
                    image.paste(self.images["wet"], (im_width * x, im_height * y))
                else:
                    image.paste(self.images["dry"], (im_width * x, im_height * y))
        return image
