
import gym
from farmgym.v2.games.register_all import register_all
from farmgym.v2.games.rungame import run_policy, run_policy_xp
import numpy as np
from farmgym.v2.games.rungame import run_xps
from farmgym.v2.games.make_farm import make_farm

from farmgym.v2.games.make_farm import *




#env_list=register_all()
#print(env_list)

#env = gym.make(env_list[2],100)
#farm = env.unwrapped

#TODO: We want these farms in dry weather !
#1. Monitor water in soil: it should decay fast.
#2. Stop evaporation in clay, not in sand.
#3. Check that water neeeds are not reached/water stress increases in plant (monitor water stress).
#farm1 = gym.make('farms_1x1_clay_bean-v0').unwrapped
#farm4 = gym.make('farms_1x1_sand_bean-v0').unwrapped
#farm2 = gym.make('farms_1x1_clay_corn-v0').unwrapped
#farm5 = gym.make('farms_1x1_sand_corn-v0').unwrapped
#farm3 = gym.make('farms_1x1_clay_tomato-v0').unwrapped
#farm6 = gym.make('farms_1x1_sand_tomato-v0').unwrapped
#farms = [farm1,farm2,farm3,farm4,farm5,farm6]


f1 = make_farm("dry_clay_bean",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'bean')], init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f7 = make_farm("dry_clay_bean_pollinator",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'bean'),(Pollinators,'bee')], init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f2 = make_farm("dry_sand_bean",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"sand"),(Plant, 'bean')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])


f3 = make_farm("dry_clay_corn",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'corn')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f8 = make_farm("dry_clay_corn_pollinator",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'corn'),(Pollinators,'bee')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f4 = make_farm("dry_sand_corn",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"sand"),(Plant, 'corn')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])


f5 = make_farm("dry_clay_tomato",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'tomato')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f9 = make_farm("dry_clay_tomato_pollinator",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'tomato'),(Pollinators,'bee')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])
f6 = make_farm("dry_sand_tomato",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"sand"),(Plant, 'tomato')],init_values=[('Field-0','Weather-0','day#int365',120),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',2500),('Field-0','Soil-0','available_P#g',2500),
                                                                                                    ('Field-0','Soil-0','available_K#g',2500),('Field-0','Soil-0','available_C#g',2500)])



ff1 = make_farm("coupling_weeds_pests",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'tomato'), (Pollinators,'bee'), (Weeds,'base_weed'), (Pests,'basic'), (Cide,'herbicide_slow')],init_values=[('Field-0','Weather-0','day#int365',121),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',5000),('Field-0','Soil-0','available_P#g',5000),
                                                                                                    ('Field-0','Soil-0','available_K#g',5000),('Field-0','Soil-0','available_C#g',5000),('Field-0','Weeds-0','grow#nb',3)])

ff2 = make_farm("coupling_weeds_nopests",
                   {'localization': {'latitude#°':43, 'longitude#°':4, 'altitude#m':150}, 'shape':{'length#nb':1, 'width#nb':1, 'scale#m': 1.} },
                   [(Weather,"dry"),(Soil,"clay"),(Plant, 'tomato'), (Pollinators,'bee'), (Weeds,'base_weed'), (Cide,'herbicide_slow')],init_values=[('Field-0','Weather-0','day#int365',121),('Field-0','Plant-0','stage','seed'),('Field-0','Soil-0','available_N#g',5000),('Field-0','Soil-0','available_P#g',5000),
                                                                                                    ('Field-0','Soil-0','available_K#g',5000),('Field-0','Soil-0','available_C#g',5000),('Field-0','Weeds-0','grow#nb',3)])



def xp_watering():
    farms = [f2,f1,f7,f4,f3,f8,f6,f5,f9]
    #farms = [f5,f9]
    #farms=[ff1,ff2]
    nb_f=len(farms)

    #policy_parameters= [0.,0.25,0.5,1.,2,5, 10, 20]
    policy_parameters= [0.,0.25,0.5,1.,2,5]
    #policy_herbicide_parameters= [0.,0.1,0.5,2,4]
    #policy_herbicide_parameters= [1,2,3,4,5]
    nb_pol=len(policy_parameters)

    nb_replicate=100

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            policy = make_policy_water_harvest(p)
            #policy = make_policy_herbicide(8.,p,0.2)
            cumrewards=[]
            for n in range(nb_replicate):
                #policies = make_policies_water_harvest(policy_parameters)
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                # print(n,":", cr)
                cumrewards.append(cr)
            #print("Mean:", np.mean(cumrewards), "Rewards:", cumrewards)
            results.append({"farm": f.name, "r": cumrewards})
    return farms,policy_parameters,results

        #policies = make_policies_water_harvest([0., 0.5, 1., 2, 4, 8])
        #for policy in policies:
        #  cumrewards, cumcosts = run_xps(f, policy, max_steps=200, nb_replicate=40)
        #  #print("Mean:",np.mean(cumrewards), "Rewards:", cumrewards)
        #  results.append({"farm":f.name, "r":cumrewards})

    #print(results)

def xp_coupling():
    farms=[ff1,ff2]

    policy_parameters= [2,3,4,6,10,12,15,20]

    nb_replicate=100

    results = []
    for f in farms:
        for p in range(len(policy_parameters)):
            #policy = make_policy_water_harvest(p)
            policy = make_policy_herbicide(0.005,policy_parameters[p],8)
            cumrewards=[]
            for n in range(nb_replicate):
                #policies = make_policies_water_harvest(policy_parameters)
                cr, _ = run_policy_xp(f, copy.deepcopy(policy), max_steps=150)
                # print(n,":", cr)
                cumrewards.append(cr)
            #print("Mean:", np.mean(cumrewards), "Rewards:", cumrewards)
            results.append({"farm": f.name, "r": cumrewards})
    return farms,policy_parameters,results


