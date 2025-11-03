import cv2
import numpy as np
import os
import math

class ImageViewer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.images = [
            cv2.imread(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".png", ".jpeg"))
        ]
        self.images = [img for img in self.images if img is not None]

        if not self.images:
            raise ValueError(f"No images found in folder: {folder_path}")

        # ---- State Variables ----
        self.index = 0

        # zoom and drag
        self.scale = 1.0
        self.target_scale = 1.0  # smooth zoom target
        self.offset_x = 0
        self.offset_y = 0
        self.target_offset_x = 0
        self.target_offset_y = 0

        self.drag_active = False
        self.prev_center = None
        self.smooth_factor = 0.25  # adjust smoothness (0.1–0.3)

    def next_image(self):
        self.index = (self.index + 1) % len(self.images)

    def prev_image(self):
        self.index = (self.index - 1) % len(self.images)

    # --- smooth transition update ---
    def smooth_update(self):
        self.scale += (self.target_scale - self.scale) * self.smooth_factor
        self.offset_x += (self.target_offset_x - self.offset_x) * self.smooth_factor
        self.offset_y += (self.target_offset_y - self.offset_y) * self.smooth_factor

    # --- drag movement ---
    def handle_drag(self, left_index, right_index):
        cx = int((left_index[0] + right_index[0]) / 2)
        cy = int((left_index[1] + right_index[1]) / 2)
        center = np.array([cx, cy])

        if not self.drag_active:
            self.drag_active = True
            self.prev_center = center
        else:
            diff = center - self.prev_center
            self.target_offset_x += int(diff[0])
            self.target_offset_y += int(diff[1])
            self.prev_center = center

    def stop_drag(self):
        self.drag_active = False
        self.prev_center = None

    # --- zoom control ---
    def zoom(self, direction):
        """Smooth zooming in/out"""
        if direction == "in":
            self.target_scale = min(self.target_scale + 0.1, 3.0)
        elif direction == "out":
            self.target_scale = max(self.target_scale - 0.1, 0.5)

    def render(self, frame):
        """Render image on webcam feed"""
        self.smooth_update()

        fh, fw, _ = frame.shape
        img = self.images[self.index]

        # compute new scaled size
        new_w = int(fw * self.scale)
        new_h = int(fh * self.scale)
        resized_img = cv2.resize(img, (new_w, new_h))

        # apply drag offset
        x_offset = (fw - new_w) // 2 + int(self.offset_x)
        y_offset = (fh - new_h) // 2 + int(self.offset_y)

        # limit drag area
        x_offset = np.clip(x_offset, -new_w + 100, fw - 100)
        y_offset = np.clip(y_offset, -new_h + 100, fh - 100)

        # visible portion
        x1 = max(x_offset, 0)
        y1 = max(y_offset, 0)
        x2 = min(x_offset + new_w, fw)
        y2 = min(y_offset + new_h, fh)

        ox1 = max(-x_offset, 0)
        oy1 = max(-y_offset, 0)
        ox2 = ox1 + (x2 - x1)
        oy2 = oy1 + (y2 - y1)

        output = frame.copy()
        output[y1:y2, x1:x2] = resized_img[oy1:oy2, ox1:ox2]
        return output
