# TRIALS AND ERRORS: Technical Postmortem of Flashing Failures & Defect Resolutions

**Document Version:** 1.0.0  
**Project:** Xiaomi Smart Clock LX04 China-to-Global Conversion  
**Platform:** MediaTek MT8167A / eMMC Kingston 4GB (`M62704`)  
**Scope:** In-depth technical autopsy of all major failures, error codes, reverse engineering traces, and eventual breakthrough resolutions.

---

## 1. Overview of Flashing Trials & Engineering Failures

During the conversion process, 8 critical engineering obstacles and cryptographic barriers were encountered. Each failure was thoroughly investigated using static assembly disassembly, binary protocol logging, and eMMC readback comparison.

| # | Trial / Stage | Error Message / Code | Subsystem / Protocol | Root Cause Classification | Resolution Status |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | Scatter Loading | `STATUS_ERR_PMT_CHANGED_FOR_ROM (0xC0040003)` | SP Flash Tool PMT Engine | Partition Layout Incompatibility | **Resolved** (GPT Synthesis) |
| **2** | Patched DA Injection | `STATUS_DA_HASH_MISMATCH (0xC0070004)` | MT8167 BROM Security | Cryptographic Stage 1/2 Verification | **Resolved** (OEM Signed DA) |
| **3** | Direct DA Boot Flash | `STATUS_SEC_IMGHDR_TYPE_MISMATCH (0xC0020029)` | DA2 Image Validation Dispatcher | Android v2 Boot Header Zero DTB Offset | **Resolved** (Fastboot Flashing) |
| **4** | Spliced Cert Flash | `STATUS_SEC_IMGHDR_HASH_VFY_FAIL (0xC002002B)` | DA2 Crypto Verifier (`0x4002ec64`) | Spliced Signature vs Payload Hash Mismatch | **Resolved** (Bootloader Unlock) |
| **5** | Direct Write Memory | `STATUS_SEC_WRITE_DATA_NOT_ALLOWED (0xC002000C)` | DA2 Flash Driver Memory Filter | eMMC Address Range Hardware Protection | **Resolved** (Bypassed via Fastboot) |
| **6** | Containerized FRP Flash | `STATUS_SEC_BUFFER_CHECK_FAIL (0xC002004B)` | DA2 Container Parser (`0x40030244`) | External Signature Range Upper Bound = 0 | **Resolved** (Partition De-masking) |
| **7** | Fastboot Unlock Attempt | `FAILED (remote: Unlock operation is not allowed)` | Little Kernel (`0x4e1b39e0`) | FRP Partition Bitflag Enforcement (`0x0FFFFC`) | **Resolved** (`frpx` De-masking) |
| **8** | Fastboot Super Flashing | Recovery Loop: `can't load android system` | Fastboot Multi-Chunk Sparse Protocol | LK Fastboot Client Offset Pointer Stagnation | **Resolved** (Contiguous SPFT Flashing) |

---

## 2. Detailed Technical Autopsy of Each Failure

---

### Failure 1: Partition Table Incompatibility (`0xC0040003`)

#### Context & Execution
- **Attempt:** Attempting to flash target Global scatter (`MT8167_Android_scatter.txt`) directly onto the factory Chinese partition scheme using SP Flash Tool v5.1812.
- **Observed Result:** Operation aborted immediately upon BROM connection.
  ```text
  ERROR: STATUS_ERR_PMT_CHANGED_FOR_ROM (0xC0040003)
  [HINT]: Please select "Firmware Upgrade" or "Format All + Download" instead of "Download Only".
  ```

#### Technical Autopsy & Root Cause
- The MT8167 BROM/DA contains a PMT (Partition Marker Table) engine that validates the layout defined in the host scatter file against the GPT partitions stored in eMMC sectors 1–33.
- The original Chinese firmware (`mico_lx04`) utilized Android 8.1 Oreo with 21 static partitions, including separate `system` (1.07 GB), `vendor` (314 MB), and `odmdtbo` (1 MB) partitions.
- The Global firmware (`mico_x04g`) utilized Android 10 with Dynamic Partitions, replacing those separate blocks with a single 1.50 GB `super` partition.
- SP Flash Tool detected differing start addresses and partition boundaries, raising error `0xC0040003`.

