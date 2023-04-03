from farmgym.v2.games.rungame import Farmgym_RandomAgent, run_gym_xp
from farmgym.v2.games.make_farm import make_farm

farm2 = make_farm("../games/farms_3x4/farm_montpellier_clay_corn_birds_fertilizer_pests_pollinators_weeds.yaml")
agent = Farmgym_RandomAgent()
run_gym_xp(farm2, agent, max_steps=15, render="text")

