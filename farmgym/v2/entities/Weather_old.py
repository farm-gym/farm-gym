import numpy as np
from PIL import Image

import farmgym.v2.specifications.specification_manager as sm
from farmgym.v2.entity_api import Entity_API, Range


class Weather(Entity_API):
    wind_directions = ["NW", "N", "NE", "W", "E", "SW", "S", "SE"]
    rain_amounts = ["None", "Light", "Heavy"]

    def __init__(self, field, parameters):
        Entity_API.__init__(self, field, parameters)
        self.localization = self.field.localization

        self.variables = {}

        # Global weather
        self.variables["year#int100"] = Range(list(range(100)), 0)
        self.variables["day#int365"] = Range(list(range(365)), 0)
        self.variables["air_temperature"] = {
            "max#°C": Range((-100, 100), 22.0),
            "mean#°C": Range((-100, 100), 20.0),
            "min#°C": Range((-100, 100), 18.0),
        }
        self.variables["humidity_index#%"] = Range((0.0, 100.0), 50.0)
        self.variables["wind"] = {
            "speed#km.h-1": Range((0.0, 500), 0.0),
            "direction": Range(self.wind_directions, "W"),
        }
        self.variables["sun_exposure#int5"] = Range(list(range(5)), 0)
        self.variables["rain_amount"] = Range(self.rain_amounts, "None")
        self.variables["rain_intensity"] = Range((0.0, 1.0), 0.0)

        self.variables["consecutive_frost#day"] = Range((0, 10000), 0.0)
        self.variables["consecutive_dry#day"] = Range((0, 10000), 0.0)

        self.variables["air_temperature.forecast"] = {
            "mean#°C": np.full(
                self.parameters["forecast_lookahead"],
                fill_value=Range((-100, 100), 20.0),
            ),
            "min#°C": np.full(
                self.parameters["forecast_lookahead"],
                fill_value=Range((-100, 100), 18.0),
            ),
            "max#°C": np.full(
                self.parameters["forecast_lookahead"],
                fill_value=Range((-100, 100), 22.0),
            ),
        }

        # self.year_weather = sm.load_weather_table(self.parameters["one_year_data_filename"])
        self.year_weathers, self.weather_alphas = sm.load_weather_table(
            self.parameters["one_year_data_filename"]
        )
        # Local weather

        # Actions
        self.actions = {}

        self.dependencies = {}

    def get_parameter_keys(self):
        return [
            "one_year_data_filename",
            "air_temperature_noise",
            "humidity_index_noise",
            "rain_lightheavy_proba",
            "rain_leakageintensity_light#%",
            "rain_leakageintensity_heavy#%",
            "forecast_lookahead",
            "forecast_noise",
        ]

    def reset(self):
        # print("WEATHER INIT", self.initial_conditions)
        self.initialize_variables(self.initial_conditions)
        # Init variables:

        if "year#int100" not in self.initial_conditions:
            self.variables["year#int100"].set_value((0))
        if "day#int365" not in self.initial_conditions:
            self.variables["day#int365"].set_value(((-1) % 365))
        else:
            self.variables["day#int365"].set_value(
                ((self.initial_conditions["day#int365"] - 1) % 365)
            )
        if "consecutive_frost#day" not in self.initial_conditions:
            self.variables["consecutive_frost#day"].set_value(0.0)
        if "cconsecutive_dry#day" not in self.initial_conditions:
            self.variables["consecutive_dry#day"].set_value(0.0)

        # if ('day#int365' in self.initial_conditions):
        #     day= self.initial_conditions['day#int365']
        # if ('consecutive_frost#day' in self.initial_conditions):
        #     self.variables["consecutive_frost#day"].set_value(self.initial_conditions['consecutive_frost#day'])
        # if ('cconsecutive_dry#day' in self.initial_conditions):
        #     self.variables["consecutive_dry#day"].set_value(self.initial_conditions['consecutive_dry#day'])

        self.update_variables(self.field, entities={})

    def update_variables(self, field, entities):
        day = (self.variables["day#int365"].value + 1) % 365
        if day == 0:
            self.variables["year#int100"].set_value(
                self.variables["year#int100"].value + 1
            )
        self.variables["day#int365"].set_value(((day) % 365))

        eps = self.np_random.normal(0, self.parameters["air_temperature_noise"], 1)[0]
        self.variables["air_temperature"]["mean#°C"].set_value(
            self.read_weathercsv("T", day % 365) + eps
        )
        self.variables["air_temperature"]["min#°C"].set_value(
            self.read_weathercsv("Tmin", day % 365) + eps
        )
        self.variables["air_temperature"]["max#°C"].set_value(
            self.read_weathercsv("Tmax", day % 365) + eps
        )

        if self.variables["air_temperature"]["min#°C"].value < 0:
            self.variables["consecutive_frost#day"].set_value(
                self.variables["consecutive_frost#day"].value + 1
            )
        else:
            self.variables["consecutive_frost#day"].set_value(0)

        self.variables["humidity_index#%"].set_value(
            self.read_weathercsv("RH", day % 365)
            + self.np_random.normal(0, self.parameters["humidity_index_noise"], 1)[0]
        )
        self.variables["wind"]["speed#km.h-1"].set_value(
            self.read_weathercsv("U", day % 365) + self.np_random.random()
        )
        self.variables["wind"]["direction"].set_value(
            self.np_random.choice(Weather.wind_directions, 1)[0]
        )
        self.variables["sun_exposure#int5"].set_value(self.np_random.integers(5))
        is_rain = self.read_weathercsv("Rain", day % 365)
        if is_rain > 0:
            self.variables["consecutive_dry#day"].set_value(0)
            self.variables["sun_exposure#int5"].set_value(0)
            self.variables["rain_amount"].set_value(
                "Light"
                if self.np_random.random() <= self.parameters["rain_lightheavy_proba"]
                else "Heavy"
            )
            self.variables["rain_intensity"].set_value(
                self.parameters["rain_leakageintensity_light#%"]
                if self.variables["rain_amount"].value == "Light"
                else self.parameters["rain_leakageintensity_heavy#%"]
            )
        else:
            self.variables["consecutive_dry#day"].set_value(
                self.variables["consecutive_dry#day"].value + 1
            )
            self.variables["rain_amount"].set_value("None")
            self.variables["rain_intensity"].set_value(0.0)

        self.variables["air_temperature.forecast"]["mean#°C"] = np.full(
            self.parameters["forecast_lookahead"], fill_value=Range((-100, 100), 0.0)
        )
        self.variables["air_temperature.forecast"]["min#°C"] = np.full(
            self.parameters["forecast_lookahead"], fill_value=Range((-100, 100), 0.0)
        )
        self.variables["air_temperature.forecast"]["max#°C"] = np.full(
            self.parameters["forecast_lookahead"], fill_value=Range((-100, 100), 0.0)
        )
        for i in range(self.parameters["forecast_lookahead"]):
            eps = self.np_random.normal(
                0,
                self.parameters["air_temperature_noise"]
                + self.parameters["forecast_noise"] * i,
                1,
            )[0]
            self.variables["air_temperature.forecast"]["mean#°C"][i].set_value(
                (self.read_weathercsv("T", (day + i) % 365) + eps)
            )
            self.variables["air_temperature.forecast"]["min#°C"][i].set_value(
                (self.read_weathercsv("Tmin", (day + i) % 365) + eps)
            )
            self.variables["air_temperature.forecast"]["max#°C"][i].set_value(
                (self.read_weathercsv("Tmax", (day + i) % 365) + eps)
            )

    def read_weathercsv(self, variable, day):
        value = 0
        # In case there are many weather files, this enables to interpolate between the values of each file:
        for i in range(len(self.weather_alphas)):
            # print("VAR",variable,"DAY",day,i,self.year_weathers[i][variable][day],self.weather_alphas[i])
            value += self.year_weathers[i][variable][day] * self.weather_alphas[i]
        return value

    def act_on_variables(self, action_name, action_params):
        pass

    def evapo_coefficient(self, field):  # in mL/m2
        day = self.variables["day#int365"].value
        phi = field.localization["longitude#°"]

        dr = 1 + 0.033 * np.cos(2 * np.pi * day / 365)
        delta = 0.409 * np.sin(2 * np.pi * day / 365 - 1.39)
        ws = np.arccos(-np.tan(np.pi / 180 * phi) * np.tan(delta))

        Gsc = 0.0820
        RA = (
            ((24 * 60) / np.pi)
            * Gsc
            * dr
            * (
                ws * np.sin(np.pi / 180 * phi) * np.sin(delta)
                + np.cos(ws) * np.cos(np.pi / 180 * phi) * np.cos(delta)
            )
        )

        rh = self.variables["humidity_index#%"].value
        tmin = self.variables["air_temperature"]["min#°C"].value
        tmax = self.variables["air_temperature"]["max#°C"].value
        t_av = self.variables["air_temperature"]["mean#°C"].value
        u = self.variables["wind"]["speed#km.h-1"].value

        # Base vaporation in mm per m2 per day
        return np.maximum(
            0,
            0.018
            * ((1 - rh / 100) ** (0.2))
            * (np.maximum(0, (tmax - tmin)) ** (0.3))
            * (RA * np.sqrt(np.maximum(0, t_av + 10)) - 40)
            + 0.1 * (t_av + 20) * (1 - rh / 100) * ((u / 2) ** 0.6),
        )

    def to_thumbnailimage(self):
        im_width, im_height = 64, 64
        image = Image.new("RGBA", (im_width, im_height), (255, 255, 255, 0))
        if self.variables["rain_amount"].value == "None":
            image.paste(self.images["sun"], (0, 0))
        if self.variables["rain_amount"].value == "Heavy":
            image.paste(self.images["rain-heavy"], (0, 0))
        if self.variables["rain_amount"].value == "Light":
            image.paste(self.images["rain-light"], (0, 0))
        return image