#### Investigation & Risk Assessment
- The GUI tool recommended "Format All + Download" or "Firmware Upgrade".
- Reverse engineering of the MT8167 eMMC memory map revealed that executing "Format All" would erase eMMC blocks `0x00080000` (`proinfo`) and `0x00380000` (`nvram`), permanently destroying factory device identity, Wi-Fi MAC addresses, and RF calibration tables (and preventing Global Android 10 from initializing `nvdata`).

#### Resolution
- Rejected automated destructive modes (`Format All + Download`, `Firmware Upgrade`) to protect physical eMMC calibration regions (`proinfo`, `nvram`).
- Generated bit-exact primary and secondary GPT images (`gpt_x04g_kingston.bin` and `gpt_backup_x04g_kingston.bin`) calibrated strictly for the Kingston 4GB sector count (`7,405,568` sectors).
- Flashed GPT tables directly via controlled partition update, aligning the on-flash geometry with Android 10 while preserving untouched sectors for calibration partitions. Verified via readback that both primary and secondary GPT were updated consistently.
- Preserved original Chinese `BOOT1` contents in offline backups (`LX04-Backup/boot1.bin`), while the device's physical `BOOT1` partition hosts the official Global preloader (`preloader_mico_x04g.bin` at offset `0x800`).

---

### Failure 2: Cryptographic DA Injection Lockout (`0xC0070004`)

#### Context & Execution
- **Attempt:** Deploying an insecure/patched Download Agent (`DA_PL.bin` / patched `DA2`) to bypass DA write restrictions and force direct physical writes to protected security partitions.
- **Observed Result:** SP Flash Tool failed during Stage 1 connection.
  ```text
  ERROR: STATUS_DA_HASH_MISMATCH (0xC0070004)
  [HINT]: The DA image checksum does not match the public key manifest in BROM.
  ```

#### Technical Autopsy & Root Cause
- The MediaTek MT8167 SoC implements a two-stage DA bootloader mechanism:
  1. **DA Stage 1:** Downloaded by BROM into internal SRAM. BROM verifies Stage 1 against an RSA public key hash fused into the SoC efuse array.
  2. **DA Stage 2:** Stage 1 downloads Stage 2 (the full flashing driver) to DRAM address `0x40000000`. Before executing, Stage 1 hashes Stage 2 and compares the SHA-256 against an embedded cryptographic manifest.
- Modifying bytes in DA Stage 2 invalidated the SHA-256 integrity check, causing Stage 1 to abort execution with `0xC0070004`.

#### Resolution
- Abandoned custom/unauthorized DA binaries completely.
- Identified and standardized upon the authentic OEM signed Download Agent: `DA_Mi_Hikaru-resign.bin` (which matches the Xiaomi hardware certificate and passes both BROM and Stage 1 cryptographic checks).

---

### Failure 3: Android Boot Image Header Mismatch (`0xC0020029`)

#### Context & Execution
- **Attempt:** Flashing the official Global Android 10 kernel (`boot.bin`, 16,777,216 bytes) via SP Flash Tool using the OEM-signed DA.
- **Observed Result:** Flash failed immediately after transferring payload buffer.
  ```text
  ERROR: STATUS_SEC_IMGHDR_TYPE_MISMATCH (0xC0020029)
  ```

#### Technical Autopsy & Root Cause
- Binary inspection of the official `boot.bin` revealed an Android Boot Image Header Version 2 structure:
  ```text
  Offset 0x000: Magic 'ANDROID!' (0x41 0x4E 0x44 0x52 0x4F 0x49 0x44 0x21)
  Offset 0x008: kernel_size  = 0x00B2E248 (11,723,336 bytes)
  Offset 0x010: ramdisk_size = 0x001B6193 (1,794,451 bytes)
  Offset 0x660: dtb_size     = 0x00000000 (0 bytes)
  ```
- In Android 10, the device tree blob was moved out of `boot.bin` into a standalone `dtbo.bin` partition.
- The OEM DA2 parser at routine `0x4002EC64` expects MediaTek legacy boot images containing embedded DTB payloads at header offset `0x660`. Because `dtb_size == 0`, the certificate offset parser calculated an invalid offset, causing the image type validator to reject the header.

#### Resolution
- Do not attempt to flash modern Android 10 AVB boot images via legacy DA2 download routines.
- Route all AVB image flashing (`boot`, `dtbo`, `vbmeta`, `recovery`) through Fastboot once the bootloader is unlocked.

---

