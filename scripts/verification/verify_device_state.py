#!/usr/bin/env python3
"""
verify_device_state.py - Query and verify device hardware state via Fastboot.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.
"""

import sys
import shutil
import subprocess

def run_fastboot(args):
    fastboot_cmd = shutil.which("fastboot") or "fastboot"
    res = subprocess.run([fastboot_cmd] + args, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    print("=" * 65)
    print("Xiaomi Smart Clock Hardware State Inspector")
    print("=" * 65)

    rc, stdout, _ = run_fastboot(["devices"])
    if rc != 0 or not stdout:
        print("[ERROR] No device detected in Fastboot mode.")
        print("Please connect the clock in Fastboot mode and retry.")
        sys.exit(1)

    print(f"[OK] Fastboot Device: {stdout}")
    print("-" * 65)

    # Key variables to audit
    vars_to_query = [
        "product",
        "version-bootloader",
        "version-preloader",
        "unlocked",
        "secure",
        "battery-soc-ok",
        "partition-size:super",
        "partition-type:super",
        "partition-size:boot",
        "partition-size:recovery"
    ]

    results = {}
    rc, stdout, stderr = run_fastboot(["getvar", "all"])
    combined = (stdout + "\n" + stderr).splitlines()

    for line in combined:
        line = line.strip()
        if line.startswith("(bootloader)"):
            parts = line[12:].strip().split(":", 1)
            if len(parts) == 2:
                results[parts[0].strip()] = parts[1].strip()

    print(f"{'Variable Name':<28} | {'Value'}")
    print("-" * 65)
    for v in vars_to_query:
        val = results.get(v, "N/A")
        print(f"{v:<28} | {val}")

    print("-" * 65)
    is_unlocked = results.get("unlocked") == "yes"
    is_global = results.get("product") == "mico_x04g"

    if is_unlocked and is_global:
        print("[SUCCESS] Device verified as unlocked Global Xiaomi Smart Clock (mico_x04g)!")
        sys.exit(0)
    elif is_global:
        print("[INFO] Device product is mico_x04g, but bootloader is currently locked.")
        sys.exit(0)
    else:
        print("[WARNING] Device state differs from expected Global target.")
        sys.exit(1)

if __name__ == "__main__":
    main()
