# MediaTek & Android USB Drivers: Setup & Troubleshooting Guide

This guide documents the installation, hardware IDs, and verification procedures for the USB drivers required during the Xiaomi Smart Clock LX04 conversion on Windows 10 and Windows 11.

---

## 1. Hardware USB Operating Modes

The MediaTek MT8167A presents three distinct USB identities across the conversion lifecycle. Each requires a matching driver in Windows:

| Operating Mode | Windows Enumeration Name | Hardware VID/PID | Associated Software | Time Window / Trigger |
| :--- | :--- | :--- | :--- | :--- |
| **1. BROM Mode** | `MediaTek USB Port` | `USB\VID_0E8D&PID_0003` | SP Flash Tool Stage 1 / `mtkclient` | BootROM recovery mode (when eMMC is blank or testpoint grounded) |
| **2. Preloader VCOM** | `MediaTek Preloader USB VCOM Port` | `USB\VID_0E8D&PID_2000` | Preloader Interceptor Script / SP Flash Tool | **1 to 2 seconds only** when plugging in Micro-USB from powered-off state |
| **3. Android Fastboot**| `Android Bootloader Interface` | `USB\VID_18D1&PID_D00D` | Google Fastboot CLI | Persistent bootloader interface once intercepted by LK |

---

## 2. Verified Driver Versions & Files

1. **MediaTek USB VCOM Driver:**
   - Driver Version: `3.0.1511.0` (or `5.1632.00`)
   - Driver Service: `usb2ser.sys`
   - Setup INF Files: `usbvcom.inf`, `usbvcom_brom.inf`, `cdc-acm.inf`
   - Source: MediaTek Driver Hub ([https://mediatekdriver.com](https://mediatekdriver.com))
2. **Google Android Bootloader Interface Driver:**
   - Driver Service: `winusb.sys` (Windows native WinUSB)
   - Setup INF File: `android_winusb.inf`
   - Source: Google Android Developer Portal ([https://developer.android.com/studio/run/win-usb](https://developer.android.com/studio/run/win-usb))

---

## 3. Step-by-Step Installation Instructions

### Step 1: Install MediaTek Preloader VCOM Driver
1. Download the official MediaTek Driver package from [https://mediatekdriver.com](https://mediatekdriver.com).
2. Extract the archive into a local folder.
3. If an automated installer (`Mediatek-Drivers-Install.bat` or `Install.bat`) is present, right-click and select **Run as administrator**.
4. To install manually via INF:
   - Open Windows **Device Manager** (`devmgmt.msc`).
   - Click on the top computer name -> click **Action** menu -> **Add legacy hardware**.
   - Select **Install the hardware that I manually select from a list (Advanced)** -> click **Next**.
   - Select **Ports (COM & LPT)** -> click **Next** -> click **Have Disk...**.
   - Browse to your extracted driver directory -> select `cdc-acm.inf` or `usbvcom.inf` -> click **OK**.
   - Select **MediaTek Preloader USB VCOM Port** -> finish installation.

### Step 2: Disable Driver Signature Enforcement (If Windows Blocks Installation)
If Windows 10/11 displays a red warning stating that the driver is unsigned:
1. Hold `Shift` on your keyboard while clicking **Restart** in the Windows Start menu.
2. Select **Troubleshoot** -> **Advanced options** -> **Startup Settings** -> click **Restart**.
3. Upon reboot, press `7` or `F7` on your keyboard ("Disable driver signature enforcement").
4. Repeat the driver installation steps above.

### Step 3: Install Android Fastboot Driver
1. Connect the clock in Fastboot mode (or enter via `python scripts/fastboot/preloader_fastboot_interceptor.py`).
2. Open Windows **Device Manager**.
3. Under **Other devices**, locate `Android` or `mico_x04g` with a yellow exclamation mark.
4. Right-click -> **Update driver** -> **Browse my computer for drivers**.
5. Select **Let me pick from a list of available drivers on my computer**.
6. Select category: **Android Device** -> Manufacturer: **Google, Inc.** -> Model: **Android Bootloader Interface**.
7. Click **Next** and confirm installation.

---

## 4. Verification Procedures

### Verifying Preloader COM Port Binding:
1. Open Windows **Device Manager** and expand **Ports (COM & LPT)**.
2. Keep the window visible while plugging the clock's Micro-USB cable into the PC.
3. For approximately 1 to 2 seconds, you should observe:
   ```text
   MediaTek Preloader USB VCOM Port (COMx)
   ```
   appear before disappearing as the device continues normal boot. Note down the assigned `COMx` port number (e.g., `COM5`).

### Verifying Fastboot Binding:
With the clock held in Fastboot mode, open PowerShell and run:
```powershell
fastboot devices
```
*Expected output:*
```text
0123456789ABCDEF    fastboot
```

---

## 5. Troubleshooting Common Driver Issues

- **Issue: The Preloader COM port appears for less than 1 second and disappears before software can connect:**
  *Solution:* This is normal MediaTek hardware behavior. Do not try to click manually. Use our low-latency Win32 interceptor (`python scripts/fastboot/preloader_fastboot_interceptor.py`), which polls the serial interface with 10 ms granularity and immediately sends the token.
- **Issue: `SP Flash Tool` reports timeout error `0xC0010001`:**
  *Solution:* Verify that UsbDk is not capturing the USB endpoint. If UsbDk is running, stop the UsbDk service (`net stop UsbDk`) or uninstall UsbDk before running SP Flash Tool.
