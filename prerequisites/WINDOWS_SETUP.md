# Windows Environment & System Preparation

Follow these instructions to configure your Windows PC before attempting the conversion.

---

## 1. Operating System Requirements
- **Supported OS:** Windows 10 (64-bit) or Windows 11 (64-bit).
- **Architecture:** x86_64 (AMD64 / Intel 64). ARM64 Windows is untested.
- **Privileges:** Administrator privileges are recommended to access low-level USB COM ports and manage MediaTek drivers.

---

## 2. Python Environment Installation
Python 3.8 or higher is required to run our automation and verification scripts.

1. Download the official installer from [python.org](https://www.python.org/downloads/).
2. During installation, **ensure you check: "Add python.exe to PATH"**.
3. Verify your installation by opening Windows PowerShell and typing:
   ```powershell
   python --version
   ```
   *Expected Output: `Python 3.8.x` or higher.*

### Zero External Dependencies
All automation scripts in this repository strictly use Python built-in standard libraries (`ctypes`, `wintypes`, `struct`, `zlib`, `subprocess`, `argparse`, `shutil`, `hashlib`). **No `pip install` commands or external packages (such as `pyserial`) are required.**

---

## 3. Android Platform Tools (Fastboot CLI)
1. Download official Android SDK Platform Tools from Google:
   [https://developer.android.com/tools/releases/platform-tools](https://developer.android.com/tools/releases/platform-tools)
2. Extract the ZIP archive to a permanent folder, for example: `C:\platform-tools\`.
3. Add `C:\platform-tools\` to your Windows System `PATH` environment variable:
   - Press `Win + R`, type `sysdm.cpl`, press Enter.
   - Go to **Advanced** tab -> click **Environment Variables**.
   - Under **User variables** or **System variables**, select `Path` -> click **Edit**.
   - Click **New** -> enter `C:\platform-tools` -> click **OK**.
4. Test by opening a new PowerShell window and typing:
   ```powershell
   fastboot --version
   ```
   *Expected Output: `fastboot version 34.x.x` (or compatible).*

---

## 4. Hardware USB Connection Recommendations
- Use a high-quality Micro-USB data cable (verify that the cable carries data lines, not just power charging).
- Connect directly to a motherboard USB 2.0 or USB 3.0 root hub port on the back of your desktop PC (or direct laptop port).
- **Avoid unpowered USB hubs or keyboard passthrough ports**, which can cause packet drops during the 1.5 GB `super.bin` flash.
