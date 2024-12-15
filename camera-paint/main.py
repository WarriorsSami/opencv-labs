import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from threading import Thread

# Global variables
drawing = False
canvas = None
# dark blue color
brush_color = (255, 128, 0)  # Default brush color
brush_width = 10  # Default brush width
last_x, last_y = None, None  # Last object positions
color_lower = np.array([90, 50, 50])  # Lower HSV limit for blue
color_upper = np.array([130, 255, 255])  # Upper HSV limit for blue


def process_video():
    global canvas, drawing, brush_color, brush_width, last_x, last_y

    # Start camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    # Initialize drawing image
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip image for natural experience
        frame = cv2.flip(frame, 1)

        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect object color
        mask = cv2.inRange(hsv, color_lower, color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Detect contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours and drawing:
            # Choose the largest contour
            max_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_contour) > 500:
                # Get the center of the contour
                ((x, y), radius) = cv2.minEnclosingCircle(max_contour)
                if radius > 10:
                    if last_x is not None and last_y is not None:
                        # Draw on canvas
                        cv2.line(canvas, (last_x, last_y), (int(x), int(y)), brush_color, int(brush_width))
                    last_x, last_y = int(x), int(y)
        else:
            last_x, last_y = None, None

        # Overlay drawing on video stream
        frame = cv2.add(frame, canvas)

        # Display result
        cv2.imshow("Drawing App", frame)

        # Exit on ESC key press
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


def toggle_drawing():
    global drawing
    drawing = not drawing


def clear_canvas():
    global canvas
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)


def set_brush_width(val):
    global brush_width
    brush_width = float(val)


# Tkinter interface
def start_interface():
    root = tk.Tk()
    root.title("Drawing App Control")

    # Checkbox to toggle drawing
    drawing_var = tk.BooleanVar()
    drawing_var.set(False)
    checkbox = ttk.Checkbutton(root, text="Activate Drawing", variable=drawing_var, command=toggle_drawing)
    checkbox.pack(pady=10)

    # Button to clear canvas
    clear_button = ttk.Button(root, text="Clear Canvas", command=clear_canvas)
    clear_button.pack(pady=10)

    # Scale to set brush width
    brush_width_scale = ttk.Scale(root, from_=1, to=20, orient='horizontal', command=set_brush_width)
    brush_width_scale.set(brush_width)
    brush_width_scale.pack(pady=10)

    root.mainloop()


# Start application
if __name__ == "__main__":
    # Run video processing in a separate thread
    video_thread = Thread(target=process_video)
    video_thread.daemon = True
    video_thread.start()

    # Run interface in the main thread
    start_interface()