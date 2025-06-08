import pyaudio
import win32file
import win32con
import pywintypes
import numpy as np

# ===== DRIVER CONFIG =====
DEVICE_NAME = r"\\.\HackAI_AudioCtrl"
FILE_DEVICE_UNKNOWN = 0x00000022
IOCTL_INDEX = 0x800
METHOD_BUFFERED = 0
FILE_WRITE_DATA = 0x00000002

IOCTL_WRITE_AUDIO = (
    (FILE_DEVICE_UNKNOWN << 16) |
    (FILE_WRITE_DATA << 14) |
    (IOCTL_INDEX << 2) |
    METHOD_BUFFERED
)

CHUNK = 1024
DESIRED_CHANNELS = 2  # Virtual mic expects stereo
RATE = 48000
FORMAT = pyaudio.paFloat32  # Mic input in float32 for easy scaling

TARGET_MIC_NAME = "Scarlett"  # Partial match for your Scarlett 2i2

# ===== FIND SCARLETT DEVICE =====
def find_input_device(p, target_name):
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"[i] Device {i}: {info['name']} - {info['maxInputChannels']} ch")
        if target_name.lower() in info['name'].lower() and info['maxInputChannels'] > 0:
            print(f"[✓] Found input device: {info['name']} (index: {i})")
            return i, info['maxInputChannels']
    print("[!] Microphone not found.")
    return None, None

# ===== OPEN VIRTUAL DRIVER =====
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

# ===== MAIN STREAMING FUNCTION =====
def stream_from_mic_to_virtual():
    p = pyaudio.PyAudio()
    mic_index, mic_channels = find_input_device(p, TARGET_MIC_NAME)
    if mic_index is None:
        return

    # Open stream from Scarlett
    stream = p.open(
        format=FORMAT,
        channels=mic_channels,
        rate=RATE,
        input=True,
        input_device_index=mic_index,
        frames_per_buffer=CHUNK
    )

    driver = open_driver()
    if not driver:
        return

    print(f"[i] Streaming: Scarlett Mic ({mic_channels}ch) ➜ Virtual Mic ({DESIRED_CHANNELS}ch)")

    try:
        while True:
            # Read from mic
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.float32)

            # Convert mono ➜ stereo interleaved (L, R, L, R, ...)
            if mic_channels == 1 and DESIRED_CHANNELS == 2:
                audio = np.repeat(audio, 2)

            # If already stereo, assume interleaved OK

            # Convert float32 ➜ int32
            audio_int32 = (np.clip(audio, -1.0, 1.0) * 2147483647).astype(np.int32)
            raw_bytes = audio_int32.tobytes()

            # Send to virtual driver
            try:
                win32file.DeviceIoControl(driver, IOCTL_WRITE_AUDIO, raw_bytes, None)
            except pywintypes.error as e:
                if e.winerror == 234:  # ERROR_MORE_DATA
                    continue
                else:
                    print(f"[!] IOCTL error: {e}")
                    break

    except KeyboardInterrupt:
        print("[i] Stopped by user.")
    finally:
        stream.stop_stream()
        stream.close()
        driver.close()
        p.terminate()

# ===== RUN =====
if __name__ == "__main__":
    stream_from_mic_to_virtual()
