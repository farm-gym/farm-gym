import numpy as np


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
        raise NotImplementedError
        # return self.farm.action_space.sample()


class Farmgym_RandomAgent(Farmgym_Agent):
    def __init__(self, mode="POMDP"):
        super(Farmgym_RandomAgent, self).__init__()
        self.x = 1
        self.mode = mode

    def get_harvest_index(self, n_obs, n_act):
        for i in range(n_obs, n_act):
            a = self.farm.gymaction_to_discretized_farmgymaction([i])
            fa, fi, e, a, p = a[0]
            if a == "harvest":
                return [i]
        return []

    def choose_action(self):
        # if self.mode == "POMDP":
        self.x += 0.25
        threshold = 10 / self.x
        if np.random.rand() > threshold:
            #print("Looking for harvest")
            obs_actions_len = len(self.farm.farmgym_observation_actions)
            action = self.get_harvest_index(
                obs_actions_len, self.farm.action_space.space.n
            )
            return action
        return self.farm.action_space.sample()


class Farmgym_PolicyAgent(Farmgym_Agent):
    def __init__(self, policy):
        super(Farmgym_PolicyAgent, self).__init__()
        self.policy = policy
        self.observation = []

    def update(self, obs, reward, terminated, truncated, info):
        self.observation = obs

    def choose_action(self):
        if self.farm.is_new_day:
            schedule = self.policy.observation_schedule(self.observation)
        else:
            schedule = self.policy.intervention_schedule(self.observation)
        print(
            "AGENT:", schedule
        )  # TODO: Convert from FarmGym [('BasicFarmer-0', 'Field-0', 'Plant-0', 'stage', [(0, 0)]),..]  to Gym [4,...]
        return schedule
