# FarmGym

FarmGym is a Farming Environment Gym factory intended to model sequential decision-making on farms seen as dynamical system with many entities interacting.
FarmGym offers the possibility to build ad-hoc games by specifying a farm with different entities, different rules and scores.
This enables to consider from very simple to highly complicated environments.


## Citing FarmGym
If you use `FarmGym` in your publications, please cite us following this Bibtex entry:

```bibtex
@article{maillard2022farmgym,
title={Farm-Gym: A modular reinforcement learning platform for agronomy games.},
author={Maillard, Odalric-Ambrym},
year={2022},
school={Inria Lille}
    }
```


## About this project

#### Authors
Odalric-Ambrym Maillard (v2) and Thomas Carta (v1)

**Principal contact**:

- first name: odalric-ambrym
- last name: maillard
- institute: inria
- country: france
- email: first name . last name @ institute . fr

#### Acknowledgements
This work has been supported by the French Ministry of
Higher Education and Research, Hauts-de-France region, Inria within the team-project Scool and the MEL. The authors
acknowledge the funding of the I-Site ULNE regarding project R-PILOTE-19-004-APPRENF, and the project A-EX SR4SG of Inria.
We also thank the French Agricultural Research Centre for International Development
(CIRAD) for insightful discussions.
We thank the contribution of Thomas Carta, who started working on an earlier version (v1) of this project during his internship at Scool in summer 2020.
We thank Romain Gautron (CIRAD/CGIAR) and Timothée Mathieu (Inria) for valuable inputs.


#### Contributing
Any new issue is welcomed! If you want to actively contribute, you can check issues the **wishlist** tag.


## Getting started

### Packages
It is recommended to use gym version >= 0.25.2, due to better support of dictionaries to define Spaces.

### Entities 
Minimal entities to define a farm are the Weather, the Soil and the Plant. 
Additional entities can be added, such as Birds, Pests, Weeds, or Facilities (e.g. Scarescrow, Hedge) and Fertilizers.
Each entity offers a list of actions made available to the learner.

### Rules 
The rules typically specify the initial and stopping conditions of the game, the subset of actions allowed for the considered game,
or the number of actions allowed each day.

### Score
The score may incorporate several features such as yield, biodiversity, resource usage, and specifies the cost of each action.

### Games
 Specifying various entities, rules and scores enables to generate various games. 
 FarmGym comes with a bunch of predefined games that can be seen as illustrative examples to build user-defined games.

### Minimal environment
```
import gym
from farmgym.v2.games.farms_1x1.clay_corn.farm import env

farm = env()

is_done = False
while not is_done:
    obs, reward, is_done, info = farm.step(farm.action_space.sample())
```
Note however that a FarmGym environment implements AO-MDP (Actively-observed Markov Decision Processes), and not just PO-MDP.
This can be recasted into a two-stage PD-MDP, alternating between observation steps and intervention steps.
Using the gym PO-MDP approach, the action space combines all observation-actions and intervention-actions, 
so that asking random actions may generate observation-actions at intervention steps or
intervention-actions at observation steps. 

Alternatively, one may want to separate between observation and intervention times, and asks random observation-action
or random interention-action at the appropriate time. 
We provide such an example below, here using the farmgym_step function instead of step.
```
import gym
from farmgym.v2.games.farms_1x1.clay_corn.farm import env

farm = env()

is_done = False
while not is_done:
    observation_schedule = []
    observation_schedule.append(farm.random_allowed_observation())
    obs1, _, _, info = farm.farmgym_step(observation_schedule)
    obs_cost = info['observation cost']

    intervention_schedule = []
    intervention_schedule.append(farm.random_allowed_intervention())
    obs2, reward, is_done, info = farm.farmgym_step(intervention_schedule)
    int_cost= info["intervention cost"]
```
The difference between step and farmgym_step is the format of the action given as input.
Any gym action can be converted into its corresponding farm_gym format using farm.gymaction_to_farmgymaction.

