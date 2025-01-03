# Virtual Audio Driver by MikeTheTech

Welcome to the **Virtual Audio Driver by MikeTheTech**! This Windows Driver Kit (WDK)–based driver creates a virtual speaker output device, suitable for remote desktop sessions, headless configurations, and streaming setups. The driver supports Windows 10 and Windows 11, including advanced audio features like Windows Sonic (Spatial Sound), Exclusive Mode, Application Priority, and volume control.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Compatibility](#compatibility)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Configuration](#configuration)
7. [Building from Source](#building-from-source)
8. [Future Plans](#future-plans)

---

## Overview

A virtual audio driver lets you configure a “virtual” or "fake" speaker device on your system. This can be essential when:

- Running a machine **headless**, but needing audio output for apps.
- Streaming or capturing audio on a **remote desktop** session.
- Testing or debugging applications that rely on audio output.
- Leveraging **Spatial Sound** and other audio enhancements in software.

By installing this driver, any audio that targets this virtual speaker can be processed or forwarded elsewhere as needed, without any physical hardware present.

---

## Key Features

| Feature                              | Description                                                                                  |
|--------------------------------------|----------------------------------------------------------------------------------------------|
| **Virtual Speaker**                  | Emulates a speaker device recognized by Windows, allowing applications to play sound to it. |
| **Spatial Sound Support**            | Integrates with Windows Sonic, enabling immersive 3D audio features in compatible software.  |
| **Exclusive Mode and App Priority**  | Allows applications to claim exclusive control of the virtual device for low-latency audio. |
| **Volume Level Handling**            | Handles global and per-application volume changes on the virtual output.                    |
| **Extensible**                       | Built to be expanded with future features and audio enhancements.                           |

---

## Compatibility

- **OS**: Windows 10 (Build 1903 and above) and Windows 11  
- **Architecture**: x64 (tested); ARM64 support under consideration  
- **Framework**: Windows Driver Kit (WDK)

---

## Installation

1. **Enable Test Signing (Optional)**  
   If you have a test-signed driver, you may need to enable test signing mode:
   ```powershell
   bcdedit /set testsigning on
   ```
   *Note: A production-signed driver can skip this step.*

2. **Install the INF**  
   - Right-click on the `.inf` file and choose “Install.”
   - OR open an elevated command prompt and run:
     ```powershell
     pnputil /add-driver .\SimpleAudioSample.inf /install
     ```

3. **Reboot** (if prompted)  
   Windows may require a reboot to finalize driver initialization.

4. **Verify Installation**  
   - Open **Device Manager** and check under **Sound, video and game controllers** for “Virtual Audio Driver.”

---

## Usage

Once installed:

1. **Select as Default Device**  
   - Open **Sound Settings** → **Output** → Choose “Virtual Audio Driver” as your default output device.  
   - In the **Volume Mixer**, you can also route individual apps to the virtual device.

2. **Remote Desktop or Streaming**  
   - When initiating a remote desktop session, the virtual audio device can appear as a valid playback device.  
   - Streaming or capture applications can detect the virtual speaker for capturing system audio.

3. **Spatial Sound**  
   - In **Sound Settings**, right-click the device, select **Properties** → **Spatial Sound** tab, and enable **Windows Sonic for Headphones** or other supported formats.

---

## Configuration

- **Exclusive Mode**:  
  By default, shared mode is enabled. For real-time, low-latency usage, open device properties, go to **Advanced** tab, and uncheck “Allow applications to take exclusive control.”

- **Application Priority**:  
  Supported through Windows APIs. To give priority to a particular application, configure it in your audio software or Windows advanced sound options.

- **Volume Level Management**:  
  You can adjust global volume in the main Sound Settings or per-application volume in the Volume Mixer.

---

## Building from Source

1. **Prerequisites**  
   - Windows Driver Kit (WDK) installed
   - Visual Studio (2019 or later)
   - Optional: Windows SDK matching your target OS

2. **Clone the Repo**  
   ```powershell
   git clone https://github.com/VirtualDisplay/Virtual-Audio-Driver.git
   cd VirtualAudioDriver
   ```

3. **Open the Driver Solution**  
   - Launch Visual Studio.
   - Open the `.sln` file within the repository.

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
- **New Modes**: Allowing different audio qualities and formats.
- **New Features**: Added features such as AVL.

> This project is maintained and actively improved. We welcome contributions, suggestions, and issue reports!

---

**Thank you for using the Virtual Audio Driver!** Feel free to open issues or submit pull requests if you encounter any problems or have ideas to share. Happy audio routing!
