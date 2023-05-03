from farmgym.v2.games.rungame import Farmgym_RandomAgent, run_gym_xp
from farmgym.v2.games.make_farm import make_farm
from farmgym.v2.rendering.monitoring import make_variables_to_be_monitored


farm2 = make_farm("../games/farms_1x1/farm_lille_clay_bean.yaml")
farm2.add_monitoring(
    make_variables_to_be_monitored(
        [
            "f0.soil.available_Water#L",
            "f0.weeds.flowers#nb",
            "f0.weeds.flowers#nb.mat",
            "f0.fertilizer.amount#kg.mat",
        ]
    )
)
farm2 = make_farm("../games/farms_3x4/farm_montpellier_clay_corn_birds_fertilizer_pests_pollinators_weeds.yaml")
farm2 = make_farm("../games/farms_3x4/farm_montpellier_clay_bean_weeds.yaml")
farm2.add_monitoring(
    make_variables_to_be_monitored(
        [
            "f0.soil.available_Water#L",
            "f0.weeds.flowers#nb",
            "f0.weeds.flowers#nb.mat",
        ]
    )
    + [("Field-0", "Weather-0", "air_temperature", lambda x: x["mean#°C"].value, "Air Temperature - Mean (°C)", "range_auto")]
)
agent = Farmgym_RandomAgent()
farm2.understand_the_farm()
run_gym_xp(farm2, agent, max_steps=60, render="image")
