.. title:: installation : contents

.. _installation:

============
Installation
============

Basic Installation
------------------

To install farm-gym using pip:

.. code:: bash

    $ pip install git+https://github.com/farm-gym/farm-gym
    

To also install the library pre-made farms using pip:

.. code:: bash

    $ pip install git+https://github.com/farm-gym/farm-gym-games

Gym version
-----------

Remark that farm-gym is has a separate internal API from gym and in principle it is compatible with the last version of gym (v0.26), although farm-gym-games we use gym v0.21 compatibility syntax for now as this is the version used by stablebaselines3. In the futur we plan to transition to gymnasium for a broader compatibility.
