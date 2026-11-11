# PROJECT STATISTICS: Xiaomi Smart Clock LX04 China-to-Global Migration

**Document Version:** 1.2.0  
**Project:** Xiaomi Smart Clock LX04 China-to-Global Firmware Conversion  
**Platform:** MediaTek MT8167A / eMMC Kingston 4GB (`M62704`, 7,405,568 sectors)  
**Status:** Completed & Hardware Verified Operational on Single Development Unit  

---

## 1. Executive Metrics Summary

| Category | Value | Verification Status |
| :--- | :--- | :--- |
| **Total Calendar Duration** | 6 days, 15 hours, 36 minutes, 55 seconds | **[VERIFIED]** (Session log timestamps) |
| **Estimated Active Engineering Time** | ~34.0 hours (± 2.5 hours) | **[INFERRED]** (Active terminal & file activity deltas) |
| **Flashing Operations (Individual Writes)** | 22 individual partition flash actions | **[VERIFIED]** (SPFT & Fastboot command logs) |
| **Meaningful Flashing Attempts** | 9 distinct high-level engineering stages | **[VERIFIED]** (SPFT & Fastboot console captures) |
| **Significant Failures & Errors** | 8 major obstacles | **[VERIFIED]** (Error codes & disassembly traces) |
| **Major Technical Breakthroughs** | 7 key discoveries | **[VERIFIED]** (Reverse engineering & protocol scripts) |
| **Partitions Flashed / Erased via Host Tools** | 17 physical & logical partitions (including BOOT1, para & userdata) | **[VERIFIED]** (eMMC GPT sector map & readbacks) |
| **Partitions Modified Internally on Device** | 1 partition (`seccfg` unlocked by LK upon `fastboot oem unlock`) | **[VERIFIED]** (Total modified partitions = 18) |
| **Total Original Partitions Preserved Untouched** | 6 partitions (2 calibration/identity + 4 security) | **[VERIFIED]** (Unchanged on physical eMMC) |
| **— Preserved Factory Calibration & Identity** | 2 partitions (`proinfo`, `nvram`) | **[VERIFIED]** (Physical readback hashes & GPT offsets) |
| **— Preserved Stock Security & Key Storage** | 4 partitions (`tee1`, `tee2`, `kb`, `dkb`) | **[VERIFIED]** (Physical byte offsets unchanged) |
| **New Global Runtime Calibration Partition** | 1 partition (`nvdata` carved from zero-filled region within the original Chinese `metadata` partition; first-boot ext4 format & `nvram` population is **[INFERRED]**) | **[VERIFIED]** (Global GPT definition SYS21) |
| **Offline Firmware Backups Preserved** | Original Chinese `BOOT1`, full GPT, and calibration | **[VERIFIED]** (`LX04-Backup` & `LX04-Dumps`) |
| **Confirmed Working Subsystems** | 7 hardware subsystems + Google Assistant voice features + Xiaomi app detection | **[VERIFIED BY OWNER]** (Direct owner physical testing on single unit) |
| **Unverified / Pending Features** | OTA System Updates & extended smart home streaming | **[UNTESTED]** (Automatic updates must remain disabled; single-unit validation) |

---

## 2. Chronological Duration & Active Work Breakdown

### 2.1 Calendar Time
- **Project Start:** November 4, 2026 at 03:15:05 UTC (Initial device identification and hardware analysis).
- **Project Completion:** November 10, 2026 at 18:52:00 UTC (Successful first boot into Global Android 10 with verified hardware functionality).
- **Total Elapsed Duration:** 159 hours, 36 minutes, 55 seconds (6.65 calendar days).

### 2.2 Active Engineering Hours Breakdown

| Date | Phase / Engineering Focus | Active Duration | Activity Description |
| :--- | :--- | :--- | :--- |
| **2026-11-04** | Port Discovery, Readback Backups & PMT Layout | ~9.5 hours | COM5 handshake setup, raw physical readbacks (`proinfo`, `nvram`, exploratory `nvdata`, `boot1`), scatter analysis, PMT layout error diagnosis. |
| **2026-11-05** | DA Security Stack & GPT Sector Calculations | ~6.0 hours | Kingston eMMC sector calculations (`7,405,568` sectors), GPT synthesis, secondary GPT alignment, patched DA execution and rejection analysis. |
| **2026-11-06 – Nov 09** | Offline Binary Reverse Engineering & Disassembly | ~8.0 hours | Static disassembly of DA2 Stage 2 (`DA_Mi_Hikaru-resign.bin`), LK boot routines, AVB 2.0 header parsing, GFH container constraints. |
| **2026-11-10** | Unlock Breakthrough, Super Flashing & Verification | ~10.5 hours | `preloader_fastboot_interceptor.py` development, partition de-masking (`frpx`), Fastboot unlock execution, super contiguous flash, recovery wipe, hardware tests. |
| **Total** | **Full Engineering Lifecycle** | **~34.0 hours** | **Total focused engineering & flashing time.** |

