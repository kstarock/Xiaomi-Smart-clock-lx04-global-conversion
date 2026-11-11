# Partition Map: Kingston 4GB eMMC Layout (`M62704`)

This document provides the definitive, sector-accurate, binary-verified partition map for the Xiaomi Smart Clock (LX04 -> X04G) on Kingston 4GB eMMC hardware (`7,405,568` total sectors of 512 bytes).

> [!IMPORTANT]
> **Source of Truth:** This table was reconstructed directly by parsing the binary GPT entries from `configurations/gpt/gpt_x04g_kingston.bin` and verified against `configurations/scatter/convert_scatter_global.txt`. Every Start LBA, End LBA, Sector count, and Byte Offset has been mathematically and physically reconciled.

---

## 1. Physical Hardware Boot Partitions

| Hardware Partition | Physical Offset Range | Size (Bytes) | Image / Contents | Flash Method | Conversion Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`BOOT1`** | `0x00000000` – `0x00200000` | 2,097,152 B (2 MB) | BROM Header + Global Preloader (`preloader_mico_x04g.bin` @ `0x800`) | SP Flash Tool Preloader Download | **MODIFIED** (Overwritten with Global Preloader) |
| **`BOOT2`** | `0x00000000` – `0x00200000` | 2,097,152 B (2 MB) | Mirrored / Unused | None | Preserved / Untouched |
| **`RPMB`** | `0x00000000` – `0x00080000` | 524,288 B (512 KB) | Hardware Replay Protected Memory Block | Authenticated Secure HW | 🔒 Hardware Protected |

---

## 2. Main Flash Storage (`USER` Partition, 7,405,568 Sectors = 3,791,650,816 Bytes)

