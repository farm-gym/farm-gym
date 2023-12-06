import numpy as np
from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, checkissubclass, expglm, fillarray


class Weeds(Entity_API):
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
        "dead",
    ]

    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["grow#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["seeds#nb"] = fillarray(X, Y, (0, 1000), 0.0)
        self.variables["flowers#nb"] = fillarray(X, Y, (0, 1000), 0.0)

        #
        self.variables["total_cumulated_plot_population#nb"] = Range((0, 10000), 0.0)

        # Actions
        self.actions = {"remove": {"plot": field.plots}}

        self.dependencies = {"Weather", "Soil"}

    def get_parameter_keys(self):
        return [
            "appear_conditions",
            "grow_conditions",
            "max_new_seeds#nb",
            "flowers_per_plant#nb",
        ]

    def reset(self):
        X = self.field.X
        Y = self.field.Y
        self.variables["grow#nb"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))
        self.variables["seeds#nb"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))
        self.variables["flowers#nb"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))
        self.variables["total_cumulated_plot_population#nb"] = Range((0, 10000), 0.0)
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

        p = 1.0 / (0.0 + self.parameters["time_to_grow#day"])
        # Pick some positions:
        pos_seed = []
        pos_grow = []
        pos_bloom = []
        positions = []
        for x in range(self.field.X):
            for y in range(self.field.Y):
                b = self.np_random.binomial(1, p)
                # print("b",b)
                if b == 1:
                    positions.append((x, y))
                    i = self.np_random.integers(0, 3)
                    # print("i",i)
                    if i == 0:
                        pos_seed.append((x, y))
                    elif i == 1:
                        pos_grow.append((x, y))
                    else:
                        pos_bloom.append((x, y))

        for pos in positions:
            x, y = pos
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
            p_appear = expglm(p["sensitivity_0"], q)
            # print("WEEDS",p_appear,field.distance_to_edge((x, y)))

            z = self.np_random.binomial(
                self.parameters["max_new_seeds#nb"], p_appear, 1
            )[0]
            self.variables["seeds#nb"][x, y].set_value(
                self.variables["seeds#nb"][x, y].value + z
            )

        for pos in pos_seed:  # Flowers to Seed
            x, y = pos
            neighbors = field.get_neighbors(pos)
            # nb_flowers = self.variables["flowers#nb"][x, y]
            # nb_flowers += np.sum([self.variables["flowers#nb"][neighbors[k]] for k in neighbors.keys()])

            z = self.np_random.binomial(
                self.variables["flowers#nb"][x, y].value,
                self.parameters["flower_to_seed#%"],
                1,
            )[0]
            self.variables["flowers#nb"][x, y].set_value(
                self.variables["flowers#nb"][x, y].value - z
            )

            nb_seeds = z * self.parameters["seed_per_flower#nb"]
            pneighbors = 1.0 / (len(neighbors) + 1)
            zz = self.np_random.binomial(nb_seeds, pneighbors, 1)[0]
            self.variables["seeds#nb"][x, y].set_value(
                self.variables["seeds#nb"][x, y].value + zz
            )
            nb_seeds -= zz
            for k in neighbors.keys():
                zz = self.np_random.binomial(nb_seeds, pneighbors, 1)[0]
                self.variables["seeds#nb"][neighbors[k]].set_value(
                    self.variables["seeds#nb"][neighbors[k]].value + zz
                )
                nb_seeds -= zz

        for pos in pos_grow:  # Seed to Grow
            x, y = pos
            # Grow
            p = self.parameters["grow_conditions"]
            q = []
            q.append(
                (
                    p["sensitivity_grow_T"],
                    weather.variables["air_temperature"]["mean#°C"].value,
                    p["grow_T_min"],
                    p["grow_T_max"],
                )
            )
            q.append(
                (
                    p["sensitivity_grow_RH"],
                    weather.variables["humidity#%"].value,
                    p["grow_RH_min"],
                    p["grow_RH_max"],
                )
            )
            q.append(
                (
                    p["sensitivity_grow_herbicide"],
                    soil.variables["amount_cide#g"]["weeds"][x, y].value,
                    -np.infty,
                    p["grow_herbicide_max#g"],
                )
            )
            # TODO: SHOULD WE ADD THESE CONDITIONS?
            #            q.append(
            #                (np.infty, soil.variables['available_N#g'][(x, y)].value, p['N_grow_consumption#g.mm-1'], np.infty))
            #            q.append(
            #                (np.infty, soil.variables['available_K#g'][(x, y)].value, p['K_grow_consumption#g.mm-1'], np.infty))
            #            q.append(
            #                (np.infty, soil.variables['available_P#g'][(x, y)].value, p['P_grow_consumption#g.mm-1'], np.infty))
            #            q.append(
            #                (np.infty, soil.variables['available_C#g'][(x, y)].value, p['C_grow_consumption#g.mm-1'], np.infty))
            p_grow = expglm(p["sensitivity_grow_0"], q)
            # print("WEEDS",p_grow,weather.variables['air_temperature']['mean#°C'].value,soil.variables['available_N#g'][(x, y)].value)

            nb_sprouts = self.np_random.binomial(
                self.variables["seeds#nb"][x, y].value, p_grow, 1
            )[0]
            self.variables["grow#nb"][x, y].set_value(
                self.variables["grow#nb"][x, y].value + nb_sprouts
            )
            self.variables["seeds#nb"][x, y].set_value(
                self.variables["seeds#nb"][x, y].value - nb_sprouts
            )
            self.variables["total_cumulated_plot_population#nb"].set_value(
                self.variables["total_cumulated_plot_population#nb"].value + nb_sprouts
            )

        for pos in pos_bloom:  # Grow to Flowers
            x, y = pos
            p = self.parameters["grow_conditions"]
            # Flowers
            q = []
            q.append(
                (
                    p["sensitivity_grow_herbicide"],
                    soil.variables["amount_cide#g"]["weeds"][x, y].value,
                    -np.infty,
                    p["grow_herbicide_max#g"],
                )
            )
            p_flowers = expglm(
                self.parameters["sensitivity_flowers_0"], q
            )  # np.exp(-self.parameters['sensitivity_flowers_0'])
            z = self.np_random.binomial(
                self.variables["grow#nb"][x, y].value, p_flowers, 1
            )[0]
            self.variables["grow#nb"][x, y].set_value(
                self.variables["grow#nb"][x, y].value - z
            )
            self.variables["flowers#nb"][x, y].set_value(
                self.variables["flowers#nb"][x, y].value
                + z
                * self.np_random.binomial(
                    self.parameters["flowers_per_plant#nb"], p_flowers, 1
                )[0]
            )

        for pos in positions:
            x, y = pos
            # Die
            p = self.parameters["grow_conditions"]
            draught = p["sensibility_draught#%"]
            w = (
                (
                    (1.0 - draught) * soil.parameters["wilting_point#L.m-3"]
                    + draught * soil.parameters["max_water_capacity#L.m-3"]
                )
                * soil.parameters["depth#m"]
                * self.field.plotsurface
            )
            q = []
            q.append(
                (
                    p["sensitivity_death_herbicide"],
                    soil.variables["amount_cide#g"]["weeds"][x, y].value,
                    -np.infty,
                    p["death_herbicide_max#g"],
                )
            )
            q.append(
                (
                    p["sensitivity_death_N"],
                    soil.variables["available_N#g"][(x, y)].value,
                    p["N_grow_consumption#g.mm-1"],
                    np.infty,
                )
            )
            q.append(
                (
                    p["sensitivity_death_K"],
                    soil.variables["available_K#g"][(x, y)].value,
                    p["K_grow_consumption#g.mm-1"],
                    np.infty,
                )
            )
            q.append(
                (
                    p["sensitivity_death_P"],
                    soil.variables["available_P#g"][(x, y)].value,
                    p["P_grow_consumption#g.mm-1"],
                    np.infty,
                )
            )
            q.append(
                (
                    p["sensitivity_death_C"],
                    soil.variables["available_C#g"][(x, y)].value,
                    p["C_grow_consumption#g.mm-1"],
                    np.infty,
                )
            )
            q.append(
                (
                    p["sensitivity_death_Water"],
                    soil.variables["available_Water#L"][(x, y)].value,
                    w,
                    np.infty,
                )
            )
            p_stayalive = expglm(p["sensitivity_death_0"], q)
            z = self.np_random.binomial(
                self.variables["grow#nb"][x, y].value, p_stayalive, 1
            )[0]

            self.variables["grow#nb"][x, y].set_value(z)

    def act_on_variables(self, action_name, action_params):
        if action_name == "remove":
            position = action_params["plot"]
            s = (  # noqa: F841
                self.variables["grow#nb"][position].value
                + self.variables["flowers#nb"][position].value
            )
            self.variables["grow#nb"][position].set_value(0)
            self.variables["flowers#nb"][position].set_value(0)

    def requirement(self, position):
        nb = self.variables["grow#nb"][position].value
        p = self.parameters["grow_conditions"]
        return {
            "N#g": nb * p["N_grow_consumption#g.mm-1"],
            "K#g": nb * p["N_grow_consumption#g.mm-1"],
            "P#g": nb * p["N_grow_consumption#g.mm-1"],
            "C#g": nb * p["N_grow_consumption#g.mm-1"],
            "Water#L": nb * p["Water_grow_consumption#mL.mm-1"] * 0.001,
        }

    def release_nutrients(self, position, soil):
        r = {"N#g": 0.0, "K#g": 0.0, "P#g": 0.0, "C#g": 0.0}  # 'Water':(0.,1.)}

        nb = self.variables["grow#nb"][position].value
        nb += self.variables["flowers#nb"][position].value

        p = self.parameters["grow_conditions"]
        estimated_size = (self.parameters["size#cm"] * 10) / 2
        r["N#g"] = nb * p["N_air_storage#g.mm-1"] * estimated_size
        r["C#g"] = nb * p["C_air_storage#g.mm-1"] * estimated_size
        return r

    def compute_shadowsurface(self, position):
        # returns shadow effective size in m2
        n = (
            self.variables["grow#nb"][position].value
            + self.variables["flowers#nb"][position].value
        )
        # Consider a plant is a ball of diameter size#cm
        r = self.parameters["size#cm"] * 0.01 / 2.0
        return np.pi * r * r * n  # * self.parameters['shadow_coeff#%']

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
                    self.variables["grow#nb"][x, y].value
                    + self.variables["flowers#nb"][x, y].value
                    > 0
                ):
                    if (
                        self.variables["grow#nb"][x, y].value
                        + self.variables["flowers#nb"][x, y].value
                        > 3
                    ):
                        image.paste(self.images["many"], (im_width * x, im_height * y))
                    else:
                        image.paste(self.images["few"], (im_width * x, im_height * y))
        return image
