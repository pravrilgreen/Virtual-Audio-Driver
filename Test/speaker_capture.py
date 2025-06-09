import ctypes
import numpy as np
import time
import wave
import os

# Cấu hình thiết bị và IOCTL
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_READ_DATA = 0x0001

DEVICE_NAME = r"\\.\HackAI_AudioCtrl"
READ_SIZE = 4096
CHANNELS = 2
SAMPLE_RATE = 44100  # Assumed sample rate
DURATION_SECONDS = 20
OUTPUT_FILENAME = "output.wav"

def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

IOCTL_READ_AUDIO = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_READ_DATA)

# Mở thiết bị
kernel32 = ctypes.windll.kernel32
CreateFileW = kernel32.CreateFileW
DeviceIoControl = kernel32.DeviceIoControl
CloseHandle = kernel32.CloseHandle
CreateFileW.restype = ctypes.c_void_p

handle = CreateFileW(
    DEVICE_NAME,
    GENERIC_READ | GENERIC_WRITE,
    0, None,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    None
)

if handle == 0 or handle == -1:
    print("[ERROR] Không thể mở thiết bị.")
    exit(1)

print("[INFO] Ghi âm bắt đầu...")

audio_frames = []
start_time = time.time()

try:
    while time.time() - start_time < DURATION_SECONDS:
        buffer = ctypes.create_string_buffer(READ_SIZE)
        bytes_returned = ctypes.c_ulong(0)

        result = DeviceIoControl(
            handle,
            IOCTL_READ_AUDIO,
            None, 0,
            buffer, READ_SIZE,
            ctypes.byref(bytes_returned),
            None
        )

        if result and bytes_returned.value > 0:
            raw = buffer.raw[:bytes_returned.value]
            audio_frames.append(raw)
        else:
            time.sleep(0.01)

except Exception as e:
    print("[ERROR]", e)

finally:
    CloseHandle(handle)
    print("[INFO] Ghi âm hoàn tất, lưu vào file WAV...")

    if audio_frames:
        with wave.open(OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # int16 => 2 bytes
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(audio_frames))

        print(f"[INFO] File WAV đã được lưu tại: {os.path.abspath(OUTPUT_FILENAME)}")
    else:
        print("[WARNING] Không có dữ liệu âm thanh để lưu.")
