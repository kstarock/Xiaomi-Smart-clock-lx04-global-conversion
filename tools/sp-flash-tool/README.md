# SP Flash Tool Setup & Operation Guide

This guide documents the setup, configuration, and operational parameters for **MediaTek Smart Phone Flash Tool (SP Flash Tool)**, the primary low-level flashing engine used in the Xiaomi Smart Clock LX04 China-to-Global conversion.

---

## 1. Application Identification & Specifications

- **Application Name:** MediaTek Smart Phone Flash Tool (SP Flash Tool)
- **Verified Host Binary:** `v5.1728.00` (Win32, `_SPFT.exe`, 10,326,528 bytes, SHA-256: `611180fbcfe6dca1ca44a494d4ee0fe0a421a9839782bf92c7e9703b63e79ad9`)
- **Compatible Versions:** `v5.1812.00` / `v5.1728.00` (Both versions share the identical MT8167 engine and XML configuration parser)
- **Executable File:** `_SPFT.exe` / `flash_tool.exe`
- **Developer / Vendor:** MediaTek Inc.
- **License:** Proprietary (Freeware for MediaTek device maintenance)
- **Official Download Source:** [https://spflashtool.com/download](https://spflashtool.com/download)
- **Tested Environment:** Windows 10 / Windows 11 (64-bit)

---

## 2. Role & Purpose in the LX04 Conversion

SP Flash Tool performs four critical functions that cannot be executed safely via standard Fastboot:

1. **Pre-Conversion Calibration Readback:** Directly reads physical eMMC byte ranges over USB to create pristine offline binary backups of `proinfo` (`0x00080000`), `nvram` (`0x00380000`), and `BOOT1` (`0x00000000`).
2. **GPT Partition Table Migration:** Flashes synthesized primary and secondary GUID Partition Tables (`pgpt` and `sgpt`) directly to eMMC sectors 0–33 and 7,405,535–7,405,567.
3. **Contiguous `super.bin` Streaming:** Streams the 1.50 GB dynamic partitions container directly to physical sectors in one contiguous transfer at ~19.77 MB/s. This **bypasses the fatal Little Kernel Fastboot multi-chunk bug** that overwrites sector 0 on chunked transfers.
4. **Bootchain Initialization:** Flashes Global Little Kernel (`lk.bin`, `lk2.bin`) and writes the Global Preloader (`preloader_mico_x04g.bin`) to eMMC `BOOT1` at offset `0x800`.

---

## 3. Required Companion Files

Due to hardware cryptographic enforcement on the MediaTek MT8167A, stock generic MediaTek Download Agents will be rejected with `STATUS_DA_HASH_MISMATCH (0xC0070004)`. You must supply authentic OEM-signed binaries:

| File Name | Required Size (Bytes) | SHA-256 Checksum | Description |
| :--- | :--- | :--- | :--- |
| **`DA_Mi_Hikaru-resign.bin`** | 492,460 | `1832cb312efdde35634ccf0a100131ac4c182ef9bd22e51c35a0685f9ab3e880` | Authentic Xiaomi OEM-signed Download Agent Stage 1 & Stage 2 |
| **`auth_sv5.auth`** | 2,256 | `84a89c4e7acd004afef3cd9c775980164ecd735c8aaa8566c58cb574eeee9b3e` | SLA cryptographic handshake response token |

*Note: These files originate from vendor maintenance packages and are not committed to this repository. Place them in your working tool folder.*

---

## 4. Installation & Setup Instructions

1. Download an official SP Flash Tool v5 package (such as `SP_Flash_Tool_v5.1812_Win.zip` or v5.1728) from [https://spflashtool.com/download](https://spflashtool.com/download).
2. Extract the archive into a dedicated directory without spaces in the path (e.g., `C:\Tools\SP_Flash_Tool\`).
3. Place `DA_Mi_Hikaru-resign.bin` and `auth_sv5.auth` inside your SP Flash Tool directory.
4. Right-click `_SPFT.exe` (or `flash_tool.exe`) -> **Properties** -> **Compatibility** -> Check **Run this program as an administrator**.

---

## 5. LX04 Configuration Rules

In SP Flash Tool GUI:

1. **Download-Agent:** Click **Choose** and select `DA_Mi_Hikaru-resign.bin`.
2. **Scatter-loading File:** Click **Choose** and select `configurations/scatter/convert_scatter_global.txt`.
3. **Authentication File:** Click **Choose** and select `auth_sv5.auth`.
4. **Flashing Mode Dropdown:** **ALWAYS set to `Download Only`**.
5. **Loading Pre-Configured XML Profiles:**
   - For Step 2 (Unlock): Open **File** -> **Open XML File...** -> select `configurations/spft/download_gpt_unlock.xml`.
   - For Step 6 (Contiguous Super): Open **File** -> **Open XML File...** -> select `configurations/spft/download_super_contiguous.xml`.
   - For Step 7 (Restore): Open **File** -> **Open XML File...** -> select `configurations/spft/download_gpt_restore.xml`.

---

## 6. How to Verify Working Operation

1. Launch `_SPFT.exe`. Click **Help** -> **About** -> Verify version reports `v5.1812.00.000`.
2. Switch to the **Readback** tab.
3. Click **Add** -> double-click row -> save as `test_proinfo.bin` -> set **Hex** Start Address: `0x00080000`, Length: `0x00300000`.
4. Click **Read Back** (blue circle icon).
5. Plug in the clock's Micro-USB cable to the PC.
6. The progress bar will advance (Red DA download -> Blue readback transfer) and finish with a large green circle **OK**.
7. Open `test_proinfo.bin` in a hex editor: bytes 0–31 must display your device's ASCII serial barcode text.

---

## 7. Critical Safety Warnings & Traps

> [!CAUTION]
> 1. **NEVER use `Format All + Download` or `Firmware Upgrade`:**
>    Selecting these options formats the entire eMMC storage, permanently erasing `proinfo` (`0x00080000`) and `nvram` (`0x00380000`). This completely destroys factory RF calibration tables, Wi-Fi MAC addresses, and motherboard serial numbers, rendering Wi-Fi permanently inoperable.
>
> 2. **Address Units in SP Flash Tool v5.1812:**
>    The Readback and Write Memory tabs operate in **HEXADECIMAL BYTE OFFSETS**, NOT LBA sector numbers. Entering sector counts (such as `0xC000` or `0x28000`) will read or write unpartitioned zero-space. Always verify full 32-bit hex addresses (e.g. `0x00080000`).
