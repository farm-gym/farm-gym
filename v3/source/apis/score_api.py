import yaml


class Score_API:
    """
    class for scoring definition
    """

    def __init__(self, score_configuration=""):
        self.score_configuration = score_configuration

    def setup(self, farm):
        if isinstance(self.score_configuration, dict):
            self.score_parameters = self.score_configuration
        else:
            string = self.score_configuration
            with open(string, "r", encoding="utf8") as file:
                doc_yaml = yaml.safe_load(file)  # Note the safe_load
                self.score_parameters = doc_yaml

    def intervention_cost(self, farmer, field_key, entity_key, action_key, params):
        return 0

    def observation_cost(
        self, farmer, field, field_key, entity_key, variable_key, path
    ):
        return 0

    def reward(self, entities_list: list):
        return 0

    def final_reward(self, entities_list: list):
        return 0
