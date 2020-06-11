import tensorflow as tf
import numpy as np
import random
import sys
import pickle
import mysql.connector
import pandas as pd

from simulator import Env
from AC.actor import *
from AC.critic import *
from ddpg import *

#####################  hyper parameters  ####################

MAX_EPISODES = 2000
MAX_EP_STEPS = 200
LR_A = 0.001    # learning rate for actor
LR_C = 0.002    # learning rate for critic
GAMMA = 0.9     # reward discount
TAU = 0.01      # soft replacement
MEMORY_CAPACITY = 10000
BATCH_SIZE = 32

"""
Not test run yet, some functions are remained empty
"""

if __name__ == "__main__":
    knobs = pd.read_csv("knobs.csv", dtype={"unit":np.int32, "lb":np.int64, "hb":np.int64})
    var = list(knobs["knobs"])

    a_lb, a_hb = list(knobs["lb"]), list(knobs["hb"])
    unit = list(knobs["unit"])

    s_dim = 5 + len(var)                                         # [insert, delete, update, select, var, latency]
    a_dim = len(var)                                             # action -> continuous value

    env = Env(variables=var, unit=unit)
    ddpg = DDPG(a_dim = a_dim, s_dim=s_dim, a_bound=a_hb)

    # env.executeAction([10])

    var = 10          # control exploration
    t1 = time.time()
    for episode in range(MAX_EPISODES):
        s = env.reset()
        ep_reward = 0
        for j in range(MAX_EP_STEPS):
            # Add exploration noise
            a = ddpg.choose_action(s)
            for t in range(a_dim):
                a[t] = np.clip(np.random.normal(a[t], var), a_lb[t], a_hb[t])    # add randomness to action selection for exploration
            print(s)
            print(a)
            s_, r, done, info = env.step(a)
            print("Current reward is : " + str(r))

            ddpg.store_transition(s, a, r / 10, s_)

            if ddpg.pointer > MEMORY_CAPACITY:
                var *= .9995    # decay the action randomness
                ddpg.learn()

            s = s_
            ep_reward += r
            if j == MAX_EP_STEPS-1:
                print('Episode:', episode, ' Reward: %i' % int(ep_reward), 'Explore: %.2f' % var, )
                # if ep_reward > -300:RENDER = True
                break

        if episode % 100 == 0:
            total_reward = 0
            for i in range(10):
                state = env.reset()
                for j in range(MAX_EP_STEPS):
                    action = ddpg.choose_action(state) # direct action for test
                    state,reward,done,_ = env.step(action)
                    total_reward += reward
                    if done:
                        break
            ave_reward = total_reward/300
            print ('episode: ',episode,'Evaluation Average Reward:',ave_reward)
    print('Running time: ', time.time() - t1)


    # # Initialize environment
    # env = Env(variables=var)
    # env.generateQueryVec()
    # setting = env.getDefaultSetting()
    # for n in setting.keys():
    #     print(n + " " + setting[n])

    # env.saveDefaultSetting()
    # print(env.getDefaultSetting())

    # # Create Actor, Critic
    # sess = tf.InteractiveSession()
    # actor = Actor(env, sess)
    # critic = Critic(env, sess)

    # for episode in range(EPISODE):
    #     # Initialize task
    #     env.reset()

    #     for step in range(STEP):
    #         state = env.getState()
    #         action = actor.choose_action(state)
    #         env.executeAction(action)

    #         if step > 0:
    #             reward = env.getReward()
    #             next_state = env.getState()
    #             td_error = critic.train_Q_newtork(
    #                 state, reward, next_state)
    #             # true_gradient = grad[logPi(s,a) * td_error]
    #             actor.learn(state, 1, td_error)
    #             state = next_state

    #     # Test every 100 episode
    #     if episode % 100 == 0:
    #         # Test
    #         env.reset()
    #         reward = 0

    #         for step in range(STEP):
    #             reward += env.getReward()
    #         print(reward)


