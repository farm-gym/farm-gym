import gym

from farmgym.v2.entities.Weather import Weather
from farmgym.v2.entities.Soil import Soil
from farmgym.v2.entities.Plant import Plant
from farmgym.v2.entities.Weeds import Weeds
from farmgym.v2.entities.Pests import Pests
from farmgym.v2.entities.Cide import Cide
from farmgym.v2.entities.Birds import Birds
from farmgym.v2.entities.Facilities import Facility
from farmgym.v2.entities.Fertilizer import Fertilizer
from farmgym.v2.entities.Pollinators import Pollinators

from farmgym.v2.games.register_all import register_all
from farmgym.v2.games.rungame import run_randomactions


import pytest

# TODO:
# - make all games deterministic (see test_games below, two env fail)
# - split this file in several files for better readability.
# - Actually assert things to check that it works and don't check only Runtime Error.


def test_farmgym():
    print("\nSTART")
    import gym
    from farmgym.v2.games.farms_1x1.clay_corn.farm import env

    farm = env()
    farm.farmgym_reset()

    print("NAME", farm.build_name())

    is_done = False
    nb_steps = 0
    while (not is_done) and (nb_steps < 10):
        observation_schedule = []
        observation_schedule.append(farm.random_allowed_observation())
        obs1, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]

        intervention_schedule = []
        intervention_schedule.append(farm.random_allowed_intervention())
        obs2, reward, is_done, info = farm.farmgym_step(intervention_schedule)
        int_cost = info["intervention cost"]
        nb_steps += 1

    print("DONE")


def test_check():
    print("\nSTART")
    from gym.utils.env_checker import check_env
    from farmgym.v2.games.farms_1x1.clay_corn.farm import env

    farm = env()
    for f in range(10):
        check_env(farm)

    print("DONE")


# def test_rlberry_check():
#     from rlberry.utils.check_env import check_env
#     from farmgym.v2.games.farms_1x1.clay_corn.farm import env
#
#     farm = env()
#     check_env(farm)


def test_gym():
    print("\nSTART")
    import gym
    from farmgym.v2.games.farms_1x1.clay_corn.farm import env

    farm = env()
    farm.reset()

    is_done = False
    nb_steps = 0
    while (not is_done) and (nb_steps < 10):
        action = farm.action_space.sample()
        obs, reward, is_done, info = farm.step(action)

        print("Step:")
        print("\tAction:", action)
        [print("\tObservations:", o) for o in obs]
        print("\tReward:", reward)
        print("\tIs done:", is_done)
        print("\tInformation:", info)

        nb_steps += 1

    print("DONE")


#####


def test_render():
    print("\nSTART")
    import gym

    from farmgym.v2.games.farms_1x1.clay_corn.farm import env
    from farmgym.v2.farm import generate_video

    farm = env()
    farm.reset()

    import os
    import time

    time_tag = time.time()
    os.mkdir("run-" + str(time_tag))
    os.chdir("run-" + str(time_tag))

    is_done = False
    nb_steps = 0
    while (not is_done) and (nb_steps < 10):
        farm.render()
        obs, reward, is_done, info = farm.step(farm.action_space.sample())
        nb_steps += 1
    generate_video(image_folder=".", video_name="farm.avi")

    os.chdir("../")

    print("DONE")


def test_register():
    print("\nSTART")
    import gym
    from farmgym.v2.games.register_all import register_all
    from farmgym.v2.games.rungame import run_randomactions

    env_list = register_all()

    # This is using gym 0.21.0 Note that gym 0.25.0 requires a second argument for make !
    env = gym.make(env_list[2])
    farm = env.unwrapped
    run_randomactions(farm, max_steps=20, render=False, monitoring=False)

    print("DONE")


def test_farmgym_render_register():

    print("\nSTART")
    import gym
    from farmgym.v2.games.register_all import register_all
    import os
    import time
    import numpy as np
    from farmgym.v2.farm import generate_video, generate_gif

    env_list = register_all()
    env = gym.make(env_list[2])
    farm = env.unwrapped

    time_tag = time.time()
    os.mkdir("run-" + str(time_tag))
    os.chdir("run-" + str(time_tag))

    cumreward = 0.0
    cumrewards = []
    cumcost = 0.0
    cumcosts = []

    observation = farm.farmgym_reset()

    max_steps = 20
    is_done = False
    i = 0
    while (not is_done) and i <= max_steps:
        farm.render()

        observation_schedule = []
        if np.random.rand() > 0.3:
            observation_schedule.append(farm.random_allowed_observation())
        obs1, obs_cost, _, _ = farm.farmgym_step(observation_schedule)
        # obs1, obs_cost, _, _ = farm.step(farm.action_space.sample())

        intervention_schedule = []
        if np.random.rand() > 0.3:
            intervention_schedule.append(farm.random_allowed_intervention())
        obs, reward, is_done, info = farm.farmgym_step(intervention_schedule)
        # obs, reward, is_done, info = farm.step(farm.action_space.sample())

        cumreward += reward
        cumrewards.append(cumreward)
        cumcost += obs_cost + info["intervention cost"]
        cumcosts.append(cumcost)
        i = i + 1

    farm.render()
    generate_video(image_folder=".", video_name="farm.avi")
    # generate_gif(image_folder='.', video_name='farm.gif')

    import matplotlib.pyplot as plt

    plt.clf()
    plt.title("Cumulative rewards")
    plt.ylabel("Rewards")
    plt.xlabel("Days")
    plt.plot(cumrewards)
    plt.savefig("rewards.png")

    plt.clf()
    plt.title("Cumulative costs")
    plt.ylabel("Costs")
    plt.xlabel("Days")
    plt.plot(cumcosts)
    plt.savefig("costs.png")

    os.chdir("../")

    print("DONE")


