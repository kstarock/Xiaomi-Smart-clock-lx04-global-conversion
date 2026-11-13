# Flashing & Device Communication Tool Suite

This directory documents and organizes every verified application, driver, and utility required to convert the **Xiaomi Smart Clock (China Model: LX04)** to the **Official Global Firmware (Model: X04G)**.

---

## 1. Tool Suite Overview

| Application / Dependency | Verified Version | License / Ownership | Primary Purpose in Conversion | Documentation & Guide |
| :--- | :--- | :--- | :--- | :--- |
| **SP Flash Tool** | `v5.1728.00` / `v5.1812.00` | Proprietary (MediaTek Inc.) | Contiguous raw block flashing of `super.bin` (1.50 GB), GPT programming, and factory readbacks | [**SP Flash Tool Guide**](sp-flash-tool/README.md) |
| **MTK Client** | Commit `118a000` (2026-10-26) | Open Source (GPL-3.0) | Low-level BROM handshake testing, exploratory memory analysis, and stock partition dumping | [**MTK Client Guide**](mtk-client/README.md) |
| **Android Fastboot CLI** | `302830efc153-android` | Apache-2.0 (Google LLC) | AVB 2.0 bootstack flashing, bootloader unlocking (`fastboot oem unlock`), and data wiping | [**Fastboot & ADB Guide**](adb-fastboot/README.md) |
| **Android Debug Bridge** | `1.0.40` (v4797878) | Apache-2.0 (Google LLC) | Post-conversion verification, logcat monitoring, and system property queries | [**Fastboot & ADB Guide**](adb-fastboot/README.md) |
| **MediaTek USB Drivers** | `3.0.1511.0` (`usb2ser.sys`) | Proprietary (MediaTek Inc.) | Windows USB driver binding for BROM (`0E8D:0003`) and Preloader VCOM (`0E8D:2000`) | [**USB Drivers Guide**](usb-drivers/README.md) |
| **Python Runtime** | `3.8+` (Tested: `3.15.1`) | PSF License | Standard library host automation, Win32 serial hooks, GPT synthesis, and verification suite | [**Utilities Guide**](utilities/README.md) |
| **Archive Utilities** | Windows native `tar.exe` / 7-Zip | BSD / GNU LGPL | Decompressing `.tar.xz` firmware dumps and archive packages | [**Utilities Guide**](utilities/README.md) |

---

## 2. Licensing, Redistribution & Safety Policy

1. **Open Source Utilities:**
   Open-source tools (such as Bjoern Kerler's `mtkclient` under GPL-3.0 and Google Android Platform Tools under Apache-2.0) are licensed for public redistribution according to their respective upstream licenses. Official repository sources are documented in their subdirectories.

2. **Proprietary Vendor Binaries:**
   MediaTek SP Flash Tool (`_SPFT.exe`), MediaTek USB VCOM drivers (`usb2ser.sys`), OEM Download Agent (`DA_Mi_Hikaru-resign.bin`), and SLA authentication descriptors (`auth_sv5.auth`) are proprietary intellectual property. They are **not committed directly to this GitHub repository** to avoid copyright infringement. Verified official download mirrors and SHA-256 checksums are documented in each subfolder so users can independently acquire and verify genuine binaries.

3. **Critical Flash Safety Constraints:**
   - **NEVER** select `Format All + Download` or `Firmware Upgrade` in SP Flash Tool.
   - **NEVER** flash `super.bin` via Fastboot. Little Kernel on MT8167 has a write cursor defect that overwrites sector 0 on each chunk.
   - **ALWAYS** preserve `proinfo` and `nvram` at eMMC offsets `0x00080000` and `0x00380000`.

---

## 3. Subdirectory Index

- [**`sp-flash-tool/`**](sp-flash-tool/README.md): Configuration of SP Flash Tool (v5.1728 / v5.1812), XML profiles, DA handling, and contiguous flashing.
- [**`mtk-client/`**](mtk-client/README.md): Setup for `mtkclient`, Python prerequisites, LibUSB configuration, and device inspection commands.
- [**`adb-fastboot/`**](adb-fastboot/README.md): Google SDK Platform Tools installation, Fastboot command sequences, and bootloader unlocking.
- [**`usb-drivers/`**](usb-drivers/README.md): MediaTek USB VCOM, CDC ACM, and Android Bootloader Interface driver setup on Windows 10/11.
- [**`utilities/`**](utilities/README.md): Python environment setup (standard library modules only), and archive tools (`tar.exe`, 7-Zip).
- [**`TOOL_VERSIONS.md`**](TOOL_VERSIONS.md): Complete version and compatibility matrix for all tools and firmware builds.
