# Tool Versions & Hardware Compatibility Matrix

This document records the exact tool versions, hardware revisions, and firmware build identifiers verified during the Xiaomi Smart Clock LX04 China-to-Global conversion project.

---

## 1. Verified Software Tools & Dependencies

| Tool / Software | Verified Version | Developer / Vendor | Executable / Package | Role in Conversion |
| :--- | :--- | :--- | :--- | :--- |
| **SP Flash Tool** | `v5.1728.00` (Win32)<br>*(v5.1812.00 also compatible)* | MediaTek Inc. | `_SPFT.exe`<br>(SHA-256: `611180fb...`) | eMMC contiguous raw block flashing of `super.bin`, GPT programming, and physical readbacks |
| **OEM Download Agent** | `DA_Mi_Hikaru-resign.bin` | Xiaomi Inc. / MediaTek | Stage 1 & 2 DA payload (492,460 bytes) | Cryptographically authentic DRAM initialization driver |
| **SLA Authentication File**| `auth_sv5.auth` | Xiaomi Inc. / MediaTek | Security token (2,256 bytes) | MediaTek BROM secure handshake response |
| **MTK Client** | Commit `118a000` (2026-10-26) | Bjoern Kerler (@bkerler) | `mtk.py` / `mtkclient/` library | Diagnostic memory readbacks, BROM testing, and partition geometry analysis |
| **Fastboot CLI** | `302830efc153-android` | Google LLC | `fastboot.exe`<br>(SHA-256: `8b68092a...`) | Flashing AVB bootchain images, bootloader unlocking (`fastboot oem unlock`), and data wipe |
| **Android Debug Bridge** | `1.0.40` (v4797878) | Google LLC | `adb.exe`<br>(SHA-256: `b40abda7...`) | Post-conversion system state inspection and runtime properties verification |
| **MediaTek VCOM Driver**| `3.0.1511.0` (`usb2ser.sys`)| MediaTek Inc. | `usbvcom.inf` / `cdc-acm.inf` | Windows USB CDC serial driver for BROM (`0E8D:0003`) and Preloader (`0E8D:2000`) |
| **Python Runtime** | `3.8+` (Tested: `3.15.1`) | Python Software Foundation | `python.exe` | Standard-library Win32 serial interceptor hook, GPT patchers, and verification audit suite |
| **Archive Extractor** | Windows native `tar.exe` | BSD / Microsoft Corp. | `C:\WINDOWS\system32\tar.exe` | Unpacking `.tar.xz` firmware dumps and archive files |
| **PySerial (Optional)** | `v3.5+` | Chris Liechti | `pyserial` Python package | External dependency for `mtkclient` only; **NOT required** by repository scripts |
| **7-Zip (Optional GUI)** | `v23.01+` | Igor Pavlov | `7z.exe` / `7zFM.exe` | Optional graphical archive manager |

> [!NOTE]
> **Repository Python Dependencies:**
> All automation and conversion scripts inside this repository use the **Python standard library only** (`ctypes`, `subprocess`, `struct`, `zlib`, `hashlib`, `xml.etree`). No `pip install` commands or external packages (such as `pyserial`) are required to run repository scripts. The `pyserial` package is only needed if you independently run the external diagnostic tool `mtkclient`.
> The minimum supported version is **Python 3.8+**. The current test workstation runs Python 3.15.1; the exact micro-version on the original conversion machine is UNKNOWN (recorded as 3.8+ compatible).

---

## 2. Verified Hardware Identifiers

| Parameter | Hardware Value | Identification Details |
| :--- | :--- | :--- |
| **Device Model** | Xiaomi Smart Clock | China Model: `LX04` / Global Model: `X04G` |
| **Motherboard ID** | `mico_lx04` / `mico_x04g` | PCB Revision: Single-board form factor with external Micro-USB |
| **SoC (Processor)** | MediaTek MT8167A | Quad-core ARM Cortex-A35 @ 1.3 GHz (ARMv8-A in AArch32 mode) |
| **GPU** | Imagination PowerVR GE8300 | OpenGL ES 3.2, Vulkan 1.1 |
| **System RAM** | 1 GB LPDDR3 SDRAM | Configured via Preloader EMI tables |
| **eMMC Flash Storage** | Kingston `M62704` (4 GB eMMC 5.1) | CID Name: `M62704`, Capacity: `0x71000000` (3,791,650,816 bytes) |
| **eMMC Block Count** | `7,405,568` sectors | Exactly 512 bytes per sector |
| **Physical Boot Block** | `BOOT1` (2,097,152 bytes) | Hosts Global Preloader `preloader_mico_x04g.bin` at offset `0x800` |
| **Display Panel IC** | BOE / CTC `jd9161z` / `gc9503w` | 3.97-inch IPS LCD, 800 × 480 WVGA resolution |
| **Touch Controller IC**| FocalTech FT6336 | Capacitive I2C multi-touch digitizer |
| **Wi-Fi / BT Chip** | MediaTek MT6631 | Single-band 2.4 GHz 802.11 b/g/n + Bluetooth 5.0 LE |
| **Microphone ADC** | Everest Semiconductor ADC | Far-field dual-microphone array |
| **Speaker Amplifier** | Class-D Audio Amp | 1.5-inch neodymium full-range speaker |

---

## 3. Verified Firmware Build Identifiers

### Original Chinese Firmware (Factory Stock):
- **Build Fingerprint:** `Xiaomi/mico_lx04/mico_lx04:8.1.0/O11019/1.3.x:user/release-keys`
- **Android Version:** Android 8.1 Oreo (Engineering base: `alps-mp-o1.mp5_W18.34`)
- **Partition Scheme:** Legacy Static Partitions (21 partitions; no dynamic `super` partition)
- **Preloader:** Original Chinese preloader preserved in offline backup `LX04-Backup/boot1.bin`

### Target Global Firmware (Converted & Hardware Verified):
- **Build Fingerprint:** `xiaomi/mico_x04g/mico_x04g:10/QP1A.190711.020/1.7.5:user/release-keys`
- **Android Version:** Android 10 (Build `QP1A.190711.020 / 1.7.5`)
- **Bootloader Version:** `mico_x04g-451d69f-20210619014509-202112`
- **Preloader Version:** `0.1.00` (Installed in `BOOT1` @ `0x800`)
- **Partition Scheme:** Android 10 Dynamic Partitions (`super` container spanning 1.50 GB)
- **Bootloader Status:** Unlocked (`fastboot getvar unlocked: yes`, AVB Orange State)