### Rendering
The basic rendering option is to print a farm, which output a text representation of the farm with all entities and available actions.
When rendering is called with farm.render(), the environment produces an image representing the farm at the current day.
Once a game is done, it is possible to assemble all these images into a movie, calling the method generate_video. 
It is also possible to generate a gif using the method generatee_gif.
Further, we store all these figures and the movie in a sub-folder for convenience.
```
import gym
from farmgym.v2.games.farms_1x1.clay_corn.farm import env
from farmgym.v2.farm import generate_video

import os
import time
time_tag = time.time()
os.mkdir("run-" + str(time_tag))
os.chdir("run-" + str(time_tag))

farm = env()

is_done = False
while not is_done:
    farm.render()
    obs, reward, is_done, info = farm.step(farm.action_space.sample())
generate_video(image_folder='.', video_name='farm.avi')
```

### Monitoring
A FarmGym environment typically comes with many states. It is possible for the developer to monitor such variables.
It is possible to do usingthe method farm.add_monitoring(var), where var is the list of considered variables.

### Complete gym example
We detail another way to try an environment below. 
The method register_all scans for all environments defined in farmgym and register them to gym.
It outputs the list of names of each environment. 
Then, the method run from  farmgym.v2.games.rungame runs a complete game,
collects rewards and costs, gather all rendered images if asked, and output all this in a sub-folder.
It also tests is the environment is compatible with gym.

```
import gym
from farmgym.v2.games.register_all import register_all
from farmgym.v2.games.rungame import run_randomactions

env_list=register_all()

env = gym.make(env_list[2],100)
farm = env.unwrapped
run_randomactions(farm,max_steps=100,render=True, monitoring=False)
```

You can find further examples in the tests folder.


## Plants

You can grow several plants. 

Beans
<p align="center">
<img src="farmgym/v2/specifications/sprites/bean_growing.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/bean_blooming.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/bean_fruiting.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/bean_fruit.png?raw=true" width="200">
</p>


Corns
<p align="center">
<img src="farmgym/v2/specifications/sprites/corn_growing.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/corn_blooming.png?raw=true" width="200" >
<img src="farmgym/v2/specifications/sprites/corn_fruiting.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/corn_fruit.png?raw=true" width="200">
</p>


Tomatoes
<p align="center">
<img src="farmgym/v2/specifications/sprites/tomato_growing.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/tomato_blooming.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/tomato_fruiting.png?raw=true" width="200">
<img src="farmgym/v2/specifications/sprites/tomato_fruit.png?raw=true" width="200">
</p>

## Examples
### Basic farm
This is an example of a 1x1 field with a Weather, Soil and Plant entity. The Plant is Corn and Soil is Clay. 
Here the learner succesfully harvest, although perhaps a little early.

<p align="center">
<img src="Readme_figs/farm_1x1_clay_corn.gif?raw=true">
    <div align="center">A basic farm</div>
</p>

### More complex farm
Below is an example of a more complex 3x4 farm, with Weather, Soil, Plant and Fertilizer entities.
The Plant is a Corn and soil is clay.
<p align="center">
<img src="Readme_figs/farm_3x4_clay_corn_fertilizer.gif?raw=true">
    <div align="center">A more complex farm</div>
</p>

Below is another example of a more complex 3x4 farm, with Weather, Soil, Plant, Weeds but also Herbicides entities.
The Plant is a Tomato and  soil is sand. Note that here, the learner has waited too long and the tomatoes have rotten before being harvested.

<p align="center">
<img src="Readme_figs/farm_3x4_sand_tomato_weeds_fail.gif?raw=true">
    <div align="center">A more complex farm</div>
</p>

Another example when the plant is Beans and the soil is clay. Here the learner has harvested at the correct time.

<p align="center">
<img src="Readme_figs/farm_3x4_clay_bean_weeds.gif?raw=true">
    <div align="center">A more complex farm</div>
</p>

### Difficult farm game
Finally, below is a harder game, showing  a 3x4 farm with Weather, Soil, Plant, Fertilizer, but also Birds, Pests, Weeds, Pollinators entities.
There are also Facility entity, which enables to put a scarecrow and Cide entity.
Here the random agent fails due to combination of all these effects.

<p align="center">
<img src="Readme_figs/farm_3x4_complex_fail.gif?raw=true">
    <div align="center">A difficult game</div>
</p>




 You can use [Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

