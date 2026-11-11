#!/usr/bin/env python3
"""
check_environment.py - Pre-conversion host environment and prerequisites validator.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.
"""

import sys
import os
import shutil
import subprocess

def print_header():
    print("=" * 65)
    print("Xiaomi Smart Clock LX04 -> X04G Host Environment Check")
    print("=" * 65)

def check_python_version():
    major, minor = sys.version_info.major, sys.version_info.minor
    print(f"[*] Checking Python version: {major}.{minor}.{sys.version_info.micro} ...", end=" ")
    if major == 3 and minor >= 8:
        print("[OK]")
        return True
    else:
        print("[FAIL] (Python 3.8+ is required)")
        return False

def check_platform():
    print(f"[*] Checking Operating System: {sys.platform} ...", end=" ")
    if sys.platform == "win32":
        print("[OK] (Windows)")
        return True
    else:
        print("[WARNING] (This conversion suite is designed and tested for Windows)")
        return False

def check_fastboot():
    print("[*] Checking Fastboot CLI executable ...", end=" ")
    fastboot_path = shutil.which("fastboot")
    if fastboot_path:
        try:
            res = subprocess.run(["fastboot", "--version"], capture_output=True, text=True, timeout=5)
            version_line = res.stdout.strip().split("\n")[0]
            print(f"[OK] ({version_line})")
            return True
        except Exception as e:
            print(f"[WARNING] (Found at {fastboot_path} but error executing: {e})")
            return False
    else:
        print("[FAIL] ('fastboot' not found in PATH)")
        print("    -> Download Android SDK Platform Tools and add to PATH.")
        return False

def check_com_ports():
    print("[*] Checking Windows COM Ports (MediaTek VCOM) ...")
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
        ports = []
        for i in range(winreg.QueryInfoKey(key)[1]):
            val_name, val_data, _ = winreg.EnumValue(key, i)
            ports.append(val_data)
        winreg.CloseKey(key)
        if ports:
            print(f"    Available COM ports detected: {', '.join(ports)}")
        else:
            print("    No active COM ports currently connected.")
        return True
    except Exception:
        print("    No serial ports found or registry access restricted.")
        return True

def check_directories():
    print("[*] Checking repository directory structure ...")
    required = ["docs", "prerequisites", "scripts", "configurations", "firmware", "checksums"]
    all_ok = True
    for req in required:
        if os.path.isdir(req):
            print(f"    [OK] Directory '{req}/'")
        else:
            print(f"    [FAIL] Missing required directory '{req}/'")
            all_ok = False
    return all_ok

def main():
    print_header()
    ok_py = check_python_version()
    ok_os = check_platform()
    ok_fb = check_fastboot()
    check_com_ports()
    ok_dir = check_directories()
    
    print("-" * 65)
    if ok_py and ok_os and ok_fb and ok_dir:
        print("[SUCCESS] Host environment meets all requirements for conversion!")
        sys.exit(0)
    else:
        print("[FAIL] Please resolve the issues marked [FAIL] before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
