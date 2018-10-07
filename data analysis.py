import pickle
import numpy as np
import umap
import matplotlib.pyplot as plt

actions = ["up-left", "up-right", "down-left", "down-right", "up", "down", "left", "right", "space", "enter"]
action_colors = {"up-left": "#f44242", "up-right": "#f49541", "down-left": "#f1f441", "down-right": "#37dd3f", "up": "#37ddd4", "down": "#375add", "left": "#cf37dd", "right": "#dd377c", "space": "#000000", "enter": "#605d5d"}

data = {i: np.ndarray(shape=(1,70)) for i in ["up-left", "up-right", "down-left", "down-right", "up", "down", "left", "right", "space", "enter"]}
x= np.ndarray(shape=(1,70))
y = []

for i in range(1,6):
    with open("./dataset/dataset "+str(i)+".pkl", "rb") as f:
        vals = pickle.load(f)
        for action_i in actions:
            if len(vals[action_i])!=0:
                a = np.array(vals[action_i])
                print(action_i, a.shape)
                print(action_i, data[action_i].shape)
                data[action_i] = np.concatenate((data[action_i], a), axis=0)
                print("after concat", action_i, data[action_i].shape)
                x = np.append(x,a,axis=0)
                [y.append(action_i) for _ in range(len(a))]
print([(i,len(data[i])) for i in actions])

with open("./dataset/combined_dataset.pkl","wb") as f:
    pickle.dump(data,f)

x = x[1:]
print(y)
print(x.shape, len(y))

y_c = [action_colors[i] for i in y]

print("fitting umap")
reducer = umap.UMAP()
embedding = reducer.fit_transform(x)
print(embedding.shape)


plt.scatter(embedding[:, 0], embedding[:, 1], c=y_c)
plt.gca().set_aspect('equal', 'datalim')

plt.show()
