import numpy as np

from farmgym.v2.farmer_api import Farmer_API


class BasicFarmer(Farmer_API):
    def __init__(self, max_daily_interventions=1, max_daily_observations=np.infty):
        Farmer_API.__init__(self)
        self.name = "BasicFarmer"

        self.can_observe = {}
        self.can_intervene = {}

        self.nb_interventions_in_day = 0
        self.nb_observations_in_day = 0
        self.max_daily_interventions = max_daily_interventions
        self.max_daily_observations = max_daily_observations

    def assign_field(self, field):
        Farmer_API.assign_field(self, field)
        self.can_observe[field.name] = True
        self.can_intervene[field.name] = True

    def set_authorization(self, field, can_observe, can_intervene):
        self.can_observe[field.name] = can_observe
        self.can_intervene[field.name] = can_intervene

    def update_to_next_day(self):
        self.nb_interventions_in_day = 0
        self.nb_observations_in_day = 0

    def perform_intervention(self, fi_key, entity_key, action, params, day):
        observations = []
        if (
            self.nb_interventions_in_day < self.max_daily_interventions
        ) and self.can_intervene[fi_key]:
            obs = (
                self.fields[fi_key]
                .entities[entity_key]
                .act_on_variables(action, params)
            )
            self.nb_interventions_in_day += 1
            # TODO: only works if obs is a single value. Not an array: pb with forecast?
            if obs is not None:
                observations.append(
                    (self.name, fi_key, entity_key, action, params, obs)
                )
        else:
            print(
                f"[Farmgym:Farmer, Day:{day}] Intervention",
                str((fi_key, entity_key, action, params)),
                "aborted by",
                self.name + ". Too many interventions today.",
            )

        return observations

    def perform_observation(self, fi_key, entity_key, variable_key, path, day):
        observations = []
        if (
            self.nb_observations_in_day < self.max_daily_observations
        ) and self.can_observe[fi_key]:
            obs = (
                self.fields[fi_key]
                .entities[entity_key]
                .observe_variable(variable_key, path)
            )
            self.nb_observations_in_day += 1
            # TODO: !! Some actions return no observations, some return a single value, some return a vector (e.g. Forecast).
            if obs is not None:
                observations.append(
                    (self.name, fi_key, entity_key, variable_key, path, obs)
                )
        else:
            print(
                f"[Farmgym:Farmer, Day:{day}] Observation",
                str((fi_key, entity_key, variable_key, path)),
                "aborted by",
                self.name + ". Too many observations today.",
            )
        return observations

    def __str__(self):
        s = self.name + ":"
        for f in self.fields:
            s += (
                "\n\t"
                + f
                + " Observation authorization: "
                + ("Y" if self.can_observe[f] else "N")
                + ". Maximum observations per day: "
                + str(self.max_daily_observations)
                + "."
            )
            s += (
                "\n\t"
                + f
                + " Intervention authorization: "
                + ("Y" if self.can_intervene[f] else "N")
                + ". Maximum interventions per day: "
                + str(self.max_daily_interventions)
                + "."
                + "\n"
            )
        return s
