import numpy as np

def compare_features(stored, new):

    stored_color = np.array(stored["mean_color"])
    new_color = np.array(new["mean_color"])

    color_distance = np.linalg.norm(stored_color - new_color)

    edge_distance = abs(stored["edge_strength"] - new["edge_strength"])

    score = color_distance + edge_distance

    return score