import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

# Initialize tkinter window
root = Tk()
root.title("Webcam App with Background Blur")
root.geometry("800x600")

# Create a label to display the video frame
label = Label(root)
label.pack()

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

# Webcam capture
cap = cv2.VideoCapture(0)

# Variable to store the current frame
current_frame = None

def process_frame():
    global current_frame
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)  # Mirror the frame
    h, w = frame.shape[:2]

    # Apply the background subtractor
    fg_mask = bg_subtractor.apply(frame)

    # Clean the mask using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    # Detect faces in the frame
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Create a mask for the faces
    face_mask = np.zeros_like(fg_mask)
    for (x, y, w, h) in faces:
        face_mask[y:y+h, x:x+w] = 255

    # Combine the face mask with the foreground mask
    combined_mask = cv2.bitwise_or(fg_mask, face_mask)

    # Create a three-channel mask for bitwise operations
    combined_mask_colored = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)

    # Blur the original frame
    blurred_frame = cv2.GaussianBlur(frame, (15, 15), 0)

    # Combine the original frame and the blurred background using the mask
    frame_with_blur = np.where(combined_mask_colored == 255, frame, blurred_frame)

    # Store the current frame
    current_frame = frame_with_blur

    # Convert the frame for tkinter display
    img = cv2.cvtColor(frame_with_blur, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the tkinter label with the new image
    label.imgtk = imgtk
    label.configure(image=imgtk)
    label.after(10, process_frame)

def save_image():
    if current_frame is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            cv2.imwrite(file_path, current_frame)

# Add a button to save the image
save_button = Button(root, text="Save Image", command=save_image)
save_button.pack()

# Start processing frames
process_frame()

# Start the tkinter main loop
root.mainloop()

# Release resources when closing
cap.release()
cv2.destroyAllWindows()