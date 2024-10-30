# Background Switcher

## Overview

Background Switcher is a Python application that allows users to change the background of a selected foreground image. Users can choose between a solid color or another image as the background. The application uses OpenCV for image processing and Tkinter for the graphical user interface.

## Features

- Load a foreground image.
- Choose a background type: color or image.
- Select a background color using a color chooser.
- Select a background image from the file system.
- Adjust the threshold for background application.
- Save the resulting image.

## Requirements

- Python 3.x
- OpenCV
- Pillow (PIL)
- Tkinter (usually included with Python)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/background-switcher.git
    cd background-switcher
    ```

2. Install the required packages:
    ```sh
    pip install opencv-python pillow
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. Use the GUI to:
    - Load a foreground image by clicking "Choose foreground image".
    - Select the background type (Color or Image).
    - If "Color" is selected, choose a background color.
    - If "Image" is selected, choose a background image.
    - Adjust the threshold using the slider.
    - Apply the background by clicking "Apply background".
    - Save the resulting image by clicking "Save Image".

### Screenshots

#### Background Image applied
![Background Image](assets/cat-show.png)

#### Background Color applied
![Background Color](assets/pink-cats.png)

### Screencast

![Screen recording](assets/screencast.gif)

## Code Structure

- `main.py`: The main script containing the application logic and GUI.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [OpenCV](https://opencv.org/)
- [Pillow](https://python-pillow.org/)
- [Tkinter](https://wiki.python.org/moin/TkInter)
- 