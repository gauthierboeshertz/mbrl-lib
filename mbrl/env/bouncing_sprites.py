"""
"""
import numpy as np
import argparse
from moog_spriteworld.moog import environment
from moog_spriteworld.moog.env_wrappers import GymWrapper
from moog_spriteworld.moog.env_wrappers import MBRLWrapper

from moog_spriteworld.moog.example_configs import bouncing_sprites


def get_env(config):

    env_config = bouncing_sprites.get_config(num_sprites=config["num_sprites"],is_demo=False,timeout_steps=50,sparse_rewards=config["sparse_rewards"])
    env = environment.Environment(**env_config)
    return MBRLWrapper(GymWrapper(env))


