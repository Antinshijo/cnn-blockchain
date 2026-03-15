import numpy as np

def compare_cnn_features(stored, new):

    stored_vec = np.array(stored)
    new_vec = np.array(new)

    distance = np.linalg.norm(stored_vec - new_vec)

    return distance