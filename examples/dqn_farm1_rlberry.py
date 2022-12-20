"""
rlberry DQN on Farm1 from farm-gym-games
========================================

This example use farm-gym-games and rlberry, please install these libraries before using.

pip install git+https://github.com/rlberry-py/rlberry.git
pip install git+https://github.com/farm-gym/farm-gym-games
"""


import farmgym_games
import numpy as np
from rlberry.envs import gym_make

from rlberry.agents.torch import DQNAgent
from rlberry.manager import AgentManager, evaluate_agents, plot_writer_data
from rlberry.agents.torch.utils.training import model_factory_from_env

import pandas as pd
import seaborn as sns
import time

actions_txt = ["doing nothing",
               "1L of water",
               "5L of water",
               "harvesting",
               "sow some seeds",
               "scatter fertilizer",
               "scatter herbicide",
               "scatter pesticide",
               "remove weeds by hand",]


env_ctor, env_kwargs = gym_make, {"id": "Farm1-v0"}

if __name__ == "__main__":
    manager = AgentManager(
        DQNAgent,
        (env_ctor, env_kwargs),
        agent_name="DQNAgent",
        init_kwargs=dict(
            learning_rate=9e-5,
        ),
        fit_budget=5e5,
        eval_kwargs=dict(eval_horizon=365),
        n_fit=1,
        parallelization="process",
        mp_context="spawn",
        enable_tensorboard=True,
    )

    init_time = time.time()
    manager.fit()
    print("training time in s is ", time.time()-init_time())
    data = plot_writer_data(manager, tag="episode_rewards", smooth_weight=0.8) # smoothing tensorboard-style

    plt.savefig('dqn_regret.pdf')

    agent = manager.agent_handlers[0] # select the agent from the manager
    env = Farm1()
    obs = env.reset()


    episode = pd.DataFrame()
    for day in range(365):
        action = agent.policy(obs)
        obs,reward, is_done,_ =  env.step(action)
        episode = pd.concat([episode, pd.DataFrame({'action':[actions_txt[action]],
                                                    'reward':[reward]})], ignore_index=True)
        if is_done:
            print('Plant is Dead')
            break
    fig, ax = plt.subplots(figsize=(12,6))
    sns.countplot(data = episode, x = "action", ax = ax)
    fig.savefig('dqn_boxplot.pdf')
