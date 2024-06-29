from pathlib import Path
import shutil
from tkinter import (Label, Tk, Canvas, Entry, Text,END ,
                     Button, PhotoImage, filedialog, messagebox)
import os,sys
import subprocess
from functools import partial
import wave
from PIL import Image,ImageTk
import time
from matplotlib import pyplot as plt
import numpy as np

from model import *
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets/frame2"
UPLOAD_FOLDER = "data_extracted"
PATH_DATA = []


def on_entry_click(entry, event):
    if entry.get() == 'Input audio watermarked':
        entry.delete(0, "end")  
        entry.insert(0, '')  
        entry.config(fg='black')


def on_focusout(entry, event):
    if entry.get() == '':
        entry.insert(0, 'Input audio watermarked')
        entry.config(fg='grey')

def extract_text_from_audio(audio_data: np.ndarray, text_length: int):
    extracted_bits = []
    for i in range(text_length * 8):
        audio_sample = audio_data[i]
        extracted_bits.append(audio_sample & 1)
    
    binary_string = "".join(str(bit) for bit in extracted_bits)
    text = "".join(chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))
    return text
def extract_image_from_audio(audio_data: np.ndarray,image_shape:tuple):
    total_pixels = np.prod(image_shape)
    total_bits = total_pixels * 8
    
    extracted_bits = []
    for i in range(total_bits):
        audio_sample = audio_data[i]
        extracted_bits.append(audio_sample & 1)
    
    extracted_pixels = np.packbits(np.array(extracted_bits, dtype=np.uint8))
    image_data = extracted_pixels[:total_pixels].reshape(image_shape)
    
    return image_data

def upload_audio():
    def path_file(path):
        audio_path_label.config(text=path)
        audio_path_label.lift()
    # Meminta user memilih file audio
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
    
    if file_path:
        # Tentukan folder tujuan
        destination_folder = os.path.join(UPLOAD_FOLDER, "music_folder")
        
        # Buat folder jika belum ada
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        # Tentukan path tujuan dengan nama file
        destination = os.path.join(destination_folder, os.path.basename(file_path))
        
        # Salin file ke folder tujuan
        if file_path != destination:
            shutil.copy(file_path, destination)
        
        # Perbarui entry dengan path file
        path_file(destination)
        
        # Tambahkan path ke daftar PATH_DATA
        PATH_DATA.append(destination)
        
        return destination
    else:
        return None

def process_files():
    global PATH_DATA
    
    if not PATH_DATA:
        messagebox.showerror("Error", "Tidak ada file yang diupload.")
        return

    # Create output folders if they don't exist
    output_folder = os.path.join(UPLOAD_FOLDER, "extracted_output")
    output_image_plot = os.path.join(UPLOAD_FOLDER, "image_plot")
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_image_plot, exist_ok=True)
    
    # Assuming only one file is uploaded, take the first one
    audio_file_path = PATH_DATA[0]
    
    # Read audio file and extract relevant parameters
    start_time = time.time()
    with wave.open(audio_file_path, 'rb') as audio_file:
        n_channels = audio_file.getnchannels()
        sample_width = audio_file.getsampwidth()
        frame_rate = audio_file.getframerate()
        n_frames = audio_file.getnframes()
        sampling_rate = audio_file.getframerate()
        frames = audio_file.readframes(-1)
        audio_data = np.frombuffer(frames,dtype=np.int16).copy()
    plt.figure(figsize=(6,6))
    plt.plot(np.linspace(0, len(audio_data) / sampling_rate, num=len(audio_data)),
                 audio_data, color='blue')
    plt.title("Audio Extracted")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitudo")
    plt.grid(True)
    audio_plot_path = os.path.join(output_folder,"plot_audio.png")
    plt.savefig(audio_plot_path)
    plt.close()
    audio_plot = Image.open(audio_plot_path)
    audio_plot_resize = audio_plot.resize((273,84))
    plot_image = ImageTk.PhotoImage(audio_plot_resize)
    label_audio_plot.config(image=plot_image)
    label_audio_plot.image = plot_image
    label_audio_plot.lift()
    
    # for image extracted
    image_save_path = os.path.join(output_folder,"image_extrated.png")
    image_data = extract_image_from_audio(audio_data,(100,100))
    plt.figure(figsize=(6,6))
    plt.imshow(image_data,cmap="gray")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(image_save_path)
    plt.close()
    image_watermark = Image.open(image_save_path)
    image_resize = image_watermark.resize((273,71))
    watermark = ImageTk.PhotoImage(image_resize)
    watermark_label.config(image=watermark)
    watermark_label.image = watermark
    watermark_label.lift()
    # Assuming ber and snr are calculated here
    ber = calculate_ber(
        audio_data,
        extract_image_from_audio(audio_data, (100, 100)).flatten()
    )
    snr = calculate_snr(
        audio_data,
        extract_image_from_audio(audio_data, (100, 100)).flatten()
    )
    
    # Update BER and SNR entries
    entry_ber.delete(0, END)
    entry_ber.insert(0, f"{ber:.4f}  dB")
    entry_5.delete(0, END)
    entry_5.insert(0, f"{snr:.4f}")
    entry_time.delete(0, END)
    entry_time.insert(0, f"{(time.time() - start_time):.4f}")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def start_dashboard():
    script_path = os.path.abspath("gui.py")
    subprocess.Popen([sys.executable, script_path])
    window.destroy()

