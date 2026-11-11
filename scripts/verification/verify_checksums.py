#!/usr/bin/env python3
"""
verify_checksums.py - Cryptographic SHA-256 integrity validator.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.
"""

import sys
import os
import hashlib
import argparse

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower()

def main():
    parser = argparse.ArgumentParser(description="Validate file integrity against SHA256SUMS manifest.")
    parser.add_argument("--manifest", default="checksums/SHA256SUMS.txt", help="Path to checksums file")
    parser.add_argument("--firmware-only", action="store_true", help="Only verify firmware/ directory files")
    args = parser.parse_args()

    if not os.path.isfile(args.manifest):
        print(f"[ERROR] Manifest file '{args.manifest}' not found!")
        sys.exit(1)

    print("=" * 75)
    print("SHA-256 Firmware Integrity Validator")
    print(f"Manifest: {args.manifest}")
    print("=" * 75)

    passed = 0
    failed = 0
    missing = 0
    total = 0

    with open(args.manifest, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts[0].lower(), parts[1].strip()

            if args.firmware_only and not rel_path.startswith("firmware/"):
                continue

            total += 1
            if not os.path.isfile(rel_path):
                print(f"[MISSING]  {rel_path}")
                missing += 1
                continue

            actual_hash = compute_sha256(rel_path)
            if actual_hash == expected_hash:
                print(f"[MATCH]    {rel_path}")
                passed += 1
            else:
                print(f"[MISMATCH] {rel_path}")
                print(f"    Expected: {expected_hash}")
                print(f"    Actual:   {actual_hash}")
                failed += 1

    print("-" * 75)
    print(f"Total: {total} | Matched: {passed} | Mismatched: {failed} | Missing: {missing}")
    print("-" * 75)

    if failed > 0:
        print("[FAIL] Corrupt or modified files detected! DO NOT FLASH!")
        sys.exit(2)
    elif missing > 0:
        print("[WARNING] Some files are missing. Ensure all firmware files are in place.")
        sys.exit(1)
    else:
        print("[SUCCESS] All verified files match their cryptographic SHA-256 sums!")
        sys.exit(0)

if __name__ == "__main__":
    main()
