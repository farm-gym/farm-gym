import os
import re

import yaml
from farmgym.v2.specifications.specification_manager import (
    build_actionsyaml,
    build_inityaml,
    build_scoreyaml,
    load_yaml,
)


# Create a sample farm with fields and entities
class Entity:
    def __init__(self, name, variables, actions):
        self.name = name
        self.actions = actions
        self.variables = variables


class Field:
    def __init__(self, name, entities):
        self.name = name
        self.entities = entities


class Farm:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


class Variable:
    def __init__(self, name):
        self.name = name


def test_load_yaml(tmp_path):
    # Create a temporary YAML file with some data
    spec_file = "test_specifications.yaml"
    spec_data = {"param1": "value1", "param2": "value2", "param3": "value3"}
    yaml_file = tmp_path / spec_file
    with open(yaml_file, "w") as file:
        yaml.dump(spec_data, file)

    # Test the load_yaml function
    parameter_string = "param2"
    loaded_data = load_yaml(str(yaml_file), parameter_string)

    # Assert the loaded data is as expected
    assert loaded_data == "value2"


def test_build_scoreyaml(tmp_path):
    # Create a temporary file path
    filepath = os.path.join(tmp_path, "score.yaml")

    fields = {
        "field1": Field(
            "field1",
            {
                "entity1": Entity("entity1", ["var1"], ["action1", "action2"]),
                "entity2": Entity("entity2", [], ["action3"]),
            },
        ),
        "field2": Field("field2", {"entity3": Entity("entity3", ["var1", "var2"], [])}),
    }

    farm = Farm("test", fields)

    # Test the build_scoreyaml function
    build_scoreyaml(filepath, farm)

    # Assert the content of the created file is as expected
    with open(filepath, "r", encoding="utf8") as file:
        content = file.read()
        expected_content = """observation-cost:
  field1:
    entity1:
    var1: 1
    entity2:
  field2:
    entity3:
    var1: 1
    var2: 1
intervention-cost:
    field1:
        entity1:
        action1: 1
        action2: 1
        entity2:
        action3: 1
    field2:
    reward-mix:
        weight_biodiversitycounts: 0.
        weight_resourceadded: 0.
        weight_soilmicrolife: 0.
        weight_harvest: 0.
        weight_stagecount: 0.
        weight_stagetransition: 1.
    final-reward-mix:
        weight_biodiversitycounts: 0.
        weight_resourceadded: 0.
        weight_soilmicrolife: 0.
        weight_harvest: 1.
        weight_stagecount: 0.
        weight_stagetransition: 0.

    """
    content = re.sub(r"[\n\t\s]*", "", content)
    expected_content = re.sub(r"[\n\t\s]*", "", expected_content)
    assert content == expected_content


def test_build_inityaml(tmp_path):
    # Create a temporary file path
    filepath = os.path.join(tmp_path, "init.yaml")

    class Entity:
        def __init__(self, name, variables):
            self.name = name
            self.variables = variables

    fields = {
        "field1": Field(
            "field1",
            {
                "entity1": Entity(
                    "entity1",
                    {
                        "variable1": Variable("variable1"),
                        "variable2": Variable("variable2"),
                    },
                ),
                "entity2": Entity("entity2", {"variable3": Variable("variable3")}),
            },
        ),
        "field2": Field(
            "field2",
            {"entity3": Entity("entity3", {"variable4": Variable("variable4")})},
        ),
    }

    farm = Farm("test", fields)

    # Test the build_inityaml function
    build_inityaml(filepath, farm=farm, mode="default")

    # Assert the content of the created file is as expected
    with open(filepath, "r", encoding="utf8") as file:
        content = file.read()
        expected_content = """Initial:
    field1:
        entity1:
        variable1: ???
        variable2: ???
        entity2:
        variable3: ???
    field2:
        entity3:
        variable4: ???
    Terminal:
    [
        [{state_variable: ["Field-0", "Weather-0", "day#int365", []],
         function: "value", operator: ">=", ref_value: 360}],
        [{state_variable: ["Field-0", "Plant-0", "global_stage", []],
         function: "value", operator: "==", ref_value: "dead"}],
    ]

    """
    content = re.sub(r"[\n\t\s]*", "", content)
    expected_content = re.sub(r"[\n\t\s]*", "", expected_content)
    assert content == expected_content


def test_build_actionsyaml(tmp_path):
    # Create a temporary file path
    filepath = os.path.join(tmp_path, "actions.yaml")

    class Farm:
        def __init__(self, name, fields, farmers):
            self.name = name
            self.fields = fields
            self.farmers = farmers

    fields = {
        "field1": Field(
            "field1",
            {
                "entity1": Entity(
                    "entity1",
                    {
                        "variable1": Variable("variable1"),
                        "variable2": Variable("variable2"),
                    },
                    {"action1": {"remove": {"plot": [(0, 0)]}}},
                ),
                "entity2": Entity("entity2", {"variable3": Variable("variable3")}, {}),
            },
        ),
        "field2": Field(
            "field2",
            {"entity3": Entity("entity3", {"variable4": Variable("variable4")}, {})},
        ),
    }

    farm = Farm("test", fields, ["farmer1", "farmer2"])

    # Test the build_actionsyaml function
    build_actionsyaml(filepath, farm)

    # Assert the content of the created file is as expected
    with open(filepath, "r", encoding="utf8") as file:
        content = file.read()
        expected_content = """params:
    max_action_schedule_size: 5
    number_of_bins_to_discretize_continuous_actions: 11
    observations:
    Free:
        Field-0:
        Weather-0:
            day#int365: 
            air_temperature: 
            '*':
    farmer1:
        field1:
        entity1:
            variable1: ???
            variable2: ???
        entity2:
            variable3: ???
        field2:
        entity3:
            variable4: ???
    farmer2:
        field1:
        entity1:
            variable1: ???
            variable2: ???
        entity2:
            variable3: ???
        field2:
        entity3:
            variable4: ???
    interventions:
    farmer1:
        field1:
        entity1:
            action1: 
            remove: {'plot': [(0, 0)]}
        field2:
    farmer2:
        field1:
        entity1:
            action1: 
            remove: {'plot': [(0, 0)]}
        field2:
    """
    content = re.sub(r"[\n\t\s]*", "", content)
    expected_content = re.sub(r"[\n\t\s]*", "", expected_content)
    assert content == expected_content
