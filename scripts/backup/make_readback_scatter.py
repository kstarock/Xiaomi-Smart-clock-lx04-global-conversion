#!/usr/bin/env python3
"""
make_readback_scatter.py - Generate SP Flash Tool readback configurations for factory calibration.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.

WARNING: SP Flash Tool v5.1812 Readback tab requires LINEAR PHYSICAL BYTE OFFSETS (Hex).
Previous drafts containing 0xC000 / 0x28000 were erroneous transcription bugs that read
unpartitioned space. The values below are verified against the physical eMMC GPT.

NOTE ON nvdata:
The stock Chinese firmware does NOT have an 'nvdata' partition; it
utilizes 'protect1' and 'protect2' for non-volatile radio storage.
'nvdata' is a Global Android 10 partition carved out at byte offset
0x0B340000 within a zero-filled region of the original Chinese
'metadata' partition.

The Global 'nvdata' partition was not directly written by the host
flashing tools. Its first-boot ext4 formatting and population by
nvram_daemon from preserved 'nvram' are [INFERRED], not directly
verified on the device.

"""

import os
import sys

# Authentic physical byte addresses for stock Chinese firmware calibration backup
CALIBRATION_PARTITIONS = [
    {
        "name": "proinfo",
        "region": "EMMC_USER",
        "start": "0x00080000",
        "length": "0x00300000",
        "size_mb": 3.0,
        "desc": "Factory serial number, barcode, and motherboard ID (LBA 1,024 - 7,167)"
    },
    {
        "name": "nvram",
        "region": "EMMC_USER",
        "start": "0x00380000",
        "length": "0x00500000",
        "size_mb": 5.0,
        "desc": "Factory RF calibration tables and Wi-Fi MAC address (LBA 7,168 - 17,407)"
    },
    {
        "name": "protect1",
        "region": "EMMC_USER",
        "start": "0x00880000",
        "length": "0x00A00000",
        "size_mb": 10.0,
        "desc": "Stock Chinese protect1 / NVRAM backup (LBA 17,408 - 37,887)"
    },
    {
        "name": "protect2",
        "region": "EMMC_USER",
        "start": "0x01280000",
        "length": "0x00A00000",
        "size_mb": 10.0,
        "desc": "Stock Chinese protect2 / NVRAM runtime (LBA 37,888 - 58,367)"
    },
    {
        "name": "boot1",
        "region": "EMMC_BOOT_1",
        "start": "0x00000000",
        "length": "0x00200000",
        "size_mb": 2.0,
        "desc": "Stock Chinese hardware boot partition 1 (Preloader)"
    }
]

def main():
    print("=" * 80)
    print("Xiaomi Smart Clock (LX04) Verified SP Flash Tool Readback Parameters")
    print("=" * 80)
    print("CRITICAL NOTE ON ADDRESS UNITS & FIRMWARE LAYOUT:")
    print("  1. SP Flash Tool v5.1812 Readback tab operates in HEXADECIMAL BYTE OFFSETS,")
    print("     NOT sector/LBA numbers.")
    print("  2. 'nvdata' does NOT exist on Chinese firmware (Chinese firmware uses 'protect1'")
    print("     and 'protect2'). 'nvdata' is created only in the Global GPT and populated")
    print("     automatically from 'nvram' on first boot. Do not attempt to read 'nvdata'")
    print("     from a stock Chinese device.\n")

    print(f"{'Partition':<16} | {'Region':<12} | {'Start (Bytes)':<14} | {'Length (Bytes)':<14} | {'Output Filename':<20}")
    print("-" * 84)
    for p in CALIBRATION_PARTITIONS:
        fname = f"{p['name']}.bin"
        print(f"{p['name']:<16} | {p['region']:<12} | {p['start']:<14} | {p['length']:<14} | {fname:<20}")

    print("-" * 84)
    print("\nDetailed Description:")
    for p in CALIBRATION_PARTITIONS:
        print(f"  * {p['name']:<16}: {p['desc']} ({p['size_mb']} MB)")

    print("\n[MANDATORY VERIFICATION STEP]")
    print("  After dumping, inspect 'proinfo.bin' in a hex editor:")
    print("  The first 32 bytes MUST contain your device serial / barcode (ASCII text string).")
    print("  If proinfo.bin contains all zeroes (0x00), the readback address was incorrect!")
    print("=" * 80)

if __name__ == "__main__":
    main()
