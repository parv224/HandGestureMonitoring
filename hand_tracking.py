import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, detection_conf=0.8, max_hands=2):
        self.hands = mp.solutions.hands.Hands(max_num_hands=max_hands, min_detection_confidence=detection_conf)
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_lms, mp.solutions.hands.HAND_CONNECTIONS)
        return results
