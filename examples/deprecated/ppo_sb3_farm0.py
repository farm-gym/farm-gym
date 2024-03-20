import farmgym_games
from rlberry.envs import gym_make
from stable_baselines3 import PPO


env = gym_make("OldV21Farm0-v0")  # compatibility version

if __name__ == "__main__":
    model = PPO("MlpPolicy", env, verbose=1)
    # Training
    model.learn(total_timesteps=1e5, log_interval=4)
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
