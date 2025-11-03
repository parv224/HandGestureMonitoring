import pyautogui

class SystemControl:
    def __init__(self):
        pass

    def minimize_window(self):
        pyautogui.hotkey('win', 'down')

    def maximize_window(self):
        pyautogui.hotkey('win', 'up')

    def close_window(self):
        pyautogui.hotkey('alt', 'f4')
