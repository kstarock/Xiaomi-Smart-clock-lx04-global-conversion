# HARDWARE & WARRANTY DISCLAIMER

**PLEASE READ THIS ENTIRE DOCUMENT CAREFULLY BEFORE PROCEEDING.**

Modifying embedded firmware, altering partition tables, flashing bootloaders, and unlocking security configurations on embedded MediaTek devices involves inherent risks of permanent, unrecoverable hardware damage ("hard-bricking").

---

## 1. Warranty Voidance
Executing any procedure described in this repository:
- **Will void your manufacturer warranty.**
- May violate terms of service regarding mainland China cloud services.
- Alters the cryptographic verification state of the device (Android Verified Boot will transition to `Orange State`).

---

## 2. Risk of Hard-Bricking
The Xiaomi Smart Clock (LX04) uses a MediaTek MT8167A System-on-Chip (SoC) with hardware eMMC storage (Kingston 4GB `M62704`).

### Critical Destructive Traps to Avoid
1. **NEVER use `Format All + Download` in SP Flash Tool:**
   Executing a global format wipes eMMC sectors containing irreplaceable factory calibration data:
   - `proinfo` (Offset `0x00080000`, LBA `1,024`): Motherboard serial numbers, factory barcode, and hardware revision ID.
   - `nvram` (Offset `0x00380000`, LBA `7,168`): Factory RF calibration tables, permanent Wi-Fi MAC address, and Bluetooth parameters.
   Formatting these will permanently destroy factory Wi-Fi and RF calibration, leaving the device unable to connect to wireless networks.
   *(Note: The stock Chinese firmware had no `nvdata` partition; it relied on `nvram`, `protect1`, and `protect2`. Under Global Android 10, the newly defined `nvdata` partition at `0x0B340000` undergoes first-boot ext4 formatting and population from preserved `nvram` [INFERRED] based on standard MediaTek Android 10 architecture. Destroying `nvram` deprives `nvdata` of the source calibration required to initialize).*

2. **NEVER overwrite eMMC `BOOT1` without an offline backup:**
   The MediaTek MT8167 BootROM (BROM) executes preloader code from the physical eMMC `BOOT1` hardware partition. SP Flash Tool operations with `preloader` enabled write `preloader_mico_x04g.bin` to `BOOT1`. Always preserve your original Chinese `BOOT1` backup before proceeding.

3. **NEVER use Fastboot client-side sparse chunking on `super.bin`:**
   As thoroughly documented in our postmortem, the Little Kernel Fastboot implementation on MT8167 contains a critical write-offset cursor bug. Flashing `super.bin` via multi-chunk Fastboot corrupts the dynamic filesystem superblock. You must use contiguous SP Flash Tool streaming.

---

## 3. Strict Limitation of Liability
THIS SOFTWARE, SCRIPTS, CONFIGURATIONS, AND DOCUMENTATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. IN NO EVENT SHALL THE AUTHORS, MAINTAINERS, OR CONTRIBUTORS BE LIABLE FOR ANY CLAIM, DAMAGES, LOSS OF DATA, DEVICE BRICKING, LOSS OF HARDWARE FUNCTIONALITY, OR EXPENSES ARISING OUT OF THE USE OR INABILITY TO USE THIS GUIDE.

YOU ASSUME FULL RESPONSIBILITY FOR ANY ACTION PERFORMED ON YOUR PHYSICAL HARDWARE.
