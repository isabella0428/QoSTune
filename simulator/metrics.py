import numpy as np
import random
import pandas as pd
import scipy.stats
from sklearn.decomposition import FactorAnalysis
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso
from sklearn.cluster import KMeans
from simulator import *
from run import *
import pickle

def factorAnalysis(data):
    transformer = FactorAnalysis(n_components=100, random_state=0)
    transformed_data = transformer.fit_transform(np.transpose(data))
    return transformed_data

def generate_knobs(variables, unit, lowerBound, higherBound):
    knobs = {}
    for i, var in enumerate(variables):
        u = unit[i]
        lb = lowerBound[i]
        hb = higherBound[i]
        knobs[var] = random.randint(lb, hb) * u
    return knobs

def correlation(metrics, knobs, knobsName, lowerBound, higherBound, unit):
    # Not sure the metrics
    # Intended:                                     metrics: row: single metrics     knobs: row: knobs
    pearson = np.zeros(knobs.shape[0])
    # print(metrics)

    for i in range(metrics.shape[0]):
        mrow = metrics[i, :]
        
        # Determine if mrow is constant array
        delta = 0
        num = set()
        for n in mrow:
            num.add(n)
        if len(num) == 1:
            continue

        for j in range(knobs.shape[0]):
            krow = knobs[j, :]
            r = scipy.stats.pearsonr(mrow, krow)[0]
            pearson[i] += r
    
    pDict = {}
    for i, knob in enumerate(knobs):
        pDict[i] = pearson[i]
    
    selected = []

    sortedDict = sorted(pDict.items(),  key=lambda d: d[1], reverse=False)

    selected_knobs, selected_unit, selected_lb, selected_hb = [], [], [], []
    topK = 5

    for item in sortedDict:
        i = item[0]
        selected_knobs.append(knobsName[i])
        selected_unit.append(unit[i])
        selected_lb.append(lowerBound[i])
        selected_hb.append(higherBound[i])
        if len(selected_knobs) >= topK:
            break
    
    return selected_knobs, selected_unit, selected_lb, selected_hb

if __name__ == "__main__":
    # All potential knobs
    knobs = pd.read_csv("knobs.csv", dtype={"unit":np.int32, "lb":np.int32, "hb":np.int32})
    variables = list(knobs["knobs"])
    lowerBound, higherBound = list(knobs["lb"]), list(knobs["hb"])
    unit = list(knobs["unit"])

    # Create environment
    env = Env(variables=variables, unit=unit)

    # Memory Pool
    queryMemoryPool = []
    knobsMemoryPool = []

    epoches,times = 300, 30

    for e in range(epoches):
        queries, queryVec = env.generateQuery()
        metricsMat = []                              # Row: one time matrix, Column:     metrics value in different configuration
        knobsMat = []                                # Row: knob, Column:    knob value in different configuration
        metricsNum = 0
        metricsDict = {}

        metricsName, knobsName = [], []

        for i in range(times):
            knobsDict = generate_knobs(variables, unit, lowerBound, higherBound)
            env.setKnobs(knobsDict)

            knobs, knobName = [], []
            for key in knobsDict.keys():
                val = knobsDict[key]
                knobs.append(val)
                knobsName.append(key)

            knobsMat.append(knobs)
            metricsDict = env.getAllMetrics(queries)

            metrics, metricsName = [], []
            for key in metricsDict.keys():
                val = metricsDict[key]
                metrics.append(val)
                metricsName.append(key)
            metricsNum = len(metrics)
            metricsMat.append(metrics)
        
        knobsMat = np.array(knobsMat)
        metricsMat = np.array(metricsMat)
        # Do Factor Analysis
        transformed_data = factorAnalysis(metricsMat)

        # Kmeans
        n_clusters = 5 
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(transformed_data)
        centers = kmeans.cluster_centers_
        selectedMetrics = [-1] * n_clusters
        dist = [0] * n_clusters

        # Get centroid metric
        for c, center in enumerate(centers):
            for i, row in enumerate(transformed_data):
                cur_dist = np.square(np.sum(row - center))
                if i == 0:
                    selectedMetrics[c] = i
                    dist[c] = cur_dist
                else:
                    if cur_dist < dist[c]:
                        selectedMetrics[c] = i
                        dist[c] = cur_dist
        
        # Get selected metric name
        selectedMetricsName = []
        for i, selectedId in enumerate(selectedMetrics):
            selectedMetricsName.append(metricsName[selectedId])

        important_metrics = []
        for row in metricsMat:
            temp = []
            for selectedId in selectedMetrics:
                temp.append(row[selectedId])
            important_metrics.append(temp)
        
        important_metrics = np.array(important_metrics)
        important_metrics = np.transpose(important_metrics)
        knobsMat = np.transpose(knobsMat)


        selectedKnobs, selectedUnit, selectedLb, selectedHb = correlation(
                important_metrics, knobsMat, knobsName, lowerBound, higherBound, unit)

        val = train(selectedKnobs, selectedLb, selectedHb, selectedUnit)
        
        print(selectedKnobs)
        print(val)
        print()
        queryMemoryPool.append(queryVec)
        knobsMemoryPool.append([selectedKnobs, val])

    with open("pickle/queryMemoryPool.pkl", "wb") as f:
        pickle.dump(queryMemoryPool, f)
    with open("pickle/knobsMemoryPool.pkl", "wb") as f:
        pickle.dump(knobsMemoryPool, f)
        

