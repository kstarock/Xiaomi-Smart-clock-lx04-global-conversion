# Global Firmware Package: Xiaomi Smart Clock X04G (Android 10 / Build 1.7.5)

This directory defines the exact official Global firmware package utilized in our successful Xiaomi Smart Clock LX04 China-to-Global conversion.

---

## 1. Target Firmware Specifications

- **Device Name:** Xiaomi Smart Clock (International Global Variant)
- **Model Number:** `X04G`
- **Motherboard / Platform:** `mico_x04g`
- **SoC:** MediaTek MT8167A (Quad-core ARM Cortex-A35 @ 1.3 GHz)
- **Target Storage:** Kingston 4GB eMMC 5.1 (`M62704`, exactly `7,405,568` sectors)
- **Android OS Version:** Android 10
- **Build Number:** `1.7.5`
- **Build ID:** `QP1A.190711.020`
- **Build Fingerprint:** `xiaomi/mico_x04g/mico_x04g:10/QP1A.190711.020/1.7.5:user/release-keys`
- **Little Kernel Bootloader Version:** `mico_x04g-451d69f-20210619014509-202112`
- **Preloader Version:** `0.1.00`

---

## 2. Firmware Provenance & Legal Redistribution Notice

> [!IMPORTANT]
> **Copyright & Legal Redistribution Notice:**
> The Global Android 10 firmware images for model X04G contain proprietary, copyrighted intellectual property owned by **Xiaomi Inc.** (MIUI/XiaoAI system frameworks and apps), **MediaTek Inc.** (BROM/Preloader EMI calibration, DSP binaries, HAL libraries, bootloader), and **Google LLC** (Google Mobile Services, Google Assistant prebuilts).
>
> Neither Xiaomi nor MediaTek grant public open-source redistribution licenses for complete stock firmware packages or raw partition dumps. **Consequently, this repository does NOT host or distribute raw proprietary firmware binaries.**
>
> To convert your device, you must independently obtain the verified firmware package from authorized or community sources and verify its SHA-256 integrity against the manifest below.

### Archive Provenance Evidence
- **Confirmed Source Archive:** `dump_mico_x04g.tar.xz` (Archive size: `857,491,844` bytes, SHA-256: `9ffd2a4b1b66d7f1ae0496b5e7e2f4db3e1d14cad74d03802f1df30d64dde214`).
  - This is the exact, verified archive file present in project evidence.
  - Extracted extraction directory: `LX04-Global-Candidate` on the conversion workstation.
  - Contains all 13 mandatory and 3 optional partition binaries, plus an internal `sha256sums.txt` manifest whose digests match our physical extractions bit-for-bit.
- **Reported OEM Archive Name:** `x04g_global_images_1.7.5_20210324.0000.00_10.0_global_8cf90dc97b.tgz`.
  - Status in project evidence: **[UNVERIFIED / UNCONFIRMED]**. This archive filename is reported in community documentation and official release channels, but was not the physical file extracted during conversion.
- **Full eMMC Raw Image Reference:** `full_flash/flash_mico_x04g.img` (`3,959,422,976` bytes, SHA-256: `80353837682340fea64413079c5f320e39432c012649e72aecc2509a9fec303e`).

---

## 3. Mandatory Component Inventory (13 Files)

The conversion procedure requires exactly these 13 binary images extracted from the Global package. Each image has been verified against the physical archive and matches the exact byte size and SHA-256 cryptographic hash:

