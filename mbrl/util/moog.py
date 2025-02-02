# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Tuple

import gym
import gym.wrappers
import numpy as np

import mbrl.env.mujoco_envs
import mbrl.planning
import mbrl.types
from mbrl.util.env import EnvHandler, Freeze
from mbrl.env.moog_spriteworld.moog.env_wrappers.simulation import SimulationEnvironment

# Include the mujoco environments in mbrl.env

class FreezeMoog(Freeze):
    """Provides a context to freeze a Mujoco environment.

    This context allows the user to manipulate the state of a Mujoco environment and return it
    to its original state upon exiting the context.

    Example usage:

    .. code-block:: python

       env = gym.make("HalfCheetah-v2")
       env.reset()
       action = env.action_space.sample()
       # o1_expected, *_ = env.step(action)
       with FreezeMujoco(env):
           step_the_env_a_bunch_of_times()
       o1, *_ = env.step(action) # o1 will be equal to what o1_expected would have been

    Args:
        env (:class:`gym.wrappers.TimeLimit`): the environment to freeze.
    """

    def __init__(self, env: gym.wrappers.TimeLimit):
        self._env = env
        self._init_state: np.ndarray = None
        self._elapsed_steps = 0
        self._step_count = 0


    def __enter__(self):
        self._elapsed_steps = self._env._elapsed_steps
        self._env.is_simulation = True

    def __exit__(self, *_args):
        self._env.is_simulation = False
        self._env._elapsed_steps = self._elapsed_steps


class MoogEnvHandler(EnvHandler):
    """Env handler for Mujoco-backed gym envs"""

    freeze = FreezeMoog

    @staticmethod
    def make_env_from_str(env_name: str) -> gym.Env:
        # Handle standard MuJoCo envs
        if env_name == "bouncing_sprites":
            env = mbrl.env.bouncing_sprites.get_env()

        env = gym.wrappers.TimeLimit(env, max_episode_steps=1000)
        return env

    @staticmethod
    def get_current_state(env: gym.wrappers.TimeLimit) -> Tuple:
        """Returns the internal state of the environment.

        Returns a tuple with information that can be passed to :func:set_env_state` to manually
        set the environment (or a copy of it) to the same state it had when this function was
        called.

        Args:
            env (:class:`gym.wrappers.TimeLimit`): the environment.

        Returns:
            (tuple):  Returns the internal state
            (position and velocity), and the number of elapsed steps so far.

        """
        state = (
            env.env.data.qpos.ravel().copy(),
            env.env.data.qvel.ravel().copy(),
        )
        elapsed_steps = env._elapsed_steps
        return state, elapsed_steps

    @staticmethod
    def set_env_state(state: Tuple, env: gym.wrappers.TimeLimit):
        """Sets the state of the environment.

        Assumes ``state`` was generated using :func:`get_current_state`.

        Args:
            state (tuple): see :func:`get_current_state` for a description.
            env (:class:`gym.wrappers.TimeLimit`): the environment.
        """
        env.set_state(*state[0])
        env._elapsed_steps = state[1]
