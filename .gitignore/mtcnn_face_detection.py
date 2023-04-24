import cv2
import torch
import numpy as np
from facenet_pytorch import MTCNN


class FaceDetector(object):
    def __init__(self, mtcnn):
        self.mtcnn = mtcnn

    def _draw(self, frame, boxes, probs, landmarks):
        try:
            for box, prob, ld in zip(boxes, probs, landmarks):
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 0, 255), thickness=1)
        except:
            pass
        return frame

    def run(self):
        cap = cv2.VideoCapture(1)
        while True:
            ret, frame = cap.read()
            try:
                boxes, probs, landmarks = self.mtcnn.detect(frame, landmarks=True)
                self._draw(frame, boxes, probs, landmarks)
            except:
                pass
            cv2.imshow('Face Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()


mtcnn = MTCNN()
fcd = FaceDetector(mtcnn)
fcd.run()
