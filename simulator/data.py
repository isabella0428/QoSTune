# import pickle

# if __name__ == "__main__":
#     with open("pickle/knobsMemoryPool.pkl", "rb") as f:
#         knobs = pickle.load(f)
    
#     with open("pickle/queryMemoryPool.pkl", "rb") as f:
#         query = pickle.load(f)
    
#     print(knobs)
#     print(query)

import matplotlib.pyplot as plt

f = open("ans.txt")
reward = []
total_reward = 0

for line in open('ans.txt'):
    line = f.readline()
    parts = line.split(":")
    other_parts = line.split("Final")
    if len(parts) < 2 or len(other_parts) < 2:
        continue
    sec_part = float(parts[1].strip())

    if sec_part < 0:
        continue

    reward.append(sec_part)
    total_reward += sec_part

print(total_reward/len(reward))

plt.title("Performance Increase with train workload")
plt.xlabel("Workload")
plt.ylabel("Performance Increase(%)")
plt.scatter(list(range(len(reward))), reward)
plt.savefig("train_workload.png")