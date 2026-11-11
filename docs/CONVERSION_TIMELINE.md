# CONVERSION TIMELINE: Xiaomi Smart Clock LX04 China-to-Global Migration

**Document Version:** 1.0.0  
**Project:** Xiaomi Smart Clock (LX04 -> X04G)  
**Timespan:** November 4, 2026 – November 11, 2026 (Local Time) / November 4, 2026 – November 10, 2026 (UTC)  
**Final Outcome:** SUCCESS — Global Android 10 (`QP1A.190711.020 / 1.7.5`) Verified Operational  

---

## 1. Timeline Methodology & Evidence Classification

Every entry in this chronology is anchored to verified timestamps extracted from file creation records, serial port transcripts, SP Flash Tool traces, Fastboot console captures, and system artifacts.

Each technical event is classified according to the project's strict evidentiary framework:
- **[VERIFIED]:** Supported by bit-for-bit file hashes, raw packet logs, readback comparisons, or direct user physical hardware tests.
- **[REPORTED]:** Recorded in session logs or tool diagnostic output, consistent with known hardware behavior.
- **[INFERRED]:** Technically deduced from observed execution behavior, assembly reverse engineering, or protocol responses where a direct debug print was unavailable.
- **[UNKNOWN]:** Information not preserved in surviving session artifacts or firmware headers.

---

## 2. Chronological Milestones Overview

| Date (UTC) | Phase | Focus / Major Breakthrough | Outcome |
| :--- | :--- | :--- | :--- |
| **2026-11-04 03:15 – 12:00** | Phase 1 | Hardware Analysis, Port Discovery & BROM Handshake | Preloader COM5 communication established; eMMC readback initiated. |
| **2026-11-04 12:00 – Nov 05 06:00** | Phase 2 | eMMC Backup, PMT/GPT Partition Table Geometry | Full physical backup completed; PMT mismatch investigated; GPT recreated. |
| **2026-11-05 06:00 – Nov 10 09:00** | Phase 3 | MediaTek Security Stack & DA2 / GFH Disassembly | Discovered DA2 signature verification routines; rejected patched DA binaries. |
| **2026-11-10 09:00 – 14:30** | Phase 4 | Preloader Serial Hook & Bootloader Unlock Breakthrough | Preloader `b"FASTBOOT"` hook verified; GPT partition de-masking (`frpx`) achieved permanent unlock. |
| **2026-11-10 14:30 – 18:52** | Phase 5 | Super Chunking Bug, Contiguous DA Flashing & Global Boot | LK chunk overwrite bypassed via SP Flash Tool; Recovery wipe initialized userdata; System booted! |

---

## 3. Detailed Chronology

### Phase 1: Hardware Analysis, Port Discovery & BROM Handshake
**Period:** November 4, 2026 (03:15:05 UTC – 12:05:10 UTC)

- **2026-11-04 03:15:05 UTC [VERIFIED] — Project Initialization & Target Identification:**
  - Device identified as Xiaomi XiaoAI Smart Clock (model `LX04`, board `mico_lx04`).
  - Target identified as Global Xiaomi Smart Clock (model `X04G`, board `mico_x04g`).
  - Hardware platform confirmed as MediaTek MT8167A with Kingston 4GB eMMC (`M62704`).
  - Objective defined: Safely flash official Global Android 10 firmware without bricking or destroying factory device calibration (`proinfo`, `nvram`).

- **2026-11-04 04:30:12 UTC [VERIFIED] — Port Identification & Driver Binding:**
  - Micro-USB interface connected to host PC.
  - Windows device enumeration identified `MediaTek Preloader USB VCOM Port (COM5)` when connected during power-on cycle.
  - Preloader handshake established via MediaTek download protocol (115200 baud, 8N1).

- **2026-11-04 06:15:40 UTC [VERIFIED] — DA Authorization Analysis:**
  - Stock SP Flash Tool v5.1812 connected to MT8167 SoC.
  - Handshake with BROM requested authorization authentication.
  - Discovered authentic OEM signed Download Agent: `DA_Mi_Hikaru-resign.bin` matches internal OEM key signature and satisfies BROM Stage 1 challenge without requiring hardware testpoint grounding.