### Failure 4: Spliced Signature Authentication Failure (`0xC002002B`)

#### Context & Execution
- **Attempt:** Constructing a hybrid boot image (`boot_mtk_signed.bin`) by splicing the signed GFH (Generic File Header) and MediaTek certificate trailer from an authentic Chinese engineering image (`boot-verified.img`) onto the Global Android 10 kernel.
- **Observed Result:** SP Flash Tool rejected the hybrid image.
  ```text
  ERROR: STATUS_SEC_IMGHDR_HASH_VFY_FAIL (0xC002002B)
  ```

#### Technical Autopsy & Root Cause
- MediaTek's secure boot verification engine inside DA2 (`0x4002EC64`) computes the SHA-256 hash across the entire payload body defined in the GFH length field.
- The decrypted signature table inside the spliced certificate contained the SHA-256 hash of the *original Chinese Android 8.1 kernel*, not the Android 10 kernel.
- The cryptographic hash verification routine compared the computed hash against the decrypted manifest hash, detected the mismatch, and halted the write with `0xC002002B`.

#### Resolution
- Demonstrated that without Xiaomi's private RSA signing key, DA2-level signature splicing is mathematically impossible.
- Re-oriented project strategy toward unlocking Little Kernel's Fastboot engine.

---

### Failure 5: Flash Driver Memory Filter Protection (`0xC002000C`)

#### Context & Execution
- **Attempt:** Using SP Flash Tool's low-level "Write Memory" interface to write directly to physical sectors corresponding to the `seccfg` partition in an attempt to manually flip the bootloader lock status byte.
- **Observed Result:** Write rejected by DA2.
  ```text
  ERROR: STATUS_SEC_WRITE_DATA_NOT_ALLOWED (0xC002000C)
  ```

#### Technical Autopsy & Root Cause
- Disassembly of `DA_Mi_Hikaru-resign.bin` Stage 2 driver revealed an internal memory protection dispatch table.
- Direct raw physical writes via the `Write Memory` protocol are subjected to address range filtering:
  - Partitions marked with critical security flags (`seccfg`, `boot1`, `rpmb`, `preloader`) are blocked by the flash driver unless an authorized hardware token or challenge-response session is authenticated.
- Raw writes to these address ranges trigger an immediate hardware protection fault (`0xC002000C`).

#### Resolution
- Abandoned direct `Write Memory` approaches.
- Confirmed that bootloader unlock flags must be set legitimately through Little Kernel's authorized `fastboot flashing unlock` interface.

---

### Failure 6: External Signature Buffer Bounds Failure (`0xC002004B`)

#### Context & Execution
- **Attempt:** Packaging raw unauthenticated binaries (such as an empty `frp.bin` or modified `seccfg.bin`) inside synthetic GFH (Generic File Header) containers and flashing via SP Flash Tool `Download`.
- **Observed Result:** SP Flash Tool reported:
  ```text
  ERROR: STATUS_SEC_BUFFER_CHECK_FAIL (0xC002004B)
  ```

#### Technical Autopsy & Root Cause
- Analyzed routine `0x40030244` (`buf_chk`) in DA2.
- When an image header identifies as GFH (`0x58881688`), the parser validates the buffer boundaries against an external signature descriptor (`allinone_ext_sig`).
- If no corresponding external signature block is mapped in the scatter configuration, the upper bound pointer defaults to `0x00000000`.
- The bounds check `(image_end <= upper_bound)` failed with a buffer check fault (`0xC002004B`).

#### Resolution
- Concluded that arbitrary non-OEM partitions cannot be injected through DA2 flashing routines.

---

### Failure 7: Little Kernel Fastboot Unlock Rejection

#### Context & Execution
- **Attempt:** Entering Fastboot via the serial handshake script and issuing:
  ```powershell
  fastboot flashing unlock
  ```
- **Observed Result:**
  ```text
  FAILED (remote: Unlock operation is not allowed)
  ```