| File Name | Size (Bytes) | SHA-256 Cryptographic Checksum | Target Partition | Flashing Engine | Role | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`preloader_mico_x04g.bin`** | 169,132 | `84f621317857a28f5566919c3e0770004ecba4f1583a12477b129a2fee3aa530` | eMMC `BOOT1` @ `0x800` | SP Flash Tool | MediaTek DRAM EMI timings & initial boot | **[VERIFIED]** |
| **`lk.bin`** | 524,288 | `79150412079402b321f1e7f2128da273d159dbc569557261bfc8ce663f1427fd` | `lk` & `lk2` | SP Flash Tool | Global Little Kernel v2.0 secondary bootloader | **[VERIFIED]** |
| **`boot.bin`** | 16,777,216 | `ca7719a8a9407b4d47dfeb5a15b6ab810b43f4de41ff43c0bf265b2ecfcd3d4d` | `boot` | Fastboot CLI | Global Android 10 Linux kernel & ramdisk | **[VERIFIED]** |
| **`recovery.bin`** | 16,777,216 | `ac475a12ddfd6c4ebab0bd91fa4401dee8e188de1a77bcae1d7d04be99aa5a2c` | `recovery` | Fastboot CLI | Global Android Recovery console | **[VERIFIED]** |
| **`dtbo.bin`** | 1,048,576 | `487141aa53a275f0bae74199c6ac70e49a0a78a8c15fbeb4af5a26a2de0b25a3` | `dtbo` | Fastboot CLI | Device Tree Blob Overlay (display/touch) | **[VERIFIED]** |
| **`vbmeta.bin`** | 4,194,304 | `1bb93a61c5da5473afe296e4270a9b20c13fbba16539f812a38e72f5fdb8517c` | `vbmeta` | Fastboot CLI | Android Verified Boot (AVB) 2.0 root descriptor | **[VERIFIED]** |
| **`vbmeta_system.bin`** | 4,194,304 | `affa5a3c0cdd084d1c9a9e2ef6c647d2434eef4e3a025b780f03eef28af3cebb` | `vbmeta_system` | Fastboot CLI | AVB 2.0 system chain verification descriptor | **[VERIFIED]** |
| **`vbmeta_vendor.bin`** | 4,194,304 | `532d22f3f651378abf1c20a21c412580fdd6872813e852f8f4a1b9da64709b49` | `vbmeta_vendor` | Fastboot CLI | AVB 2.0 vendor chain verification descriptor | **[VERIFIED]** |
| **`super.bin`** | 1,610,612,736 | `271127b4d3a901b0a3c8ad6f08de6c915a39a0da7ad4f5d4ddf05548f8f3aca7` | `super` | **SP Flash Tool ONLY** | Android 10 dynamic partitions container | **[VERIFIED]** |
| **`cache.bin`** | 134,217,728 | `698f588753f51889cb5e6171f36d5948db4658167cd51dd479222fa874af6382` | `cache` | Fastboot CLI | Clean cache ext4 filesystem image | **[VERIFIED]** |
| **`metadata.bin`** | 34,603,008 | `c28a8f34a7efbd4cffe424a21e4a6e4d5bfa8b5daccc381f9eb3c1dc5bac689c` | `metadata` | Fastboot CLI | Dynamic partitions metadata & encryption state | **[VERIFIED]** |
| **`md_udc.bin`** | 23,068,672 | `1acd2908bee471b61904d1c97f75409da8acad36bf3d79874144d32f67ade3b9` | `md_udc` | Fastboot CLI | Wireless subsystem / modem operational data | **[VERIFIED]** |
| **`para.bin`** | 524,288 | `d4c4991789c700d33978f51542a354dbdac63c653316517ebd8791765d90b3a5` | `para` | Fastboot CLI | MISC bootloader message parameter block | **[VERIFIED]** |

---

## 4. Optional Components & TEE Hash Identity Analysis

| File Name | Size (Bytes) | SHA-256 Checksum | Target Partition | Role | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`logo.bin`** | 8,388,608 | `82ecd4ac0ca574f00b99494fdb782e5e047e273eb9930f6a9a007fe5214aca6d` | `logo` | Global boot splash & battery icons | **[VERIFIED]** |
| **`tee1.bin`** | 5,242,880 | `f9848a2d060d5672a11b5f0acd5d037a1ca08acc9f9d6556ed8c9fe29700a309` | `tee1` | Primary Trusted Execution Environment | **[VERIFIED]** |
| **`tee2.bin`** | 5,242,880 | `f9848a2d060d5672a11b5f0acd5d037a1ca08acc9f9d6556ed8c9fe29700a309` | `tee2` | Redundant TEE backup | **[VERIFIED]** |

### Why `tee1.bin` and `tee2.bin` Have Identical Checksums
In MediaTek MT8167 architectures, `tee1` (Primary slot) and `tee2` (Secondary fallback slot) are mirrored redundant partitions designed to ensure TEE resilience against corrupt flash writes. The OEM firmware build system packages the exact same signed Trusty OS binary payload for both targets:
1. Direct extraction of `dump_mico_x04g.tar.xz` reveals that `tee1.bin` and `tee2.bin` have identical byte counts (`5,242,880` bytes) and identical SHA-256 digests (`f9848a2d060d5672a11b5f0acd5d037a1ca08acc9f9d6556ed8c9fe29700a309`).
2. This mirroring pattern is standard across MediaTek firmware packages: `lk.bin` and `lk2.bin` also share the identical hash (`79150412079402b3...`), as do `kb.bin` and `dkb.bin` (`5647f05ec1895894...`).
3. **Important Preservation Note:** During our successful conversion, neither `tee1` nor `tee2` from the Global package was flashed to the device. As documented in the partition preservation audit, the original factory Chinese `tee1`, `tee2`, `kb`, and `dkb` partitions were preserved untouched on eMMC to maintain hardware security binding.

---

## 5. Extraction & Placement Procedure

1. Obtain the verified archive (`dump_mico_x04g.tar.xz`).
2. Extract the files directly into the repository root `firmware/` directory:
   ```powershell
   # Windows PowerShell using native tar:
   tar -xf dump_mico_x04g.tar.xz -C firmware/
   ```
3. Run the automated hash validator to ensure 100% bit-exact compliance:
   ```powershell
   python scripts/verification/verify_checksums.py
   ```
4. Confirm all 13 required images report `[PASS]`. Do not attempt to flash if any checksum fails.
