import numpy as np
import soundfile as sf
import win32file
import win32con
import pywintypes
import time
import librosa
import os

# ===== DRIVER CONFIG =====
DEVICE_NAME = r"\\.\VirtualAudio"
FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_WRITE_DATA = 0x00000002
IOCTL_INDEX = 0x800


def ctl_code(device_type, function, method, access):
    return ((device_type << 16) | (access << 14) | (function << 2) | method)

IOCTL_VIRTUALAUDIO_WRITE = ctl_code(FILE_DEVICE_UNKNOWN, IOCTL_INDEX, METHOD_BUFFERED, FILE_WRITE_DATA)

CHUNK_SIZE = 4096  # bytes per chunk
DESIRED_SAMPLE_RATE = 48000
DESIRED_CHANNELS = 2
DESIRED_BIT_DEPTH = 32  # int32 → 4 bytes

def open_driver():
    try:
        handle = win32file.CreateFile(
            DEVICE_NAME,
            win32con.GENERIC_WRITE,
            0,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )
        print("[✓] Opened virtual driver.")
        return handle
    except Exception as e:
        print(f"[!] Failed to open driver: {e}")
        return None

def send_wav_to_virtual_driver(wav_path):
    if not os.path.exists(wav_path):
        print(f"[!] File not found: {wav_path}")
        return

    try:
        data, samplerate = sf.read(wav_path, always_2d=True)
        num_channels = data.shape[1]
        print(f"[i] Loaded WAV: {samplerate}Hz, {num_channels}ch, {len(data)} frames")

        # Expand mono → stereo if needed
        if num_channels == 1 and DESIRED_CHANNELS == 2:
            data = np.repeat(data, 2, axis=1)
            print("[i] Expanded mono to stereo")
        elif num_channels != DESIRED_CHANNELS:
            print(f"[!] Channel mismatch: WAV has {num_channels}ch, expected {DESIRED_CHANNELS}ch")
            return

        # Resample if needed
        if samplerate != DESIRED_SAMPLE_RATE:
            print(f"[i] Resampling {samplerate} → {DESIRED_SAMPLE_RATE}")
            data = librosa.resample(data.T, orig_sr=samplerate, target_sr=DESIRED_SAMPLE_RATE).T
            samplerate = DESIRED_SAMPLE_RATE

        # Normalize and convert to int32
        data = np.clip(data, -1.0, 1.0)
        data_int32 = (data * 2147483647).astype(np.int32)
        raw_bytes = data_int32.flatten().tobytes()

        handle = open_driver()
        if not handle:
            return

        bytes_per_frame = DESIRED_CHANNELS * 4
        frames_per_chunk = CHUNK_SIZE // bytes_per_frame
        total_bytes = len(raw_bytes)

        print(f"[i] Sending {total_bytes} bytes...")
        offset = 0
        chunk_index = 0
        start_time = time.time()

        while offset < total_bytes:
            chunk = raw_bytes[offset:offset + CHUNK_SIZE]
            expected_time = start_time + (chunk_index * frames_per_chunk / samplerate)

            try:
                win32file.DeviceIoControl(handle, IOCTL_VIRTUALAUDIO_WRITE, chunk, None)
            except pywintypes.error as e:
                if e.winerror == 234:  # ERROR_MORE_DATA
                    continue
                else:
                    print(f"[!] IOCTL error: {e}")
                    break

            offset += len(chunk)
            chunk_index += 1

            # Keep real-time playback
            now = time.time()
            sleep_time = expected_time - now
            if sleep_time > 0:
                time.sleep(sleep_time)

        handle.close()
        end_time = time.time()
        print(f"[✓] Done. Duration: {len(data)/samplerate:.2f}s, Real time: {end_time - start_time:.2f}s")

    except Exception as e:
        print(f"[!] Error: {e}")

# ===== RUN EXAMPLE =====
if __name__ == "__main__":
    send_wav_to_virtual_driver("sample_2.wav")
