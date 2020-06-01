import tensorflow as tf
import numpy as np
import random
import sys
import pickle
import mysql.connector

from simulator import Env
from AC.actor import *
from AC.critic import *

# Hyper Parameters
EPISODE = 30  # Episode limitation
STEP = 300     # Step limitation in an episode
TEST = 100     # The number of experiment test every 100 episode
alpha = 0.9     # Hyper parameter for reward function
beta = 0.6      # Hyper parameter for reward function


"""
Not test run yet, some functions are remained empty
"""


if __name__ == "__main__":
    # Initialize environment
    env = Env()

    # Create Actor, Critic
    sess = tf.InteractiveSession()
    actor = Actor(env, sess)
    critic = Critic(env, sess)

    # Logging
    queries = []

    for episode in range(EPISODE):
        # Initialize task
        env.reset()

        for step in range(STEP):
            state = env.getState()
            action = actor.choose_action()
            env.execute(action)

            if step > 0:
                reward = env.getReward()
                next_state = env.getState()
                td_error = critic.train_Q_network(
                    state, reward, next_state)
                # true_gradient = grad[logPi(s,a) * td_error]
                actor.learn(state, 1, td_error)
                state = next_state

        # Test every 100 episode
        if episode % 100 == 0:
            # Test
            env.reset()
            reward = 0

            for step in range(STEP):
                reward += env.getReward()
            print(reward)


