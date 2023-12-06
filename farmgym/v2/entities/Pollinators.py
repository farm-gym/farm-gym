import numpy as np
from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, checkissubclass, expglm, fillarray


class Pollinators(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["occurrence#bin"] = fillarray(X, Y, ["True", "False"], "False")

        # Actions
        self.actions = {}

        #
        self.variables["total_cumulated_occurrence#nb"] = Range((0, 1000), 0.0)

        self.dependencies = {"Weather", "Soil", "Plant", "Birds"}

    def get_parameter_keys(self):
        return ["visit_conditions"]

    def reset(self):
        X = self.field.X
        Y = self.field.Y
        self.variables["occurrence#bin"] = fillarray(
            X, Y, ["True", "False"], "False"
        )  # np.full((X,Y),fill_value=Range(['True','False'],'True'))
        self.variables["total_cumulated_occurrence#nb"] = Range((0, 1000), 0.0)
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
        birds = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Birds")
        ]
        nb_birds_eating_pollinators = np.sum(
            [
                b.variables["population#nb"].value
                for b in birds
                if b.parameters["pollinator_eater"]
            ]
        )
        for x in range(self.field.X):
            for y in range(self.field.Y):
                flowers = np.sum(
                    [
                        1
                        if p.variables["stage"][x, y].value
                        in ["entered_blossom", "blossom"]
                        else 0.0
                        for p in plants
                    ]
                )

                p = self.parameters["visit_conditions"]
                q = []
                q.append(
                    (
                        p["theta_dist_edge"],
                        field.distance_to_edge((x, y)),
                        -np.infty,
                        0.0,
                    )
                )
                q.append(
                    (
                        p["theta_death_birds"],
                        nb_birds_eating_pollinators,
                        0,
                        p["death_birds_max"],
                    )
                )
                q.append(
                    (
                        p["theta_T"],
                        weather.variables["air_temperature"]["mean#°C"].value,
                        p["T_min"],
                        p["T_max"],
                    )
                )
                q.append(
                    (
                        p["theta_Wind"],
                        weather.variables["wind"]["speed#km.h-1"].value,
                        -np.infty,
                        p["Wind_max"],
                    )
                )
                q.append(
                    (
                        p["theta_Rain"],
                        0
                        if weather.variables["rain_amount#mm.day-1"].value == "None"
                        else 1.0,
                        -np.infty,
                        0.0,
                    )
                )
                q.append(
                    (
                        p["theta_pesticide"],
                        soil.variables["amount_cide#g"]["pollinators"][x, y].value,
                        -np.infty,
                        p["pesticide_tol"],
                    )
                )
                # q.append((p['theta_pesticide'], soil.variables['amount_cide#g']['pollinators'][x,y], -np.infty, p['pesticide_tol']))
                q_appear = expglm(p["theta_0"], q)
                # print("POLLINATOR appearance proba",q_appear)

                self.variables["occurrence#bin"][x, y].set_value(
                    "True"
                    if self.np_random.binomial(flowers, q_appear, 1) > 0
                    else "False"
                )
                if self.variables["occurrence#bin"][x, y].value == "True":
                    self.variables["total_cumulated_occurrence#nb"].set_value(
                        self.variables["total_cumulated_occurrence#nb"] + 1
                    )

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
                if self.variables["occurrence#bin"][x, y].value == "True":
                    image.paste(self.images["some"], (im_width * x, im_height * y))
        return image
