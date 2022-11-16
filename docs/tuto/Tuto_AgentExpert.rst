Code : Expert Agent
-------------------

The following code can be find in the ``expert_farm1.py`` in
``examples/`` folder.

Imports:
~~~~~~~~

- ``AgentWithSimplePolicy, AgentManager, evaluate_agents``: for rlberry use
- ``Farm1`` : the model environment
- ``display_evaluation_result`` : print the mean, median and std of the evaluation

.. code:: python

    from rlberry.agents import AgentWithSimplePolicy
    from rlberry.manager import AgentManager, evaluate_agents
    from rlberry_farms import Farm1
    import numpy as np
    from rlberry_farms.utils import display_evaluation_result

Settings :
~~~~~~~~~~

We’ll use the ‘Farm1’ environment For this specific expert agent, we can
decide the day we will start the policy in ‘starting_day_for_policy’.

.. code:: python

    env_ctor, env_kwargs = Farm1, {}
    starting_day_for_policy = 100

Class Expert Agent :
~~~~~~~~~~~~~~~~~~~~

To be compatible with our system, the expert Agent should be a RLBerry
agent. So it have to extend ``AgentWithSimplePolicy``, and implement
``__init__, fit``, and ``policy``. - init : we can use it to manage
specific settings (here ‘starting_day_for_policy’). - fit : we use
*classic* rlberry **fit**, but it will be called with a budget of 1
(because expert agent don’t need training). - policy : it’s where you
define how your agent choose an action from the given observation.

--------------

**HERE, the policy of this agent is to :**

- 1) wait until the ‘starting_day_for_policy’.
- 2) Watering, herbicide, pesticide, fertilize,sow, watering.
- 3) Waiting the plant got fruits, wait 4 more days, then harvest.

**HERE, the available actions are :**

- 0) Do nothing
- 1) Pour 1L of water
- 2) Pour 5L of water
- 3) Harvest the plant
- 4) sow
- 5) Fertilizer
- 6) Herbicide
- 7) Pesticide
- 8) Remove weeds by hand

**HERE, the content of the observation array is :**

- observation[0] : Day (from 1 to 365)
- observation[1] : Mean air temperature (°C)
- observation[2] : Min air temperature (°C)
- observation[3] : Max air temperature (°C)
- observation[4] : Rain amount
- observation[5] : Sun-exposure (from 1 to 5)
- observation[6] : Consecutive dry day (int)
- observation[7] : Stage of growth of the plant
- observation[8] : Number of fruits (int)
- observation[9] : Size of the plant in cm
- observation[10] : Soil wet_surface (m2.day-1)
- observation[11] : fertilizer amount (kg)
- observation[12] : Pollinators occurrence (bin)
- observation[13] : Weeds grow (nb)
- observation[14] : Weeds flowers(nb)
- observation[15] : weight of fruits
- observation[16] : microlifehealth index (%)

.. code:: python

    
    class ExpertAgent(AgentWithSimplePolicy):
        name = "ExpertAgentFarm1"
        fruit_stage_duration_count = 0
    
        def __init__(self, env, starting_day_for_policy=0, **kwargs):
            AgentWithSimplePolicy.__init__(self, env ,**kwargs)
            self.starting_day_for_policy = starting_day_for_policy
    
        def fit(self, budget=100, **kwargs):
            observation = self.env.reset()
            episode_reward = 0
            for ep in range(int(budget)):
                action = self.policy(observation)
                observation, reward, done, info = self.env.step(action)
                episode_reward += reward
                if done:
                    self.writer.add_scalar("episode_rewards", episode_reward, ep)
                    episode_reward = 0
                    self.env.reset()
    
    
        def policy(self, observation):
            next_action = 0 #default
            if observation[0] == starting_day_for_policy:
                next_action = 2  # 5L of water
            elif observation[0] == starting_day_for_policy+1:
                next_action = 6  # herbicide
            elif observation[0] == starting_day_for_policy+2:
                next_action = 7  # pesticide
            elif observation[0] == starting_day_for_policy+3:
                next_action = 5  # Fertilizer
            elif observation[0] == starting_day_for_policy+4:
                next_action = 4  # sow
            elif observation[0] == starting_day_for_policy+5:
                next_action = 1  # 1L of water
            elif observation[0] > starting_day_for_policy+5:
                if observation[7] in [6, 7, 8, 9]:
                    if (self.fruit_stage_duration_count > 4):
                        next_action = 3  # harvesting
                        self.fruit_stage_duration_count = 0
                    else:
                        self.fruit_stage_duration_count += 1
                
            return next_action

Class Agent :
~~~~~~~~~~~~~

Create an Agent (called ‘Agent’) that heritate from ExpertAgent, to
match the name and the expected signature for the challenge.

.. code:: python

    class Agent(ExpertAgent):
        def __init__(self,env,**kwargs):
            ExpertAgent.__init__(self, env, starting_day_for_policy,**kwargs)

Main code: 
~~~~~~~~~~


Run your agent through the `RLBerry agent manager <https://rlberry.readthedocs.io/en/latest/generated/rlberry.manager.AgentManager.html#rlberry.manager.AgentManager>`__
with the setting you need. *(here we use ``n_fit=1`` : because expert
agent don’t need training)*

Then display the results of the evaluation.

.. code:: python

    manager = AgentManager(
        Agent,
        (env_ctor, env_kwargs),
        agent_name="ExpertAgentFarm1",
        fit_budget=1,
        eval_kwargs=dict(eval_horizon=365),
        n_fit=1,
        output_dir="expert_farm1_results",
    )
    manager.fit()
    evaluation = evaluate_agents([manager], n_simulations=128, plot=False)
    print(evaluation.describe())


.. parsed-literal::

    [38;21m[INFO] 15:13: Running AgentManager fit() for ExpertAgentFarm1 with n_fit = 1 and max_workers = None. 
    [38;21m[INFO] 15:13: Evaluating ExpertAgentFarm1... 
    [INFO] Evaluation:................................................................................................................................  Evaluation finished 


.. parsed-literal::

           ExpertAgentFarm1
    count        128.000000
    mean          21.774720
    std            6.324920
    min            5.098892
    25%           18.039289
    50%           21.757822
    75%           25.429321
    max           43.886563


