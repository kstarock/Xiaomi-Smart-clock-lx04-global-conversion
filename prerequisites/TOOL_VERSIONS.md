# Tool Versions & Hardware Compatibility Matrix

This document records the exact tool versions, hardware revisions, and firmware build identifiers verified during the project.

---

## 1. Verified Software Tools

| Tool / Software | Verified Version | Developer / Vendor | Purpose in Conversion |
| :--- | :--- | :--- | :--- |
| **SP Flash Tool** | `v5.1812.00` (Win32) | MediaTek Inc. | Primary eMMC contiguous flash engine & GPT programmer |
| **Download Agent** | `DA_Mi_Hikaru-resign.bin` | Xiaomi Inc. / MediaTek | Authentic OEM signed Stage 1 & Stage 2 flash driver |
| **Authentication File**| `auth_sv5.auth` | Xiaomi Inc. / MediaTek | Stage 1 cryptographic authentication descriptor |
| **Fastboot CLI** | `v1.1916.00` / `34.0.5` | Google LLC | Fastboot flashing of boot, dtbo, vbmeta, and unlock commands |
| **Python Runtime** | `3.10.x` / `3.8+` | Python Software Foundation | Execution of interceptor scripts and checksum validators |
| **MediaTek VCOM Driver**| `3.0.1511.0` (`usb2ser.sys`) | MediaTek Inc. | Windows USB CDC serial driver for BROM / Preloader |

---

## 2. Verified Hardware Identifiers

| Parameter | Hardware Value | Notes |
| :--- | :--- | :--- |
| **Device Model** | Xiaomi Smart Clock (China: `LX04` / Global: `X04G`) | Motherboard: `mico_lx04` / `mico_x04g` |
| **SoC Model** | MediaTek MT8167A | 4x ARM Cortex-A35 @ 1.3GHz |
| **eMMC Flash CID** | Kingston `M62704` | 4 GB eMMC 5.1 |
| **eMMC Capacity** | `0x71000000` bytes | Exactly `7,405,568` sectors of 512 bytes |
| **Display Panel IC** | BOE / CTC `jd9161z` / `gc9503w` | 800 × 480 WVGA IPS |
| **Touch Controller IC**| FocalTech FT6336 | I2C Capacitive Multi-touch |
| **Wi-Fi / BT Chip** | MediaTek MT6631 | 2.4 GHz 802.11b/g/n + BT 5.0 LE |

---

## 3. Verified Firmware Build Identifiers

### Original Chinese Firmware:
- **Build Fingerprint:** `Xiaomi/mico_lx04/mico_lx04:8.1.0/O11019/1.3.x:user/release-keys`
- **Android Version:** Android 8.1 Oreo (Engineering base: `alps-mp-o1.mp5_W18.34`)
- **Partition Scheme:** Legacy Static Partitions (21 partitions)

### Target Global Firmware:
- **Build Fingerprint:** `xiaomi/mico_x04g/mico_x04g:10/QP1A.190711.020/1.7.5:user/release-keys`
- **Android Version:** Android 10 (Build `QP1A.190711.020 / 1.7.5`)
- **Bootloader Version:** `mico_x04g-451d69f-20210619014509-202112`
- **Preloader Version:** `0.1.00`
- **Partition Scheme:** Android 10 Dynamic Partitions (`super` container)
