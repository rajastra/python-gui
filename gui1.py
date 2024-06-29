from pathlib import Path
import shutil
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, filedialog, messagebox,Label,END
import os
import sys
import subprocess
import zipfile
import numpy as np
from PIL import Image,ImageTk
import matplotlib.pyplot as plt
from model import *
import wave
import time

# Define constants for paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets/frame1"
PATH_DATA = []


def upload_audio():
    def path_file(path):
        path_label.config(text=path)
        path_label.lift()

    # Meminta user memilih file audio
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
    
    if file_path:
        # Tentukan folder tujuan
        destination_folder = os.path.join("data", "music_folder")
        
        # Buat folder jika belum ada
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        # Tentukan path tujuan dengan nama file
        destination = os.path.join(destination_folder, os.path.basename(file_path))
        
        # Salin file ke folder tujuan
        if file_path != destination:
            shutil.copy(file_path, destination)
        
        # Perbarui label dengan path file
        path_file(destination)
        
        # Tambahkan path ke daftar PATH_DATA
        PATH_DATA.append(destination)
        
        return destination
    else:
        return None

def upload_zip():
    def update_zip_path(path):
        entry_image_4.config(text="Path file ZIP: " + path)
        entry_image_4.lift()
    file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
    if file_path:
        destination_folder = os.path.join("data", "music_folder")
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        destination = os.path.join(destination_folder, os.path.basename(file_path))
        if file_path != destination:
            shutil.copy(file_path, destination)
        update_zip_path(destination)
        try:
            extract_to_path = os.path.join("data", "extracted_files")
            os.makedirs(extract_to_path, exist_ok=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                for file in file_list:
                    if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.txt')):
                        zip_ref.extract(file, extract_to_path)
                        PATH_DATA.append(os.path.join(extract_to_path, file))
            return extract_to_path
        except zipfile.BadZipFile:
            messagebox.showerror("Error", "File ZIP rusak dan tidak dapat diekstraksi")
            return None
    else:
        return None
def process_files():
    if not PATH_DATA:
        messagebox.showerror("Error", "Tidak ada file yang diupload.")
        return
    
    output_folder = os.path.join("data", "embedded_files")
    os.makedirs(output_folder, exist_ok=True)
    output_image_plot = os.path.join("data", "image_plot")
    os.makedirs(output_image_plot, exist_ok=True)

    # Initialize variables
    audio_data = None
    image_array = None
    text = ""

    # Process audio files
    audio_files = [os.path.join("data", "music_folder", audio_file) for audio_file in os.listdir("data/music_folder") if audio_file.endswith((".wav", ".mp3"))]
    for audio_file in audio_files:
        with wave.open(audio_file, "rb") as audio_file:
            params = audio_file.getparams()
            sampling_rate = audio_file.getframerate()
            n_frames = audio_file.getnframes()
            sample_width = audio_file.getsampwidth()
            audio_params = audio_file.getparams()
            frames = audio_file.readframes(-1)
            audio_data = np.frombuffer(frames, dtype=np.int16).copy()

    # Process image files
    image_files = [os.path.join("data", "extracted_files", image_file) for image_file in os.listdir("data/extracted_files") if image_file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    for image_file in image_files:
        image_array = np.array(Image.open(image_file).resize((100,100)))
    print(image_array.shape)
    if len(image_array.shape) == 2:
        # Grayscale image
        image_shape = image_array.shape
    elif len(image_array.shape) == 3:
        # Color image (RGB or RGBA)
        image_shape = image_array.shape

    # Process text files
    txt_files = [os.path.join("data", "extracted_files", txt_file) for txt_file in os.listdir("data/extracted_files") if txt_file.endswith((".txt"))]
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            text += file.read()

    # Embedding and calculations
    if audio_data is not None and image_array is not None:
        start_time = time.time()
        combined_image_audio = embed_image_into_audio(audio_data, image_array)
        combined_all = embed_text_into_audio(combined_image_audio, text)
        ber = calculate_ber(audio_data, combined_all)
        snr = calculate_snr(image_array, audio_data - combined_all)
        save_audio_path = os.path.join(output_folder, "embedded_audio.wav")
        # saved_audio_path = load_model(audio_data, sampling_rate, sample_width, save_audio_path)
        with wave.open(save_audio_path, 'wb') as output_file:
            output_file.setparams(audio_params)
            output_file.writeframes(combined_image_audio)
        # Update GUI elements
        entry_BER.delete(0, END)
        entry_BER.insert(0, f"{ber:.4f}")
        entry_SNR.delete(0, END)
        entry_SNR.insert(0, f"{snr:.4f} dB")

        # Plot and display audio waveform
        plt.figure(figsize=(6, 6))
        plt.plot(np.linspace(0, len(combined_all) / sampling_rate, num=len(combined_all)),
                 combined_all, color='red')
        plt.title("Modified Audio Waveform with Watermark")
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.grid(True)
        audio_plot_path = os.path.join(output_folder, "plot_audio.png")
        plt.savefig(audio_plot_path)
        plt.close()

        # make file embeded text
        with open(os.path.join(output_folder, "embeded_text.txt"), 'w') as file:
            file.write(text)
            
        # Display plot in Tkinter GUI
        audio_plot = Image.open(audio_plot_path)
        audio_plot_resize = audio_plot.resize((273, 84))
        plot_image = ImageTk.PhotoImage(audio_plot_resize)
        plot_label.config(image=plot_image)
        plot_label.image = plot_image
        plot_label.lift()
        
        plt.figure(figsize=(6, 6))
        plt.imshow(image_array, cmap="gray")
        plt.title('Extracted Image from Audio')
        plt.axis('off')
        plt.tight_layout()
        image_watermark_path = os.path.join(output_folder, "image_watermark.png")
        plt.savefig(image_watermark_path)
        plt.close()
        
        image_watermark = Image.open(image_watermark_path)
        image_resized = image_watermark.resize((273, 71))
        plot_watermark = ImageTk.PhotoImage(image_resized)
        plot_watermark_label.config(image=plot_watermark)
        plot_watermark_label.image = plot_watermark
        plot_watermark_label.lift()
        
        entry_time.delete(0, END)
        entry_time.insert(0, f"{(time.time() - start_time):.4f}")
    else:
        messagebox.showerror("Error", "Gagal memproses file. Pastikan ada file audio dan gambar yang valid.")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def start_dashboard():
    script_path = os.path.abspath("gui.py")
    subprocess.Popen([sys.executable, script_path])
    window.destroy()

window = Tk()
window.geometry("745x504")
window.configure(bg="#FFFFFF")
window.resizable(False, False)

canvas = Canvas(window, bg="#FFFFFF", height=504, width=745, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(372.0, 252.0, image=image_image_1)

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
canvas.create_image(372.0, 301.0, image=image_image_2)

canvas.create_text(286.0, 119.0, anchor="nw", text="Embedding", fill="#F62602", font=("Inter Medium", 32))

plot_label = Label(window)
plot_label.place(x=416.0, y=209.0, width=273.0, height=84.0)
entry_1 = Entry(bd=0, bg="#E8E4CB", fg="#000716", highlightthickness=0)
entry_1.place(x=416.0, y=209.0, width=273.0, height=84.0)

plot_watermark_label = Label(window)
plot_watermark_label.place(x=416.0, y=336.0, width=273.0, height=71.0)
entry_2 = Entry(bd=0, bg="#E8E4CB", fg="#000716", highlightthickness=0)
entry_2.place(x=416.0, y=336.0, width=273.0, height=71.0)


button_img_upload_audio = PhotoImage(file=relative_to_assets("image_3.png"))
button_upload_audio = Button(image=button_img_upload_audio, borderwidth=0, highlightthickness=0, command=upload_audio, relief="flat")
button_upload_audio.place(x=258.9, y=199.8)
path_label = Label(window, text="", bg="#E8E4CB",width=30, height=3)
path_label.place(x=45, y=196)


# section file for embeded
entry_image_4 = Label(window,bg="#E8E4CB",width=30,height=3)
entry_image_4.place(x=45,y=252)

button_upload_img_txt = PhotoImage(file=relative_to_assets("image_4.png"))
button_upload_zip = Button(window, image=button_upload_img_txt, borderwidth=0, highlightthickness=0, command=upload_zip, relief="flat")
button_upload_zip.place(x=258.9, y=260.0)

## point SNR label
entry_SNR = Entry(bd=0, bg="#E8E4CB", fg="#000716", highlightthickness=0)
entry_SNR.place(x=98.0, y=383.0, width=225.0, height=30.0)

## BER
entry_BER = Entry(bd=0, bg="#E8E4CB", fg="#000716", highlightthickness=0)
entry_BER.place(x=98.0, y=428.0, width=225.0, height=30.0)

## time excutable

# entry_image_7 = PhotoImage(file=relative_to_assets("entry_7.png"))
# canvas.create_image(576.5, 444.0, image=entry_image_7)
entry_time = Entry(bd=0, bg="#E8E4CB", fg="#000716", highlightthickness=0)
entry_time.place(x=464.0, y=428.0, width=225.0, height=30.0)
time_label= Label(window)
canvas.create_text(476.0, 310.0, anchor="nw", text="WATERMARK INPUT", fill="#000000", font=("Inter", 16))
canvas.create_text(501.0, 184.0, anchor="nw", text="AUDIO INPUT", fill="#000000", font=("Inter", 16))

canvas.create_text(51.0, 390.0, anchor="nw", text="SNR :", fill="#000000", font=("Inter", 15))
canvas.create_text(51.0, 435.0, anchor="nw", text="BER :", fill="#000000", font=("Inter", 15))
canvas.create_text(411.0, 435.0, anchor="nw", text="TIME :", fill="#000000", font=("Inter", 15))

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=process_files, relief="flat")
button_1.pack()
button_1.place(x=230.0, y=311.0, width=95.0, height=31.0)

image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
button_back = Button(image=image_image_5, borderwidth=0, highlightthickness=0, command=start_dashboard, relief="flat")
button_back.place(x=45.0, y=140.0)

image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
canvas.create_image(372.0, 20.0, image=image_image_6)

window.mainloop()
