import copy
import os
import time
import numpy as np
from gym.utils.env_checker import check_env
import gym

from farmgym.v2.farm import generate_video, generate_gif

from distutils.version import LooseVersion


class Farmgym_Agent:
    def __init__(self):
        self.farm = None

    def reset(self, farm):
        self.farm = farm

    def init(self, observation):
        pass

    def update(self, obs, reward, terminated, truncated, info):
        pass

    def choose_action(self):
        raise NotImplemented
        # return self.farm.action_space.sample()


class Farmgym_RandomAgent(Farmgym_Agent):
    def __init__(self, mode="POMDP"):
        super(Farmgym_RandomAgent, self).__init__()
        self.x = 1
        self.mode = mode

    def choose_action(self):
        #if self.mode == "POMDP":
            self.x += 0.25
            threshold = 10 / self.x
            if np.random.rand() > threshold:
                return [27]
            return self.farm.action_space.sample()


def run_gym_xp(farm, agent, max_steps=np.infty, render=True, monitoring=False):
    agent.reset(farm)
    observation, information = farm.reset()
    if render == "text":
        print("Initial step:")
        print(farm.render_step([], observation, 0, False, False, information))
        print("###################################")
    elif render == "image":
        time_tag = time.time()
        os.mkdir("run-" + str(time_tag))
        os.chdir("run-" + str(time_tag))
        farm.render()
    agent.init(observation)

    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:

        action = agent.choose_action()
        obs, reward, terminated, truncated, info = farm.step(action)
        if render == "text":
            print(farm.render_step(action, obs, reward, terminated, truncated, info))
            print("###################################")
        elif render == "image":
            farm.render()
        agent.update(obs, reward, terminated, truncated, info)
        i += 1
    if render == "image":
        farm.render()
        generate_video(image_folder=".", video_name="farm.avi")
        os.chdir("../")


def run_xps(farm, policy, max_steps=np.infty, nb_replicate=100):

    if farm.monitor != None:
        farm.monitor = None

    cumrewards = []
    cumcosts = []

    for n in range(nb_replicate):
        cumreward = 0.0
        cumcost = 0.0

        policy.reset()
        observation = farm.farmgym_reset()
        # check_env(farm)
        is_done = False
        i = 0
        while (not is_done) and i <= max_steps:

            # observation= [((None,'Field-0', 'Weather-0', 'day#int365', [], (farm.fields['Field-0'].entities['Weather-0'].observe_variable('day#int365', []))))]
            observations = farm.get_free_observations()
            # print("FREE observations", observations)
            observation_schedule = policy.observation_schedule(
                observations
            )  # Actually, farmgym step  returns freeobservations of the day already, so better to consider observation_schedule = policy.observation_schedule()
            observation, _, _, info = farm.farmgym_step(observation_schedule)
            obs_cost = info["observation cost"]
            # obs1, obs_cost, _, _ = farm.step(farm.action_space.sample())
            # print(observations, observation,info)
            # print(farm.render_step(observation_schedule, observation, _, _, info))

            intervention_schedule = policy.intervention_schedule(observation)
            obs, reward, is_done, info = farm.farmgym_step(intervention_schedule)
            int_cost = info["intervention cost"]
            # print(obs,reward,is_done,info)

            cumreward += reward
            cumcost += obs_cost + int_cost
            i = i + 1
        cumrewards.append(cumreward)
        cumcosts.append(cumcost)
    return cumrewards, cumcosts


def run_randomactions(farm, max_steps=np.infty, render="", monitoring=True):
    #   if LooseVersion(gym.__version__) >= LooseVersion("0.25.2"):
    #        check_env(farm)
    # Gym 0.21 has bugs: does not support dictionaries for instance, it has the following:
    # def _is_numpy_array_space(space: spaces.Space) -> bool:
    #    """
    #    Returns False if provided space is not representable as a single numpy array
    #    (e.g. Dict and Tuple spaces return False)
    #    """
    #    return not isinstance(space, (spaces.Dict, spaces.Tuple))
    # Also it cannot check for NaNs beyond basic spaces (Dict, Tuple, Array).

    proba_observe = 0.8
    proba_intervene = 0.4

    time_tag = time.time()
    os.mkdir("run-" + str(time_tag))
    os.chdir("run-" + str(time_tag))

    if not monitoring:
        if farm.monitor != None:
            farm.monitor = None
    if render:
        print(farm)
        print("##############################################")

    cumreward = 0.0
    cumrewards = []
    cumcost = 0.0
    cumcosts = []

    observation = farm.reset()
    if render:
        print("Initial observations", observation)

    # check_env(farm)
    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:
        if render:
            print("[FarmGym] Step\t", i)
            farm.render()

        observation_schedule = []
        if np.random.rand() < proba_observe:
            a = farm.random_allowed_observation()
            if a != None:
                observation_schedule.append(a)
        obs1, _, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]
        # obs1, obs_cost, _, _ = farm.step(farm.action_space.sample())

        if render:
            print("Observation step:")
            [print("\tScheduled:\t", o) for o in observation_schedule]
            [print("\tObserved:\t", o) for o in obs1]
            print("\tInformation:\t", info)

        intervention_schedule = []
        if np.random.rand() < proba_intervene:
            intervention_schedule.append(farm.random_allowed_intervention())
            # TODO: BUG on Aborted interventions ? Some are still executed!
            # intervention_schedule.append(farm.random_allowed_intervention())
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        int_cost = info["intervention cost"]
        # obs, reward, is_done, info = farm.step(farm.action_space.sample())

        if render:
            print("Intervention step:")
            [print("\tScheduled:\t", o) for o in intervention_schedule]
            [print("\tObserved:\t", o) for o in obs]
            print("\tReward:\t", reward)
            print("\tIs terminated:\t", terminated)
            print("\tIs truncated:\t", truncated)
            print("\tInformation:\t", info)

        cumreward += reward
        cumrewards.append(cumreward)
        cumcost += obs_cost + int_cost
        cumcosts.append(cumcost)
        i = i + 1

    if render:
        farm.render()
        generate_video(image_folder=".", video_name="farm.avi")
        # generate_gif(image_folder='.', video_name='farm.gif')
        print("##############################################")

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

    return cumrewards, cumcosts


