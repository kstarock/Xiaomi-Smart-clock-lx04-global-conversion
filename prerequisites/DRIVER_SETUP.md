# Driver Setup & USB Interface Guide

MediaTek MT8167 devices present three distinct USB hardware modes during the boot and conversion lifecycle. Each mode requires a matching Windows driver.

---

## 1. Summary of USB Operating Modes

| Mode | Enumeration Name | Hardware VID/PID | Associated Software | Trigger Method |
| :--- | :--- | :--- | :--- | :--- |
| **1. MediaTek BROM Mode** | `MediaTek USB Port` | `VID_0E8D&PID_0003` | SP Flash Tool Stage 1 | Connected when preloader is empty or testpoint held |
| **2. Preloader VCOM Mode**| `MediaTek Preloader USB VCOM Port` | `VID_0E8D&PID_2000` | Preloader Interceptor Script / SP Flash Tool | Appears for 500ms – 2 seconds when plugging in USB |
| **3. Android Fastboot Mode**| `Android Bootloader Interface` | `VID_18D1&PID_D00D` | Fastboot CLI | Triggered by interceptor script or `fastboot reboot-bootloader` |

---

## 2. Installing the MediaTek VCOM Drivers

1. Download the official MediaTek USB VCOM driver package (Driver Version `3.0.1511.0` or `5.1632.00`).
2. Run the driver installer as **Administrator** (`Install.bat` or `cdc-acm.inf`).
3. If Windows 10/11 blocks unsigned driver installation:
   - Hold `Shift` while clicking **Restart** in Windows Start Menu.
   - Select **Troubleshoot** -> **Advanced options** -> **Startup Settings** -> **Restart**.
   - Upon reboot, press `7` to "Disable driver signature enforcement".
   - Install the MediaTek driver.

### How to Verify Preloader VCOM Binding:
1. Open Windows **Device Manager** (`devmgmt.msc`).
2. Expand the **Ports (COM & LPT)** section.
3. Plug in the clock's Micro-USB cable while watching the screen.
4. For approximately 1 to 2 seconds, you should see:
   `MediaTek Preloader USB VCOM Port (COMx)` appear before disappearing or continuing boot.
5. Take note of the assigned port number (e.g. `COM5`).

---

## 3. Installing the Android Fastboot Driver

When the clock enters Fastboot mode via our interceptor script, Windows must bind the Android Bootloader Interface driver:

1. Connect the clock in Fastboot mode (or enter via `scripts/fastboot/preloader_fastboot_interceptor.py`).
2. Open **Device Manager**.
3. Under "Other devices", locate `Android` or `mico_x04g` with a yellow exclamation point.
4. Right-click -> **Update driver**.
5. Select: **Browse my computer for drivers**.
6. Select: **Let me pick from a list of available drivers on my computer**.
7. Select category: **Android Device** (or "Universal Serial Bus devices").
8. Select manufacturer: **Google, Inc.** -> Model: **Android Bootloader Interface**.
9. Click **Next** and accept the warning prompt.
10. Test in PowerShell:
    ```powershell
    fastboot devices
    ```
    *Expected output: `<SERIAL_NUMBER>   fastboot`.*
