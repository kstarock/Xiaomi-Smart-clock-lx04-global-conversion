# Utilities, Python Environment & Archive Extraction Guide

This guide documents the Python runtime dependencies, built-in system tools, archive utilities, and verification scripts used across the Xiaomi Smart Clock LX04 conversion project.

---

## 1. Python Runtime & Zero External Dependencies

Our conversion automation scripts (`preloader_fastboot_interceptor.py`, `flash_global_bootstack.py`, `patch_gpt_unlock.py`, `verify_checksums.py`, `run_full_audit.py`) run natively on Python 3 using **standard library modules only**.

### Requirements:
- **Python Version:** Python 3.8 or newer (tested on Python `3.15.1` on Windows; original conversion host version: UNKNOWN, 3.8+ compatible).
- **Official Download:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Installation Note:** During installation on Windows, ensure you check the box:
  ```text
  [X] Add python.exe to PATH
  ```

### External Packages:
- **Repository Scripts:** **ZERO external pip packages required**. No `pip install` commands are necessary.
- **Why no PySerial?** Early prototypes tested `pyserial`, but the ~500ms Preloader handshake window required sub-millisecond port polling. `preloader_fastboot_interceptor.py` uses direct Win32 `ctypes` calls (`kernel32.dll` via `CreateFileW`, `SetCommState`, `SetCommTimeouts`) to eliminate interpreter overhead.
- **External Tools Note:** `pyserial` is only required if you independently choose to run the external diagnostic utility `mtkclient` (`pip install pyserial`).

### Standard Library Modules Utilized:
- `ctypes`: Direct Win32 `kernel32.dll` access for zero-latency Preloader port polling, buffer flushing, and serial handshaking.
- `struct` & `binascii`: Parsing binary GPT partitions, Little Kernel GFH headers, and unpacking LBA records.
- `zlib` & `hashlib`: CRC32 checksum recalculation for modified GPT tables and SHA-256 image verification.
- `shutil` & `subprocess`: Automating Fastboot CLI commands and environmental prerequisite detection.
- `xml.etree.ElementTree`: Parsing SP Flash Tool XML configurations.

---

## 2. Archive & Decompression Utilities

The Global X04G firmware images are sourced from the verified archive `dump_mico_x04g.tar.xz` (or community fastboot packages).

### Primary Extractor: Windows Built-in `tar.exe`
Windows 10 (build 17063 and later) and Windows 11 include a native BSD `tar.exe` located at `C:\WINDOWS\system32\tar.exe` that natively supports both `.tar.xz` and `.tgz`:

```powershell
# Extracting verified .tar.xz archive directly into the firmware directory:
tar -xf dump_mico_x04g.tar.xz -C firmware/
```

### Optional GUI Extractor: 7-Zip
For users who prefer a graphical archive utility:
- **Application:** 7-Zip
- **Author:** Igor Pavlov
- **License:** GNU LGPL / BSD
- **Official Download:** [https://www.7-zip.org/](https://www.7-zip.org/)
- **Usage:** Right-click the `.tar.xz` archive -> **7-Zip** -> **Extract to "firmware\"**. (Note: `.tar.xz` archives may require extracting the `.tar` intermediate archive in a second step in 7-Zip GUI).

---

## 3. Repository Automation & Verification Scripts

The repository includes a suite of standalone Python utilities located in `scripts/`:

| Script Path | Purpose | Execution Command |
| :--- | :--- | :--- |
| **`scripts/setup/check_environment.py`** | Validates host Windows version, Python runtime, Fastboot CLI availability, and COM ports | `python scripts/setup/check_environment.py` |
| **`scripts/backup/make_readback_scatter.py`** | Generates an SP Flash Tool readback scatter file with verified byte offsets for calibration | `python scripts/backup/make_readback_scatter.py` |
| **`scripts/fastboot/preloader_fastboot_interceptor.py`** | High-speed Win32 serial hook that intercepts the 1-second Preloader window to force Fastboot mode | `python scripts/fastboot/preloader_fastboot_interceptor.py` |
| **`scripts/fastboot/flash_global_bootstack.py`** | Automates pre-flight device checks, unlock verification, and flashing of all AVB boot partitions | `python scripts/fastboot/flash_global_bootstack.py` |
| **`scripts/utilities/patch_gpt_unlock.py`** | Automatically patches a binary GPT table to de-mask `frp` -> `frpx` and recalculates CRC32 checksums | `python scripts/utilities/patch_gpt_unlock.py <input.bin> <output.bin>` |
| **`scripts/verification/verify_checksums.py`** | Validates SHA-256 hashes of all firmware images before flashing to prevent bricking | `python scripts/verification/verify_checksums.py` |
| **`scripts/verification/verify_device_state.py`** | Post-conversion inspector querying bootloader and Android system properties | `python scripts/verification/verify_device_state.py` |
| **`scripts/verification/run_full_audit.py`** | Master 7-stage verification suite auditing all scripts, GPTs, scatter, and manifests | `python scripts/verification/run_full_audit.py` |
