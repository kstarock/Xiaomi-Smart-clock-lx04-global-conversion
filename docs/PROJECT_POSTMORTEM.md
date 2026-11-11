# PROJECT POSTMORTEM: Xiaomi Smart Clock LX04 China-to-Global Conversion

**Document Version:** 1.0.0  
**Status:** Completed & Verified Operational  
**Date of Completion:** November 11, 2026 (02:52:00 Local / 18:52:00 UTC)  
**Author:** Antigravity Firmware & Embedded Systems Engineering Pair

---

## 1. Executive Summary

This postmortem documents the complete engineering conversion of the **Xiaomi Smart Clock (China Model: LX04)** to the **Official Global Firmware (Model: X04G)**. The procedure modified partition layouts, bootloaders, and system storage while strictly preserving critical factory calibration partitions.

The device originally ran Xiaomi's restricted mainland China firmware (`mico_lx04`), locking the hardware into the proprietary XiaoAI ecosystem with no multilingual support, no Google Assistant integration, and mandatory mainland cloud servers.

Through firmware reverse engineering, MediaTek DA2/LK static disassembly, safe GPT partition-layout migration, bootloader unlocking via partition de-masking, and direct eMMC contiguous block flashing, the clock was successfully converted to **Android 10 Global (`mico_x04g` build `QP1A.190711.020 / 1.7.5 user/release-keys`)**.

### Final Hardware Verification Status
The device owner has directly tested and personally confirmed the following hardware subsystems on the running Global firmware (tested on a single Kingston 4GB eMMC development unit):
- [x] **Global Android 10 Firmware Boot:** Verified (Clean startup, display initialized, UI responsive).
- [x] **LCD Display (800x480 WVGA):** Verified (Clean graphics rendering, backlight active, no visual artifacts).
- [x] **Capacitive Touchscreen:** Verified (Touch coordinates mapped accurately across the 800x480 panel).
- [x] **Wi-Fi Subsystem (2.4 GHz):** Verified (Authenticated and connected to local network).
- [x] **Bluetooth Subsystem (BT 5.0):** Verified (Scanning and pairing functional).
- [x] **Audio / Speaker Subsystem:** Verified (Audio output operational with clean reproduction).
- [x] **Far-field Microphone Array:** Verified by Owner (Dual-microphone array with Everest ADC responsive to Google Assistant voice triggers).
- [x] **Google Assistant Core Voice Commands:** Verified by Owner (Repeated successful tests for weather query, current time query, and setting an alarm with clear voice recognition and spoken audio responses).
- [x] **Xiaomi Companion App Detection:** Verified by Owner (Clock successfully recognized and paired in the official Xiaomi app).
- [x] **Overall Device Operability:** Verified (Device stable, no thermal runaway or spontaneous reboot).

*Note on Unverified Subsystems:* OTA system updates remain strictly **[UNTESTED]** (automatic OTA updates should remain disabled). Extended smart home integrations beyond the three tested voice commands have not been evaluated. All verifications were conducted on a single Kingston 4GB eMMC development clock and have not yet been independently reproduced across other hardware variants.

---

## 2. Hardware and Firmware Architecture

### 2.1 Physical Hardware Specifications
- **Device Identifiers:** Xiaomi Smart Clock LX04 (China variant) / X04G (Global equivalent).
- **SoC (System-on-Chip):** MediaTek MT8167A (Quad-core ARM Cortex-A35 @ 1.3 GHz, 28nm, 64-bit ARMv8-A architecture running in AArch32 mode).
- **GPU:** Imagination Technologies PowerVR GE8300.
- **System Memory:** 1 GB LPDDR3 SDRAM.
- **Storage:** 4 GB Kingston eMMC 5.1 (Hardware CID Model: `M62704`, Capacity: `0x71000000` / 3,791,650,816 bytes, Block count: `7,405,568` sectors).
  - Physical `BOOT1`: 2,097,152 bytes (Hardware boot partition containing Global Preloader `preloader_mico_x04g.bin` at offset `0x800`; original Chinese preloader preserved in offline backup).
  - Physical `BOOT2`: 2,097,152 bytes.
  - Physical `RPMB`: 524,288 bytes.
  - Physical `USER`: 3,786,932,224 bytes (GPT partitions).
