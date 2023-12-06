import numpy as np
from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, checkissubclass, expglm, fillarray


class Pests(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["plot_population#nb"] = fillarray(X, Y, (0, 1000), 0.0)

        # TODO: This is bad, as plants are perhaps added later on. + What about weeds?
        plants = [
            field.entities[e]
            for e in field.entities
            if checkissubclass(field.entities[e].__class__, "Plant")
        ]
        weeds = [
            self.field.entities[e]
            for e in self.field.entities
            if checkissubclass(self.field.entities[e].__class__, "Weeds")
        ]
        self.variables["onplant_population#nb"] = {}
        for i in range(len(plants)):
            self.variables["onplant_population#nb"][plants[i].name] = fillarray(
                X, Y, (0, 1000), 0.0
            )
        for i in range(len(weeds)):
            self.variables["onplant_population#nb"][weeds[i].name] = fillarray(
                X, Y, (0, 1000), 0.0
            )

        # Actions
        self.actions = {}

        #
        self.variables["total_cumulated_plot_population#nb"] = Range((0, 10000), 0.0)

        self.dependencies = {"Weather", "Soil", "Plant", "Birds"}

    def get_parameter_keys(self):
        return [
            "min_population#nb",
            "max_population#nb",
            "arrival_frequency#day-1",
            "appear_conditions",
            "leave_conditions",
        ]

    def reset(self):
        X = self.field.X
        Y = self.field.Y

        self.variables["plot_population#nb"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))

        plants = [
            self.field.entities[e]
            for e in self.field.entities
            if checkissubclass(self.field.entities[e].__class__, "Plant")
        ]
        weeds = [
            self.field.entities[e]
            for e in self.field.entities
            if checkissubclass(self.field.entities[e].__class__, "Weeds")
        ]
        self.variables["onplant_population#nb"] = {}
        for i in range(len(plants)):
            self.variables["onplant_population#nb"][plants[i].name] = fillarray(
                X, Y, (0, 1000), 0.0
            )  # np.full((X, Y), fill_value=Range((0, 1000), 0.))
        for i in range(len(weeds)):
            self.variables["onplant_population#nb"][weeds[i].name] = fillarray(
                X, Y, (0, 1000), 0.0
            )  # np.full((X,Y),fill_value=Range((0,1000),0.))
        self.initialize_variables(self.initial_conditions)

    def update_variables(self, field, entities):
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
        plants = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Plant")
        ]
        weeds = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Weeds")
        ]
        birds = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Birds")
        ]

        nb_birds_eating_pests = np.sum(
            [
                b.variables["population#nb"].value
                for b in birds
                if b.parameters["pest_eater"]
            ]
        )
        # print("BIRDS_EAT_PESTS",nb_birds_eating_pests)
        for x in range(self.field.X):
            for y in range(self.field.Y):
                # pests randomly move to neighbor locations:
                neighbors = field.get_neighbors((x, y))
                w = {"H": self.np_random.random()}
                for k in neighbors.keys():
                    w[k] = self.np_random.random()
                    # Adding wind effect
                    if weather.variables["wind"]["direction"].value == k:
                        w[k] += weather.variables["wind"]["speed#km.h-1"].value / 10.0
                W = np.sum(list(w.values()))
                pop = self.variables["plot_population#nb"][x, y].value
                for k in neighbors.keys():
                    nbp = min(
                        np.ceil(w[k] / W * pop),
                        self.variables["plot_population#nb"][x, y].value,
                    )
                    self.variables["plot_population#nb"][neighbors[k]].set_value(
                        self.variables["plot_population#nb"][neighbors[k]].value + nbp
                    )
                    self.variables["plot_population#nb"][x, y].set_value(
                        self.variables["plot_population#nb"][x, y].value - nbp
                    )

                # Add random pests on field border:
                # if (field.plots[x][y].type=='edge'):
                # nb_edge_arrival =self.parameters['min_population#nb']+ np.ceil( (self.parameters['max_population#nb']-self.parameters['min_population#nb'])*max(np.sin(self.parameters['arrival_frequency#day-1']* weather.variables['day#int365'].value),0))
                is_arrival = (
                    self.np_random.binomial(
                        1, self.parameters["arrival_frequency#day-1"], 1
                    )[0]
                    == 1
                )
                if is_arrival:
                    nb_edge_arrival = self.np_random.integers(
                        self.parameters["min_population#nb"],
                        self.parameters["max_population#nb"],
                    )
                else:
                    nb_edge_arrival = 0

                p = self.parameters["leave_conditions"]
                q = []
                maxd = max(field.X, field.Y) / 2.0
                q.append(
                    (
                        p["sensitivity_dist_edge"],
                        field.distance_to_edge((x, y)),
                        maxd,
                        np.infty,
                    )
                )
                q.append(
                    (
                        p["sensitivity_death_birds"],
                        nb_birds_eating_pests,
                        0,
                        p["death_birds_max"],
                    )
                )
                q.append(
                    (
                        p["sensitivity_T"],
                        weather.variables["air_temperature"]["mean#°C"].value,
                        p["T_min"],
                        p["T_max"],
                    )
                )
                q.append(
                    (
                        p["sensitivity_pesticide"],
                        soil.variables["amount_cide#g"]["pests"][x, y].value,
                        -np.infty,
                        p["pesticide_min"],
                    )
                )
                # TODO: Add total repulsive/attractive effect of plants on plot!
                q_stay = expglm(p["sensitivity_0"], q)

                self.variables["plot_population#nb"][x, y].set_value(
                    self.np_random.binomial(
                        (int)(self.variables["plot_population#nb"][x, y].value),
                        q_stay,
                        1,
                    )[0]
                )

                p = self.parameters["appear_conditions"]
                q = []
                q.append(
                    (
                        p["sensitivity_dist_edge"],
                        field.distance_to_edge((x, y)),
                        -np.infty,
                        0.0,
                    )
                )
                q.append(
                    (
                        p["sensitivity_T"],
                        weather.variables["air_temperature"]["mean#°C"].value,
                        p["T_min"],
                        p["T_max"],
                    )
                )
                q.append(
                    (
                        p["sensitivity_pesticide"],
                        soil.variables["amount_cide#g"]["pests"][x, y].value,
                        -np.infty,
                        p["pesticide_min"],
                    )
                )
                # TODO: Add total repulsive/attractive effect of plants on plot!
                q_appear = expglm(p["sensitivity_0"], q)

                nb_appear = self.np_random.binomial(nb_edge_arrival, q_appear, 1)[0]
                new_value = min(
                    self.variables["plot_population#nb"][x, y].value + nb_appear,
                    self.parameters["max_population#nb"],
                )
                self.variables["total_cumulated_plot_population#nb"].set_value(
                    self.variables["total_cumulated_plot_population#nb"].value
                    + new_value
                    - self.variables["plot_population#nb"][x, y].value
                )
                self.variables["plot_population#nb"][x, y].set_value(new_value)

        ## We do the following next in order not to mess up with for x, for y loop and  neighbors changes.
        for x in range(self.field.X):
            for y in range(self.field.Y):
                # TODO:  Add repulsive effect only if plant is there and not dead !!
                # Distribute pests equally amongst plants:
                weights = np.zeros((len(plants) + len(weeds)))
                for i in range(len(plants)):
                    if plants[i].is_active((x, y)):
                        weights[i] = (
                            np.exp(-plants[i].parameters["pest_repulsive_effect#float"])
                            * plants[i].variables["population#nb"][x, y].value
                        )
                for i in range(len(weeds)):
                    if (
                        weeds[i].variables["grow#nb"][x, y].value
                        + weeds[i].variables["flowers#nb"][x, y].value
                        > 0
                    ):
                        weights[i + len(plants)] = np.exp(
                            -weeds[i].parameters["pest_repulsive_effect#float"]
                        ) * (
                            weeds[i].variables["grow#nb"][x, y].value
                            + weeds[i].variables["flowers#nb"][x, y].value
                        )
                if np.sum(weights) > 0:
                    weights = weights / np.sum(weights)
                    # print("WW",weights,len(plants))
                    ns = self.np_random.multinomial(
                        (int)(self.variables["plot_population#nb"][x, y].value), weights
                    )
                    for i in range(len(plants)):
                        self.variables["onplant_population#nb"][plants[i].name][
                            x, y
                        ].set_value(ns[i])
                    for i in range(len(weeds)):
                        self.variables["onplant_population#nb"][weeds[i].name][
                            x, y
                        ].set_value(ns[i + len(plants)])
                else:
                    for i in range(len(plants)):
                        self.variables["onplant_population#nb"][plants[i].name][
                            x, y
                        ].set_value(0)
                    for i in range(len(weeds)):
                        self.variables["onplant_population#nb"][weeds[i].name][
                            x, y
                        ].set_value(0)

    def act_on_variables(self, action_name, action_params):
        pass

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
                if self.variables["plot_population#nb"][x, y].value > 0:
                    if self.variables["plot_population#nb"][x, y].value > 3:
                        image.paste(self.images["many"], (im_width * x, im_height * y))
                    else:
                        image.paste(self.images["few"], (im_width * x, im_height * y))
        return image
