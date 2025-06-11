import sounddevice as sd

ACCEPTED_APIS = ["Windows WASAPI"]

def get_accepted_hostapi_indices():
    hostapis = sd.query_hostapis()
    return [
        i for i, api in enumerate(hostapis)
        if api["name"] in ACCEPTED_APIS
    ]

def list_input_devices():
    devices = sd.query_devices()
    accepted_hostapis = set(get_accepted_hostapi_indices())
    seen = set()
    result = []

    for d in devices:
        if (
            d["hostapi"] in accepted_hostapis
            and d["max_input_channels"] > 0
        ):
            name = d["name"]
            if name not in seen:
                seen.add(name)
                result.append(name)

    return result

def list_output_devices():
    devices = sd.query_devices()
    accepted_hostapis = set(get_accepted_hostapi_indices())
    seen = set()
    result = []

    for d in devices:
        if (
            d["hostapi"] in accepted_hostapis
            and d["max_output_channels"] > 0
        ):
            name = d["name"]
            if name not in seen:
                seen.add(name)
                result.append(name)

    return result

def find_input_device_index_by_name(name):
    devices = sd.query_devices()
    accepted_hostapis = set(get_accepted_hostapi_indices())

    for i, d in enumerate(devices):
        if (
            d["hostapi"] in accepted_hostapis
            and d["max_input_channels"] > 0
            and name.lower() in d["name"].lower()
        ):
            return i

    print(f"[WARN] Input device '{name}' not found. Falling back to default.")
    return None

def find_output_device_index_by_name(name):
    devices = sd.query_devices()
    accepted_hostapis = set(get_accepted_hostapi_indices())

    for i, d in enumerate(devices):
        if (
            d["hostapi"] in accepted_hostapis
            and d["max_output_channels"] > 0
            and name.lower() in d["name"].lower()
        ):
            return i
    return None