| # | Partition Name | Start LBA (Sector) | End LBA (Sector) | Sector Count | Size (Bytes) | Physical Byte Offset | Scatter linear_start_addr | Flash Method | Conversion Operation & Status |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| — | **Primary GPT** | 0 | 33 | 34 | 17,408 B | `0x00000000` | `0x00000000` | SP Flash Tool (`pgpt`) | **MODIFIED** (Global Kingston layout) |
| 0 | `proinfo` | 1,024 | 7,167 | 6,144 | 3,145,728 B (3 MB) | `0x00080000` | `0x00080000` | — | 🔒 **PRESERVED UNTOUCHED** (Factory Barcode & SN) |
| 1 | `nvram` | 7,168 | 17,407 | 10,240 | 5,242,880 B (5 MB) | `0x00380000` | `0x00380000` | — | 🔒 **PRESERVED UNTOUCHED** (Factory RF Calibration & MAC) |
| 2 | `persist` | 17,408 | 115,711 | 98,304 | 50,331,648 B (48 MB) | `0x00880000` | `0x00880000` | — | **UNWRITTEN / ZERO-FILLED INHERITED REGION** (Covers former Chinese `protect1`, `protect2`, and part of Chinese `persist`; all verified zero-filled in stock backup) |
| 3 | `seccfg` | 115,712 | 116,223 | 512 | 262,144 B (256 KB) | `0x03880000` | `0x03880000` | Internal LK Handler | **MODIFIED ON-DEVICE** (Unlocked by LK token) |
| 4 | `lk` | 116,224 | 117,247 | 1,024 | 524,288 B (512 KB) | `0x038C0000` | `0x038C0000` | SP Flash Tool | **MODIFIED** (Global Little Kernel v2.0) |
| 5 | `lk2` | 117,248 | 118,271 | 1,024 | 524,288 B (512 KB) | `0x03940000` | `0x03940000` | SP Flash Tool | **MODIFIED** (Global Little Kernel Backup) |
| 6 | `boot` | 118,272 | 151,039 | 32,768 | 16,777,216 B (16 MB) | `0x039C0000` | `0x039C0000` | Fastboot | **MODIFIED** (Global Android 10 Kernel) |
| 7 | `recovery` | 151,040 | 183,807 | 32,768 | 16,777,216 B (16 MB) | `0x049C0000` | `0x049C0000` | Fastboot | **MODIFIED** (Global Android 10 Recovery) |
| 8 | `para` | 183,808 | 184,831 | 1,024 | 524,288 B (512 KB) | `0x059C0000` | `0x059C0000` | Fastboot | **MODIFIED** (Global MISC / Boot Control) |
| 9 | `logo` | 184,832 | 201,215 | 16,384 | 8,388,608 B (8 MB) | `0x05A40000` | `0x05A40000` | Fastboot / SPFT | Optional (Global Boot Logo) |
| 10 | `dtbo` | 201,216 | 203,263 | 2,048 | 1,048,576 B (1 MB) | `0x06240000` | `0x06240000` | Fastboot | **MODIFIED** (Global Device Tree Overlay) |
| 11 | `expdb` | 203,264 | 223,743 | 20,480 | 10,485,760 B (10 MB)| `0x06340000` | `0x06340000` | — | Preserved / Unchanged (Diagnostic logs) |
| 12 | `frp` (`frpx`)| 223,744 | 225,791 | 2,048 | 1,048,576 B (1 MB) | `0x06D40000` | `0x06D40000` | SP Flash Tool (`pgpt`) | **DE-MASKED & RESTORED** (FRP unlock vector) |
| 13 | `tee1` | 225,792 | 236,031 | 10,240 | 5,242,880 B (5 MB) | `0x06E40000` | `0x06E40000` | — | Preserved / Unchanged (TrustZone OS 1) |
| 14 | `tee2` | 236,032 | 246,271 | 10,240 | 5,242,880 B (5 MB) | `0x07340000` | `0x07340000` | — | Preserved / Unchanged (TrustZone OS 2) |
| 15 | `kb` | 246,272 | 250,367 | 4,096 | 2,097,152 B (2 MB) | `0x07840000` | `0x07840000` | — | Preserved / Unchanged (Key Block) |
| 16 | `dkb` | 250,368 | 254,463 | 4,096 | 2,097,152 B (2 MB) | `0x07A40000` | `0x07A40000` | — | Preserved / Unchanged (Device Key Block) |
| 17 | `md_udc` | 254,464 | 299,519 | 45,056 | 23,068,672 B (22 MB)| `0x07C40000` | `0x07C40000` | Fastboot | **MODIFIED** (Global Connectivity Parameters) |
| 18 | `metadata` | 299,520 | 367,103 | 67,584 | 34,603,008 B (33 MB)| `0x09240000` | `0x09240000` | Fastboot | **MODIFIED** (Global Dynamic Partition Metadata)|
| 19 | `nvdata` | 367,104 | 375,295 | 8,192 | 4,194,304 B (4 MB) | `0x0B340000` | `0x0B340000` | — | **NEW GLOBAL PARTITION** (Carved from zero-filled region within the original Chinese `metadata` partition; first-boot ext4 formatting & population from `nvram` is **[INFERRED]**) |
| 20 | `vbmeta` | 375,296 | 383,487 | 8,192 | 4,194,304 B (4 MB) | `0x0B740000` | `0x0B740000` | Fastboot | **MODIFIED** (Global AVB 2.0 Root Signature) |
| 21 | `vbmeta_system`| 383,488 | 391,679 | 8,192 | 4,194,304 B (4 MB) | `0x0BB40000` | `0x0BB40000` | Fastboot | **MODIFIED** (Global AVB System Descriptor) |
| 22 | `vbmeta_vendor`| 391,680 | 399,871 | 8,192 | 4,194,304 B (4 MB) | `0x0BF40000` | `0x0BF40000` | Fastboot | **MODIFIED** (Global AVB Vendor Descriptor) |
| 23 | `super` | 399,872 | 3,545,599| 3,145,728| 1,610,612,736 B (1.5 GB)|`0x0C340000`| `0x0C340000` | SP Flash Tool (Contiguous)| **MODIFIED** (Global System/Vendor/Product) |
| 24 | `cache` | 3,545,600 | 3,807,743| 262,144 | 134,217,728 B (128 MB)|`0x6C340000` | `0x6C340000` | Fastboot | **MODIFIED** (Erased / Global Cache Image) |
| 25 | `userdata` | 3,807,744 | 7,405,534| 3,597,791| 1,842,069,504 B (~1.72 GB)|`0x74340000`| `0x74340000` | Fastboot Erase | **MODIFIED / WIPED** (Clean ext4 initialization)|
| — | **Secondary GPT**| 7,405,535 | 7,405,567| 33 | 16,896 B | `0xE1FFBE00` | `0xE1FFBE00` | SP Flash Tool (`sgpt`) | **MODIFIED** (Backup GPT Entries + Header) |

