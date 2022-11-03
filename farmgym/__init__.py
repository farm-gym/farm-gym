from gym.envs.registration import register

register(
    id="farmgym_level0-v0",
    entry_point="farmgym.v2.games.level0-farm:level0_farm",
)
