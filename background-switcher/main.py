import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import os

main_img = None
main_img_cv = None  # Declare main_img_cv as a global variable
bg_img = None
bg_img_cv = None  # Declare bg_img_cv as a global variable
bg_color = (255, 255, 255)
threshold_value = 127
result = None  # Declare result as a global variable

def open_main_image():
    global main_img, main_img_cv
    home_dir = os.path.expanduser("~")
    file_path = filedialog.askopenfilename(initialdir=home_dir, filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        main_img_cv = cv2.imread(file_path)
        main_img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(main_img_cv, cv2.COLOR_BGR2RGB)))
        canvas.config(width=main_img.width(), height=main_img.height())
        canvas.create_image(0, 0, anchor="nw", image=main_img)

def open_bg_image():
    global bg_img_cv
    home_dir = os.path.expanduser("~")
    file_path = filedialog.askopenfilename(initialdir=home_dir, filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        bg_img_cv = cv2.imread(file_path)
    apply_background()

def choose_bg_color():
    global bg_color
    color_code = colorchooser.askcolor()[0]
    if color_code:
        bg_color = (int(color_code[2]), int(color_code[1]), int(color_code[0]))  # RGB to BGR
    apply_background()

def apply_background():
    global main_img_cv, bg_img_cv, bg_color, threshold_value, result

    if main_img_cv is None:
        messagebox.showerror("Error", "Please choose a foreground image")
        return

    gray = cv2.cvtColor(main_img_cv, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    mask_inv = cv2.bitwise_not(mask)

    if bg_type.get() == "image" and bg_img_cv is not None:
        bg_resized = cv2.resize(bg_img_cv, (main_img_cv.shape[1], main_img_cv.shape[0]))
        background = cv2.bitwise_and(bg_resized, bg_resized, mask=mask)
    else:
        background = np.full(main_img_cv.shape, bg_color, dtype=np.uint8)
        background = cv2.bitwise_and(background, background, mask=mask)

    foreground = cv2.bitwise_and(main_img_cv, main_img_cv, mask=mask_inv)

    result = cv2.add(foreground, background)

    result_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)))
    canvas.create_image(0, 0, anchor="nw", image=result_image)
    canvas.image = result_image

    save_button.config(state=tk.NORMAL)  # Enable the save button

def update_threshold(value):
    global threshold_value
    threshold_value = int(value)
    if main_img_cv is not None:
        apply_background()

def save_image():
    global result
    if result is not None:
        home_dir = os.path.expanduser("~")
        file_path = filedialog.asksaveasfilename(
            initialdir=home_dir,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")]
        )
        if file_path:
            cv2.imwrite(file_path, result)
            messagebox.showinfo("Image Saved", f"Image saved to {file_path}")
    else:
        messagebox.showerror("Error", "No image to save")

def update_bg_options():
    if bg_type.get() == "image":
        bg_image_button.config(state=tk.NORMAL)
        bg_color_button.config(state=tk.DISABLED)
    else:
        bg_image_button.config(state=tk.DISABLED)
        bg_color_button.config(state=tk.NORMAL)

root = tk.Tk()
root.title("Background Switcher")

bg_type = tk.StringVar(value="color")  # Variable to store the selected background type

open_button = tk.Button(root, text="Choose foreground image", command=open_main_image)
open_button.pack()

bg_type_frame = tk.Frame(root)
bg_type_frame.pack()

bg_type_label = tk.Label(bg_type_frame, text="Background Type:")
bg_type_label.pack(side=tk.LEFT)

bg_color_radio = tk.Radiobutton(bg_type_frame, text="Color", variable=bg_type, value="color", command=update_bg_options)
bg_color_radio.pack(side=tk.LEFT)

bg_image_radio = tk.Radiobutton(bg_type_frame, text="Image", variable=bg_type, value="image", command=update_bg_options)
bg_image_radio.pack(side=tk.LEFT)

bg_image_button = tk.Button(root, text="Choose background image", command=open_bg_image, state=tk.DISABLED)
bg_image_button.pack()

bg_color_button = tk.Button(root, text="Choose background color", command=choose_bg_color, state=tk.DISABLED)
bg_color_button.pack()

threshold_slider = tk.Scale(root, from_=0, to=255, orient="horizontal", label="Threshold", command=update_threshold)
threshold_slider.set(threshold_value)
threshold_slider.pack()

canvas = tk.Canvas(root, width=600, height=400, bg="grey")
canvas.pack()

save_button = tk.Button(root, text="Save Image", command=save_image, state=tk.DISABLED)
save_button.pack(pady=10)

update_bg_options()  # Initialize the state of the buttons

root.mainloop()