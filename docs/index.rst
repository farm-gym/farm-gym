.. _farm-gym: https://github.com/farm-gym/farm-gym

.. _index:

FarmGym
-------

FarmGym is a **Farming Environment Gym factory** intended to model sequential decision-making on farms seen as dynamical system with many entities interacting.

FarmGym offers the possibility to build ad-hoc games by specifying a farm with different entities, different rules and scores.
This enables to consider from very simple to highly complicated environments, using one plot of land or several field with or without pest, birds, fertiliser... 

Farm-gym is based on the interaction of several **entities** (:class:`~farmgym.v2.entities.Plant.Plant`, :class:`~farmgym.v2.entities.Soil.Soil`, :class:`~farmgym.v2.entities.Weeds.Weeds`, ...) with the :class:`~farmgym.v2.farm.Farm` which contains potentially several :class:`~farmgym.v2.field.Field`. Each entity is described using a yaml file, we give several basic specifications in `farmgym/v2/specifications <https://github.com/farm-gym/farm-gym/tree/main/farmgym/v2/specifications>`_, that can also be seen in the docs, see :ref:`specifications <specifications>`. The reward is then described by a score function through :class:`~farmgym.v2.scorings.BasicScore.BasicScore`, configurable through yaml initialisation files. All of this is expandable: you can use your own entities and score functions!

See the :ref:`User-Guide <user_guide>` for more in-depth explanations.

See the `pdf guide <https://github.com/farm-gym/farm-gym/raw/main/FarmGym.pdf>`_ for a detailed mathematical description of farm-gym (aimed at researchers) in particular concerning the choice we made during the construction of farm-gym and the modelisation as a partially observable markov decision process.