- **Display:** 3.97-inch IPS LCD, 800 × 480 WVGA resolution (MIPI-DSI interface, BOE / CTC driver ICs `jd9161z` / `gc9503w`).
- **Touch Controller:** FocalTech FT6336 capacitive I2C touch panel.
- **Audio:** Class-D amplifier driving a 1.5-inch full-range neodymium speaker.
- **Wireless Connectivity:** MediaTek MT6631 Wi-Fi (802.11 b/g/n, 2.4 GHz) + Bluetooth 5.0 LE.

### 2.2 Firmware Architecture Comparison

| Architectural Property | Original China Firmware (LX04) | Target Global Firmware (X04G) |
| :--- | :--- | :--- |
| **Product Target** | `mico_lx04` | `mico_x04g` |
| **Android Version** | Android 8.1 Oreo (Engineering ROM `alps-mp-o1.mp5_W18.34`) | Android 10 (Build `QP1A.190711.020 / 1.7.5`) |
| **Partition Scheme** | Legacy Static Partitions (`system`, `vendor`, `odmdtbo`) | Dynamic Partitions (`super` containing `system`, `vendor`, `product`) |
| **Security Framework** | MediaTek Certificate Chain (`cert2`, GFH headers) | Pure Android Verified Boot 2.0 (AVB `vbmeta`, `vbmeta_system`, `vbmeta_vendor`) |
| **User Interface** | Custom XiaoAI Smart Display Shell | Android 10 Embedded Global Setup / Google Smart Display Framework |
| **Voice Assistant** | Xiaomi XiaoAI (Mandarin Chinese only) | Google Assistant (Multilingual) |
| **Boot Chain Engine** | MediaTek Little Kernel (LK v1.0, 2018) | Global Little Kernel (LK v2.0, 2021-06-19 `451d69f`) |

---

## 3. Project Objectives and Strict Boundaries

From inception, this project operated under strict engineering safety constraints to prevent unrecoverable device destruction:
1. **Zero Destructive eMMC Formatting:** The physical hardware partitions were never subjected to destructive global erases like SP Flash Tool `Format All + Download`.
2. **Preservation of Specific Factory Calibration Partitions:** Partition blocks for `proinfo` (serial numbers, hardware revisions) and `nvram` (Wi-Fi/Bluetooth MAC addresses, RF calibration tables) were confirmed preserved untouched at identical physical offsets on the eMMC. (Note: Stock Chinese firmware had no `nvdata` partition; under Global Android 10, the newly defined `nvdata` partition at `0x0B340000` is formatted as ext4 and populated from preserved `nvram` on first boot, an **[INFERRED]** mechanism based on standard MediaTek Android 10 architecture).
3. **Physical Backup Verification:** Complete byte-exact backups of the original Chinese preloader (`LX04-Backup/boot1.bin`) and physical readback (`boot1_physical_backup.bin`, SHA-256: `9280f36941daf7ac2b096511252346be4e24e634568b1f92de907e9477f11319`, verifying the Global preloader at offset `0x800`) were secured and cataloged.
4. **Permanent Operability:** The target was a fully functional, self-booting Global device, avoiding tethered boot requirements or persistent boot loops.

---

## 4. Major Technical Challenges Encountered

### Challenge 1: The MediaTek Download Agent (DA) Security Barrier
MediaTek's secure download engine relies on a two-stage Download Agent (DA1 in BROM, DA2 in DRAM). Xiaomi's factory security configuration enforces strict verification:
- DA Stage 1 validates the cryptographic SHA-256 hash of DA Stage 2 before execution. Modified DA binaries intended to bypass write protections were immediately rejected with `STATUS_DA_HASH_MISMATCH (0xC0070004)`.
- DA Stage 2 (`DA_Mi_Hikaru-resign.bin`) analyzes incoming binary headers via routine `0x4002EC64`. Partitions marked with security flags enforce authentic Xiaomi certificates. Flashing raw uncontainerized images triggered `STATUS_SEC_IMG_TYPE_MISMATCH (0xC002002A)`.
- When custom signed images with mismatched SHA certificates were attempted, DA2's internal crypto engine failed with `STATUS_SEC_IMGHDR_HASH_VFY_FAIL (0xC002002B)`.
- Direct physical block writes using `Write Memory` were intercepted by DA2 address filter tables (`0x40004A80`/`0x400068A8`), rejecting writes to protected partitions with `STATUS_SEC_WRITE_DATA_NOT_ALLOWED (0xC002000C)`.