window = Tk()

window.geometry("745x504")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 504,
    width = 745,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    372.0,
    252.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    372.0,
    301.0,
    image=image_image_2
)

canvas.create_text(
    294.0,
    120.0,
    anchor="nw",
    text="Extracting",
    fill="#F62602",
    font=("Inter Medium", 32 * -1)
)

label_audio_plot = Label(window)
label_audio_plot.place(x=416.0,
    y=209.0,
    width=273.0,
    height=84.0)

entry_1 = Entry(
    bd=0,
    bg="#E8E4CB",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=416.0,
    y=209.0,
    width=273.0,
    height=84.0
)



watermark_label = Label(window)
watermark_label.place(x=416.0,
    y=336.0,
    width=273.0,
    height=73.0)
entry_2 = Entry(
    bd=0,
    bg="#E8E4CB",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=416.0,
    y=336.0,
    width=273.0,
    height=73.0
)

audio_path_label = Label(window)
audio_path_label.place(x=45.0, y=196.0, width=278.0, height=41.0)
entry_3 = Entry(window, bd=0, bg="#E8E4CB",fg="#000716", highlightthickness=0)
entry_3.place(x=45.0, y=196.0, width=278.0, height=41.0)
entry_3.insert(0, 'Input audio watermarked')


# entry
entry_ber = Entry(
    bd=0,
    bg="#E8E4CB",
    fg="#000716",
    highlightthickness=0
)
entry_ber.place(
    x=98.0,
    y=349.0,
    width=225.0,
    height=30.0
)


entry_image_5 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(
    210.5,
    410.0,
    image=entry_image_5
)
entry_5 = Entry(
    bd=0,
    bg="#E8E4CB",
    fg="#000716",
    highlightthickness=0
)
entry_5.place(
    x=98.0,
    y=394.0,
    width=225.0,
    height=30.0
)

entry_image_6 = PhotoImage(
    file=relative_to_assets("entry_6.png"))
entry_bg_6 = canvas.create_image(
    576.5,
    444.0,
    image=entry_image_6
)
entry_time = Entry(
    bd=0,
    bg="#E8E4CB",
    fg="#000716",
    highlightthickness=0
)
entry_time.place(
    x=464.0,
    y=428.0,
    width=225.0,
    height=30.0
)

# canvas.create_text(
#     59.0,
#     209.0,
#     anchor="nw",
#     text="Input audio watermarked",
#     fill="#F62602",
#     font=("Inter", 12 * -1)
# )

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=process_files,
    relief="flat"
)
button_1.place(
    x=230.0,
    y=272.0,
    width=95.0,
    height=31.0
)

canvas.create_text(
    467.0,
    312.0,
    anchor="nw",
    text="WATERMARK OUTPUT",
    fill="#000000",
    font=("Inter", 16 * -1)
)

canvas.create_text(
    501.0,
    184.0,
    anchor="nw",
    text="AUDIO INPUT",
    fill="#000000",
    font=("Inter", 16 * -1)
)

canvas.create_text(
    51.0,
    356.0,
    anchor="nw",
    text="SNR :",
    fill="#000000",
    font=("Inter", 15 * -1)
)

canvas.create_text(
    51.0,
    401.0,
    anchor="nw",
    text="BER :",
    fill="#000000",
    font=("Inter", 15 * -1)
)

canvas.create_text(
    411.0,
    435.0,
    anchor="nw",
    text="TIME :",
    fill="#000000",
    font=("Inter", 15 * -1)
)

imageButton = PhotoImage(
    file=relative_to_assets("image_3.png"))
buttonUpload=Button(image=imageButton, borderwidth=0, highlightthickness=0, command=upload_audio, relief="flat")
buttonUpload.place(x=262.9, y=196)

image_back_button = PhotoImage(file=relative_to_assets("image_4.png"))
button_back = Button(image=image_back_button, borderwidth=0, highlightthickness=0, command=start_dashboard, relief="flat")
button_back.place(x=31, y=126.0)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    372.0,
    20.0,
    image=image_image_5
)
window.resizable(False, False)
window.mainloop()