#### Technical Autopsy & Root Cause
- Disassembly of Little Kernel (`lk.bin`) at function `get_unlock_allowed` (`0x4e1b39e0`):
  ```armasm
  4E1B39E0  PUSH    {R4, LR}
  4E1B39E2  LDR     R0, =aFrp          ; "frp"
  4E1B39E4  BL      partition_get_len
  4E1B39E8  CMP     R0, #0
  4E1B39EA  BEQ     loc_unlock_allow   ; If "frp" not found -> unlock_allowed = 1
  4E1B39EC  LDR     R0, =aFrp          ; "frp"
  4E1B39EE  LDR     R1, =0xFFFFC       ; Read offset 0xFFFFC (last 4 bytes of 1MB FRP)
  4E1B39F0  BL      partition_read_word
  4E1B39F4  AND     R0, R0, #1         ; Bit 0 check
  4E1B39F8  CMP     R0, #1
  4E1B39FA  BEQ     loc_unlock_allow
  4E1B39FC  MOV     R0, #0             ; Return 0: Unlock not allowed!
  4E1B39FE  POP     {R4, PC}
  ```
- In Android devices, the "OEM Unlocking" setting in Developer Options writes byte `0x01` to offset `0x0FFFFC` of the `frp` partition.
- Because the device was locked in the Chinese firmware with no Developer Options UI access, offset `0x0FFFFC` contained `0x00`, causing LK to reject the unlock command.

#### Investigation & The De-masking Discovery
- Notice the check at `4E1B39EA`: If the partition named `frp` does *not* exist in the partition table, the routine branches directly to `loc_unlock_allow` (returning `1`).
- The developer implemented this fallback so that prototype engineering boards without an FRP partition could be unlocked freely.

#### Resolution
- Modified the Primary GPT binary (`gpt_x04g_unlock.bin`):
  - Changed partition entry 12 name from `frp\0` to `frpx`.
  - Recalculated CRC32 checksums for partition entries and GPT header.
- Flashed `gpt_x04g_unlock.bin` to eMMC via SP Flash Tool.
- Re-entered Fastboot and re-ran `fastboot flashing unlock`.
- LK checked for `frp`, failed to find it, defaulted `unlock_allowed = 1`, and displayed the hardware confirmation screen on the LCD (*"press + to unlock"*).
- User pressed physical Volume+, permanently setting `seccfg` to `unlocked: yes`.

---

### Failure 8: Fastboot Multi-Chunk Write Defect & Recovery Bootloop

#### Context & Execution
- **Attempt:** Flashing the 1.50 GB Android 10 Dynamic Partitions container (`super.bin`, 1,610,612,736 bytes) via Fastboot:
  ```powershell
  fastboot flash super super.bin
  ```
- **Observed Result:** Fastboot chunked the binary into 8 segments (`sparse0` to `sparse7`) and reported `OKAY` for all chunks.
- Upon reboot, the device displayed `Red State` and dropped directly into Android Recovery:
  ```text
  xiaomi/mico_x04g/mico_x04g
  10/QP1A.190711.020/1.7.5
  user /release-keys
  can't load android system your data may be corrupt
  ```
- Attempting "Factory data reset" repeatedly returned to the same recovery screen.

#### Technical Autopsy & Root Cause
- SP Flash Tool readback of the first 50 MB of the `super` partition revealed that the Dynamic Partition metadata header `0x67446c61` (`gDla`) was completely missing from sector 0.
- Detailed analysis revealed a defect in Little Kernel's Fastboot flash handler on MT8167:
  - When the Fastboot client transmits fragmented chunks (`super.bin_sparse0`, `super.bin_sparse1`, etc.), LK receives each chunk via download buffer but fails to maintain an incremental physical sector write cursor across separate `flash` packets.
  - Instead, LK reset the target partition write offset to `0x00000000` for *every* incoming chunk.
  - As a result, chunk 0 was written to offset 0, then chunk 1 overwrote offset 0, and finally chunk 7 (the last 38 MB) overwrote offset 0.
  - The actual dynamic filesystem was destroyed, leaving Android with an invalid `/system` partition, triggering an automatic fallback to Recovery.

#### Resolution
- Abandoned Fastboot chunked flashing for `super.bin`.
- Created an SP Flash Tool XML download manifest (`download_super.xml`) targeting the `super` partition with `type: NORMAL_ROM`.
- Streamed the unfragmented, contiguous 1,610,612,736 bytes of `super.bin` directly via SP Flash Tool's verified DA engine at 19.77 MB/s in a single uninterrupted operation.
- Restored standard GPT partition names (`gpt_x04g_kingston.bin` restoring `frp`).
- Re-entered Recovery, executed `Factory data reset` to format `/data` with fresh Android 10 encryption keys, and rebooted into a fully functional Global Android 10 system.
