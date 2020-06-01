import tensorflow as tf
import numpy as np
import random
from collections import deque

# Hyper Parameters
GAMMA = 0.95  # discount factor
LEARNING_RATE = 0.01

class Actor():
    def __init__(self, env, sess):
        self.time_step = 0
        # state = [upCarNum, downCarNum, leftCarNum, rightCarNum,
        #   upOrderNum, downOrderNum, leftOrderNum, rightOrderNum, d.city_time]
        self.state_dim = 9
        # action 0: Onlien action 1: Offline
        self.action_dim = 2             # Set to online or set to offline
        self.create_softmax_network()

        # Init Session
        self.session = sess
        self.session.run(tf.global_variables_initializer())

    def generate_weight(self, shape):
        return tf.Variable(tf.truncated_normal(shape))
    
    def generate_bias(self, shape):
        return tf.Variable(tf.constant(0.01, shape = shape))

    def create_softmax_network(self):
        # network weights
        W1 = self.generate_weight([self.state_dim, 20])
        b1 = self.generate_bias([20])
        W2 = self.generate_weight([20, self.action_dim])
        b2 = self.generate_bias([self.action_dim])

        # layers
        self.state_input = tf.placeholder(tf.float32, [1, self.state_dim], "state")
        self.tf_acts = tf.placeholder(tf.float32, [1, 2], "action_num")
        self.td_error = tf.placeholder(tf.float32, 1, "td_error")

        # hidden layer
        h_layer = tf.nn.relu(tf.linalg.matmul(self.state_input, W1) + b1)
        # softmax layer
        self.softmax_layer = tf.linalg.matmul(h_layer, W2) + b2
        self.all_act_prob = tf.nn.softmax(self.softmax_layer, name = "act_prob")
        self.neg_log_prob = tf.nn.softmax_cross_entropy_with_logits(logits=self.softmax_layer,
                                                                    labels=self.tf_acts)
        self.exp = tf.reduce_mean(self.neg_log_prob * self.td_error)    # Gradient

        # Train network (Maximize exp, minimize -self.exp)
        self.train_op = tf.train.AdamOptimizer(LEARNING_RATE).minimize(-self.exp)

    def choose_action(self, state):
        probs = self.session.run(self.all_act_prob, feed_dict={
                                 self.state_input: [state]})
        probs = probs[0]
        if probs[0] > probs[1]:
            return 0
        return 1

    def learn(self, state, action, td_error):
        s = state[np.newaxis, :]
        one_hot_action = np.zeros(self.action_dim)
        one_hot_action[action] = 1
        a = one_hot_action[np.newaxis, :]
        # Train on an episode
        self.session.run(self.train_op, feed_dict={
            self.state_input: s,
            self.tf_acts: a,
            self.td_error: td_error,
        })