def run_policy(farm, policy, max_steps=np.infty, render=True, monitoring=True):

    time_tag = time.time()
    os.mkdir("run-" + str(time_tag))
    os.chdir("run-" + str(time_tag))

    if not monitoring:
        if farm.monitor != None:
            farm.monitor = None
    if render:
        print(farm)
        print("##############################################")

    cumreward = 0.0
    cumrewards = []
    cumcost = 0.0
    cumcosts = []

    policy.reset()
    observation = farm.reset()
    if render:
        print("Initial observations", observation)

    # check_env(farm)
    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:
        if render:
            print("[FarmGym] Step\t", i)
            farm.render()

        # observation= [((None,'Field-0', 'Weather-0', 'day#int365', [], (farm.fields['Field-0'].entities['Weather-0'].observe_variable('day#int365', []))))]
        observations = farm.get_free_observations()
        # print("FREE observations", observations)
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]
        # obs1, obs_cost, _, _ = farm.step(farm.action_space.sample())

        if render:
            print("Observation step:")
            [print("\tScheduled:\t", o) for o in observation_schedule]
            [print("\tObserved:\t", o) for o in observation]
            print("\tInformation:\t", info)

        intervention_schedule = policy.intervention_schedule(observation)
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        int_cost = info["intervention cost"]

        if render:
            print("Intervention step:")
            [print("\tScheduled:\t", o) for o in intervention_schedule]
            [print("\tObserved:\t", o) for o in obs]
            print("\tReward:\t", reward)
            print("\tIs terminated:\t", terminated)
            print("\tIs truncated:\t", truncated)
            print("\tInformation:\t", info)

        cumreward += reward
        cumrewards.append(cumreward)
        cumcost += obs_cost + int_cost
        cumcosts.append(cumcost)
        i = i + 1

    if render:
        farm.render()
        generate_video(image_folder=".", video_name="farm.avi")
        generate_gif(image_folder=".", video_name="farm.gif")
        print("##############################################")

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

    return cumrewards, cumcosts


def run_policy_xp(farm, policy, max_steps=np.infty):
    if farm.monitor != None:
        farm.monitor = None

    cumreward = 0.0
    cumcost = 0.0

    policy.reset()
    observation = farm.reset()

    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]

        intervention_schedule = policy.intervention_schedule(observation)
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        int_cost = info["intervention cost"]

        cumreward += reward
        cumcost += obs_cost + int_cost
        i = i + 1

    return cumreward, cumcost


if __name__ == "__main__":
    import farmgym.v2.games.farms_1x1.clay_corn.farm as cc
    import farmgym.v2.games.farms_1x1.clay_bean.farm as cb
    import farmgym.v2.games.farms_1x1.clay_tomato.farm as ct
    import farmgym.v2.games.farms_3x4.clay_bean_weeds.farm as cbw

    # understand_the_farm(cbw.env())
    # understand_the_farm(cc.env())

    farm = ct.env()
    farm.understand_the_farm()
    # understand_the_farm(cb.env())
    # run_randomactions(cb.env(), max_steps=100, render=True, monitoring=False)

    from farmgym.v2.policy_api import Policy_API
    #
    # def make_policy():
    #     triggered_observations = []
    #
    #     trigger_constant = [[]]
    #     action_schedule1 = [("BasicFarmer-0", "Field-0", "Plant-0", "stage", [(0, 0)])]
    #     triggered_observations.append((trigger_constant, action_schedule1))
    #
    #     trigger_periodic = [[(("Field-0", "Weather-0", "day#int365", []), lambda x: x % 7, "==", 0)]]
    #     action_schedule2 = [("BasicFarmer-0", "Field-0", "Weather-0", "rain_amount", [])]
    #     triggered_observations.append((trigger_periodic, action_schedule2))
    #
    #     triggered_interventions = []
    #
    #     trigger_bloom = [
    #         [
    #             (
    #                 ("Field-0", "Plant-0", "stage", [(0, 0)]),
    #                 lambda x: x,
    #                 "==",
    #                 "entered_grow",
    #             )
    #         ]
    #     ]
    #     action_schedule3 = [
    #         {
    #             "action": (
    #                 "BasicFarmer-0",
    #                 "Field-0",
    #                 "Soil-0",
    #                 "water_discrete",
    #                 {"plot": (0, 0), "amount#L": 4, "duration#min": 30},
    #             ),
    #             "delay": 0,
    #         }
    #     ]
    #     triggered_interventions.append((trigger_bloom, action_schedule3))
    #
    #     return Policy_API("config-file", triggered_observations, triggered_interventions)

    # policy = make_policy()
    # run_xps(farm, policy, 10, 1)
    # run_policy(cb.env(), policy, max_steps=20, render=False, monitoring=True)
