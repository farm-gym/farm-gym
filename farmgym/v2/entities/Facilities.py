# ruff: noqa: F841
from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range


class Facility(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        X = self.field.X
        Y = self.field.Y

        self.variables = {}
        self.variables["scarecrow"] = Range(["none", "basic", "advanced"], "none")

        # Actions
        self.actions = {
            "put_scarecrow": {"type": ["basic", "advanced"]},
            "remove_scarecrow": {},
        }  # we could list different types of scare_crows....

    def get_parameter_keys(self):
        return ["scarecrow_strength"]

    # TODO: Add effective time parameter, saying for how long the scarecrw is actually working ?.

    def scarecrow_strength(self, value):
        return self.parameters["scarecrow_strength"][value]

    def reset(self):
        self.initialize_variables(self.initial_conditions)
        if "scarecrow" not in self.initial_conditions:
            self.variables["scarecrow"].set_value("none")

    def update_variables(self, field, entities):
        pass

    def act_on_variables(self, action_name, action_params):
        self.assert_action(action_name, action_params)
        if action_name == "put_scarecrow":
            self.variables["scarecrow"].set_value(action_params["type"])
        if action_name == "remove_scarecrow":
            self.variables["scarecrow"].set_value("none")

    def to_thumbnailimage(self):
        im_width, im_height = 64, 64
        image = Image.new("RGBA", (im_width, im_height), (255, 255, 255, 0))
        if self.variables["scarecrow"].value != "none":
            image.paste(
                self.images["scarecrow-" + self.variables["scarecrow"].value], (0, 0)
            )
        return image
