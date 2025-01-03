# Virtual Audio Driver by MikeTheTech

Welcome to the **Virtual Audio Driver by MikeTheTech**! This project provides two key drivers based on the Windows Driver Kit (WDK):

1. **Virtual Audio Driver** – Creates a virtual speaker output device and a virtual microphone input device.

Both features in the driver are suitable for remote desktop sessions, headless configurations, streaming setups, and more. They support Windows 10 and Windows 11, including advanced audio features like Windows Sonic (Spatial Sound), Exclusive Mode, Application Priority, and volume control.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Compatibility](#compatibility)
4. [Installation](#installation)
5. [Usage](#usage)
   - [Using the Virtual Speaker](#using-the-virtual-speaker)
   - [Using the Virtual Microphone](#using-the-virtual-microphone)
6. [Configuration](#configuration)
7. [Building from Source](#building-from-source)
8. [Future Plans](#future-plans)

---

## Overview

A virtual audio driver set consists of:

- **Virtual Audio** ("fake" speaker output)
  - Essential for headless servers, remote desktop streaming, testing audio in environments without physical speakers, etc.

- **Virtual Microphone** ("fake" mic input)
  - Ideal for streaming setups, voice chat tests, combining or routing audio internally, or feeding software-generated audio to apps expecting a microphone input.

By installing these driver, you can process or forward audio without physical hardware present, making them incredibly useful for various development, testing, and media production scenarios.

---

## Key Features

| Feature                                      | Virtual Speaker                                                                                | Virtual Microphone                                                                                                                              |
|----------------------------------------------|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Emulated Device**                          | Emulates a speaker device recognized by Windows.                                               | Emulates a microphone device recognized by Windows.                                                                                             |
| **Supported Audio Formats**                  | **16-bit 48,000 Hz**.                                                                         | **16-bit 44,100 Hz**, **16-bit 48,000 Hz**, **24-bit 96,000 Hz**, **24-bit 192,000 Hz**, **32-bit 4,800 Hz** (for testing or specialized scenarios). |
| **Spatial Sound Support** (Speaker Only)     | Integrates with Windows Sonic, enabling immersive 3D audio features.                            | Integrated with Audio Enhancements such as Voice Focus and Background Noise Reduction.                                                          |
| **Exclusive Mode and App Priority**          | Applications can claim exclusive control of the device.                                        | Same WDK architecture applies, allowing exclusive access in supported workflows.                                                                 |
| **Volume Level Handling**                    | Handles global and per-application volume changes (Windows mixer).                              | Microphone level adjustments accessible via Windows Sound Settings or audio software.                                                            |
| **High Customizability**                     | Built to be extended with future features and audio enhancements.                               | Allows flexible configuration of sampling rates and bit depths for specialized audio requirements.                                               |

---

## Compatibility

- **OS**: Windows 10 (Build 1903 and above) and Windows 11
- **Architecture**: x64 (tested); ARM64 support under consideration
- **Framework**: Windows Driver Kit (WDK)

---

## Installation

1. **Enable Test Signing (Optional)**
   If you have a test-signed driver, you may need to enable test signing mode:
   \`\`\`powershell
   bcdedit /set testsigning on
   \`\`\`
   *Note: A production-signed driver can skip this step.*

2. **Install the INF**
   - Right-click on the \`.inf\` file and choose “Install.”
   - OR open an elevated command prompt and run:
     \`\`\`powershell
     pnputil /add-driver .\\SimpleAudioSample.inf /install
     \`\`\`

3. **Reboot** (if prompted)
   Windows may require a reboot to finalize driver initialization.

4. **Verify Installation**
   - Open **Device Manager**.
   - Check under **Sound, video and game controllers** for “Virtual Audio Driver” (speaker).
   - Check under **Audio inputs and outputs** for “Virtual Mic Driver” (microphone).

---

## Usage

### Using the Virtual Speaker

1. **Select as Default Device**
   - Open **Sound Settings** → **Output** → Choose “Virtual Audio Driver” as your default output device.
   - Or use the **Volume Mixer** to route specific apps to the virtual speaker.

2. **Remote Desktop or Streaming**
   - When initiating a remote desktop session, the virtual speaker device can appear as a valid playback device.
   - Streaming or capture apps can detect the virtual speaker for capturing system audio.

3. **Spatial Sound**
   - In **Sound Settings**, right-click the device, select **Properties** → **Spatial Sound** tab, and enable **Windows Sonic for Headphones** or another supported format.

### Using the Virtual Microphone

1. **Select as Default Recording Device**
   - Open **Sound Settings** → **Input** → Choose “Virtual Mic Driver” as your default input device.
   - Alternatively, in the **Volume Mixer** or your specific application’s audio settings, route or select the “Virtual Mic Driver” for input.

2. **Supported Formats**
   - The Virtual Microphone Driver supports:
     - **16-bit, 44,100 Hz**
     - **16-bit, 48,000 Hz**
     - **24-bit, 96,000 Hz**
     - **24-bit, 192,000 Hz**
     - **32-bit, 48,000 Hz**

3. **Use Cases**
   - **Voice Chat / Conference Apps**: Emulate or inject audio into Zoom, Teams, Discord, etc.
   - **Streaming / Broadcasting**: Feed application-generated audio to OBS, XSplit, or other streaming tools.
   - **Audio Testing**: Confirm that your software or game engine’s microphone-handling logic works without real hardware.

4. **Volume & Level Controls**
   - Adjust input levels in **Sound Settings** → **Recording** tab.
   - Per-app mic levels can be configured in certain software or system volume mixers (where supported).

---

## Configuration

- **Exclusive Mode** (Speaker and Mic)
  By default, shared mode is enabled. For real-time, low-latency usage, open device properties, go to the **Advanced** tab, and uncheck “Allow applications to take exclusive control.”

- **Application Priority**
  Supported through Windows APIs. To prioritize a specific application for either the speaker or microphone, configure it via Windows advanced sound options or in your audio software.

- **Volume/Level Management**
  - For the Virtual Speaker, adjust in the main Sound Settings or the Volume Mixer.
  - For the Virtual Microphone, adjust input levels in the Recording tab of Sound Settings or in your audio software’s device preferences.

---

## Building from Source

1. **Prerequisites**
   - Windows Driver Kit (WDK) installed
   - Visual Studio (2019 or later)
   - Optional: Windows SDK matching your target OS

2. **Clone the Repo**
   \`\`\`powershell
   git clone https://github.com/VirtualDisplay/Virtual-Audio-Driver.git
   cd Virtual-Audio-Driver
   \`\`\`

3. **Open the Driver Solution**
   - Launch Visual Studio.
   - Open the \`.sln\` file within the repository.

4. **Build**
   - Select **Release** or **Debug** configuration.
   - Right-click the project in Solution Explorer and choose **Build**.

5. **Sign the Driver** (Optional/Recommended)
   - Use your own code signing certificate or a test certificate for development.
   - Ensure your system is in test mode if using a test certificate.

---

## Future Plans

- **ARM64** compatibility
- **Advanced Diagnostics**: Logging and debugging tools
- **New Modes & Additional Formats**: Continued expansion of supported audio qualities.
- **Additional Features**: Such as Automatic Volume Leveling (AVL), further spatial audio improvements, and custom routing tools.

> This project is maintained and actively improved. We welcome contributions, suggestions, and issue reports!

---

**Thank you for using the Virtual Audio Driver!**  
Feel free to open issues or submit pull requests if you encounter any problems or have ideas to share. Happy audio routing!
