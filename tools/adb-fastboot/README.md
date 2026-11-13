# Android Fastboot & ADB CLI: Setup & Command Guide

This guide documents the setup, driver configuration, command sequences, and safety restrictions for **Google Android SDK Platform-Tools (Fastboot and ADB CLI)** used in the Xiaomi Smart Clock LX04 China-to-Global conversion.

---

## 1. Application Identification & Specifications

- **Application Name:** Google Android SDK Platform-Tools
- **Binaries:** `fastboot.exe` and `adb.exe`
- **Verified Versions:**
  - Fastboot: `fastboot version 302830efc153-android` (Platform-Tools release 34.0.5+)
  - ADB: `Android Debug Bridge version 1.0.40` (Version `4797878`)
- **Developer / Vendor:** Google LLC
- **License:** Apache License 2.0
- **Official Download Source:** [https://developer.android.com/tools/releases/platform-tools](https://developer.android.com/tools/releases/platform-tools)
- **Direct Official Package:** [https://dl.google.com/android/repository/platform-tools-latest-windows.zip](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
- **Tested Environment:** Windows 10 / Windows 11 (64-bit)

---

## 2. Role & Purpose in the LX04 Conversion

Fastboot and ADB perform the core operating system flashing and configuration tasks once Little Kernel is booted:

1. **Bootloader Unlocking (`fastboot oem unlock`):** After the de-masked `frpx` GPT is flashed, Fastboot initiates the OEM unlock handshake, displaying the confirmation dialog on the 800x480 LCD panel and recording the unlock token in `seccfg`.
2. **Device State Auditing (`fastboot getvar all`):** Queries Little Kernel for boot status, AVB lock state (`unlocked: yes`), product identifier (`mico_x04g`), and partition table definitions.
3. **Flashing Android Verified Boot (AVB) Bootstack:** Flashes `boot.bin`, `recovery.bin`, `dtbo.bin`, `vbmeta.bin`, `vbmeta_system.bin`, and `vbmeta_vendor.bin`.
4. **Flashing System Parameter Partitions:** Flashes `cache.bin`, `metadata.bin`, `md_udc.bin`, and `para.bin`.
5. **Erasing Corrupted User Data (`fastboot erase userdata`):** Clears residual Chinese encrypted userdata so Global Recovery can initialize a clean ext4 filesystem.
6. **Post-Boot Device Validation (ADB):** Queries Android runtime properties (`adb shell getprop`) to confirm Global build fingerprint, Wi-Fi MAC preservation, and audio HAL initialization.

---

## 3. Installation & PATH Setup Instructions

1. Download `platform-tools-latest-windows.zip` from Google's official developer portal:
   [https://dl.google.com/android/repository/platform-tools-latest-windows.zip](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
2. Extract the archive into a permanent directory, e.g. `C:\platform-tools\`.
3. Add `C:\platform-tools\` to your Windows System Environment `PATH`:
   - Press `Win + R`, type `sysdm.cpl`, and press **Enter**.
   - Navigate to the **Advanced** tab -> click **Environment Variables**.
   - Under **System variables**, select `Path` -> click **Edit**.
   - Click **New** -> add `C:\platform-tools\` -> click **OK**.
4. Open a new PowerShell terminal and verify:
   ```powershell
   fastboot --version
   adb version
   ```

---

## 4. Hardware Driver Binding (Fastboot Mode)

When the clock enters Fastboot mode via our interceptor script (`scripts/fastboot/preloader_fastboot_interceptor.py`), Windows must bind the Android Bootloader Interface driver:

1. Connect the clock in Fastboot mode.
2. Open Windows **Device Manager** (`devmgmt.msc`).
3. Under "Other devices", locate `Android` or `mico_x04g` with a yellow exclamation mark.
4. Right-click -> **Update driver** -> **Browse my computer for drivers**.
5. Select **Let me pick from a list of available drivers on my computer**.
6. Select category: **Android Device** -> Manufacturer: **Google, Inc.** -> Model: **Android Bootloader Interface**.
7. Click **Next** and accept the installation prompt.
8. Verify in PowerShell:
   ```powershell
   fastboot devices
   ```
   *Expected output: `<SERIAL_NUMBER>   fastboot`.*

---

## 5. Automated vs. Manual Flashing Commands

### Automated Script (Recommended)
Our automated script performs pre-flight device checks, verifies unlock state, and flashes the full bootstack safely:
```powershell
python scripts/fastboot/flash_global_bootstack.py
```

### Manual Command Sequence
If executing manually in PowerShell:
```powershell
# 1. Verify unlock state
fastboot getvar unlocked

# 2. Flash AVB bootchain
fastboot flash boot firmware/boot.bin
fastboot flash recovery firmware/recovery.bin
fastboot flash dtbo firmware/dtbo.bin
fastboot flash vbmeta firmware/vbmeta.bin
fastboot flash vbmeta_system firmware/vbmeta_system.bin
fastboot flash vbmeta_vendor firmware/vbmeta_vendor.bin

# 3. Flash system parameter partitions
fastboot flash cache firmware/cache.bin
fastboot flash metadata firmware/metadata.bin
fastboot flash md_udc firmware/md_udc.bin
fastboot flash para firmware/para.bin

# 4. Erase encrypted userdata
fastboot erase userdata

# 5. Reboot to bootloader for final SP Flash Tool super write
fastboot reboot-bootloader
```

---

## 6. Critical Safety Warnings & Traps

> [!CAUTION]
> **FATAL DEFECT: NEVER FLASH `super.bin` VIA FASTBOOT!**
>
> Little Kernel on the MediaTek MT8167A contains a critical write-offset defect in routine `cmd_flash` (`0x4e1b273a`). Because `super.bin` is 1.50 GB and exceeds Fastboot's maximum chunk buffer (`max-download-size: 0x8000000` / 128 MB), Fastboot attempts client-side chunking.
>
> On each chunk, Little Kernel **resets the write pointer back to physical offset `0x00000000` of `super`**, repeatedly overwriting the filesystem superblock with later chunks.
>
> Flashing `super.bin` via Fastboot produces an unbootable dynamic container and causes bootloops into Recovery. **`super.bin` must ALWAYS be flashed contiguously via SP Flash Tool.**
