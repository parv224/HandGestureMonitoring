import cv2
import mediapipe as mp
import numpy as np
import os
import math

class ImageViewer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.images = [cv2.imread(os.path.join(folder_path, f))
                       for f in os.listdir(folder_path)
                       if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        self.images = [img for img in self.images if img is not None]

        if not self.images:
            raise ValueError(f"No images found in folder: {folder_path}")

        self.index = 0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def next_image(self):
        self.index = (self.index + 1) % len(self.images)

    def prev_image(self):
        self.index = (self.index - 1) % len(self.images)

    def render(self, frame):
        """Render current image (scaled, centered) on given frame."""
        fh, fw, _ = frame.shape
        img = self.images[self.index]

        new_w = int(fw * self.scale)
        new_h = int(fh * self.scale)
        resized_img = cv2.resize(img, (new_w, new_h))

        x_offset = (fw - new_w) // 2 + self.offset_x
        y_offset = (fh - new_h) // 2 + self.offset_y

        # keep inside bounds
        x_offset = np.clip(x_offset, -new_w + 100, fw - 100)
        y_offset = np.clip(y_offset, -new_h + 100, fh - 100)

        x1 = max(x_offset, 0)
        y1 = max(y_offset, 0)
        x2 = min(x_offset + new_w, fw)
        y2 = min(y_offset + new_h, fh)

        ox1 = max(-x_offset, 0)
        oy1 = max(-y_offset, 0)
        ox2 = ox1 + (x2 - x1)
        oy2 = oy1 + (y2 - y1)

        overlay = frame.copy()
        overlay[y1:y2, x1:x2] = resized_img[oy1:oy2, ox1:ox2]

        return overlay


class ClickGestures:
    def __init__(self):
        self.click_threshold = 25
        self.clicking = False

    def click_check(self, thumb_tip, index_tip):
        # your click logic here (same as before)
        pass

    def detect_gestures(self, thumb_tip, index_tip):
        self.click_check(thumb_tip, index_tip)