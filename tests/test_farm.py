import os

import pytest

from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.farm import Farm
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.field import Field
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.scorings.BasicScore import BasicScore


@pytest.fixture
def sample_fields():
    # Define sample fields for testing
    entities = [(Weather, "dry"), (Soil, "clay"), (Plant, "bean")]
    field_infos = {
        "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
        "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
    }
    field = Field(
        localization=field_infos["localization"],
        shape=field_infos["shape"],
        entities_specifications=entities,
    )
    return [field]


@pytest.fixture
def sample_farmers():
    # Define sample farmers for testing
    farmers = [{"max_daily_interventions": 1}]
    farmers = [BasicFarmer(max_daily_interventions=f["max_daily_interventions"]) for f in farmers]
    return farmers


@pytest.fixture
def sample_scoring():
    # Define a sample scoring object for testing
    name_score = "test_score.yaml"
    scoring = BasicScore(score_configuration=name_score)
    return scoring


@pytest.fixture
def sample_rules():
    # Define a sample rules object for testing
    name_init = "test_init.yaml"
    name_actions = "test_actions.yaml"
    rules = BasicRule(
        init_configuration=name_init,
        actions_configuration=name_actions,
    )
    return rules


@pytest.fixture
def sample_policies():
    # Define sample policies for testing
    policies = []
    return policies


@pytest.fixture
def sample_farm(sample_fields, sample_farmers, sample_scoring, sample_rules, sample_policies):
    # Define sample farm for testing
    farm = Farm(sample_fields, sample_farmers, sample_scoring, sample_rules, sample_policies)
    return farm


def test_farm_initialization(sample_fields, sample_farmers, sample_scoring, sample_rules, sample_policies):
    # Create an instance of the Farm class
    farm = Farm(sample_fields, sample_farmers, sample_scoring, sample_rules, sample_policies)

    # Verify the initialization of fields, farmers, scoring, rules, and policies
    assert farm.fields == {field.name: field for field in sample_fields}
    assert farm.farmers == {farmer.name: farmer for farmer in sample_farmers}
    assert farm.scoring == sample_scoring
    assert farm.rules == sample_rules
    assert farm.policies == sample_policies

    # Verify the interaction mode is set correctly
    assert farm.interaction_mode == "AOMDP"


def test_build_name(sample_farm):
    farm = sample_farm
    expected_name = "Farm_Fields[Field-0[Weather-0(dry)_Soil-0(clay)_Plant-0(bean)]]_Farmers[BasicFarmer-0]"
    assert farm.build_name() == expected_name


def test_build_shortname(sample_farm):
    farm = sample_farm
    expected_shortname = "farm_1x1(dry_clay_bean)"
    assert farm.build_shortname() == expected_shortname
    # Clean folder
    files_to_remove = ["test_actions.yaml", "test_init.yaml", "test_score.yaml"]
    for file in files_to_remove:
        os.remove(file)
