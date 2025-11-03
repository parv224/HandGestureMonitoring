import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_width, screen_height = pyautogui.size()

# Webcam
cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
smooth_factor = 5

# Gesture thresholds
PINCH_THRESHOLD = 30       # When thumb and index join (click)
IDLE_THRESHOLD = 50        # Ignore actions when far apart (stable zone)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Index and Thumb coordinates
            x1, y1 = lm_list[8]   # Index tip
            x2, y2 = lm_list[4]   # Thumb tip

            # Visual markers
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)

            # Distance between thumb and index
            length = math.hypot(x2 - x1, y2 - y1)

            # Convert coordinates to screen space
            screen_x = int(np.interp(x1, [0, w], [0, screen_width]))
            screen_y = int(np.interp(y1, [0, h], [0, screen_height]))

            curr_x = prev_x + (screen_x - prev_x) / smooth_factor
            curr_y = prev_y + (screen_y - prev_y) / smooth_factor
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Stable open hand (no accidental click)
            if length > IDLE_THRESHOLD:
                cv2.putText(img, "Cursor Mode", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # Pinch click
            elif length < PINCH_THRESHOLD:
                cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                pyautogui.click()
                cv2.putText(img, "Click!", (x1 - 20, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Gesture Cursor", img)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
