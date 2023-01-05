#####################
Pre-Constructed Farms
#####################

.. _games:

.. currentmodule:: farmgym_games
                   
.. warning::
   The elements of this page are from the companion library `farm-gym-games <https://github.com/farm-gym/farm-gym-games>`_, please install it to use the pre-made farms.


* `Farm0` is a very easy farm, any policy that makes sense should work well.
* `Farm1` is a more challenging farm game with pests, bad weather and weeds.

The farms are automatically registered and can be called using

.. code:: python

    import farmgym_games
    import gym
    env = gym.make("Farm1-v0")

One may also import ``"Farm0-v0"``. Farm-gym is primarirly gym v0.26 compatible but one may use the environments ``"OldV21Farm0-v0"`` and ``"OldV21Farm0-v0"`` to get environments that are compatible with gym v0.21 API (remark that gym v0.26 still needs to be the version installed for farm-gym to work).
   
                   
Farms
-----

.. autosummary::
  :toctree: generated/
  :template: class.rst
             
    Farm0
    Farm1
