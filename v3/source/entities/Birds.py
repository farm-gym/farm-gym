from PIL import Image

from farmgym.v2.entity_api import Entity_API, Range, checkissubclass


class Birds(Entity_API):
    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)

        self.variables = {}
        self.variables["population#nb"] = Range((0, 100000), 0.0)
        self.variables["total_cumulated_birds#nb"] = Range((0, 1000000), 0.0)

        # Actions
        self.actions = {}

    def get_parameter_keys(self):
        return ["seed_eater", "pest_eater", "pollinator_eater", "max_population"]

    def reset(self):
        self.initialize_variables(self.initial_conditions)
        if "population#nb" not in self.initial_conditions:
            self.variables["population#nb"].set_value(0.0)

    def update_variables(self, field, entities):
        facilities = [
            entities[e]
            for e in entities
            if checkissubclass(entities[e].__class__, "Facility")
        ]

        strength_scarecrow = 0
        for f in facilities:
            strength_scarecrow += f.parameters["scarecrow_strength"][
                f.variables["scarecrow"].value
            ]

        self.variables["population#nb"].set_value(
            max(
                self.np_random.integers(0, self.parameters["max_population"])
                - strength_scarecrow,
                0,
            )
        )

        self.variables["total_cumulated_birds#nb"].set_value(
            self.variables["total_cumulated_birds#nb"].value
            + self.variables["population#nb"].value
        )

    def act_on_variables(self, action_name, action_params):
        pass

    def to_thumbnailimage(self):
        im_width, im_height = 64, 64
        image = Image.new("RGBA", (im_width, im_height), (255, 255, 255, 0))
        if self.variables["population#nb"].value > 0:
            if self.variables["population#nb"].value > 2:
                image.paste(self.images["many"], (0, 0))
            else:
                image.paste(self.images["few"], (0, 0))
        return image
