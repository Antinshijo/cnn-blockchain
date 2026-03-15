import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image

# Load pretrained CNN
model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

def extract_cnn_features(img_path):

    img = image.load_img(img_path, target_size=(224,224))
    img_array = image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    features = model.predict(img_array)

    return features.flatten().tolist()