def test_farmgym_policy():
    print("\nSTART")
    import gym
    from farmgym.v2.games.farms_1x1.clay_bean.farm import env

    farm = env()
    if farm.monitor != None:
        farm.monitor = None
    farm.farmgym_reset()

    policies = farm.policies
    policy = farm.np_random.choice(policies)

    is_done = False
    nb_steps = 0
    while (not is_done) and (nb_steps < 10):
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, info = farm.farmgym_step(observation_schedule)

        print("Observation step:")
        [print("\tScheduled:\t", o) for o in observation_schedule]
        [print("\tObserved:\t", o) for o in observation]
        print("\tInformation:\t", info)

        intervention_schedule = policy.intervention_schedule(observation)
        obs2, reward, is_done, info = farm.farmgym_step(intervention_schedule)

        print("Intervention step:")
        [print("\tScheduled:\t", o) for o in intervention_schedule]
        [print("\tObserved:\t", o) for o in obs2]
        print("\tReward:\t", reward)
        print("\tIs done:\t", is_done)
        print("\tInformation:\t", info)

        nb_steps += 1

    print("DONE")


ENTITIES = [
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn")],
    [(Weather, "dry"), (Soil, "sand"), (Plant, "corn")],
    [(Weather, "dry"), (Soil, "clay"), (Plant, "corn"), (Pollinators, "bee")],
    [(Weather, "dry"), (Soil, "clay"), (Plant, "tomato")],
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "tomato"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Pests, "basic"),
        (Cide, "herbicide_slow"),
    ],
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "tomato"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Cide, "herbicide_slow"),
    ],
    [
        (Weather, "dry"),
        (Soil, "clay"),
        (Plant, "corn"),
        (Pollinators, "bee"),
        (Weeds, "base_weed"),
        (Cide, "herbicide_slow"),
        (Cide, "pesticide"),
        (Facility, "base_facility"),
        (Birds, "base_bird"),
        (Fertilizer, "basic_N"),
    ],
]


@pytest.mark.parametrize("entities", ENTITIES)
def test_make_farm(entities):
    from farmgym.v2.games.make_farm import make_farm

    farm = make_farm(
        "farm_test",
        {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        },
        entities,
    )


ENV_NAMES = register_all()


@pytest.mark.parametrize("env_name", ENV_NAMES)
def test_games(env_name):
    if env_name not in ["farms_1x1_clay_bean-v0", "farms_3x4_clay_corn_weeds-v0"]:
        env = gym.make(env_name, 100)
        farm = env.unwrapped
        run_randomactions(farm, max_steps=3, render=False, monitoring=False)


INIT_STAGE = [
    "none",
    "seed",
    "entered_grow",
    "grow",
    "entered_bloom",
    "bloom",
    "entered_fruit",
    "fruit",
    "entered_ripe",
    "ripe",
    "entered_seed",
    "harvested",
    "dead",
]

FULL_ENTITY = [
    (Weather, "dry"),
    (Soil, "clay"),
    (Plant, "corn"),
    (Pollinators, "bee"),
    (Weeds, "base_weed"),
    (Cide, "herbicide_slow"),
    (Cide, "pesticide"),
    (Facility, "base_facility"),
    (Birds, "base_bird"),
    (Fertilizer, "basic_N"),
]


@pytest.mark.parametrize("stage", INIT_STAGE)
def test_stages(stage):
    from farmgym.v2.games.make_farm import make_farm
    from farmgym.v2.games.rungame import run_randomactions

    f = make_farm(
        "dry_clay_bean",
        {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        },
        FULL_ENTITY,
        init_values=[
            ("Field-0", "Weather-0", "day#int365", 120),
            ("Field-0", "Plant-0", "stage", stage),
            ("Field-0", "Soil-0", "available_N#g", 5000),
            ("Field-0", "Soil-0", "available_P#g", 5000),
            ("Field-0", "Soil-0", "available_K#g", 5000),
            ("Field-0", "Soil-0", "available_C#g", 5000),
        ],
    )
    run_randomactions(f, max_steps=5)


if __name__ == "__main__":
    pass
