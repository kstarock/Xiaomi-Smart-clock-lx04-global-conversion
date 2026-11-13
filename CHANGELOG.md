# Changelog

All notable changes to the Xiaomi Smart Clock LX04 China-to-Global conversion project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.0] - 2026-11-11

### Added
- **Conversion Applications & Tooling Documentation Suite (`tools/`):**
  - `tools/README.md`: Central tooling index, toolchain architecture, and legal distribution/licensing policy.
  - `tools/TOOL_VERSIONS.md`: Authoritative matrix of verified tool versions, executable names, vendor origins, SHA-256 hashes, and hardware compatibility. Documents verified host binary SP Flash Tool `v5.1728.00` (`_SPFT.exe`) and `v5.1812.00` compatibility, Fastboot `302830efc153-android`, and `mtkclient` commit `118a000`.
  - `tools/sp-flash-tool/README.md`: In-depth guide for SP Flash Tool setup, XML download configurations, signed Download Agent (`DA_Mi_Hikaru-resign.bin`) selection, contiguous eMMC flashing, and byte-offset readback rules.
  - `tools/mtk-client/README.md`: Setup instructions for Bjoern Kerler's `mtkclient`, UsbDk/LibUSB filter driver configuration, and non-destructive diagnostic readback commands.
  - `tools/adb-fastboot/README.md`: Android SDK Platform Tools (ADB & Fastboot) guide, Windows PATH configuration, OEM bootloader unlock flow, and documentation of the Little Kernel multi-chunk flashing defect.
  - `tools/usb-drivers/README.md`: MediaTek USB VCOM (`usb2ser.sys`), BROM, and Google Fastboot driver installation and Windows signature verification troubleshooting.
  - `tools/utilities/README.md`: Documentation for host archive tools (Windows native `tar.exe`, 7-Zip), Python standard-library environment (zero external pip packages required for repository scripts; `pyserial` only needed for `mtkclient`), and conversion automation scripts.
- **Global X04G Firmware Documentation & Integrity Suite (`firmware/`):**
  - `firmware/global-x04g/README.md`: Detailed component breakdown of official Global build 1.7.5 (`mico_x04g` / `QP1A.190711.020`), partition targets, filesystem types, and extraction instructions. Explains verified source archive provenance (`dump_mico_x04g.tar.xz`) and technical basis for identical `tee1.bin`/`tee2.bin` hashes (OEM redundant slot packaging).
  - `firmware/global-x04g/SHA256SUMS.txt`: Authoritative cryptographic SHA-256 integrity manifest for all 13 mandatory and 3 optional Global partition images, cross-referenced against `dump_mico_x04g.tar.xz`.
  - `firmware/firmware_manifest.json`: Machine-readable partition manifest specifying partition names, exact byte sizes, verified source archive metadata, and SHA-256 hashes.
- Updated root `README.md` with links to the expanded `tools/` and `firmware/` resources.

---

## [1.2.0] - 2026-11-11

### Added
- Complete standalone open-source community repository structure.
- Python automation suite:
  - `check_environment.py`: Verifies Windows dependencies, Fastboot CLI, Python version, and COM ports.
  - `verify_checksums.py`: Cryptographic hash validator for all firmware files.
  - `preloader_fastboot_interceptor.py`: Low-latency Win32 ctypes serial handshake hook.
  - `flash_global_bootstack.py`: Automated Fastboot flashing of core AVB boot partitions.
  - `patch_gpt_unlock.py`: Automated tool to rename `frp` -> `frpx` and recalculate GPT CRC32 checksums.
  - `verify_device_state.py`: Post-conversion hardware state inspector.
- Detailed dedicated technical guides:
  - `HARDWARE_SPECIFICATIONS.md`
  - `FIRMWARE_ARCHITECTURE.md`
  - `PARTITION_MAP.md`
  - `TROUBLESHOOTING.md`
  - `RECOVERY_GUIDE.md`
  - `FAQ.md`
  - `GLOSSARY.md`
  - `prerequisites/WINDOWS_SETUP.md`
  - `prerequisites/DRIVER_SETUP.md`
  - `prerequisites/TOOL_VERSIONS.md`
- Added GitHub issue templates and CI syntax validation workflow.

### Status Updates
- **Microphone Array Subsystem:** Reclassified as **[VERIFIED BY OWNER]**. Far-field dual-microphone array and Everest ADC confirmed operational via repeated Google Assistant voice recognition tests on physical hardware. Total confirmed working hardware subsystems updated to 7 (OS Boot, Touchscreen, Display, Wi-Fi, Bluetooth, Audio, Microphone).
- **Google Assistant Voice Interaction:** Reclassified as **[VERIFIED BY OWNER]**. Repeated voice commands tested and confirmed operational: weather forecast query, current time query, and setting an alarm, with clear spoken audio feedback.
- **Xiaomi Companion App Integration:** Confirmed **[VERIFIED BY OWNER]**. Converted clock is detected and recognized in the official Xiaomi companion app.
- **OTA Updates:** Maintained strictly as **[UNTESTED]**. Automatic system updates should remain disabled.
- **Single-Unit Validation Notice:** All physical verification tests were performed by the device owner on a single Kingston 4GB eMMC development unit and have not yet been independently reproduced across other hardware variants.
- **Partition Calibration & Preservation Audit:** Removed inaccurate descriptions of the conversion as "non-destructive". Reconciled partition preservation accounting across all documentation to reflect exactly 6 original Chinese partitions preserved untouched (2 factory calibration partitions: `proinfo`, `nvram`; and 4 vendor security partitions: `tee1`, `tee2`, `kb`, `dkb`). Confirmed that stock Chinese firmware possessed no `nvdata` partition, that `persist` is a repartitioned zero-filled physical range rather than a preserved partition, and that Global `nvdata` first-boot ext4 formatting and population from `nvram` is explicitly classified as **[INFERRED]**.

---

## [1.1.0] - 2026-11-11

### Changed
- Clarified `BOOT1` physical partition state: confirmed by physical readback (`boot1_physical_backup.bin`) that Global preloader (`preloader_mico_x04g.bin`) is installed at offset `0x800` on the physical device.
- Reclassified `BOOT1` from untouched to modified physical partition; confirmed original Chinese `BOOT1` is archived as an offline file backup (`LX04-Backup/boot1.bin`).
- Verified secondary GPT (`sgpt`) readback (`readback_secondary_gpt_lba7405535_7405567.bin`) matches `gpt_backup_x04g_kingston.bin` bit-for-bit.
- Resolved `para` partition investigation: stock `para.bin` flashed via Fastboot to ensure pristine bootloader message state.
- Formalized operation counting into 3 tiers: 22 individual write/erase commands, 9 meaningful engineering phases, 8 failed attempts.

---

## [1.0.0] - 2026-11-10

### Initial Release
- Successful conversion from mainland China `mico_lx04` to official Global `mico_x04g` Android 10 (`QP1A.190711.020 / 1.7.5`).
- Initial postmortem documentation suite created: `PROJECT_POSTMORTEM.md`, `CONVERSION_TIMELINE.md`, `TRIALS_AND_ERRORS.md`, `FINAL_CONVERSION_GUIDE.md`, `PROJECT_STATISTICS.md`.
