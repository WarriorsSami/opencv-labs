import cv2
import numpy as np
from tkinter import Tk, Button, Label, Scale, HORIZONTAL, filedialog, messagebox, Canvas
from PIL import Image, ImageTk
import os


class ObjectCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Object Counter")

        # Initialize variables
        self.image = None
        self.processed_image = None
        self.dilation_iterations = 1

        # Buttons and Sliders
        self.load_button = Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        self.dilate_label = Label(root, text="Dilation Iterations")
        self.dilate_label.pack()
        self.dilate_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=self.update_dilation)
        self.dilate_slider.set(self.dilation_iterations)
        self.dilate_slider.pack()

        self.save_button = Button(root, text="Save Processed Image", command=self.save_image, state="disabled")
        self.save_button.pack()

        # Canvas for displaying the image
        self.canvas = Canvas(root, width=600, height=400)
        self.canvas.pack()

    def load_image(self):
        initial_dir = os.path.expanduser("~")
        file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
        if not file_path:
            return
        self.image = cv2.imread(file_path)
        if self.image is None:
            messagebox.showerror("Error", "Could not load image.")
            return
        self.process_image()

    def update_dilation(self, value):
        self.dilation_iterations = int(value)
        self.process_image()

    def process_image(self):
        if self.image is None:
            return

        # Convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (11, 11), 0)

        # Use Canny edge detector
        canny = cv2.Canny(blur, 30, 150, 3)

        # Dilate the edges
        dilated = cv2.dilate(canny, (1, 1), iterations=self.dilation_iterations)

        # Find contours
        contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a black background image
        output_image = np.zeros_like(self.image)
        font = cv2.FONT_HERSHEY_SIMPLEX

        for i, contour in enumerate(contours):
            color = tuple(np.random.randint(0, 255, size=3).tolist())
            cv2.drawContours(output_image, [contour], -1, color, thickness=cv2.FILLED)

            # Calculate the center of the enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))

            # Add the contour number to the image
            cv2.putText(output_image, str(i + 1), center, font, 0.6, (255, 255, 255), 2)

        self.processed_image = output_image

        # Resize the image to fit the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_resized = cv2.resize(output_image, (canvas_width, canvas_height))

        # Convert the image to a format that can be displayed in Tkinter
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        # Display the image on the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk)
        self.canvas.image = image_tk  # Keep a reference to avoid garbage collection

        self.save_button.config(state="normal")

    def save_image(self):
        if self.processed_image is None:
            messagebox.showerror("Error", "No processed image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if not file_path:
            return
        cv2.imwrite(file_path, self.processed_image)
        messagebox.showinfo("Info", f"Image saved to {file_path}")


def main():
    root = Tk()
    app = ObjectCounterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()