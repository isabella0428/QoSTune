import tensorflow as tf
import numpy as np
import random
from collections import deque

EPSILON = 0.01  # final value of epsilon
REPLAY_SIZE = 10000  # experience replay buffer size
BATCH_SIZE = 32  # size of minibatch
REPLACE_TARGET_FREQ = 10  # frequency to update target Q network
GAMMA = 0.95

class Critic():
    def __init__(self, env, sess):
        # init some parameters
        self.time_step = 0
        self.epsilon = EPSILON
        # state = [upCarNum, downCarNum, leftCarNum, rightCarNum,
        #   upOrderNum, downOrderNum, leftOrderNum, rightOrderNum, d.city_time]
        self.state_dim = 9
        self.action_dim = 2

        self.create_Q_Network()
        self.create_training_method()

        # init session
        self.session = sess
        self.session.run(tf.global_variables_initializer())

    def generate_weight(self, shape):
        return tf.Variable(tf.truncated_normal(shape))

    def generate_bias(self, shape):
        return tf.Variable(tf.constant(0.01, shape=shape))

    def create_Q_Network(self):
        # network weights
        W1 = self.generate_weight([self.state_dim, 20])
        b1 = self.generate_bias([20])
        W2 = self.generate_weight([20, 1])
        b2 = self.generate_bias([1])

        # layer
        self.state_input = tf.placeholder(tf.float32, [1, self.state_dim], "state")
        self.hidden_layer = tf.nn.relu(
            tf.linalg.matmul(self.state_input, W1) + b1)
        self.Q_value = tf.linalg.matmul(self.hidden_layer, W2) + b2

    def create_training_method(self):
        self.next_value = tf.placeholder(tf.float32, [1, 1], "v_next")
        self.reward = tf.placeholder(tf.float32, None, 'reward')

        with tf.variable_scope('squared_TD_error'):
            self.td_error = self.reward + GAMMA * self.next_value - self.Q_value
            self.loss = tf.square(self.td_error)
        with tf.variable_scope('train'):
            self.train_op = tf.train.AdamOptimizer(self.epsilon).minimize(self.loss)

    def train_Q_newtork(self, state, reward, next_state):
        s, s_ = state[np.newaxis, :], next_state[np.newaxis, :]
        v_ = self.session.run(self.Q_value, {self.state_input: s_})
        td_error, _ = self.session.run([self.td_error, self.train_op],
                                       {self.state_input: s, self.next_value: v_, self.reward: reward})
        return td_error
