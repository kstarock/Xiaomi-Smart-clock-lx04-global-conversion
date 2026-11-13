# Firmware Acquisition & Directory Placement Guide

To comply with copyright laws and software distribution licensing, **this repository does not host or distribute proprietary Xiaomi or MediaTek firmware binaries**.

Users must acquire official firmware images independently and place them into this `firmware/` directory before proceeding.

---

## 1. Directory Structure & Quick Links

- [**Global X04G Build 1.7.5 Detailed Guide & Component Map**](global-x04g/README.md)
- [**Global X04G Checksum Manifest**](global-x04g/SHA256SUMS.txt)
- [**Machine-Readable Firmware Manifest**](firmware_manifest.json)

---

## 2. Required Firmware Archive
- **Confirmed Source Archive:** `dump_mico_x04g.tar.xz` (Archive size: `857,491,844` bytes, SHA-256: `9ffd2a4b1b66d7f1ae0496b5e7e2f4db3e1d14cad74d03802f1df30d64dde214`). This is the exact archive verified in project evidence.
- **Reported OEM Archive:** `x04g_global_images_1.7.5_20210324.0000.00_10.0_global_8cf90dc97b.tgz` (Reported OEM package name; unverified in project files).
- **Target Firmware Build:** Xiaomi Global Smart Clock Build `10/QP1A.190711.020/1.7.5 user/release-keys`.
- **Extraction Command (PowerShell):**
  ```powershell
  # Using the verified source archive:
  tar -xf dump_mico_x04g.tar.xz -C firmware/
  ```

---

## 3. Mandatory vs. Optional Firmware Components

### 3.1 Mandatory Components (Required for Successful Boot)
Place the following extracted images directly into this `firmware/` directory and verify them using `python scripts/verification/verify_checksums.py`:

| File Name | Required Size (Bytes) | SHA-256 Checksum | Partition Destination | Role |
| :--- | :--- | :--- | :--- | :--- |
| `preloader_mico_x04g.bin` | 169,132 | `84f621317857a28f5566919c3e0770004ecba4f1583a12477b129a2fee3aa530` | eMMC `BOOT1` @ `0x800` | DRAM EMI timings & boot |
| `lk.bin` | 524,288 | `79150412079402b321f1e7f2128da273d159dbc569557261bfc8ce663f1427fd` | `lk` & `lk2` | Global Little Kernel v2.0 |
| `boot.bin` | 16,777,216 | `ca7719a8a9407b4d47dfeb5a15b6ab810b43f4de41ff43c0bf265b2ecfcd3d4d` | `boot` | Global Android 10 Kernel |
| `recovery.bin` | 16,777,216 | `ac475a12ddfd6c4ebab0bd91fa4401dee8e188de1a77bcae1d7d04be99aa5a2c` | `recovery` | Global Android Recovery |
| `dtbo.bin` | 1,048,576 | `487141aa53a275f0bae74199c6ac70e49a0a78a8c15fbeb4af5a26a2de0b25a3` | `dtbo` | Device Tree Blob Overlay |
| `vbmeta.bin` | 4,194,304 | `1bb93a61c5da5473afe296e4270a9b20c13fbba16539f812a38e72f5fdb8517c` | `vbmeta` | AVB 2.0 Root Signature |
| `vbmeta_system.bin` | 4,194,304 | `affa5a3c0cdd084d1c9a9e2ef6c647d2434eef4e3a025b780f03eef28af3cebb` | `vbmeta_system` | AVB System Descriptor |
| `vbmeta_vendor.bin` | 4,194,304 | `532d22f3f651378abf1c20a21c412580fdd6872813e852f8f4a1b9da64709b49` | `vbmeta_vendor` | AVB Vendor Descriptor |
| `super.bin` | 1,610,612,736 | `271127b4d3a901b0a3c8ad6f08de6c915a39a0da7ad4f5d4ddf05548f8f3aca7` | `super` | Dynamic Partitions Container |
| `cache.bin` | 134,217,728 | `698f588753f51889cb5e6171f36d5948db4658167cd51dd479222fa874af6382` | `cache` | Cache Filesystem |
| `metadata.bin` | 34,603,008 | `c28a8f34a7efbd4cffe424a21e4a6e4d5bfa8b5daccc381f9eb3c1dc5bac689c` | `metadata` | Dynamic Partition State |
| `md_udc.bin` | 23,068,672 | `1acd2908bee471b61904d1c97f75409da8acad36bf3d79874144d32f67ade3b9` | `md_udc` | Modem / Connectivity UDC |
| `para.bin` | 524,288 | `d4c4991789c700d33978f51542a354dbdac63c653316517ebd8791765d90b3a5` | `para` | Bootloader Message State |

### 3.2 Optional Components
These images are present in full firmware dumps but are not strictly mandatory to establish the initial bootable Android 10 state:
- `logo.bin` (8,388,608 bytes, SHA-256: `82ecd4ac0ca574f00b99494fdb782e5e047e273eb9930f6a9a007fe5214aca6d`): Global splash logo.
- `tee1.bin` / `tee2.bin` (5,242,880 bytes each, SHA-256: `f9848a2d060d5672a11b5f0acd5d037a1ca08acc9f9d6556ed8c9fe29700a309`): Microtrust Trusted Execution Environment binaries.

---

## 4. Tool Authentication Binaries (Separately Supplied)
For SP Flash Tool to communicate with the MediaTek MT8167 BROM on secure Xiaomi hardware:
- `DA_Mi_Hikaru-resign.bin` (SHA-256: `1832cb312efdde35634ccf0a100131ac4c182ef9bd22e51c35a0685f9ab3e880`): Download Agent Stage 1 & 2 signed by OEM.
- `auth_sv5.auth` (SHA-256: `84a89c4e7acd004afef3cd9c775980164ecd735c8aaa8566c58cb574eeee9b3e`): Authentication certificate.

*Legal Notice:* Because these files originate from vendor engineering packages, users must provide their own verified copies and place them in the `tools/` folder. Do not redistribute unauthorized mirrors.
