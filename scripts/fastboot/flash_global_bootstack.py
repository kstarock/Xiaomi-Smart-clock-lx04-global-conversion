#!/usr/bin/env python3
"""
flash_global_bootstack.py - Flash Global Android 10 bootstack via Fastboot.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.

Flashes core partitions (boot, dtbo, vbmeta, recovery, cache, metadata, md_udc, para)
and formats userdata.
DOES NOT FLASH super.bin (super.bin must be flashed contiguously via SP Flash Tool).
"""

import sys
import os
import time
import shutil
import subprocess

def run_cmd(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    print("=" * 75)
    print("Xiaomi Smart Clock Global Android 10 Fastboot Bootchain Flasher")
    print("=" * 75)

    fastboot_cmd = shutil.which("fastboot") or "fastboot"

    # 1. Check device connectivity
    print("[*] Checking Fastboot device connectivity...")
    rc, stdout, stderr = run_cmd([fastboot_cmd, "devices"])
    if rc != 0 or not stdout:
        print("\n[ERROR] No device detected in Fastboot mode!")
        print("Please ensure your clock is connected and in Fastboot mode.")
        print("Run 'python scripts/fastboot/preloader_fastboot_interceptor.py' if needed.")
        sys.exit(1)

    device_serial = stdout.split()[0]
    print(f"    [OK] Detected Fastboot device: {device_serial}")

    # 2. Strict unlock state verification
    print("[*] Verifying bootloader unlock state...")
    rc, stdout, stderr = run_cmd([fastboot_cmd, "getvar", "unlocked"])
    combined = (stdout + " " + stderr).lower()
    if "unlocked: yes" not in combined:
        print("\n" + "!" * 75)
        print("[HARD STOP] Device bootloader is LOCKED!")
        print(f"Fastboot response: {stdout or stderr}")
        print("Flashing unsigned Global firmware to a locked bootloader is rejected by")
        print("MediaTek Little Kernel (LK) and will fail or cause device corruption.")
        print("You MUST complete Phase 4 (FRP de-mask and 'fastboot oem unlock') first.")
        print("!" * 75)
        sys.exit(1)

    print("    [OK] Bootloader is confirmed UNLOCKED ('unlocked: yes')")

    # 3. Pre-flight verification of all required image files
    flash_targets = [
        ("dtbo",           "firmware/dtbo.bin"),
        ("vbmeta",         "firmware/vbmeta.bin"),
        ("vbmeta_system",  "firmware/vbmeta_system.bin"),
        ("vbmeta_vendor",  "firmware/vbmeta_vendor.bin"),
        ("boot",           "firmware/boot.bin"),
        ("recovery",       "firmware/recovery.bin"),
        ("cache",          "firmware/cache.bin"),
        ("metadata",       "firmware/metadata.bin"),
        ("md_udc",         "firmware/md_udc.bin"),
        ("para",           "firmware/para.bin")
    ]

    print("[*] Validating presence of all firmware images before starting...")
    missing_files = []
    for part, path in flash_targets:
        if not os.path.isfile(path):
            missing_files.append((part, path))

    if missing_files:
        print("\n[ERROR] Missing required firmware images:")
        for part, path in missing_files:
            print(f"  - Partition '{part}': File '{path}' not found!")
        print("Aborting before any flash operation. Please place all Global images into 'firmware/'.")
        sys.exit(1)

    print(f"    [OK] All {len(flash_targets)} required image files are present on disk.")

    # 4. Explicit user confirmation
    print("-" * 75)
    print("WARNING: This operation will overwrite core partitions on your device")
    print("and erase the 'userdata' partition.")
    print("-" * 75)
    confirm = input("Type 'YES' to proceed with flashing: ").strip()
    if confirm != "YES":
        print("Aborted by user. No partitions were modified.")
        sys.exit(0)

    # 5. Execute flashing sequence
    print("-" * 75)
    for idx, (part, path) in enumerate(flash_targets, 1):
        file_size = os.path.getsize(path)
        print(f"[{idx}/{len(flash_targets)}] Flashing '{part}' ({file_size} B) from {path} ...", end=" ", flush=True)
        t0 = time.time()
        rc, out, err = run_cmd([fastboot_cmd, "flash", part, path])
        elapsed = time.time() - t0
        if rc == 0:
            print(f"[OK] ({elapsed:.2f}s)")
        else:
            print(f"[FAIL]")
            print(f"\n[ERROR] Fastboot flash failed for partition '{part}'!")
            print(f"Output: {out}")
            print(f"Error:  {err}")
            print("Aborting flashing sequence. Do NOT reboot until resolved.")
            sys.exit(2)

    # 6. Erase userdata
    print(f"[{len(flash_targets)+1}/{len(flash_targets)+1}] Erasing 'userdata' partition ...", end=" ", flush=True)
    t0 = time.time()
    rc, out, err = run_cmd([fastboot_cmd, "erase", "userdata"])
    elapsed = time.time() - t0
    if rc == 0:
        print(f"[OK] ({elapsed:.2f}s)")
    else:
        print(f"[FAIL]")
        print(f"\n[ERROR] Failed to erase 'userdata' partition!")
        print(f"Output: {out}")
        print(f"Error:  {err}")
        print("Device cannot boot into Android without clean userdata initialization.")
        sys.exit(3)

    print("=" * 75)
    print("[SUCCESS] All 10 core Global bootstack partitions successfully flashed!")
    print("=" * 75)
    print("CRITICAL MANDATORY INSTRUCTION:")
    print("  DO NOT REBOOT THE CLOCK INTO ANDROID YET!")
    print("  'super.bin' (1.50 GB) MUST now be flashed contiguously via SP Flash Tool.")
    print("  Attempting to boot without 'super.bin' will cause an immediate bootloop.")
    print("  Follow Phase 6 Step 6 in the Conversion Guide.")
    print("=" * 75)

if __name__ == "__main__":
    main()
