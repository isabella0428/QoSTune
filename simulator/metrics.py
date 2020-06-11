import numpy as np
import random
import pandas as pd
import scipy.stats
from sklearn.decomposition import FactorAnalysis
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso
from sklearn.cluster import KMeans
from simulator import *

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

def correlation(metrics, knobs, knobsName):
    # Not sure the metrics
    # Intended:                 metrics: row: single metrics     knobs: row: knobs
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
    
    topK = 3
    selected = []

    sortedDict = sorted(pDict.items(),  key=lambda d: d[1], reverse=False)

    selected = []
    topK = 10

    for item in sortedDict:
        selected.append(knobsName[item[0]])
        if len(selected) >= topK:
            break
    
    return selected

if __name__ == "__main__":
    knobs = pd.read_csv("knobs.csv", dtype={"unit":np.int32, "lb":np.int32, "hb":np.int32})
    variables = list(knobs["knobs"])

    lowerBound, higherBound = list(knobs["lb"]), list(knobs["hb"])
    unit = list(knobs["unit"])

    # variables = ["sort_buffer_size", "read_buffer_size", "tmp_table_size", 
    #     "preload_buffer_size", "transaction_prealloc_size"]
    # unit = [8 * 1024, 8 * 1024, 10000, 2*1024, 1024]
    # lowerBound = [1, 1, 100, 1, 1]
    # higherBound = [32, 32, 100000000, 100, 10]

    # Create environment
    env = Env(variables=variables, unit=unit)

    epoches,times = 3, 10

    for e in range(epoches):
        queries, _ = env.generateQuery()
        metricsMat = []                     # Row: one time matrix, Column:     metrics value in different configuration
        knobsMat = []                        # Row: knob, Column:    knob value in different configuration
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

        print(selectedMetricsName)

        important_metrics = []
        for row in metricsMat:
            temp = []
            for selectedId in selectedMetrics:
                temp.append(row[selectedId])
            important_metrics.append(temp)
        
        important_metrics = np.array(important_metrics)
        important_metrics = np.transpose(important_metrics)
        knobsMat = np.transpose(knobsMat)

        selectedKnobs = correlation(important_metrics, knobsMat, knobsName)
        print(selectedKnobs)
        
        
