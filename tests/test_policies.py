import pytest

from farmgym.v2.policy_api import Policy_API


@pytest.fixture
def and_conditions_policy():
    fi, idx, loc = 0, 0, (0, 0)
    frequency = 5
    threshold = 2.0
    scatter_conditions = [
        [
            ((f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc]), lambda x: x, ">=", float(threshold)),
            ((f"Field-{fi}", "Weather-0", "day#int365", []), lambda x: x % frequency, "==", 0),
        ]
    ]
    scatter_cide = (scatter_conditions, [])
    policy = Policy_API([], [scatter_cide])
    return policy


def test_and_condition_true(and_conditions_policy):
    policy = and_conditions_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 360),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 718),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]

    assert trigger_on, "Both conditions are satisified in current obs, should trigger"


def test_and_condition_false(and_conditions_policy):
    policy = and_conditions_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 361),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 718),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert not trigger_on, "At least one condition is not satisfied in obs, should not trigger"


@pytest.fixture
def single_condition_policy():
    fi, idx, loc = 0, 0, (0, 0)
    threshold = 2.0
    scatter_conditions = [[((f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc]), lambda x: x, ">=", float(threshold))]]
    scatter_cide = (scatter_conditions, [])
    policy = Policy_API([], [scatter_cide])
    return policy


def test_single_condition_true(single_condition_policy):
    policy = single_condition_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 360),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 718),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert trigger_on, "Observation does not match condition, should not trigger"


def test_single_condition_false(single_condition_policy):
    policy = single_condition_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 360),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 1),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert not trigger_on, "Observation does not match condition, should not trigger"


@pytest.fixture
def or_conditions_policy():
    fi, idx, loc = 0, 0, (0, 0)
    threshold = 2.0
    frequency = 5
    scatter_conditions = [
        [((f"Field-{fi}", f"Weeds-{idx}", "grow#nb", [loc]), lambda x: x, ">=", float(threshold))],
        [((f"Field-{fi}", "Weather-0", "day#int365", []), lambda x: x % frequency, "==", 0)],
    ]
    scatter_cide = (scatter_conditions, [])
    policy = Policy_API([], [scatter_cide])
    return policy


def test_or_condition_one_true(or_conditions_policy):
    policy = or_conditions_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 360),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 1),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert trigger_on, "One condition is verified at least, should trigger"


def test_or_condition_false(or_conditions_policy):
    policy = or_conditions_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 361),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 1),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert not trigger_on, "No condition is verified, should not trigger"


def test_or_condition_all_true(or_conditions_policy):
    policy = or_conditions_policy
    obs = [
        ("Free", "Field-0", "Weather-0", "day#int365", [], 360),
        ("Free", "Field-0", "Weather-0", "sun_exposure#int5", [], 0),
        ("Free", "Field-0", "Weeds-0", "grow#nb", [(0, 0)], 3),
    ]
    for trigger, actions in policy.triggered_interventions:
        trigger_on = policy.is_trigger_on(trigger, obs) or trigger == [[]]
    assert trigger_on, "Both conditions are verified, should trigger"
