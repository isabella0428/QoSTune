import pickle
from simulator import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def findSimilarKnobs(queryVec, allQuery):
    dist = 10000000000000000
    idx = -1
    for i, query in enumerate(allQuery):
        # cur_dist = np.sum()
        cur_dist = np.sum(np.square(np.array(query)-np.array(queryVec)))
        if cur_dist < dist:
            dist = cur_dist
            idx = i
    return idx

if __name__ == "__main__":
    potential_knobs = pd.read_csv("knobs.csv", dtype={"unit":np.int32, "lb":np.int32, "hb":np.int32})
    variables = list(potential_knobs["knobs"])
    lowerBound, higherBound = list(potential_knobs["lb"]), list(potential_knobs["hb"])
    unit = list(potential_knobs["unit"])

    env = Env(variables=variables, unit=unit)

    with open("pickle/knobsMemoryPool.pkl", "rb") as f:
        knobs = pickle.load(f)
    
    with open("pickle/queryMemoryPool.pkl", "rb") as f:
        query = pickle.load(f)

    epoches = 100

    reward = []
    total_reward = 0

    for e in range(epoches):
        queries, queryVec = env.generateQuery()
        idx = findSimilarKnobs(queryVec, query)
        cur_knobs = knobs[idx]

        env.reset()
        cmd = "set session {}={};"
        for i, k in enumerate(cur_knobs[0]):
            value = cur_knobs[1][i]
            c = cmd.format(k, value)
            env.execute(c)
        cur_reward = env.getMetricsVec(queries)[0]
        if cur_reward > -2:
            reward.append(cur_reward)
            total_reward += cur_reward

    print(total_reward/len(reward))
    
    plt.title("Performance increase with test workload")
    plt.xlabel("Workload")
    plt.ylabel("Performance increase(%)")
    plt.scatter(list(range(len(reward))), reward)
    plt.savefig("test_workload.png")

