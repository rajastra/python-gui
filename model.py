import wave
import numpy as np
from PIL import Image
import pickle

def embed_text_into_audio(audio_data: np.ndarray, text: str):
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    
    for i, bit in enumerate(binary_text):
        audio_data[i] &= ~1
        audio_data[i] |= int(bit)
    
    return audio_data

def extract_text_from_audio(audio_data: np.ndarray, text_length: int):
    extracted_bits = []
    for i in range(text_length * 8):
        audio_sample = audio_data[i]
        extracted_bits.append(audio_sample & 1)
    
    binary_string = "".join(str(bit) for bit in extracted_bits)
    text = "".join(chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))
    return text

def embed_image_into_audio(audio_data: np.ndarray, image_data: np.ndarray):
    audio_data = audio_data.astype(np.int16)
    image_data = image_data.flatten()
    
    total_bits = image_data.size * 8
    if total_bits > len(audio_data):
        raise ValueError("Audio data is too short to hold the image data.")
    
    bits = np.unpackbits(image_data)
    for i, bit in enumerate(bits):
        audio_data[i] &= ~1
        audio_data[i] |= bit
        
    return audio_data

def extract_image_from_audio(audio_data: np.ndarray, image_shape: tuple):
    if (image_shape[0]==100) and (image_shape[1]==100):
        raise ValueError("size must be 100x100")
    total_pixels = np.prod(image_shape)
    total_bits = total_pixels * 8
    
    extracted_bits = []
    for i in range(total_bits):
        audio_sample = audio_data[i]
        extracted_bits.append(audio_sample & 1)
    
    extracted_pixels = np.packbits(np.array(extracted_bits, dtype=np.uint8))
    image_data = extracted_pixels[:total_pixels].reshape(image_shape)
    
    return image_data


def save_audio(audio_data: np.ndarray, sampling_rate: int, sample_width: int, output_path: str):
    with wave.open(output_path, 'wb') as output_file:
            # Set parameters for the output file
        output_file.setnchannels(1)  # Mono channel, adjust as needed
        output_file.setsampwidth(sample_width)
        output_file.setframerate(sampling_rate)
        output_file.writeframes(audio_data.tobytes())
    return output_file

# Save model to pickle
def save_model(filename='steganography_model.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((embed_text_into_audio, extract_text_from_audio, embed_image_into_audio, extract_image_from_audio), f)

# Load model from pickle
def load_model(filename='steganography_model.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
def calculate_ber(original_audio, modified_audio):
    original_audio = np.array(original_audio)
    modified_audio = np.array(modified_audio)
    
    # Ensure the arrays have the same length
    min_len = min(len(original_audio), len(modified_audio))
    original_audio = original_audio[:min_len]
    modified_audio = modified_audio[:min_len]

    # Handle case where arrays might be empty
    if len(original_audio) == 0:
        return float('inf')  # Return infinity if no data to compare
    
    # Calculate Bit Error Rate (BER)
    ber = np.sum(original_audio != modified_audio) / len(original_audio)
    return ber

def calculate_snr(original_signal, extracted_signal):
    original_signal = np.array(original_signal)
    extracted_signal = np.array(extracted_signal)
    
    # Flatten the signals if they're not already 1D
    original_signal = original_signal.flatten()
    extracted_signal = extracted_signal.flatten()
    
    # Ensure the signals have the same length
    min_len = min(len(original_signal), len(extracted_signal))
    original_signal = original_signal[:min_len]
    extracted_signal = extracted_signal[:min_len]

    # Handle case where signals might be empty
    if min_len == 0:
        return float('inf')  # Return infinity if no data to compare
    
    # Calculate the noise (difference between the original and extracted signals)
    noise = original_signal - extracted_signal
    
    # Calculate signal power and noise power
    signal_power = np.sum(original_signal ** 2)
    noise_power = np.sum(noise ** 2)

    # Check for valid signal and noise power to avoid invalid log10 argument
    if noise_power <= 0:
        return float('inf')  # Infinite SNR if there is no noise
    if signal_power <= 0:
        return float('-inf')  # Negative infinite SNR if there is no signal

    # Calculate SNR in dB
    snr = 10 * np.log10(signal_power / noise_power)
    return snr


if __name__ == "__main__":
    save_model()
