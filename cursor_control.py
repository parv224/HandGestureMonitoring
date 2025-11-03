import pyautogui
import numpy as np

class CursorController:
    def __init__(self, smooth_factor=5):
        self.prev_x, self.prev_y = 0, 0
        self.smooth_factor = smooth_factor
        self.screen_w, self.screen_h = pyautogui.size()

    def move_cursor(self, x, y, frame_w, frame_h):
        screen_x = np.interp(x, [0, frame_w], [0, self.screen_w])
        screen_y = np.interp(y, [0, frame_h], [0, self.screen_h])
        curr_x = self.prev_x + (screen_x - self.prev_x) / self.smooth_factor
        curr_y = self.prev_y + (screen_y - self.prev_y) / self.smooth_factor
        pyautogui.moveTo(curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y
