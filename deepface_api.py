from deepface import DeepFace
import numpy as np
import cv2

models = [
    "VGG-Face",
    "Facenet",
    "Facenet512",
    "OpenFace",
    "DeepFace",
    "DeepID",
    "ArcFace",
    "Dlib",
    "SFace",
]

objs = DeepFace.stream(db_path="dataset", model_name=models[1], detector_backend="opencv", enable_face_analysis=True)
