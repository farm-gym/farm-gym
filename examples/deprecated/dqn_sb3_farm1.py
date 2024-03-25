"""
DQN from stablebaselines3 on Farm 1
===================================

This example use farm-gym-games and stablebaselines3, please install these libraries before using.

pip install stablebaselines3
pip install git+https://github.com/farm-gym/farm-gym-games
"""


import farmgym_games
from rlberry.envs import gym_make
from stable_baselines3 import DQN


env = gym_make("OldV21Farm1-v0")  # compatibility version

if __name__ == "__main__":
    model = DQN("MlpPolicy", env, verbose=1)
    # Training
    model.learn(total_timesteps=5e5, log_interval=4)
    # Evaluation

    obs = env.reset()
    ep_rew = 0
    n_episodes = 0
    while True:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        ep_rew += reward
        if done:
            obs = env.reset()
            print(f"Episode Reward on evaluation was {ep_rew}")
            ep_rew = 0
            n_episodes += 1
            if n_episodes == 5:  # Look at only 5 evaluation episodes
                break
