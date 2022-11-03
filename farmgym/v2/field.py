from textwrap import indent


class Plot:
    def __init__(self, field, position, type="base"):
        self.field = field
        self.position = position  # x,y
        assert type in ["base", "edge"]
        self.type = type

    def __str__(self):
        return "'" + str(self.position) + ":" + self.type + "'"


class Field:
    def __init__(self, localization, shape, entity_managers: list):
        """

        :param localization: (latitude, longitude, altitude)
        :param shape: (length (int), width (int), scale of 1 unit in meter)
        """
        self.name = "Field"
        self.localization = localization
        assert list(localization.keys()) == ["latitude#°", "longitude#°", "altitude#m"]
        assert list(shape.keys()) == ["length#nb", "width#nb", "scale#m"]
        self.shape = shape
        self.plotsurface = shape["scale#m"] ** 2.0
        # TODO: Make it np.zeros list, then manually fill
        # self.plots = [[Plot(self,[x,y], "edge" if x in [0,shape['length']-1] or y in [0, shape['width']-1] else "base")  for y in range (shape['width'])] for x in range(shape['length'])]

        self.X = self.shape["length#nb"]
        self.Y = self.shape["width#nb"]
        self.plots = [str((x, y)) for x in range(self.X) for y in range(self.Y)]
        # self.plots =  [Plot(self,[x,y], "edge" if x in [0,shape['length']-1] or y in [0, shape['width']-1] else "base") for x in range(X) for y in range (Y)]

        self.entity_managers = entity_managers

        self.entities = {}
        cpt = {}
        for e, param in self.entity_managers:
            # print('ENAME',e.__name__)
            # print(self.entities.keys())
            if e.__name__ in cpt.keys():
                cpt[e.__name__] += 1
                name = e.__name__ + "-" + str(cpt[e.__name__])
                self.entities[name] = e(self, param)
                self.entities[name].name = name
            else:
                cpt[e.__name__] = 0
                name = e.__name__ + "-0"
                self.entities[name] = e(self, param)
                self.entities[name].name = name

    def reset(self):
        for e in self.entities.values():
            e.reset()

    def get_neighbors(self, plot):
        """NW N NE,W,E,SW,S,SE"""
        x, y = plot
        xm = self.X
        ym = self.Y
        assert 0 <= x < xm and 0 <= y < ym
        neighbors = {}
        if y > 0:
            if x > 0:
                neighbors["NW"] = (x - 1, y - 1)
            neighbors["N"] = (x, y - 1)
            if x < xm - 1:
                neighbors["NE"] = (x + 1, y - 1)
        if x > 0:
            neighbors["W"] = (x - 1, y)
        if x < xm - 1:
            neighbors["E"] = (x + 1, y)
        if y < ym - 1:
            if x > 0:
                neighbors["SW"] = (x - 1, y + 1)
            neighbors["S"] = (x, y + 1)
            if x < xm - 1:
                neighbors["SE"] = (x + 1, y + 1)
        return neighbors

    def distance_to_edge(self, position):
        x, y = position
        if x > self.X / 2:
            x = self.X - x
        if y > self.Y / 2:
            y = self.Y - y
        return min(x, y)

    def update_to_next_day(self):
        for e in self.entities.values():
            e.update_variables(self, self.entities)

    def __str__(self):
        s = (
            self.name
            + ": "
            + str(self.localization)
            + " scale: "
            + str(self.shape["scale#m"])
            + "m\n"
        )
        s += "\tShape:\n\t\t"
        for x in range(self.X):
            for y in range(self.Y):
                s += "E" if self.distance_to_edge((x, y)) <= 1 else "B"
            s += "\n\t\t"
        s += "\n"
        s += "\t" + self.name + "-Entities:\n"
        for k in self.entities.keys():
            s += indent(str(self.entities[k]), "\t\t", lambda line: True) + "\n"
        return s
