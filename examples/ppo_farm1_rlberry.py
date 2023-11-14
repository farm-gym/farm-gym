"""
rlberry PPO on Farm1 from farm-gym-games
========================================

This example use farm-gym-games and rlberry, please install these libraries before using.

pip install git+https://github.com/rlberry-py/rlberry.git
pip install git+https://github.com/farm-gym/farm-gym-games
"""


import farmgym_games
import numpy as np
from rlberry.envs import gym_make

from rlberry.agents.torch import PPOAgent
from rlberry.manager import AgentManager, evaluate_agents, plot_writer_data
from rlberry.agents.torch.utils.training import model_factory_from_env

import pandas as pd
import seaborn as sns
import time
import matplotlib.pyplot as plt

policy_configs = {
    "type": "MultiLayerPerceptron",  # A network architecture
    "layer_sizes": (256, 256),  # Network dimensions
    "reshape": False,
    "is_policy": True,
}

value_configs = {
    "type": "MultiLayerPerceptron",
    "layer_sizes": (256, 256),
    "reshape": False,
    "out_size": 1,
}

actions_txt = [
    "doing nothing",
    "1L of water",
    "5L of water",
    "harvesting",
    "sow some seeds",
    "scatter fertilizer",
    "scatter herbicide",
    "scatter pesticide",
    "remove weeds by hand",
]

env_ctor, env_kwargs = gym_make, {"id": "OldV21Farm1-v0"}  # compatibility version

if __name__ == "__main__":
    manager = AgentManager(
        PPOAgent,
        (env_ctor, env_kwargs),
        agent_name="PPOAgent",
        init_kwargs=dict(
            policy_net_fn=model_factory_from_env,
            policy_net_kwargs=policy_configs,
            value_net_fn=model_factory_from_env,
            value_net_kwargs=value_configs,
            learning_rate=9e-5,
            n_steps=5 * 365,
            batch_size=365,
            eps_clip=0.1,
        ),
        fit_budget=5e5,
        eval_kwargs=dict(eval_horizon=365),
        n_fit=1,
        parallelization="process",
        mp_context="spawn",
        enable_tensorboard=True,
        seed=42,
    )

    init_time = time.time()
    manager.fit()
    manager.save()
    print("training time in s is ", time.time() - init_time)
    fig, ax = plt.subplots(figsize=(8, 4))
    data = plot_writer_data(
        manager, tag="episode_rewards", smooth_weight=0.8, ax=ax
    )  # smoothing tensorboard-style

    fig.savefig("ppo_regret.pdf")

    agent = manager.agent_handlers[0]  # select the agent from the manager
    env = gym_make("Farm1-v0")

    rew = 0
    while rew < 1:
        rew = 0
        obs = env.reset()
        episode = pd.DataFrame()
        for day in range(365):
            action = agent.policy(obs)
            obs, reward, is_done, _ = env.step(action)
            episode = pd.concat(
                [
                    episode,
                    pd.DataFrame({"action": [actions_txt[action]], "reward": [reward]}),
                ],
                ignore_index=True,
            )
            rew = rew + reward
            if is_done:
                print("Plant is Dead")
                break

        print(rew)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.countplot(
        data=episode, x="action", order=episode["action"].value_counts().index, ax=ax
    )
    fig.savefig("ppo_barplot.pdf")
