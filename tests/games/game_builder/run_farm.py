import os
import time

import numpy as np
from farmgym.v2.farm import generate_video  # generate_gif


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

    if farm.monitor is not None:
        farm.monitor.stop()

    if render == "image":
        farm.render()
        generate_video(image_folder=".", video_name="farm.avi")
        os.chdir("../")


def run_policy_xp(farm, policy, max_steps=np.infty):
    if farm.monitor is not None:
        farm.monitor = None
    cumreward = 0.0
    cumcost = 0.0
    policy.reset()
    observation = farm.reset()
    terminated = False
    i = 0
    while (not terminated) and i <= max_steps:
        i += 1
        observations = farm.get_free_observations()
        observation_schedule = policy.observation_schedule(observations)
        observation, _, _, _, info = farm.farmgym_step(observation_schedule)
        obs_cost = info["observation cost"]
        intervention_schedule = policy.intervention_schedule(observation)
        obs, reward, terminated, truncated, info = farm.farmgym_step(intervention_schedule)
        int_cost = info["intervention cost"]
        cumreward += reward
        cumcost += obs_cost + int_cost
    return cumreward, cumcost