---

## 3. Flashing Operations, Meaningful Attempts & Failure Classification

To maintain strict evidentiary precision, project operations are categorized into three distinct tiers:

1. **Individual Flashing Operations (22):** Every individual command or transfer executed across SP Flash Tool and Fastboot (e.g., flashing `dtbo`, `vbmeta`, `boot`, `recovery`, `cache`, `metadata`, `md_udc`, `para`, `super`, `pgpt`, `sgpt`, erasing `userdata`, and readback verification passes).
2. **Meaningful Flashing Attempts (9):** Distinct, coherent engineering stages aimed at advancing the device conversion:
   - *Attempt 1 (Scatter Download):* Global scatter download via SP Flash Tool -> Blocked by PMT layout check (`0xC0040003`).
   - *Attempt 2 (Patched DA Injection):* Custom DA Stage 2 loading -> Blocked by BROM SHA-256 hash check (`0xC0070004`).
   - *Attempt 3 (Direct Boot Flash):* Direct DA flashing of Android 10 `boot.bin` -> Blocked by boot header DTB size offset check (`0xC0020029`).
   - *Attempt 4 (Spliced Certificate Flash):* Flashing `boot_mtk_signed.bin` with spliced cert -> Blocked by decrypted SHA mismatch (`0xC002002B`).
   - *Attempt 5 (Direct Write Memory):* Raw physical sector write to `seccfg` partition -> Blocked by DA2 hardware memory filter (`0xC002000C`).
   - *Attempt 6 (Synthetic GFH FRP Flash):* Flashing synthetic GFH-encapsulated `frp.bin` -> Blocked by external signature buffer bounds check (`0xC002004B`).
   - *Attempt 7 (Unlock GPT + LK Flash):* Flashed `gpt_x04g_unlock.bin` (`frpx` de-masked) and Global `lk.bin` via SP Flash Tool -> **SUCCESS** (LK entered unlocked state).
   - *Attempt 8 (Fastboot Multi-Chunk Super Flash):* Flashed 1.50 GB `super.bin` via Fastboot client-side sparse chunking -> Failed on boot due to LK multi-chunk offset overwrite defect; Recovery bootloop.
   - *Attempt 9 (Final Contiguous Flashing & Recovery Initialization):* Flashed `super.bin` contiguously via SP Flash Tool (`download_super_contiguous.xml`), restored `gpt_x04g_kingston.bin`, executed Recovery factory data reset -> **SUCCESS** (System booted into Global Android 10).
3. **Failed Attempts (8):** Attempts 1 through 6, and Attempt 8, which each hit a documented technical barrier before the final resolution.

---

## 4. Major Technical Discoveries (Total: 7)

1. **Preloader Serial Fastboot Interceptor:**  
   Identified that MediaTek MT8167 Preloader polls UART/USB CDC serial for the token `b"FASTBOOT"` during the initial 500ms boot window. Created native Win32 `preloader_fastboot_interceptor.py` to trigger Fastboot entry without testpoints or hardware disassembly.
2. **Bootloader Unlock via Partition De-masking:**  
   Disassembled Little Kernel routine `0x4e1b39e0` (`get_unlock_allowed`) and proved that renaming `frp` to `frpx` in the Primary GPT bypasses the factory OEM unlock lock, causing LK to default `unlock_allowed = 1`.
3. **Authentic OEM Signed DA Authorization:**  
   Discovered that `DA_Mi_Hikaru-resign.bin` satisfies BROM cryptographic authentication for Xiaomi MT8167 hardware without requiring patched DA binaries or hardware testpoints.
4. **Kingston 4GB Geometry Alignment & Dual-GPT Consistency:**  
   Calculated the precise eMMC user area boundary (`7,405,568` sectors of 512 bytes) and synthesized matching Primary and Backup GPT structures with valid CRC32 checksums. Verified via physical readback that both `pgpt` (LBA 0–33) and `sgpt` (LBA 7,405,535–7,405,567) matched candidate binaries bit-for-bit.
5. **Fastboot Multi-Chunk Offset Stagnation Defect:**  
   Discovered that Little Kernel's Fastboot engine resets the target eMMC write offset pointer to `0x00000000` for every incoming sparse chunk, corrupting multi-part dynamic partition containers.
