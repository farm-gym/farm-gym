import matplotlib.pyplot as plt

def box_plot(ax, data, labels, edge_color, fill_color, hatch):
    bp = ax.boxplot(data, patch_artist=True, labels=labels, notch=True)

    for element in ["boxes", "whiskers", "fliers", "means", "medians", "caps"]:
        plt.setp(bp[element], color=edge_color)

    for patch in bp["boxes"]:
        patch.set(facecolor=fill_color)
        patch.set(hatch=hatch)

    return bp


def plot_results2(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    nb_f = len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]
    # names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc = 3
    nr = 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1))

    axes = mat_axes.flatten()

    i = 4 * nb_pol
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
    #axes[0].set_ylim([0, 150])
    axes[0].set_ylim([0, 30])

    i = 1 * nb_pol
    bp1 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 2 * nb_pol
    bp2 = box_plot(
        axes[1],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[1].legend([bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"])
    axes[1].set_title("Pollinators in beans")
    axes[1].set_ylabel("Rewards")
    axes[1].set_xlabel(title)
    axes[1].yaxis.grid(True)
    #axes[1].set_ylim([0, 150])
    axes[1].set_ylim([0, 30])

    i = 4 * nb_pol
    bp1 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "pink",
        (1.0, 0, 0, 0.8),
        "/",
    )
    i = 5 * nb_pol
    bp2 = box_plot(
        axes[2],
        all_data[i : i + nb_pol],
        labels[i : i + nb_pol],
        "lightblue",
        (0, 0, 1, 0.8),
        ".",
    )

    axes[2].legend([bp1["boxes"][0], bp2["boxes"][0]], ["no pollinators", "pollinators"])
    axes[2].set_title("Pollinators in corn")
    axes[2].set_ylabel("Rewards")
    axes[2].set_xlabel(title)
    axes[2].yaxis.grid(True)
    #axes[2].set_ylim([0, 150])
    axes[2].set_ylim([0, 30])

    # fill with colors
    # colors = ['pink', 'lightblue', 'lightgreen']
    # for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig("fig_adjusted.pdf")
    plt.savefig("fig_adjusted.png")


def plot_results3(farms, policy_parameters, results, title):
    nb_pol = len(policy_parameters)
    nb_f = len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res["r"] for res in results]
    labels = [str(policy_parameters[i % nb_pol]) for i in range(len(results))]
    # names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc = 2
    nr = 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4 * nc + 1, 4 * nr + (nr - 1) + 1))

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
    axes[0].set_ylim([0, 150])

    # fill with colors
    # colors = ['pink', 'lightblue', 'lightgreen']
    # for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig("fig.pdf")
    plt.savefig("fig.png")