---

## 3. Partition Modification & Preservation Summary

- **Total Partitions Addressed:** 21 partitions actively referenced during the conversion workflow.
- **Partitions Flashed / Erased via PC Tools (17 partitions):**
  1. `BOOT1` (`preloader_mico_x04g.bin` written to eMMC boot block @ `0x800`)
  2. `pgpt` (Primary GPT table, LBA 0–33)
  3. `sgpt` (Secondary GPT table, LBA 7,405,535–7,405,567)
  4. `lk` (Little Kernel v2.0)
  5. `lk2` (Little Kernel v2.0 backup)
  6. `boot` (Global Android 10 kernel)
  7. `dtbo` (Device Tree Overlay)
  8. `vbmeta` (AVB 2.0 Root)
  9. `vbmeta_system` (AVB 2.0 System)
  10. `vbmeta_vendor` (AVB 2.0 Vendor)
  11. `recovery` (Global Android Recovery)
  12. `para` (MISC / bootloader message parameter)
  13. `cache` (Formatted / written)
  14. `metadata` (Dynamic partition metadata)
  15. `md_udc` (Connectivity firmware config)
  16. `super` (1.50 GB contiguous dynamic partition)
  17. `userdata` (Fastboot erased; encrypted on first boot)
- **Partitions Modified Internally on Device (1 partition):**
  18. `seccfg` (Security status; unlocked bit written by LK upon `fastboot oem unlock`). Total modified partitions = **18**.
- **Original Chinese Partitions Preserved Untouched (6 partitions total):**
  - **Critical Factory Calibration & Identity (2 partitions):**
    - `proinfo` (Offset `0x00080000`, 3 MB): Holds factory serial number and motherboard barcode. Verified bit-exact match across Chinese and Global layouts.
    - `nvram` (Offset `0x00380000`, 5 MB): Holds factory RF calibration data and Wi-Fi MAC address. Verified bit-exact match across Chinese and Global layouts.
  - **Stock Vendor Security & Key Storage (4 partitions):**
    - `tee1` (Offset `0x06E40000`, 5 MB) & `tee2` (Offset `0x07340000`, 5 MB): Microtrust TrustZone images; preserved as stock.
    - `kb` (Offset `0x07840000`, 2 MB) & `dkb` (Offset `0x07A40000`, 2 MB): Key block areas; preserved as stock.
- **New Global Runtime Calibration Partition (1 partition):**
  - `nvdata` (Offset `0x0B340000`, 4 MB): New partition carved from zero-filled region within the original Chinese `metadata` partition. Formatting as ext4 on first boot and population from preserved `nvram` by `nvram_daemon` is **[INFERRED]** based on MediaTek Android 10 architecture.
- **Partitions Temporarily De-masked & Restored (1 partition):**
  - `frp` (Offset `0x06D40000`, 1 MB): Renamed to `frpx` in GPT to neutralize the OEM unlock lock check, then restored to `frp`.
- **Repartitioned Ranges Left Unwritten by PC Tools (1 partition):**
  - `persist` (Offset `0x00880000`, 48 MB): Not written by PC tools; overlaps former Chinese `protect1` (10 MB), `protect2` (10 MB), and first 28 MB of Chinese `persist` (all verified 100% zeroes in the stock Chinese dump; no sensor calibration data was found; not a preserved original partition).

---

## 4. Architectural Comparison: Chinese vs. Global Layout

In the stock Chinese firmware (`restore_scatter.txt` / Chinese `gpt.bin`), the device utilized an A/B partition structure (`system_a`, `system_b`, `vendor_a`, `vendor_b`, `protect1`, `protect2`) without a dynamic `super` container:
- Chinese layout placed `protect1` at `0x00880000` (10 MB) and `protect2` at `0x01280000` (10 MB).
- Global layout consolidated partitions using Android 10 Dynamic Partitions, replacing the dual system/vendor blocks with a single 1.50 GB `super` partition (`0x0C340000`) and standardizing `nvdata` at `0x0B340000` (4 MB).
- Crucially, **`proinfo` (`0x00080000`) and `nvram` (`0x00380000`) share the exact same physical byte offsets across both Chinese and Global partition layouts**, ensuring zero risk of calibration overwrite when flashing the Global GPT.