- **2026-11-04 07:22:59 UTC [VERIFIED] — Initial Preflight Inspection & PMT Layout Error:**
  - Loaded Global scatter file (`MT8167_Android_scatter.txt`) containing 17 partition definitions.
  - SP Flash Tool reported `STATUS_ERR_PMT_CHANGED_FOR_ROM (0xC0040003)`.
  - **Analysis [INFERRED]:** The physical eMMC layout from the Chinese Android 8.1 firmware used legacy static partitions (`system` = 1.0 GB, `vendor` = 300 MB, `odmdtbo`), whereas Global Android 10 uses dynamic partitions with a unified `super` partition (1.50 GB). SP Flash Tool's safety mechanism halted operations to prevent accidental boundary truncation.

- **2026-11-04 08:38:53 UTC [VERIFIED] — Technical Report Generation (`stage_6_4_technical_report.md`):**
  - Documented that automated "Firmware Upgrade" or "Format All + Download" would destroy factory RF calibration data at physical byte offsets `0x00080000` (`proinfo`) and `0x00380000` (`nvram`).
  - Hard constraint established: Only readback and targeted partition writes will be permitted.

---

### Phase 2: eMMC Readback, Partition Layout & GPT Geometry Analysis
**Period:** November 4, 2026 (12:05:10 UTC) – November 5, 2026 (06:00:00 UTC)

- **2026-11-04 14:10:00 UTC [VERIFIED] — Comprehensive Physical Readback Backup:**
  - Performed raw physical readbacks via SP Flash Tool `Readback` engine:
    - Physical `BOOT1` readback: `boot1_physical_backup.bin` (2,097,152 bytes, SHA-256: `9280f369...`). Forensic byte-level verification confirmed that bytes `0x800` to `0x800 + 169,132` match `preloader_mico_x04g.bin` with 0 differences, confirming the Global preloader was written to `BOOT1` on the device, while the original Chinese preloader was preserved in offline backups (`LX04-Backup/boot1.bin`).
    - Physical `USER` calibration partitions: `proinfo.bin` (3,145,728 bytes) and `nvram.bin` (5,242,880 bytes). *(Note: An exploratory 32 MB readback of `nvdata.bin` was confirmed to consist entirely of bytes from the zero-filled region within the original Chinese `metadata` partition).*
    - Original Chinese Master Boot Record and Primary GPT: sectors 0–33 readback.

- **2026-11-04 19:45:20 UTC [VERIFIED] — Storage Geometry Calculations:**
  - eMMC capacity verified: `0x71000000` bytes (3,791,650,816 bytes = 7,405,568 sectors of 512 bytes).
  - Primary GPT header: LBA 1.
  - Partition array entries: LBA 2–33 (128 entries x 128 bytes = 16,384 bytes).
  - Usable LBA range: LBA 34 to LBA 7,405,534.
  - Backup GPT header: LBA 7,405,567; Backup entries: LBA 7,405,535 to 7,405,566.

- **2026-11-05 02:53:29 UTC [VERIFIED] — Modified DA Security Audit (`modified_da_security_audit.md`):**
  - Evaluated patched Download Agent binary (`DA_PL.bin` / patched `DA2`) designed to bypass write restrictions.
  - Discovered that MT8167 BROM validates Stage 1 DA signature against public keys fused in efuse.
  - Stage 1 DA in turn validates the cryptographic hash of Stage 2 DA before transferring execution control to SRAM address `0x40000000`.
  - Attempting to load an unsigned DA produced `STATUS_DA_HASH_MISMATCH (0xC0070004)`.
  - Decision [VERIFIED]: Abandon all modified/patched DA binaries; use strictly OEM-signed `DA_Mi_Hikaru-resign.bin`.

- **2026-11-05 04:27:22 UTC [VERIFIED] — GPT Alignment Verification (`chinese_gpt_recovery_verification_report.md`):**
  - Synthesized and flashed target Global GPT structures matching exact Kingston eMMC sector count (`7,405,568` sectors):
    - `gpt_x04g_kingston.bin` (Primary GPT, 17,408 bytes, SHA-256: `f9c80034...`).
    - `gpt_backup_x04g_kingston.bin` (Secondary Backup GPT, 16,896 bytes, SHA-256: `9004570e...`).
  - Verified via physical readbacks (`readback_primary_gpt_lba0_33.bin` and `readback_secondary_gpt_lba7405535_7405567.bin`) that both primary and secondary GPT tables matched candidate binaries bit-for-bit.
  - Preserved exact physical LBA offsets for critical factory calibration partitions (`proinfo`, `nvram`).
  - Created single contiguous `super` partition spanning LBA `0x00138000` to LBA `0x00438000` (1.50 GB).

---

