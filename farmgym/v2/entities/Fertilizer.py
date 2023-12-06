from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, fillarray


class Fertilizer(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["amount#kg"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))

        #
        self.variables["total_cumulated_scattered_amount#kg"] = Range((0, 10000), 0.0)

        # Actions
        self.actions = {
            "scatter": {"plot": field.plots, "amount#kg": (0, 10)},
            "scatter_bag": {"plot": field.plots, "amount#bag": list(range(5))},
        }

        self.dependencies = {"Soil"}

    def get_parameter_keys(self):
        return ["N#%", "K#%", "P#%", "C#%", "base_absorption_speed#kg.week-1", "bag#kg"]

    def reset(self):
        X = self.field.X
        Y = self.field.Y

        self.variables["amount#kg"] = fillarray(
            X, Y, (0, 1000), 0.0
        )  # np.full((X,Y),fill_value=Range((0,1000),0.))
        self.initialize_variables(self.initial_conditions)

    def update_variables(self, field, entities):
        # TODO: Add leaching?
        pass

    def release_nutrients(self, position, soil):
        r = {"N": 0.0, "K": 0.0, "P": 0.0, "C": 0.0}  # 'Water':(0.,1.)}
        amount = (
            self.variables["amount#kg"][position].value
            * self.parameters["base_absorption_speed#kg.week-1"]
            / 7.0
            * (soil.variables["microlife_health_index#%"][position].value / 100.0)
        )
        for n in ["N", "K", "P", "C"]:
            r[n] = self.parameters[n + "#%"] * amount
        self.variables["amount#kg"][position].set_value(
            max(0, self.variables["amount#kg"][position].value - amount)
        )
        return r

    def act_on_variables(self, action_name, action_params):
        self.assert_action(action_name, action_params)
        if action_name == "scatter":
            x, y = action_params["plot"]
            self.variables["amount#kg"][x, y].set_value(
                self.variables["amount#kg"][x, y].value + action_params["amount#kg"]
            )
            self.variables["total_cumulated_scattered_amount#kg"].set_value(
                self.variables["total_cumulated_scattered_amount#kg"].value
                + action_params["amount#kg"]
            )

        elif action_name == "scatter_bag":
            x, y = action_params["plot"]
            self.variables["amount#kg"][x, y].set_value(
                self.variables["amount#kg"][x, y].value
                + action_params["amount#bag"] * self.parameters["bag#kg"]
            )
            self.variables["total_cumulated_scattered_amount#kg"].set_value(
                self.variables["total_cumulated_scattered_amount#kg"].value
                + action_params["amount#bag"] * self.parameters["bag#kg"]
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
                if self.variables["amount#kg"][x, y].value > 0:
                    image.paste(self.images["some"], (im_width * x, im_height * y))
        return image