def plot_results(farms,policy_parameters,results,title):
    nb_pol=len(policy_parameters)
    nb_f=len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res['r'] for res in results]
    labels = [str(policy_parameters[i%nb_pol]) for i in range(len(results))]
    #names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc= (int) (np.ceil(np.sqrt(nb_f)))
    nr= nb_f//nc
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4*nc+1, 4*nr+(nr-1)+1))

    axes=mat_axes.flatten()

    i=0
    bplots = []
    for j in range(nb_f):
    # rectangular box plot
        bplots.append(axes[j].boxplot(all_data[i:i+nb_pol],
                         notch=True,  # notch shape
                         vert=True,  # vertical box alignment
                         patch_artist=True,  # fill with color
                         labels=labels[i:i+nb_pol]))  # will be used to label x-ticks
        axes[j].set_title(names[j])
        axes[j].set_ylabel('Rewards')
        axes[j].set_xlabel(title)
        axes[j].yaxis.grid(True)
        axes[j].set_ylim([0, 150])
        i+=nb_pol


    # fill with colors
    #colors = ['pink', 'lightblue', 'lightgreen']
    #for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig('fig.pdf')
    plt.savefig('fig.png')


import matplotlib.pyplot as plt
def box_plot(ax, data, labels, edge_color, fill_color):
    bp = ax.boxplot(data, patch_artist=True, labels=labels,notch=True)

    for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
        plt.setp(bp[element], color=edge_color)

    for patch in bp['boxes']:
        patch.set(facecolor=fill_color)

    return bp

def plot_results2(farms,policy_parameters,results,title):
    nb_pol=len(policy_parameters)
    nb_f=len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res['r'] for res in results]
    labels = [str(policy_parameters[i%nb_pol]) for i in range(len(results))]
    #names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc= 3
    nr= 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4*nc+1, 4*nr+(nr-1)+1))

    axes=mat_axes.flatten()

    i=4*nb_pol
    bp1 = box_plot(axes[0], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'pink')
    i=3*nb_pol
    bp2 = box_plot(axes[0], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'lightblue')

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ['clay', 'sand'])
    axes[0].set_title("Sand vs Clay (corn)")
    axes[0].set_ylabel('Rewards')
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 150])


    i=1*nb_pol
    bp1 = box_plot(axes[1], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'pink')
    i=2*nb_pol
    bp2 = box_plot(axes[1], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'lightblue')

    axes[1].legend([bp1["boxes"][0], bp2["boxes"][0]], ['no pollinators', 'pollinators'])
    axes[1].set_title("Pollinators in beans")
    axes[1].set_ylabel('Rewards')
    axes[1].set_xlabel(title)
    axes[1].yaxis.grid(True)
    axes[1].set_ylim([0, 150])


    i=4*nb_pol
    bp1 = box_plot(axes[2], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'pink')
    i=5*nb_pol
    bp2 = box_plot(axes[2], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'lightblue')

    axes[2].legend([bp1["boxes"][0], bp2["boxes"][0]], ['no pollinators', 'pollinators'])
    axes[2].set_title("Pollinators in corn")
    axes[2].set_ylabel('Rewards')
    axes[2].set_xlabel(title)
    axes[2].yaxis.grid(True)
    axes[2].set_ylim([0, 150])


    # fill with colors
    #colors = ['pink', 'lightblue', 'lightgreen']
    #for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig('fig.pdf')
    plt.savefig('fig.png')



def plot_results3(farms,policy_parameters,results,title):
    nb_pol=len(policy_parameters)
    nb_f=len(farms)

    import matplotlib.pyplot as plt
    import numpy as np

    for r in results:
        print(r)

    all_data = [res['r'] for res in results]
    labels = [str(policy_parameters[i%nb_pol]) for i in range(len(results))]
    #names = ["soil:clay, plant:bean", "soil:sand, plant:bean", "soil:clay, plant:corn", "soil:sand, plant:corn",  "soil:clay, plant:tomato",  "soil:sand, plant:tomato"]
    names = [f.name for f in farms]

    nc= 2
    nr= 1
    fig, mat_axes = plt.subplots(nrows=nr, ncols=nc, figsize=(4*nc+1, 4*nr+(nr-1)+1))

    axes=mat_axes.flatten()

    i=0*nb_pol
    bp1 = box_plot(axes[0], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'pink')
    i=1*nb_pol
    bp2 = box_plot(axes[0], all_data[i:i + nb_pol], labels[i:i + nb_pol], 'black', 'lightblue')

    axes[0].legend([bp1["boxes"][0], bp2["boxes"][0]], ['pests', 'no pests'])
    axes[0].set_title("Weeds without vs with pests")
    axes[0].set_ylabel('Rewards')
    axes[0].set_xlabel(title)
    axes[0].yaxis.grid(True)
    axes[0].set_ylim([0, 150])




    # fill with colors
    #colors = ['pink', 'lightblue', 'lightgreen']
    #for bplot in bplots:
    #    for patch, color in zip(bplot['boxes'], colors):
    #        patch.set_facecolor(color)

    plt.show()
    plt.savefig('fig.pdf')
    plt.savefig('fig.png')
#farms,policy_parameters,results = xp_watering()
#plot_results2(farms,policy_parameters,results,'Watering policy (daily input in L)')


farms,policy_parameters,results = xp_coupling()
plot_results3(farms,policy_parameters,results,'Herbicide policy (every x day)')