### Challenge 2: The Android Verified Boot (AVB) "Red State" Bootloop
Whenever the device booted using the authentic Global Little Kernel with mismatched or incomplete AVB metadata, Little Kernel's AVB validation routine (`0x4e1c7bcc`) returned an invalid verification state. On a locked bootloader (`unlocked: no`), LK triggered the mandatory AVB security response:
```text
Red State
Your device has failed verification and may not work properly.
Please download wireless update with PC or contact customer service.
Device will reboot in 5s.
```
In Red State, Little Kernel sleeps 5,000 ms (`0x4e1c140e`) and calls `arch_reset()`, trapping the device in an endless 5-second reboot cycle.

### Challenge 3: The Little Kernel OEM Unlock Gate
To allow Fastboot flashing of Android 10 Global partitions (`boot`, `recovery`, `super`, `vbmeta*`), the bootloader had to be unlocked via `fastboot flashing unlock`. However, executing this command initially failed with:
```text
FAILED (remote: Unlock operation is not allowed)
```
Disassembly of LK's command handler revealed that OEM unlocking is gated by function `0x4e1b39e0` (`get_unlock_allowed`). The Little Kernel reads a 4-byte flag from the end of the `frp` partition (`offset = frp_size - 4` / `0x0FFFFC`). Because the factory `frp` partition contained all zeros (`unlock_allowed == 0`), LK refused to unlock.

### Challenge 4: The Fastboot Client Multi-chunk Overwrite Bug
When flashing the 1.5 GB `super.bin` partition over Fastboot, the Windows Fastboot client noticed the image exceeded the device's advertised `max-download-size` (128 MB / `0x8000000`). Fastboot client-side split the raw image into 8 sequential chunks and sent each with `flash:super`.

However, Little Kernel's `cmd_flash` handler (`0x4e1b273a`) unconditionally writes every incoming `flash:super` payload starting at `linear_start_addr` (sector 0 of `super`). It lacked support for Android sparse chunk offsets. Consequently:
- Chunk 1 (sectors 0 to 128 MB) was written at offset 0.
- Chunk 2 was written at offset 0, overwriting Chunk 1.
- Chunk 8 (the final 38 MB) was written at offset 0, overwriting everything before it.
The dynamic partition geometry header (`gDla` at offset 4096) was replaced with random trailing image data. When Android booted, the kernel could not locate `/system` or `/vendor`, bouncing into Android Recovery with:
```text
Can't load Android system. Your data may be corrupt.
```

---

## 5. Root Causes and Engineering Breakthroughs

### Breakthrough 1: Preloader Handshake Interception to Fastboot
MediaTek devices execute the Preloader before initializing Little Kernel or the main OS. The Preloader checks USB COM for a specific ASCII handshake string. 

We developed a Win32 low-latency serial interceptor script (`preloader_fastboot_win32.py`). When the clock powers on or reboots from Red State, the script monitors `COM5`, immediately sends `b"FASTBOOT"`, and receives `b"TOOBTSAF"` from the Preloader. The Preloader forces Little Kernel to boot directly into **Fastboot Mode**, bypassing the OS boot cycle entirely without requiring test-points or hardware disassembly.

### Breakthrough 2: Bootloader Unlocking via GPT Partition De-masking
Static disassembly of Little Kernel routine `0x4e1b39e0` (`get_unlock_allowed`) yielded a vital insight:
```arm
0x4e1b39ea: mov r0, r4          ; r4 = "frp"
0x4e1b39ec: bl  #0x4e1c1638     ; partition_exists("frp")
0x4e1b39f0: cmp r0, #1
0x4e1b39f4: beq #0x4e1b3a38     ; If "frp" DOES NOT EXIST, branch!
...
0x4e1b3a38: ldr r0, [pc, #0x18] ; "frp paritition does not exist\n"
0x4e1b3a40: movs r0, #0
0x4e1b3a42: str r6, [r5]        ; *unlock_allowed = 1 (ENABLED!)
0x4e1b3a44: add sp, #0xc
0x4e1b3a46: pop {r4, r5, r6, r7, pc}
```
**If the partition named `frp` does not exist in the partition table, Little Kernel defaults `unlock_allowed = 1` and permits bootloader unlocking.**

