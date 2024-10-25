import os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk

# Global variables to keep track of the text position and offset
text_x, text_y = 50, 50
offset_x, offset_y = 0, 0
canvas_text = None

# Function to open an image and set it as background on the canvas
def open_image():
    global img, img_tk, canvas_image, canvas_text
    home_dir = os.path.expanduser("~")
    file_path = filedialog.askopenfilename(initialdir=home_dir, filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    img = Image.open(file_path)
    img_tk = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas_image = canvas.create_image(0, 0, anchor='nw', image=img_tk)

    # Create the text item to ensure it is on top
    if canvas_text is None:
        canvas_text = canvas.create_text(text_x, text_y, text="Sample Text", anchor="nw", font=('Helvetica', 20, 'bold'))
        canvas.tag_bind(canvas_text, "<Button-1>", start_drag)
        canvas.tag_bind(canvas_text, "<B1-Motion>", drag_text)
        canvas.tag_bind(canvas_text, "<Enter>", lambda _: canvas.config(cursor="fleur"))
        canvas.tag_bind(canvas_text, "<Leave>", lambda _: canvas.config(cursor=""))
    update_text()

# Function to handle text dragging
def start_drag(event):
    global text_x, text_y, offset_x, offset_y
    offset_x = event.x - text_x
    offset_y = event.y - text_y

def drag_text(event):
    global text_x, text_y
    new_x = event.x - offset_x
    new_y = event.y - offset_y
    canvas.coords(canvas_text, new_x, new_y)
    text_x, text_y = new_x, new_y

# Function to choose the text color
def choose_color():
    color_code = colorchooser.askcolor()[1]
    if color_code:
        canvas.itemconfig(canvas_text, fill=color_code)

# Function to update text attributes (font size)
def update_text(event=None):
    global canvas_text
    if canvas_text is not None:
        font_size = int(font_size_slider.get())
        font = ('Helvetica', font_size, 'bold')

        # Get the text from the text area
        text_content = text_area.get("1.0", "end-1c")
        canvas.itemconfig(canvas_text, text=text_content, font=font)

# Function to save the final image using OpenCV
def save_image():
    global img
    if img is None:
        messagebox.showerror("Error", "No image to save.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
    if not save_path:
        return

    # Convert canvas text to OpenCV (numpy array) format
    np_image = np.array(img.convert('RGB'))

    # Calculate scaling factor
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    img_width, img_height = img.size
    scale_x = img_width / canvas_width
    scale_y = img_height / canvas_height

    # Create drawing context with OpenCV
    text = text_area.get("1.0", "end-1c")
    font_size = int(font_size_slider.get())
    thickness = int(thickness_slider.get())
    color = canvas.itemcget(canvas_text, "fill")
    color_bgr = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))  # Convert hex color to BGR

    # Use OpenCV to put text on image
    font_path = cv2.FONT_HERSHEY_SIMPLEX  # Using OpenCV's default font
    (text_w, text_h), _ = cv2.getTextSize(text, font_path, font_size / 30, thickness)

    # Position text relative to canvas coordinates
    text_position = (int(text_x * scale_x), int((text_y + text_h) * scale_y))

    cv2.putText(np_image, text, text_position, font_path, (font_size / 30) * scale_y, color_bgr, int(thickness * scale_y))

    # Save the image
    cv2.imwrite(save_path, cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR))
    messagebox.showinfo("Success", "Image saved successfully!")

if __name__ == "__main__":
    # Tkinter setup
    root = tk.Tk()
    root.title("Image Editor with Text Overlay")

    # Main frame to hold canvas and control panel
    main_frame = tk.Frame(root)
    main_frame.pack()

    # Canvas to display the image and text
    canvas = tk.Canvas(main_frame, width=600, height=400, bg="white")
    canvas.pack(side="left")

    # Control panel frame
    control_panel = tk.Frame(main_frame)
    control_panel.pack(side="left", padx=10)

    # Image selection button
    open_button = tk.Button(control_panel, text="Open Image", command=open_image)
    open_button.pack()

    # Text area for entering multiple lines of text
    text_area = tk.Text(control_panel, height=4, width=50)
    text_area.pack(pady=10)
    text_area.insert("1.0", "Sample Text")  # Default text
    text_area.bind("<KeyRelease>", update_text)

    # Font size slider
    font_size_slider = tk.Scale(control_panel, from_=10, to=100, orient='horizontal', label="Font Size",
                                command=lambda _: update_text())
    font_size_slider.pack()

    # Font thickness slider
    thickness_slider = tk.Scale(control_panel, from_=1, to=10, orient='horizontal', label="Thickness")
    thickness_slider.pack()

    # Color picker button
    color_button = tk.Button(control_panel, text="Choose Text Color", command=choose_color)
    color_button.pack(pady=10)

    # Save image button
    save_button = tk.Button(control_panel, text="Save Image", command=save_image)
    save_button.pack(pady=10)

    root.mainloop()