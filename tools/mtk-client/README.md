# MTK Client (`mtkclient`): Setup & Diagnostic Guide

This guide documents the setup, installation, and operation of **MTK Client by Bjoern Kerler (@bkerler)**, the open-source diagnostic and forensic tool used during hardware discovery and initial partition verification of the Xiaomi Smart Clock LX04.

---

## 1. Application Identification & Specifications

- **Application Name:** MTK Client (`mtkclient`)
- **Verified Version:** Git commit `118a000a83ea31c4f427fe5225abfe964546e05e` (v2.0.x branch)
- **Author / Maintainer:** Bjoern Kerler ([@bkerler](https://github.com/bkerler))
- **License:** GNU General Public License v3.0 (GPL-3.0)
- **Official Repository:** [https://github.com/bkerler/mtkclient](https://github.com/bkerler/mtkclient)
- **Tested Environment:** Windows 10 / Windows 11 with Python 3.8+ (tested on Python 3.15.1)

---

## 2. Role & Purpose in the LX04 Conversion

During the reverse-engineering and pre-flashing phases, `mtkclient` was used to:

1. **Hardware & SoC Identification:** Establish raw USB communication with the MediaTek MT8167A BootROM (BROM) at `VID_0E8D&PID_0003` and verify chipset ID `0x0335`.
2. **Partition Geometry Verification:** Read the factory eMMC Master Boot Record and Primary GPT (`python mtk.py printgpt`), proving the clock uses a 4 GB Kingston eMMC (`M62704`) with exactly `7,405,568` sectors of 512 bytes.
3. **Forensic Backup of Stock Partitions:** Create raw binary dumps of original Chinese partition images (`boot_a`, `system_a`, `vendor_a`, `protect1`, `protect2`, `persist`) for offline analysis.
4. **Zero-Byte Region Forensic Proof:** Verify that stock Chinese `protect1` (10 MB), `protect2` (10 MB), and the first 28 MB of Chinese `persist` consisted of 100% zeroes on the factory flash.

---

## 3. Installation & Setup Instructions

### Step 1: Clone the Official Repository
```powershell
git clone https://github.com/bkerler/mtkclient.git
cd mtkclient
```

### Step 2: Install Python Dependencies
Ensure Python 3.8+ is installed on your system, then install the required Python packages:
```powershell
pip install -r requirements.txt
```

Key dependencies installed include:
- `pyusb` (`v1.3.1+`)
- `pyserial` (`v3.5+`)
- `pycryptodome` (`v4.3.0+`)
- `colorama`

### Step 3: Windows USB Driver Configuration
On Windows, `mtkclient` uses `pyusb` with `libusb-1.0`. To enable direct USB communication with the MediaTek BootROM:
1. Download and install **UsbDk** (USB Development Kit) from [https://github.com/daynix/UsbDk/releases](https://github.com/daynix/UsbDk/releases).
2. Alternatively, use Zadig ([https://zadig.akeo.ie](https://zadig.akeo.ie)) to install the `libusbK` or `WinUSB` driver on the `MediaTek USB Port` (`VID_0E8D&PID_0003`).

---

## 4. Operational Usage & Verification Commands

### Read and Print Device Partition Table (GPT)
```powershell
python mtk.py printgpt
```
*Action:* Run the command, then plug the clock's Micro-USB cable into the PC while holding the physical Volume- or Volume+ button. The tool will handshake with the BootROM and print the active partition map.

### Dump a Specific Partition for Backup
```powershell
python mtk.py r proinfo proinfo_backup.bin
python mtk.py r nvram nvram_backup.bin
```

---

## 5. Important Warnings & Driver Conflicts

> [!WARNING]
> **Windows Driver Coexistence Notice:**
> - `mtkclient` requires `libusb` or `UsbDk` to capture raw USB transfers from `VID_0E8D&PID_0003`.
> - `SP Flash Tool` and our `preloader_fastboot_interceptor.py` script require the official **MediaTek USB VCOM serial driver (`usb2ser.sys`)** bound to `VID_0E8D&PID_2000` or `VID_0E8D&PID_0003`.
>
> If UsbDk intercepts the Preloader COM port, SP Flash Tool and our serial interceptor will not be able to open `COMx`. If you encounter COM port connection timeouts, ensure UsbDk is stopped or that the VCOM driver is cleanly bound in Windows Device Manager.
