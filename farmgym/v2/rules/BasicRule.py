from farmgym.v2.rules_api import Rules_API
import numpy as np


class BasicRule(Rules_API):
    def __init__(
        self,
        init_configuration,
        free_observations,
        actions_configuration,
        terminal_CNF_conditions,
        max_action_schedule_cost=np.infty,
        initial_conditions_values=None,
    ):
        Rules_API.__init__(
            self,
            init_configuration,
            free_observations,
            actions_configuration,
            terminal_CNF_conditions,
            initial_conditions_values=initial_conditions_values,
        )

        self.max_action_schedule_cost = max_action_schedule_cost
        self.current_day_action_schedule_cost = 0

    def assert_actions(self, actions):
        pass

    def filter_actions(self, farm, actions, is_observation_time):
        actions_schedule = []
        for a in actions:
            if self.is_allowed_action(a, is_observation_time):
                actions_schedule.append(a)
            else:
                print(
                    "[Farmgym:Rules] Action",
                    str(a),
                    "is not allowed by configured rules. Note that this is ",
                    "observation" if is_observation_time else "intervention",
                    "time.",
                )

        if farm.is_new_day:
            filtered = []
            total_cost = 0
            for observation_item in actions_schedule:
                fa_key, fi_key, entity, variable_key, path = observation_item
                # assert(action_type=='observe')
                # We can change this to policies using:
                # fa_key,fi_key,pos,action = policy_item.action(observations)
                cost = farm.scoring.observation_cost(
                    farm.farmers[fa_key],
                    farm.fields[fi_key],
                    fi_key,
                    entity,
                    variable_key,
                    path,
                )
                if total_cost + cost <= self.max_action_schedule_cost:
                    filtered.append(observation_item)
                    total_cost += cost
                else:
                    print("[Rules] Observation is too costly", str(observation_item))
            self.current_day_action_schedule_cost = total_cost
            return filtered

        else:
            filtered = []
            total_cost = self.current_day_action_schedule_cost
            for intervention_item in actions_schedule:
                fa_key, fi_key, entity_key, action_name, params = intervention_item
                cost = farm.scoring.intervention_cost(
                    fa_key, fi_key, entity_key, action_name, params
                )
                if total_cost + cost <= self.max_action_schedule_cost:
                    filtered.append(intervention_item)
                    total_cost += cost
                else:
                    print("[Rules] Intervention is too costly", str(intervention_item))
            self.current_day_action_schedule_cost = (
                0  # End of day: reset cost for next day.
            )
            return filtered
