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
