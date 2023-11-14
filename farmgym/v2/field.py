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
    """
    Instanciate a Field. One or several fields are included in a farm and one field includes several plants.

    Parameters
    ----------
    localization: (latitude, longitude, altitude)
        localisation of the field

    shape: (length (int), width (int), scale (multiples of 1 unit in meter))
        Shape of the field. Each field of shape (width,length,scale) contains width × length many plots each of size scale

    entities_specifications: list
        list of couples (entity, name) used to construct the field.

    Examples
    --------
    >>> from farmgym.v2.field import Field
    >>> from farmgym.v2.entities.Weather import Weather
    >>> from farmgym.v2.entities.Soil import Soil
    >>> from farmgym.v2.entities.Plant import Plant
    >>> entities = [(Weather, "lille"), (Soil, "clay"), (Plant, "bean")]
    >>> field1 = Field(localization={"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
    >>>                shape={"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    >>>                entities_specifications=entities)

    """

    def __init__(self, localization, shape, entities_specifications: list):
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

        self.entity_managers = entities_specifications
        self.np_random = None

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
                self.entities[name].fullname = name + "(" + param + ")"
                self.entities[name].shortname = param
            else:
                cpt[e.__name__] = 0
                name = e.__name__ + "-0"
                self.entities[name] = e(self, param)
                self.entities[name].name = name
                self.entities[name].fullname = name + "(" + param + ")"
                self.entities[name].shortname = param

    def reset(self):
        """
        Reset to initial values
        """
        for e in self.entities.values():
            e.set_random(self.np_random)
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
        """
        Update internal variables of the field after an increment of 1 day.
        """
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
