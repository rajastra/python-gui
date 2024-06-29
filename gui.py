from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import subprocess
import os
import sys

# Define constants for paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets/frame0"

def start_embedded_gui():
    """Launch the embedded GUI application."""
    script_path = os.path.abspath("gui1.py")
    subprocess.Popen([sys.executable, script_path])
    window.destroy()
    
def start_extract_gui():
    """Lauch the extract GUI application"""
    script_path= os.path.abspath("gui2.py")
    subprocess.Popen([sys.executable,script_path])
    window.destroy()

def relative_to_assets(path: str) -> Path:
    """Get the absolute path to the asset."""
    return ASSETS_PATH / Path(path)

# Initialize the main window
window = Tk()
window.geometry("745x504")
window.configure(bg="#FFFFFF")
window.resizable(False, False)

# Create a canvas widget
canvas = Canvas(window, bg="#FFFFFF", height=504, width=745, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Load and place images and text
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(199.0, 252.0, image=image_image_1)

canvas.create_text(449.0, 161.0, anchor="nw", text="Audio Watermarking", fill="#F62602", font=("Inter Medium", 24))
canvas.create_text(449.0, 96.0, anchor="nw", text="Welcome !", fill="#F62602", font=("Inter", 20))
canvas.create_text(419.0, 451.0, anchor="nw", text="watermark your audio for identity", fill="#F62602", font=("Inter Italic", 13))

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
canvas.create_image(372.0, 20.0, image=image_image_2)

# Load and place buttons
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=start_embedded_gui, relief="flat")
button_1.place(x=473.0, y=232.0, width=186.4, height=55.4)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=start_extract_gui, relief="flat")
button_2.place(x=473.0, y=308.0, width=186.4, height=55.4)

# Run the application
window.mainloop()