Instead of attempting complex cryptographic writes to the protected `frp` partition, we modified the GPT partition table in software:
1. In `gpt_x04g_kingston.bin`, Partition 12's name was changed from `frp` to `frpx` in UTF-16LE.
2. Sector boundaries, sizes, and surrounding partition entries were left 100% identical.
3. The Partition Entry Array CRC32 and Header CRC32 were recalculated.
4. The modified partition table (`gpt_x04g_unlock.bin`) was flashed via SP Flash Tool.

Upon rebooting into Fastboot:
```text
fastboot flashing get_unlock_ability
(bootloader) unlock_ability = 1
OKAY [ 0.003s ]
```
Executing `fastboot flashing unlock` prompted the user on the LCD screen. Pressing `+` (Volume Up) executed `unlock_erase()`, committed the unlocked status to `seccfg`, and permanently set `unlocked: yes`.

### Breakthrough 3: Contiguous eMMC Block Streaming via SP Flash Tool
To overcome the Fastboot multi-chunk overwrite bug on `super.bin`:
1. We configured `convert_scatter_global.txt` with partition `SYS25` (`super`) defined as `type: NORMAL_ROM` with boundary check disabled.
2. We generated `download_super.xml` targeting only `preloader` (for DRAM buffer init) and `super` (1,610,612,736 bytes).
3. SP Flash Tool connected to DA2 and streamed the entire 1.50 GB `super.bin` file contiguously directly into physical eMMC blocks `0x61a00` through `0x3619ff` at **19.77 MB/s**.
4. The dynamic partition geometry (`gDla`), metadata (`0PLA`), and sub-volumes (`system`, `vendor`, `product`) were preserved with bit-perfect integrity.

### Breakthrough 4: Recovery Encryption Initialization
With `super.bin` properly written, Android Recovery was entered. Selecting **`Factory data reset`** in recovery formatted the `userdata` partition and generated the Android 10 cryptographic superblock. On the subsequent reboot, Android 10 mounted `/system`, `/vendor`, and `/data` cleanly, booting straight into the Global initialization setup screen.

---

## 6. Project Outcome Summary

The conversion was a complete success. The physical hardware has transitioned from a locked mainland Chinese device into an open Global variant running certified Android 10 software:

```text
Product:            mico_x04g
Build Version:      10/QP1A.190711.020/1.7.5
Build Fingerprint:  xiaomi/mico_x04g/mico_x04g:10/QP1A.190711.020/1.7.5:user/release-keys
Bootloader Status:  unlocked: yes (AVB Orange State)
Calibration Data:   Intact (proinfo, nvram)
```

---

## 7. Lessons Learned & Embedded Engineering Takeaways

1. **Static Binary Analysis Trumps Brute Force:** Disassembling Little Kernel (`lk.bin`) revealed the exact fallback behavior of `get_unlock_allowed` when `frp` is absent, transforming an impossible cryptographic barrier into a straightforward GPT rename.
2. **Never Trust Fastboot Client-Side Chunking on Legacy LK:** Fastboot clients assume devices support Android sparse image formats or stateful chunk offsets. On legacy or embedded Little Kernel builds, multi-chunk flashing can silently overwrite sector 0 repeatedly. Direct raw block streaming via SP Flash Tool is required for large dynamic partitions like `super`.
3. **Partition De-masking as a Safe OEM Unlock Primitive:** Renaming a gating partition in the GPT allows triggering internal bootloader recovery logic without touching physical sector allocations or corrupting adjacent user data.
4. **Strict Isolation of Device Calibration:** Segregating `proinfo` and `nvram` from download manifests ensures that full firmware transitions do not degrade radio calibration, Bluetooth pairing, or unique factory identity.
