# Hardware Specifications: Xiaomi Smart Clock LX04 / X04G

This reference document details the physical hardware components, integrated circuits, pin multiplexing, interfaces, and memory boundaries of the Xiaomi Smart Clock (China Model: `LX04`, Global Equivalent: `X04G`).

---

## 1. System-on-Chip (SoC)

| Specification | Technical Detail |
| :--- | :--- |
| **Model** | MediaTek MT8167A |
| **Process Node** | 28nm HPC+ |
| **CPU Architecture** | Quad-Core ARM Cortex-A35 |
| **Core Frequency** | Up to 1.3 GHz |
| **Instruction Set** | ARMv8-A (64-bit architecture running in AArch32 mode) |
| **L1 Cache** | 32 KB I-Cache + 32 KB D-Cache per core |
| **L2 Cache** | 512 KB unified cache |
| **GPU** | Imagination Technologies PowerVR GE8300 @ 500 MHz (OpenGL ES 3.2, Vulkan 1.1) |
| **Hardware Crypto Engine** | MediaTek Crypto Engine (AES, SHA-1, SHA-256, RSA) |
| **BootROM (BROM)** | Embedded internal ROM (handles Preloader verification from eMMC BOOT1) |

---

## 2. Memory & Storage Architecture

### 2.1 System Memory (DRAM)
- **Capacity:** 1 GB LPDDR3 SDRAM.
- **Clock Rate:** 800 MHz (LPDDR3-1600).
- **Bus Width:** 32-bit single channel.
- **Controller:** MediaTek EMI (External Memory Interface). Requires timing calibration blocks (`EMI_DATA`) supplied by the preloader during Stage 1 DA handshake.

### 2.2 Non-Volatile Flash Storage (eMMC)
- **Model:** Kingston 4GB eMMC 5.1 (`M62704`).
- **Capacity:** 3,791,650,816 bytes (`0x71000000`, ~3.53 GiB / 3.79 GB).
- **Block Count:** 7,405,568 sectors (512 bytes per sector).
- **Physical Regions:**
  - `BOOT1` (Hardware Boot Partition 1): 2,097,152 bytes (2 MB). Contains BROM EMMC header at `0x000` and Preloader binary (`preloader_mico_x04g.bin`) at `0x800`.
  - `BOOT2` (Hardware Boot Partition 2): 2,097,152 bytes (2 MB). Unused/Mirrored.
  - `RPMB` (Replay Protected Memory Block): 524,288 bytes (512 KB). Secure key storage.
  - `USER` (Main Flash Storage): 3,786,932,224 bytes (LBA 0 through LBA 7,405,567). Contains MBR, Primary GPT, all system/calibration partitions, and Secondary GPT.

---

## 3. Display & Touch Controller

### 3.1 LCD Panel
- **Size:** 3.97-inch diagonally measured.
- **Resolution:** WVGA 800 × 480 pixels (16:9 aspect ratio).
- **Display Technology:** IPS LCD panel with LED backlighting.
- **Interface:** MIPI-DSI (Display Serial Interface) 2-lane.
- **Driver Controller ICs:** BOE / CTC driver ICs (`jd9161z` / `gc9503w`).
- **Initialization:** Initialized during Little Kernel (`lk.bin`) execution before Linux kernel handoff.

### 3.2 Capacitive Touchscreen
- **Touch Controller:** FocalTech FT6336 series.
- **Protocol:** I2C interface bound to MediaTek I2C Controller Channel 0.
- **Multi-Touch:** 2-point capacitive sensing with gesture detection.
- **Sampling Rate:** 60 Hz – 100 Hz.

---

## 4. Audio Subsystem

### 4.1 Audio Output (Speaker)
- **Transducer:** 1.5-inch full-range neodymium high-efficiency speaker driver.
- **Amplifier:** Class-D digital smart power amplifier (I2S input interface).
- **Power Output:** 1.5W nominal, 2.5W peak.
- **Acoustic Design:** Sealed acoustic chamber with passive radiator tuning.

### 4.2 Audio Input (Microphones)
- **Transducers:** Dual far-field digital MEMS microphones.
- **Array Geometry:** Top-mounted linear array with noise-canceling beamforming.
- **Audio Codec / ADC:** Integrated MediaTek MT6392 / MT8167 audio front-end with hardware acoustic echo cancellation (AEC).

---

## 5. Wireless Connectivity

- **Chipset:** MediaTek MT6631 combo wireless chip.
- **Wi-Fi Subsystem:**
  - Standard: IEEE 802.11 b/g/n (Single-band 2.4 GHz).
  - Data Rates: Up to 150 Mbps (HT40).
  - MAC Address: Factory programmed into `nvram` partition (Physical Byte Offset `0x00380000`, LBA `7,168`).
- **Bluetooth Subsystem:**
  - Standard: Bluetooth 5.0 Low Energy (LE).
  - Profiles: A2DP, AVRCP, BLE GATT, HFP.
  - MAC Address: Factory programmed into `nvram` partition (Physical Byte Offset `0x00380000`, LBA `7,168`; confirmed factory calibration location).

---

## 6. Physical Controls & Ports

- **External Ports:**
  - Micro-USB 2.0 Client Port: Located at rear bottom. Serves dual role for 5V/2A DC power supply and High-Speed USB 2.0 communication (BROM / Preloader VCOM / Fastboot / ADB).
- **Physical Buttons:**
  - Volume Up (`+`): Active low, connected to GPIO. Confirms bootloader unlock in LK.
  - Volume Down (`-`): Active low, connected to GPIO. Cancels bootloader unlock in LK.
  - Microphone Mute / Power: Top center push button. Toggles microphone mute state; powers down unit on long press.
