import os
from unittest import mock

import pytest
from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Cide import Cide
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Pollinators import Pollinators
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.farm import Farm
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.field import Field
from farmgym.v2.policy_api import Policy_helper
from farmgym.v2.rendering.monitoring import MonitorTensorBoard, make_variables_to_be_monitored
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.scorings.BasicScore import BasicScore


@pytest.fixture
def sample_fields():
    # Define sample fields for testing
    entities = [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "bean"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Pests, "basic"),
        (Cide, "herbicide_slow"),
        (Fertilizer, "basic_N"),
        (Birds, "base_bird"),
    ]
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
    expected_name = (
        "Farm_Fields[Field-0[Weather-0(dry)_Soil-0(clay)_Plant-0(bean)"
        + "_Pollinators-0(bee)_Weeds-0(base_weed)_Pests-0(basic)_Cide-0(herbicide_slow)_F"
        + "ertilizer-0(basic_N)_Birds-0(base_bird)]]_Farmers[BasicFarmer-0]"
    )
    assert farm.build_name() == expected_name


def test_build_shortname(sample_farm):
    farm = sample_farm
    expected_shortname = "farm_1x1(dry_clay_bean_bee_base_weed_basic_herbicide_slow_basic_N_base_bird)"
    assert farm.build_shortname() == expected_shortname


fi = 0
idx = 0
loc = (0, 0)
POLICY_ACTIONS = [
    (
        "create_harvest_fruit",
        ("BasicFarmer-0", f"Field-{fi}", f"Plant-{idx}", "harvest", {}),
        [("Free", "Field-0", "Plant-0", "stage", [(0, 0)], "fruit")],
    ),
    (
        "create_scatter_cide",
        ("BasicFarmer-0", f"Field-{fi}", "Cide-0", "scatter", {"plot": loc, "amount#kg": 5}),
        [("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 4), ("Free", "Field-0", "Weather-0", "day#int365", [], 360)],
    ),
    (
        "create_remove_weeds",
        (("BasicFarmer-0", f"Field-{fi}", f"Weeds-{idx}", "remove", {"plot": loc})),
        [("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 4)],
    ),
    (
        "create_water_soil",
        ("BasicFarmer-0", "Field-0", "Soil-0", "water_discrete", {"amount#L": 5, "duration#min": 60, "plot": (0, 0)}),
        [],
    ),
    (
        "create_water_soil_continious",
        ("BasicFarmer-0", "Field-0", "Soil-0", "water_continuous", {"amount#L": 5, "duration#min": 60, "plot": (0, 0)}),
        [],
    ),
    (
        "create_scatter_fert",
        ("BasicFarmer-0", f"Field-{fi}", f"Fertilizer-{idx}", "scatter_bag", {"plot": loc, "amount#bag": 4}),
        [],
    ),
    ("create_put_scarecrow", ("BasicFarmer-0", f"Field-{fi}", f"Facility-{idx}", "put_scarecrow", {}), []),
]


@pytest.mark.parametrize("policy_tuple", POLICY_ACTIONS)
@pytest.mark.parametrize("delay", [0, 1, 5])
def test_policy_delay(sample_farm, delay, policy_tuple):
    farm = sample_farm
    helper = Policy_helper(farm)

    policy_name, action, condition = policy_tuple
    policy_creator = getattr(helper, policy_name)
    policy = policy_creator(delay=delay)
    policy = policy.api
    policy.reset()
    observation = farm.reset()
    i = 0
    while i < delay + 2:
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        observation += condition
        intervention_schedule = policy.intervention_schedule(observation)
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        if i < delay:
            assert action not in intervention_schedule
        if i == delay:
            assert action in intervention_schedule
        i = i + 1


@pytest.mark.parametrize("policy_tuple", POLICY_ACTIONS)
@pytest.mark.parametrize("frequency", [1, 3, 5])
def test_policy_frequency(sample_farm, frequency, policy_tuple):
    farm = sample_farm
    helper = Policy_helper(farm)

    policy_name, action, condition = policy_tuple
    policy_creator = getattr(helper, policy_name)
    policy = policy_creator(delay=0, frequency=frequency)
    policy = policy.api
    policy.reset()
    observation = farm.reset()
    i = 0
    while i < 2 * frequency + 2:
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        observation += condition
        intervention_schedule = policy.intervention_schedule(observation)
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        if i % frequency == 0:
            assert action in intervention_schedule
        else:
            assert action not in intervention_schedule
        i = i + 1


@pytest.fixture
def mock_tf_summary():
    with mock.patch("tensorflow.summary") as tf_summary:
        yield tf_summary


def test_monitor_tensorboard(mock_tf_summary, sample_farm):
    # Create a sample farm
    farm = sample_farm

    # Create a list of variables to monitor
    list_of_variables_to_monitor = make_variables_to_be_monitored(
        [
            "f0.soil.available_Water#L",
            "f0.weeds.flowers#nb.mat",
        ]
    )

    # Create an instance of MonitorTensorBoard
    monitor = MonitorTensorBoard(
        farm, list_of_variables_to_monitor, logdir="logs", run_name="test_run", matview=True, wait_for_exit=False
    )

    # Call the update_fig method
    monitor.update_fig()

    # Assert that the expected TensorFlow summary functions were called
    tf_summary = mock_tf_summary
    tf_summary.scalar.assert_called_once_with("Soil-0/Available Water (L) (Field-0, Soil-0)", mock.ANY, step=0)

    # Stop monitoring
    monitor.stop()


def test_clean_folder():
    """
    Not actually a test, removes created temp farms created for tests
    """
    # Clean folder
    files_to_remove = ["test_actions.yaml", "test_init.yaml", "test_score.yaml"]
    for file in files_to_remove:
        os.remove(file)
