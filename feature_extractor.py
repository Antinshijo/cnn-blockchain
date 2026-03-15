import cv2
import numpy as np

def extract_features(image_path):

    image = cv2.imread(image_path)

    # Resize image
    image = cv2.resize(image, (200,200))

    # Color feature
    mean_color = image.mean(axis=(0,1)).tolist()

    # Edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,100,200)

    edge_count = int(edges.sum())

    # Pattern feature
    blur = cv2.GaussianBlur(gray,(5,5),0)
    pattern_score = int(blur.mean())

    features = {
        "mean_color": mean_color,
        "edge_strength": edge_count,
        "pattern_score": pattern_score
    }

    return features