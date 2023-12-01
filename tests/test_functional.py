# ruff: noqa: F401
from farmgym.v2.entities import (
    Birds,
    Cide,
    Fertilizer,
    Pests,
    Plant,
    Pollinators,
    Soil,
    Weather,
    Weeds,
)
from farmgym.v2.farm import Farm
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.field import Field
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.scorings.BasicScore import BasicScore


class FarmCreator:
    @staticmethod
    def create_field(entities, field_infos):
        field = Field(
            localization=field_infos["localization"],
            shape=field_infos["shape"],
            entities_specifications=entities,
        )
        return [field]

    @staticmethod
    def create_farmer(max_daily_interventions):
        farmers = [{"max_daily_interventions": max_daily_interventions}]
        farmers = [
            BasicFarmer(max_daily_interventions=f["max_daily_interventions"])
            for f in farmers
        ]
        return farmers

    @staticmethod
    def create_scoring(farm_name):
        name_score = f"{farm_name}_score.yaml"
        scoring = BasicScore(score_configuration=name_score)
        return scoring

    @staticmethod
    def create_rules(farm_name):
        name_init = f"{farm_name}_init.yaml"
        name_actions = f"{farm_name}_actions.yaml"
        rules = BasicRule(
            init_configuration=name_init,
            actions_configuration=name_actions,
        )
        return rules

    @staticmethod
    def update_rules(farm_name):
        name_init = f"{farm_name}_init.yaml"
        # Remove plant rule:
        with open(name_init, "r") as file:
            content = file.readlines()
        # Remove harvest terminal condition
        line_to_remove = '[{state_variable: ["Field-0", "Plant-0", "global_stage", []], function: "value", operator: "==", ref_value: "dead"}],'
        content = [line for line in content if line.strip() != line_to_remove]
        # Save the modified content back to the file
        with open(name_init, "w") as file:
            file.writelines(content)

    @staticmethod
    def create_farm(weather, soil, plant=None, remove_plant_rule=True):
        farm_name = f"{weather}_{soil}"
        if plant:
            farm_name += f"_{plant}"

        entities = [
            (Weather, weather),
            (Soil, soil),
        ]
        if plant:
            entities.append((Plant, plant))

        field_infos = {
            "localization": {"latitude#°": 43, "longitude#°": 4, "altitude#m": 150},
            "shape": {"length#nb": 1, "width#nb": 1, "scale#m": 1.0},
        }

        field = FarmCreator.create_field(entities, field_infos)
        farmer = FarmCreator.create_farmer(max_daily_interventions=1)
        scoring = FarmCreator.create_scoring(farm_name)
        rules = FarmCreator.create_rules(farm_name)
        farm = Farm(field, farmer, scoring, rules)

        # Remove plant rules
        if remove_plant_rule:
            FarmCreator.update_rules(farm_name)

        farm = Farm(field, farmer, scoring, rules)

        return farm


def run_n_steps(farm, n=10):
    obs = farm.reset()
    terminated = False
    i = 0
    while not terminated and i < n:
        i += 1
        obs, reward, terminated, truncated, info = farm.step([])
    return farm


def get_available_water(farm):
    return (
        farm.fields["Field-0"]
        .entities["Soil-0"]
        .variables["available_Water#L"][(0, 0)]
        .value
    )


def get_day(farm):
    day = int(
        farm.fields["Field-0"].entities["Weather-0"].variables["day#int365"].value
    )
    return day


def test_clay_sand_soils():
    # Create soils
    dry_clay = FarmCreator.create_farm(
        weather="montpellier", soil="clay", remove_plant_rule=True
    )
    dry_sand = FarmCreator.create_farm(
        weather="montpellier", soil="sand", remove_plant_rule=True
    )
    print(f"Starting day : {get_day(dry_clay)}")
    # Simulate days
    simulated_days = 80
    n_clay = run_n_steps(farm=dry_clay, n=simulated_days)
    n_sand = run_n_steps(farm=dry_sand, n=simulated_days)
    # Get available water
    water_clay = get_available_water(n_clay)
    water_sand = get_available_water(n_sand)
    assert (
        water_clay > water_sand
    ), f"Clay water : {water_clay:.2f} 'SHOULD BE >' Sand water : {water_sand:.2f}"


def test_plant_farm():
    # Create soils
    dry_clay = FarmCreator.create_farm(
        weather="montpellier", soil="clay", plant="bean", remove_plant_rule=True
    )
    dry_sand = FarmCreator.create_farm(
        weather="montpellier", soil="sand", plant="bean", remove_plant_rule=True
    )
    # Simulate days
    simulated_days = 80
    n_clay = run_n_steps(farm=dry_clay, n=simulated_days)
    n_sand = run_n_steps(farm=dry_sand, n=simulated_days)
    # Get available water
    water_clay = get_available_water(n_clay)
    water_sand = get_available_water(n_sand)
    assert (
        water_clay > water_sand
    ), f"Clay water : {water_clay:.2f} 'SHOULD BE >' Sand water : {water_sand:.2f}"