### Phase 3: MediaTek Security Stack & DA2 / GFH Disassembly
**Period:** November 5, 2026 (06:00:00 UTC) – November 10, 2026 (09:00:00 UTC)

- **2026-11-06 11:20:00 UTC [VERIFIED] — DA2 Binary Reverse Engineering:**
  - Analyzed decompiled assembly of `DA_Mi_Hikaru-resign.bin` Stage 2 payload at base address `0x40000000`.
  - Identified validation dispatch table at routine `0x4002EC64`:
    - Checks for GFH (Generic File Header) magic `0x58881688`.
    - Checks for Android boot header magic `ANDROID!`.
    - Checks for Device Tree Blob header magic `0x1EABB7D7`.
  - Confirmed that raw unencapsulated partitions (such as `seccfg` and `frp`) fail validation with error `STATUS_SEC_IMG_TYPE_MISMATCH (0xC002002A)`.

- **2026-11-08 14:15:30 UTC [VERIFIED] — Flash Buffer Verification Investigation:**
  - Evaluated routine `0x40030244` (`buf_chk`) in DA2.
  - Routine verifies container memory bounds against external signature table `allinone_ext_sig`.
  - Flashing synthetic GFH containers for non-signed partitions caused `STATUS_SEC_BUFFER_CHECK_FAIL (0xC002004B)`.
  - Flashing spliced certificates resulted in `STATUS_SEC_IMGHDR_HASH_VFY_FAIL (0xC002002B)`.
  - **Strategic Pivot [INFERRED]:** Direct low-level unlocking via SP Flash Tool write operations is cryptographically blocked by DA2 without Xiaomi internal private keys. However, the bootloader itself (Little Kernel) contains standard Fastboot protocol routines. If LK can be reached in Fastboot mode, MediaTek DA restrictions can be bypassed completely.

---

### Phase 4: Preloader Serial Hook & Bootloader Unlock Breakthrough
**Period:** November 10, 2026 (09:00:00 UTC – 14:30:00 UTC)

- **2026-11-10 09:50:26 UTC [VERIFIED] — Global Firmware Audit (`phase2_global_firmware_audit_report.md`):**
  - Audited all partitions of Global Android 10 build `1.7.5`.
  - Confirmed `super.bin` (1,610,612,736 bytes) contains pure Android dynamic sparse filesystem (`gDla` header).
  - Confirmed `boot.bin` (16,777,216 bytes) uses pure Android AVB 2.0 with embedded kernel and ramdisk.

- **2026-11-10 11:37:43 UTC [VERIFIED] — The Preloader Fastboot Interception Discovery:**
  - Analyzed preloader startup sequence in disassembly. Preloader polls UART/USB CDC serial for magic handshake string during early power-on.
  - Developed custom Windows Python script: `preloader_fastboot_win32.py`.
  - Script holds COM5 open with DTR/RTS pulsing while streaming `b"FASTBOOT"`.
  - Upon device USB insertion, Preloader captured the token, replied with `b"TOOBTSAF"`, set the boot argument `BOOT_ARGUMENT_FASTBOOT = 0x58464254`, and handed execution over to Little Kernel.
  - Little Kernel initialized display and entered Fastboot mode without needing physical button combinations or testpoints.

- **2026-11-10 13:10:15 UTC [VERIFIED] — Fastboot Unlock Operation Blocked:**
  - Executed `fastboot flashing unlock`.
  - Console responded: `FAILED (remote: Unlock operation is not allowed)`.
  - **Investigation [VERIFIED]:** LK disassembly at routine `0x4e1b39e0` (`get_unlock_allowed`) showed that LK reads offset `0x0FFFFC` (the last 4 bytes) of the `frp` partition. If the flag equals `0x00`, unlocking is rejected.

- **2026-11-10 13:50:40 UTC [VERIFIED] — The Partition De-masking Breakthrough:**
  - Discovered fallback branch in LK `get_unlock_allowed`:
    ```c
    if (!partition_exists("frp")) {
        return 1; // Default to ALLOWED if partition does not exist!
    }
    ```
  - Constructed `gpt_x04g_unlock.bin`: modified partition name entry 12 from `frp` (ASCII `66 72 70 00`) to `frpx` (ASCII `66 72 70 78`), recalculating CRC32 checksums.
  - Flashed `gpt_x04g_unlock.bin` via SP Flash Tool.
  - Re-entered Fastboot via `preloader_fastboot_win32.py`.
  - Executed `fastboot flashing unlock`.
  - Device screen displayed unlock confirmation prompt: *"press + to unlock"*.
  - User pressed Volume+ physical button.
  - Terminal confirmed: `OKAY [ 12.450s ]`. Device seccfg updated to `unlocked: yes`!

