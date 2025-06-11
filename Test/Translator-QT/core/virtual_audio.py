import threading
import sounddevice as sd

# ==== VIRTUAL MIC KEEP ALIVE ====
class VirtualMicKeepAlive(threading.Thread):
    def __init__(self, device_name):
        super().__init__(daemon=True)
        self.running = True
        self.device_name = device_name
        self.stream = None

    def find_device_index(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if self.device_name.lower() in dev['name'].lower() and dev['max_input_channels'] > 0:
                return i
        return None

    def run(self):
        device_index = self.find_device_index()
        if device_index is None:
            print(f"[!] Cannot find virtual mic device: {self.device_name}")
            return

        def callback(indata, frames, time, status):
            pass  # No-op, just keep alive

        try:
            with sd.InputStream(
                samplerate=48000,
                channels=2,
                dtype='int32',
                blocksize=1024,
                callback=callback,
                device=device_index
            ):
                print("[+] Virtual mic keep-alive started.")
                while self.running:
                    sd.sleep(500)
        except Exception as e:
            print(f"[!] VirtualMicKeepAlive error: {e}")

    def stop(self):
        self.running = False


# ==== VIRTUAL SPEAKER KEEP ALIVE ====
class VirtualSpeakerKeepAlive(threading.Thread):
    def __init__(self, device_name):
        super().__init__(daemon=True)
        self.running = True
        self.device_name = device_name
        self.stream = None

    def find_device_index(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if self.device_name.lower() in dev['name'].lower() and dev['max_output_channels'] > 0:
                return i
        return None

    def run(self):
        device_index = self.find_device_index()
        if device_index is None:
            print(f"[!] Cannot find virtual speaker device: {self.device_name}")
            return

        def callback(outdata, frames, time, status):
            outdata.fill(0)  # Silence

        try:
            with sd.OutputStream(
                samplerate=48000,
                channels=2,
                dtype='int32',
                blocksize=1024,
                callback=callback,
                device=device_index
            ):
                print("[+] Virtual speaker keep-alive started.")
                while self.running:
                    sd.sleep(500)
        except Exception as e:
            print(f"[!] VirtualSpeakerKeepAlive error: {e}")

    def stop(self):
        self.running = False
