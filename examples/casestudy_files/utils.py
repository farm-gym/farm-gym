import matplotlib.pyplot as plt
from farmgym.v2.farm import Farm
from farmgym.v2.farmers.BasicFarmer import BasicFarmer
from farmgym.v2.field import Field
from farmgym.v2.rules.BasicRule import BasicRule
from farmgym.v2.scorings.BasicScore import BasicScore


# Daily interventios is set to 2 otherwise farmer
# does not harvest on days where it has another action
def make_basicfarm(name, field, entities, farmers=[{"max_daily_interventions": 2}]):
    name = "casestudy/" + name
    name_score = name + "_score.yaml"
    name_init = name + "_init.yaml"
    name_actions = name + "_actions.yaml"
    entities1 = []
    for e, i in entities:
        entities1.append((e, i))

    field1 = Field(
        localization=field["localization"],
        shape=field["shape"],
        entities_specifications=entities1,
    )

    ffarmers = [
        BasicFarmer(max_daily_interventions=f["max_daily_interventions"])
        for f in farmers
    ]
    scoring = BasicScore(score_configuration=name_score)

    rules = BasicRule(
        init_configuration=name_init,
        actions_configuration=name_actions,
    )

    farm = Farm(
        fields=[field1],
        farmers=ffarmers,
        scoring=scoring,
        rules=rules,
        policies=[],
    )
    farm.name = name
    return farm


def box_plot(ax, data, labels, edge_color, fill_color, hatch):
    bp = ax.boxplot(data, patch_artist=True, labels=labels, notch=True)

    for element in ["boxes", "whiskers", "fliers", "means", "medians", "caps"]:
        plt.setp(bp[element], color=edge_color)

    for patch in bp["boxes"]:
        patch.set(facecolor=fill_color)
        patch.set(hatch=hatch)

    return bp


def plot_watering_results(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]

    nc = 3
    nr = 1
    fig, mat_axes = plt.subplots(
        nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1)
    )

    axes = mat_axes.flatten()

    i = 2 * nb_pol
    bp1 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 3 * nb_pol
    bp2 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ["clay", "sand"])
    axes[0].set_title("Sand vs Clay (corn)")
    axes[0].set_ylabel("Rewards")
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 100])

    i = 0 * nb_pol
    bp1 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 6 * nb_pol
    bp2 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[1].legend(
        [bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"]
    )
    axes[1].set_title("Pollinators in beans")
    axes[1].set_ylabel("Rewards")
    axes[1].set_xlabel(title)
    axes[1].yaxis.grid(True)
    axes[1].set_ylim([0, 100])

    i = 2 * nb_pol
    bp1 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 7 * nb_pol
    bp2 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[2].legend(
        [bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"]
    )
    axes[2].set_title("Pollinators in corn")
    axes[2].set_ylabel("Rewards")
    axes[2].set_xlabel(title)
    axes[2].yaxis.grid(True)
    axes[2].set_ylim([0, 100])

    plt.savefig("watering_results.pdf")
    plt.savefig("watering_results.png")
    plt.show()


def plot_coupling_results(farms, policy_parameters, results, title, fname=None):
    nb_pol = len(policy_parameters)
    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]

    nc = 2
    nr = 1
    fig, mat_axes = plt.subplots(
        nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1)
    )

    axes = mat_axes.flatten()

    i = 0 * nb_pol
    bp1 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 1 * nb_pol
    bp2 = box_plot(
        axes[0],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1.0, 0.8),
        ".",
    )

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ["pests", "no pests"])
    axes[0].set_title("Weeds without vs with pests")
    axes[0].set_ylabel("Rewards")
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 100])

    plt.savefig("coupling_results.pdf")
    plt.savefig("coupling_results.png")
    plt.show()
