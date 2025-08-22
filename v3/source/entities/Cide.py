from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, fillarray


class Cide(Entity_API):
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
        return [
            "weeds",
            "pollinators",
            "pests",
            "soil",
            "base_absorption_speed#kg.week-1",
            "bag#kg",
        ]

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

    def release(self, position):
        amount = min(
            self.parameters["base_absorption_speed#kg.week-1"] / 7.0,
            self.variables["amount#kg"][position].value,
        )
        self.variables["amount#kg"][position].set_value(
            max(0, self.variables["amount#kg"][position].value - amount)
        )
        return amount

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
                if self.variables["amount#kg"][x, y].value > 0:
                    image.paste(self.images["some"], (im_width * x, im_height * y))
        return image