6. **SP Flash Tool Contiguous Linear Streaming:**  
   Demonstrated that configuring SP Flash Tool's XML download engine with `type: NORMAL_ROM` allows streaming 1.50 GB raw dynamic partition images contiguously at 19.77 MB/s without triggering chunk corruption.
7. **Recovery-Mediated Cryptographic Userdata Initialization:**  
   Identified that selecting "Factory data reset" in the newly installed Android 10 Recovery formats and encrypts `/data` with keys compatible with Android 10 AVB, resolving the initial recovery bounce loop once `super.bin` was contiguously written.

---

## 5. Partition Modification & Geometry Audit

### 5.1 Modified / Flashed Partitions (17 Flashed via Tools + 1 On-Device = 18 Total)

Physical and logical partitions updated on the device to establish the Global Android 10 firmware (LBA ranges parsed directly from binary GPT):

| # | Partition Name | Hardware Region | Sector / LBA Range | Size (Bytes) | Image / Contents | Verification Method |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `BOOT1` | eMMC Boot 1 | Offset `0x00000800` | 169,132 B | Global Preloader (`preloader_mico_x04g.bin`) | **[VERIFIED]** (Physical readback matches global preloader SHA-256) |
| 2 | `pgpt` | Physical USER | LBA 0 – 33 | 17,408 B | Primary GPT (Kingston 4GB geometry; de-masked `frpx` for unlock, restored `frp`) | **[VERIFIED]** (Readback SHA-256 match `f9c80034...`) |
| 3 | `sgpt` | Physical USER | LBA 7,405,535 – 7,405,567 | 16,896 B | Secondary Backup GPT (Kingston 4GB geometry) | **[VERIFIED]** (Readback SHA-256 match `9004570e...`) |
| 4 | `lk` | Physical USER | LBA 116,224 – 117,247 | 524,288 B | Global Little Kernel v2.0 (`lk.bin`) | **[VERIFIED]** (Fastboot `version-bootloader` query) |
| 5 | `lk2` | Physical USER | LBA 117,248 – 118,271 | 524,288 B | Global Little Kernel Backup (`lk.bin`) | **[VERIFIED]** (SPFT Download Log) |
| 6 | `boot` | Physical USER | LBA 118,272 – 151,039 | 16,777,216 B | Global Android 10 Kernel (`boot.bin`) | **[VERIFIED]** (Fastboot Flash Log & Boot) |
| 7 | `dtbo` | Physical USER | LBA 201,216 – 203,263 | 1,048,576 B | Global Device Tree Overlay (`dtbo.bin`) | **[VERIFIED]** (Fastboot Flash Log & Display Init) |
| 8 | `vbmeta` | Physical USER | LBA 375,296 – 383,487 | 4,194,304 B | Global AVB 2.0 Root (`vbmeta.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 9 | `vbmeta_system` | Physical USER | LBA 383,488 – 391,679 | 4,194,304 B | Global AVB System Chain (`vbmeta_system.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 10 | `vbmeta_vendor` | Physical USER | LBA 391,680 – 399,871 | 4,194,304 B | Global AVB Vendor Chain (`vbmeta_vendor.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 11 | `recovery` | Physical USER | LBA 151,040 – 183,807 | 16,777,216 B | Global Android Recovery (`recovery.bin`) | **[VERIFIED]** (Recovery UI capture on LCD) |
| 12 | `para` | Physical USER | LBA 183,808 – 184,831 | 524,288 B | Global Bootloader Message (`para.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 13 | `cache` | Physical USER | LBA 3,545,600 – 3,807,743 | 134,217,728 B | Global Cache Image (`cache.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 14 | `metadata` | Physical USER | LBA 299,520 – 367,103 | 34,603,008 B | Global Dynamic Partitions Metadata (`metadata.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 15 | `md_udc` | Physical USER | LBA 254,464 – 299,519 | 23,068,672 B | Global Modem UDC (`md_udc.bin`) | **[VERIFIED]** (Fastboot Flash Log) |
| 16 | `super` | Physical USER | LBA 399,872 – 3,545,599 | 1,610,612,736 B | Dynamic Partitions Container (`super.bin`) | **[VERIFIED]** (Contiguous SPFT Write @ 19.77 MB/s) |
| 17 | `userdata` | Physical USER | LBA 3,807,744 – 7,405,534 | ~1.72 GB | Formatted & cryptographically encrypted by Recovery | **[VERIFIED]** (Fastboot erase & Recovery Reset) |
| 18 | `seccfg` | Physical USER | LBA 115,712 – 116,223 | 262,144 B | Modified on-device by Little Kernel unlock handler | **[VERIFIED]** (`fastboot getvar unlocked: yes`) |

### 5.2 Preserved Original Factory Partitions (6 Partitions Total)

A total of 6 original Chinese partitions were confirmed preserved untouched on the physical device: 2 critical calibration and hardware identity partitions (`proinfo`, `nvram`) and 4 stock vendor security and TrustZone partitions (`tee1`, `tee2`, `kb`, `dkb`).

#### 5.2.1 Critical Factory Calibration Partitions Preserved Untouched (2)

The physical factory identity and RF calibration partitions were strictly excluded from all flashing and formatting operations:

| Partition Name | Physical Region | Start LBA | Byte Offset | Size | Verification Method | Justification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `proinfo` | Physical USER | LBA `1,024` | `0x00080000` | 3,145,728 B | Readback backup hash | Motherboard serial number, factory barcode, and hardware revision ID. |
| `nvram` | Physical USER | LBA `7,168` | `0x00380000` | 5,242,880 B | Readback backup hash | Factory radio frequency calibration and permanent Wi-Fi MAC address. |

#### 5.2.2 Stock Chinese Security & Key Storage Partitions Preserved (4)

The following original TrustZone and key storage partitions were left untouched and carry forward their original Chinese firmware contents:

| Partition Name | Physical Region | Start LBA | Byte Offset | Size | Function / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tee1` | Physical USER | LBA `225,792` | `0x06E40000` | 5,242,880 B | Primary Microtrust TrustZone TEE OS image. |
| `tee2` | Physical USER | LBA `236,032` | `0x07340000` | 5,242,880 B | Secondary Microtrust TrustZone backup image. |
| `kb` | Physical USER | LBA `246,272` | `0x07840000` | 2,097,152 B | Key Block storage partition. |
| `dkb` | Physical USER | LBA `250,368` | `0x07A40000` | 2,097,152 B | Device Key Block storage partition. |

### 5.3 Detailed Technical Investigation: Global `persist` and `nvdata` Physical Overlaps

The relationship between the stock Chinese layout, Global partition map, and physical eMMC byte ranges is detailed below:

| Physical Range | Original Chinese Owner | Original Data | Conversion Operation | Final Global Owner | Evidence & Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x00080000` – `0x0037FFFF` | `proinfo` (3 MB) | Factory serial barcode string | None (Preserved) | `proinfo` (3 MB) | **[VERIFIED]** Exact match in Chinese and Global GPTs; physical readback verified |
| `0x00380000` – `0x0087FFFF` | `nvram` (5 MB) | Factory RF calibration & MAC | None (Preserved) | `nvram` (5 MB) | **[VERIFIED]** Exact match in Chinese and Global GPTs; physical readback verified |
| `0x00880000` – `0x0127FFFF` | `protect1` (10 MB) | 100% Zeroes (`e5b844cc...`) | Repartitioned (Unwritten) | `persist` (`0x00880000`–`0x0387FFFF`) | **[VERIFIED]** Physical backup `protect1.bin` is all zeroes; scatter specifies `is_download: false` |
| `0x01280000` – `0x01C7FFFF` | `protect2` (10 MB) | 100% Zeroes (`e5b844cc...`) | Repartitioned (Unwritten) | `persist` (continued) | **[VERIFIED]** Physical backup `protect2.bin` is all zeroes; scatter specifies `is_download: false` |
| `0x01C80000` – `0x0387FFFF` | `persist` (First 28 MB of Chinese 48 MB `persist`) | 100% Zeroes (`152ba99d...`) | Repartitioned (Unwritten) | `persist` (continued) | **[VERIFIED]** Physical backup `persist.bin` is all zeroes; scatter specifies `is_download: false` |
| `0x03880000` – `0x04C7FFFF` | `persist` (Remaining 20 MB of Chinese 48 MB `persist`) | 100% Zeroes | Overwritten by Global Bootchain | `seccfg`, `lk`, `lk2`, `boot`, `recovery` (part) | **[VERIFIED]** Reallocated by Global GPT; written during conversion by SPFT/Fastboot |
| **`0x0B340000` – `0x0B73FFFF`** | **`metadata` (Bytes 4MB–8MB of Chinese `metadata`)** | **100% Zeroes (Zero-filled region within original Chinese metadata partition)** | **Carved out by Global GPT (Unwritten by tools)** | **`nvdata` (4 MB)** | **[VERIFIED]** Chinese `metadata.bin` slice is all zeroes; scatter has `file_name: NONE`; formatting as ext4 and population by `nvram_daemon` is **[INFERRED]** based on MediaTek Android 10 architecture |

> [!IMPORTANT]
> **Definitive Findings:**
> 1. **Global `persist` (`0x00880000`–`0x0387FFFF`):** Global `persist` covers a physical region formerly occupied by Chinese `protect1` (10 MB), Chinese `protect2` (10 MB), and the first 28 MB of Chinese `persist`. Forensic hashing of all three backup images proves the entire 48 MB region was **100% zeroes** on the stock factory eMMC. No sensor calibration data was found in this region. The physical bytes were left unwritten by PC tools, inheriting the zero-filled state.
> 2. **Global `nvdata` (`0x0B340000`–`0x0B73FFFF`):** The Global `nvdata` partition was **NOT PRESERVED** from Chinese firmware (Chinese firmware did not possess an `nvdata` partition). Instead, the physical range was a zero-filled region within the original Chinese `metadata` partition. During conversion, the Global GPT carved out this 4 MB slice as `nvdata`. First-boot ext4 formatting and `nvram_daemon` population from preserved `nvram` is an **[INFERRED]** architectural mechanism.

### 5.4 Offline Firmware Backups Preserved

The original Chinese device firmware components were securely read back via `mtkclient` direct partition dump and archived prior to modification:
- **Original Chinese `BOOT1`:** Preserved in `LX04-Backup/boot1_physical_backup.bin` (2,097,152 bytes) with original Chinese preloader.
- **Factory Calibration:** Full binary backups of `proinfo.bin`, `nvram.bin`, `protect1.bin`, and `protect2.bin`.
- **Factory Chinese GPT:** Primary and secondary GPT backups (`gpt.bin`, `gpt_backup.bin`).

---

## 6. Hardware Verification Matrix

The device owner has physically evaluated the converted device and confirmed operational status for the following subsystems on the running Global firmware (tested on a single Kingston 4GB eMMC development unit):

| Hardware Subsystem | Component / Controller | Verified Status | Evidence & Observation |
| :--- | :--- | :--- | :--- |
| **Operating System** | Android 10 (`QP1A.190711.020 / 1.7.5`) | **[VERIFIED BY OWNER]** | System boots cleanly past bootloader; reaches Setup Wizard. |
| **Touchscreen Digitizer**| FocalTech FT6336 (I2C) | **[VERIFIED BY OWNER]** | Responsive touch interactions and swipe navigation across screen. |
| **LCD Display Panel** | 3.97" IPS WVGA (800x480) | **[VERIFIED BY OWNER]** | Clean graphics rendering, backlight active, no visual artifacts. |
| **Wi-Fi Subsystem** | MediaTek MT6631 (2.4 GHz) | **[VERIFIED BY OWNER]** | Scanned local SSIDs, authenticated, and maintained connection. |
| **Bluetooth Subsystem**| MediaTek MT6631 (BT 5.0 LE) | **[VERIFIED BY OWNER]** | Bluetooth stack active; advertising, discovery, and pairing operational. |
| **Speaker / Audio** | Neodymium Speaker / Class-D Amp | **[VERIFIED BY OWNER]** | Audio chime and system sound reproduction verified clean. |
| **Far-field Microphones** | Dual Mic Array + Everest ADC | **[VERIFIED BY OWNER]** | Hardware capture and ADC operational; repeatedly verified via live Google Assistant voice recognition and spoken responses. |
| **Google Assistant Voice Interaction** | Google Assistant Stack | **[VERIFIED BY OWNER]** | Repeated voice queries confirmed working: weather forecast inquiry, current time check, and alarm setting with spoken responses. |
| **Xiaomi Companion App** | Xiaomi Companion App Ecosystem | **[VERIFIED BY OWNER]** | Converted clock successfully detected and recognized in the official Xiaomi app. |
| **Hardware Buttons** | Mute, Vol+, Vol- | **[VERIFIED / PARTIAL]** | Volume+ verified working during bootloader unlock prompt; Vol+/Vol- functional. |
| **OTA System Updates** | Google / Xiaomi Global CDN | **[UNTESTED]** | Update engine untested; automatic updates should be disabled as a precaution. |

> [!NOTE] Single-Unit Hardware Validation
> All physical hardware and software verifications were performed by the device owner on a single development clock equipped with a Kingston 4GB eMMC (`M62704`, 7,405,568 sectors). Not independently reproduced on other hardware or storage vendor variants. Only specific Google Assistant commands (weather, time, alarm) and Xiaomi app detection have been confirmed; other extended smart home voice integrations remain untested.
