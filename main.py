import cv2
import math
import numpy as np
import mediapipe as mp
import pyautogui

from modules.image_viewer import ImageViewer
from modules.click_gestures import ClickGestures
from modules.cursor_control import CursorController
from modules.hand_tracking import HandDetector
from modules.system_control import SystemControl
from modules.text_selection import TextSelection

# === Initialize modules ===
detector = HandDetector(detection_conf=0.8, max_hands=2)
cursor = CursorController(smooth_factor=4)
clicker = ClickGestures()
system = SystemControl()
selector = TextSelection()  #  Correct initialization
viewer = ImageViewer(folder_path=r"D:\\HandGestureMonitoring\\images")

# === Webcam Setup ===
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# === Mediapipe Utils ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# === Variables ===
current_mode = "cursor"
prev_distance = None
clap_cooldown = 0
click_cooldown = 0
hand_labels = {}

print("""
======================================
 Cursor Mode + Image Mode Project
======================================
Press [M] → Switch Mode
Press [Q] → Quit
======================================
""")

# --- Helper functions ---
def is_pinch(lm):
    x1, y1 = lm[4]
    x2, y2 = lm[8]
    return math.hypot(x2 - x1, y2 - y1) < 40

def is_clap(lm1, lm2):
    wrist1, wrist2 = lm1[0], lm2[0]
    distance = math.hypot(wrist2[0] - wrist1[0], wrist2[1] - wrist1[1])
    return distance < 180

def is_right_click(lm):
    """Detects right click when middle and thumb touch."""
    x1, y1 = lm[4]
    x2, y2 = lm[12]
    return math.hypot(x2 - x1, y2 - y1) < 40

# === Main Loop ===
while True:
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    results = detector.find_hands(frame)
    h, w, _ = frame.shape
    hand_positions = []
    hand_labels.clear()

    # Detect hands and classify (Left/Right)
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm_list = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
            hand_positions.append(lm_list)
            hand_labels[len(hand_positions) - 1] = label

    # === MODE 1: CURSOR MODE ===
    if current_mode == "cursor":
        if len(hand_positions) == 1:
            lm = hand_positions[0]
            index_tip = lm[8]
            thumb_tip = lm[4]
            middle_tip = lm[12]

            #  Move system cursor
            cursor.move_cursor(index_tip[0], index_tip[1], w, h)

            #  Left Click (thumb + index pinch)
            if math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1]) < 40:
                pyautogui.click()
                print("Left Click")

            #  Right Click (thumb + middle touch)
            elif math.hypot(thumb_tip[0] - middle_tip[0], thumb_tip[1] - middle_tip[1]) < 40:
                pyautogui.click(button="right")
                print("🖱Right Click")

            # Text Selection (index + middle fingers close)
            dist = math.hypot(index_tip[0] - middle_tip[0], index_tip[1] - middle_tip[1])
            if dist < 50:
                if not selector.selecting:
                    pyautogui.mouseDown()
                    selector.selecting = True
                    print(" Start Selecting Text")
            else:
                if selector.selecting:
                    pyautogui.mouseUp()
                    selector.selecting = False
                    print("Stop Selecting Text")

            # Capati → Maximize Window
            capati_dist = math.hypot(thumb_tip[0] - middle_tip[0], thumb_tip[1] - middle_tip[1])
            if capati_dist < 40 and clap_cooldown == 0:
                system.maximize_window()
                print("Flatten → Maximize Window")
                clap_cooldown = 25

        elif len(hand_positions) == 2:
            lm1, lm2 = hand_positions
            if is_clap(lm1, lm2) and clap_cooldown == 0:
                system.minimize_window()
                print("CLAP → Minimize Window")
                clap_cooldown = 25

    # === MODE 2: IMAGE VIEWER ===
    elif current_mode == "image":
        if len(hand_positions) == 2:
            lm1, lm2 = hand_positions
            left_hand = right_hand = None
            left_index = right_index = None

            for i, lm in enumerate(hand_positions):
                if hand_labels[i] == "Left":
                    left_hand, left_index = lm, lm[8]
                elif hand_labels[i] == "Right":
                    right_hand, right_index = lm, lm[8]

            # Zoom with both pinched
            if left_hand and right_hand and is_pinch(left_hand) and is_pinch(right_hand):
                x1, y1 = left_index
                x2, y2 = right_index
                distance = math.hypot(x2 - x1, y2 - y1)
                if prev_distance is not None:
                    diff = distance - prev_distance
                    if abs(diff) > 10:
                        viewer.zoom("in" if diff > 0 else "out")
                prev_distance = distance
            else:
                prev_distance = None

            # Clap → Next Image
            if is_clap(lm1, lm2) and clap_cooldown == 0:
                viewer.next_image()
                print(" CLAP → Next Image")
                clap_cooldown = 25

        elif len(hand_positions) == 1:
            label = list(hand_labels.values())[0]
            lm = hand_positions[0]
            index_tip = lm[8]
            if label == "Right":
                viewer.handle_drag(index_tip, index_tip)
            else:
                viewer.stop_drag()

    # === Label Display ===
    for i, lm in enumerate(hand_positions):
        label = hand_labels.get(i, "?")
        x, y = lm[0]
        color = (0, 128, 255) if label == "Right" else (255, 0, 128)
        cv2.putText(frame, label.upper(), (x - 30, y - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # === Display ===
    output = viewer.render(frame) if current_mode == "image" else frame
    color = (0, 255, 0) if current_mode == "cursor" else (0, 255, 255)
    cv2.putText(output, f"MODE: {current_mode.upper()}", (40, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    cv2.namedWindow("AI Gesture Control", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("AI Gesture Control",
                          cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("AI Gesture Control", output)

    # === Cooldowns ===
    if clap_cooldown > 0:
        clap_cooldown -= 1
    if click_cooldown > 0:
        click_cooldown -= 1

    # === Keys ===
    key = cv2.waitKey(10) & 0xFF
    if key == ord('m'):
        current_mode = "image" if current_mode == "cursor" else "cursor"
        print(f" Switched to {current_mode.upper()} MODE")
    elif key == ord('q'):
        print(" Exiting...")
        break

cap.release()
cv2.destroyAllWindows()

