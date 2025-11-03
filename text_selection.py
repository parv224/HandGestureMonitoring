import pyautogui
import math

class TextSelection:
    def __init__(self, select_threshold=50):
        self.select_threshold = select_threshold
        self.selecting = False

    def select_text(self, index_tip, middle_tip):
        dist = math.hypot(index_tip[0] - middle_tip[0], index_tip[1] - middle_tip[1])
        if dist < 40 and not self.selecting:
            pyautogui.mouseDown()
            self.selecting = True
        elif dist >= 40 and self.selecting:
            pyautogui.mouseUp()
            self.selecting = False