---

### Phase 5: Super Chunking Bug, Contiguous DA Flashing & Global Boot
**Period:** November 10, 2026 (14:30:00 UTC – 18:52:00 UTC)

- **2026-11-10 15:14:36 UTC [VERIFIED] — Unlocked Partition Flashing via Fastboot:**
  - Flashed verified Global core boot components via Fastboot:
    - `fastboot flash boot boot.bin` (OKAY)
    - `fastboot flash dtbo dtbo.bin` (OKAY)
    - `fastboot flash vbmeta vbmeta.bin` (OKAY)
    - `fastboot flash vbmeta_system vbmeta_system.bin` (OKAY)
    - `fastboot flash vbmeta_vendor vbmeta_vendor.bin` (OKAY)
    - `fastboot flash recovery recovery.bin` (OKAY)
    - `fastboot flash cache cache.bin` (OKAY)
    - `fastboot flash metadata metadata.bin` (OKAY)
    - `fastboot flash md_udc md_udc.bin` (OKAY)
    - `fastboot flash para para.bin` (OKAY)
    - `fastboot erase userdata` (OKAY)

- **2026-11-10 15:45:10 UTC [VERIFIED] — The Fastboot Sparse/Chunking Defect:**
  - Executed `fastboot flash super super.bin`.
  - Fastboot client split the 1.50 GB binary into 8 sparse chunks of ~200 MB:
    `super.bin_sparse0` through `super.bin_sparse7`.
  - Flashing completed with `OKAY` statuses.
  - On reboot, device displayed `Red State` (normal for unlocked MediaTek bootloader) followed by immediate drop into Android Recovery:
    ```text
    xiaomi/mico_x04g/mico_x04g
    10/QP1A.190711.020/1.7.5
    user /release-keys
    can't load android system your data may be corrupt
    ```
  - Selecting `Factory data reset` failed and looped back to recovery.

- **2026-11-10 16:30:25 UTC [VERIFIED] — Chunk Offset Overwrite Root Cause Analysis:**
  - Read back the first 50 MB of the `super` partition via SP Flash Tool.
  - Expected dynamic partition header `0x67446c61` (`gDla`) was absent; sector contained binary data matching the *end* of chunk 8.
  - **Root Cause Identified [VERIFIED]:** The MediaTek LK Fastboot implementation on MT8167 does not advance the eMMC write offset pointer across multi-chunk downloads when receiving sparse chunks. Each chunk was written to offset `0x00000000`, causing the final chunk to overwrite the superblock dynamic metadata.

- **2026-11-10 17:15:40 UTC [VERIFIED] — Contiguous eMMC Streaming via SP Flash Tool:**
  - Created dedicated XML download profile: `download_super.xml` targeting partition name `super` with linear write addressing (`type: NORMAL_ROM`).
  - Executed SP Flash Tool download:
    - Entire 1,610,612,736 bytes of `super.bin` streamed contiguously at 19.77 MB/s.
    - Write completed in 81.4 seconds with zero fragmentation.
  - Restored standard GPT partition table (`gpt_x04g_kingston.bin`) restoring `frpx` back to `frp`.

- **2026-11-10 18:10:15 UTC [VERIFIED & REPORTED] — Userdata Cryptographic Initialization via Recovery:**
  - Following the contiguous write of `super.bin`, the device rebooted into Android Recovery.
  - User reported: *"it goes back again to android recovery. will i try again to factory data reset?"*
  - Engineering instruction confirmed that because the dynamic partitions (`system`, `vendor`, `product`) were now fully intact and contiguous, executing `Factory data reset` would properly format `/data` and generate the necessary Android 10 cryptographic superblock.
  - User selected `Factory data reset` on the Recovery menu.
  - Android 10 recovery completed the cryptographic format of `/data` without error, and initiated a system reboot.

- **2026-11-10 18:52:00 UTC [VERIFIED] — Successful First Global Boot & Subsystem Testing:**
  - Device booted through Red State warning directly into official Global Android 10 Setup Wizard.
  - Full display initialization verified (800x480 WVGA).
  - Touchscreen digitizer verified responsive.
  - Speaker audio played startup chime cleanly.
  - Wi-Fi 2.4 GHz scanned and authenticated successfully.
  - Bluetooth 5.0 scanning operational.
  - Device reached stable idle operational state.
  - **Project Successfully Completed.**
