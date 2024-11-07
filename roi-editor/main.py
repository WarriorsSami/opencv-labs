import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import os

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor with ROI Selector")

        # Variables for storing image and ROI coordinates
        self.image_path = None
        self.image_cv = None
        self.roi_start = None
        self.roi_end = None
        self.canvas_image_id = None

        # Canvas for displaying the image
        self.canvas = tk.Canvas(root, width=800, height=600, bg="gray")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Button to select image
        self.select_image_button = tk.Button(root, text="Select Image", command=self.load_image)
        self.select_image_button.pack()

        # Binding mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.start_roi_selection)
        self.canvas.bind("<B1-Motion>", self.update_roi_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_roi_selection)

    def load_image(self):
        home_dir = os.path.expanduser("~")
        file_path = filedialog.askopenfilename(initialdir=home_dir, filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path:
            return
        self.image_path = file_path
        self.image_cv = cv2.imread(self.image_path)
        self.display_image(self.image_cv)

    def display_image(self, image_cv):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate the scaling factor to fit the image within the canvas
        scale = min(canvas_width / image_cv.shape[1], canvas_height / image_cv.shape[0])
        new_width = int(image_cv.shape[1] * scale)
        new_height = int(image_cv.shape[0] * scale)

        # Resize the image
        resized_image_cv = cv2.resize(image_cv, (new_width, new_height))

        # Update the image_cv with the resized image
        self.image_cv = resized_image_cv

        image_rgb = cv2.cvtColor(resized_image_cv, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)

        # Calculate the coordinates to center the image
        x_center = (canvas_width - new_width) // 2
        y_center = (canvas_height - new_height) // 2

        self.canvas_image_id = self.canvas.create_image(x_center, y_center, anchor="nw", image=image_tk)
        self.canvas.image = image_tk  # Keep a reference to avoid garbage collection

    def start_roi_selection(self, event):
        self.roi_start = (event.x, event.y)

    def update_roi_selection(self, event):
        if self.roi_start:
            self.canvas.delete("roi_rectangle")
            self.roi_end = (event.x, event.y)
            self.canvas.create_rectangle(
                self.roi_start[0], self.roi_start[1], event.x, event.y,
                outline="green", width=2, tags="roi_rectangle"
            )

    def end_roi_selection(self, event):
        if self.roi_start:
            self.roi_end = (event.x, event.y)
            self.ask_color_fill()

    def ask_color_fill(self):
        color = colorchooser.askcolor(title="Select Background Color")[0]
        if color:
            self.fill_background_with_color(color)

    def fill_background_with_color(self, color):
        if not self.roi_start or not self.roi_end:
            messagebox.showerror("Error", "ROI not properly defined.")
            return

        # Convert the selected color to BGR for OpenCV
        bgr_color = (int(color[2]), int(color[1]), int(color[0]))

        # Calculate the ROI coordinates
        x1, y1 = min(self.roi_start[0], self.roi_end[0]), min(self.roi_start[1], self.roi_end[1])
        x2, y2 = max(self.roi_start[0], self.roi_end[0]), max(self.roi_start[1], self.roi_end[1])

        # Create a mask for the entire image
        mask = np.zeros(self.image_cv.shape[:2], dtype=np.uint8)

        # Create a mask for the ROI
        roi = self.image_cv[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        roi_flood_fill = binary_mask.copy()

        # Flood fill the ROI mask to remove any holes
        h, w = binary_mask.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(roi_flood_fill, mask, (0, 0), 255)

        # Combine the binary mask with the flood filled mask to get the foreground object
        roi_flood_fill_inv = cv2.bitwise_not(roi_flood_fill)
        foreground_mask = cv2.bitwise_or(binary_mask, roi_flood_fill_inv)
        foreground_object = cv2.bitwise_and(roi, roi, mask=foreground_mask)

        # Create a mask for the background
        background_mask = cv2.bitwise_not(foreground_mask)

        # Fill the background with the selected color
        background = np.full_like(roi, bgr_color, dtype=np.uint8)
        result_roi = cv2.bitwise_and(background, background, mask=background_mask)

        # Combine the foreground object and the background
        result_roi = cv2.add(foreground_object, result_roi)

        # Update the background of the original image with the selected color
        self.image_cv = cv2.rectangle(self.image_cv, (0, 0), (self.image_cv.shape[1], self.image_cv.shape[0]), bgr_color, -1)

        # Replace the ROI in the original image with the result
        self.image_cv[y1:y2, x1:x2] = result_roi

        # Display the result
        self.display_image(self.image_cv)
        self.save_image(self.image_cv)

    def save_image(self, image_cv):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, image_cv)
            messagebox.showinfo("Success", f"Image saved to {file_path}")

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()