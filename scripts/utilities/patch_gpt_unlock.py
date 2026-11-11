#!/usr/bin/env python3
"""
patch_gpt_unlock.py - De-mask or restore FRP partition name in GPT binaries.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.

Implements the bootloader unlock breakthrough by changing partition 12 'frp' to 'frpx'
(or restoring 'frpx' to 'frp') with strict pre/post CRC32 verification and bounds checks.
"""

import sys
import os
import struct
import zlib
import argparse

def validate_and_parse_gpt(data, is_backup=False):
    """
    Validates GPT structure, bounds, and verifies both Header CRC and Partition Array CRC.
    Returns (hdr_offset, pe_offset, hdr_dict) or None on failure.
    """
    if len(data) < 1024:
        print("[ERROR] File too small to contain a valid GPT.")
        return None

    if not is_backup:
        # Primary GPT: Header in Sector 1 (512-1023), Entries start at Sector 2 (1024)
        hdr_offset = 512
        pe_offset = 1024
    else:
        # Backup GPT: In standalone dump (16,896 bytes), entries are at 0..16383, header at 16384..16895
        # In larger dump, header is at len(data) - 512
        hdr_pos = data.find(b'EFI PART')
        if hdr_pos == -1:
            print("[ERROR] EFI PART signature not found in backup GPT!")
            return None
        hdr_offset = hdr_pos
        if hdr_offset >= 16384:
            pe_offset = 0
        else:
            pe_offset = hdr_offset + 512

    if hdr_offset + 92 > len(data):
        print(f"[ERROR] Buffer overflow: header offset {hdr_offset} exceeds data size {len(data)}.")
        return None

    hdr_raw = data[hdr_offset:hdr_offset+92]
    magic, rev, hdr_sz, hdr_crc, res, my_lba, alt_lba, first_lba, last_lba, guid, pe_lba, num_pe, pe_sz, pe_crc = struct.unpack(
        '<8sIIIIQQQQ16sQIII', hdr_raw
    )

    if magic != b'EFI PART':
        print(f"[ERROR] Invalid GPT Magic: expected b'EFI PART', got {magic}")
        return None

    if hdr_sz < 92 or hdr_sz > 512:
        print(f"[ERROR] Invalid GPT header size: {hdr_sz}")
        return None

    if pe_sz < 128:
        print(f"[ERROR] Invalid partition entry size: {pe_sz}")
        return None

    pe_total_bytes = num_pe * pe_sz
    if pe_offset + pe_total_bytes > len(data):
        print(f"[ERROR] Partition entry array bounds exceed file size: {pe_offset + pe_total_bytes} > {len(data)}")
        return None

    # Verify input partition array CRC
    pe_raw = data[pe_offset:pe_offset + pe_total_bytes]
    calc_pe_crc = zlib.crc32(pe_raw) & 0xFFFFFFFF
    if calc_pe_crc != pe_crc:
        print(f"[ERROR] Input Partition Array CRC mismatch! Stored: 0x{pe_crc:08X}, Computed: 0x{calc_pe_crc:08X}")
        return None

    # Verify input header CRC (with CRC field at 16:20 zeroed)
    hdr_copy = bytearray(data[hdr_offset:hdr_offset + hdr_sz])
    hdr_copy[16:20] = b'\x00\x00\x00\x00'
    calc_hdr_crc = zlib.crc32(hdr_copy) & 0xFFFFFFFF
    if calc_hdr_crc != hdr_crc:
        print(f"[ERROR] Input Header CRC mismatch! Stored: 0x{hdr_crc:08X}, Computed: 0x{calc_hdr_crc:08X}")
        return None

    hdr_dict = {
        'hdr_sz': hdr_sz,
        'hdr_crc': hdr_crc,
        'my_lba': my_lba,
        'alt_lba': alt_lba,
        'pe_lba': pe_lba,
        'num_pe': num_pe,
        'pe_sz': pe_sz,
        'pe_crc': pe_crc,
        'pe_total_bytes': pe_total_bytes
    }
    return hdr_offset, pe_offset, hdr_dict

def patch_gpt_file(input_path, output_path, restore=False, is_backup=False, in_place=False, dry_run=False):
    if not os.path.isfile(input_path):
        print(f"[ERROR] Input file '{input_path}' not found!")
        return False

    if os.path.abspath(input_path) == os.path.abspath(output_path) and not in_place and not dry_run:
        print(f"[ERROR] Input and output paths are identical: '{input_path}'")
        print("To overwrite in-place, pass --in-place.")
        return False

    with open(input_path, "rb") as f:
        data = bytearray(f.read())

    print(f"[*] Inspecting: {input_path} ({len(data)} bytes, is_backup={is_backup})")
    parsed = validate_and_parse_gpt(data, is_backup=is_backup)
    if not parsed:
        return False

    hdr_offset, pe_offset, h = parsed
    print(f"    [OK] Input CRC valid! (PE CRC: 0x{h['pe_crc']:08X}, Header CRC: 0x{h['hdr_crc']:08X})")

    old_name = "frpx" if restore else "frp"
    new_name = "frp" if restore else "frpx"
    old_utf16 = old_name.encode("utf-16le")
    new_utf16 = new_name.encode("utf-16le")

    found_idx = None
    for i in range(h['num_pe']):
        entry_offset = pe_offset + (i * h['pe_sz'])
        name_raw = data[entry_offset + 56 : entry_offset + 128]
        name_str = name_raw.decode("utf-16le", errors="ignore").rstrip("\x00")
        if name_str == old_name:
            found_idx = i
            break

    if found_idx is None:
        print(f"[ERROR] Partition '{old_name}' NOT FOUND in {input_path}!")
        print("Hard failure: refusing to modify GPT when target partition name is missing.")
        return False

    entry_offset = pe_offset + (found_idx * h['pe_sz'])
    print(f"    [+] Found target partition '{old_name}' at Entry #{found_idx} (byte offset 0x{entry_offset:X})")

    # Replace partition name with padded utf-16
    data[entry_offset + 56 : entry_offset + 128] = b'\x00' * 72
    data[entry_offset + 56 : entry_offset + 56 + len(new_utf16)] = new_utf16

    # Recalculate Partition Entries Array CRC32
    pe_raw_new = data[pe_offset : pe_offset + h['pe_total_bytes']]
    new_pe_crc = zlib.crc32(pe_raw_new) & 0xFFFFFFFF
    struct.pack_into('<I', data, hdr_offset + 88, new_pe_crc)

    # Recalculate Header CRC32 (with header CRC field zeroed)
    hdr_copy = bytearray(data[hdr_offset : hdr_offset + h['hdr_sz']])
    hdr_copy[16:20] = b'\x00\x00\x00\x00'
    new_hdr_crc = zlib.crc32(hdr_copy) & 0xFFFFFFFF
    struct.pack_into('<I', data, hdr_offset + 16, new_hdr_crc)

    # Post-patch self-verification
    post_check = validate_and_parse_gpt(data, is_backup=is_backup)
    if not post_check:
        print("[ERROR] Post-patch validation failed! Generated invalid GPT structure.")
        return False

    print(f"    [OK] Transformed: '{old_name}' -> '{new_name}'")
    print(f"    [OK] Recalculated PE CRC: 0x{new_pe_crc:08X} | Header CRC: 0x{new_hdr_crc:08X}")

    if dry_run:
        print(f"    [DRY-RUN] Verification complete. Skipping file write for {output_path}.")
        return True

    # Ensure parent output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"    [SUCCESS] Wrote verified binary to: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="De-mask or restore FRP partition in GPT binaries.")
    parser.add_argument("--primary-in", help="Input Primary GPT path")
    parser.add_argument("--primary-out", help="Output Primary GPT path")
    parser.add_argument("--backup-in", help="Input Backup GPT path")
    parser.add_argument("--backup-out", help="Output Backup GPT path")
    parser.add_argument("--restore", action="store_true", help="Restore mode: convert 'frpx' back to 'frp'")
    parser.add_argument("--in-place", action="store_true", help="Allow in-place overwrite of input file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate and verify CRCs without writing files")
    args = parser.parse_args()

    # Determine default paths based on mode
    if not args.restore:
        # De-mask mode: kingston (frp) -> unlock (frpx)
        p_in = args.primary_in or "configurations/gpt/gpt_x04g_kingston.bin"
        p_out = args.primary_out or "configurations/gpt/gpt_x04g_unlock.bin"
        b_in = args.backup_in or "configurations/gpt/gpt_backup_x04g_kingston.bin"
        b_out = args.backup_out or "configurations/gpt/gpt_backup_x04g_unlock.bin"
        mode_desc = "De-masking ('frp' -> 'frpx')"
    else:
        # Restore mode: unlock (frpx) -> kingston (frp)
        p_in = args.primary_in or "configurations/gpt/gpt_x04g_unlock.bin"
        p_out = args.primary_out or "configurations/gpt/gpt_x04g_kingston.bin"
        b_in = args.backup_in or "configurations/gpt/gpt_backup_x04g_unlock.bin"
        b_out = args.backup_out or "configurations/gpt/gpt_backup_x04g_kingston.bin"
        mode_desc = "Restoring ('frpx' -> 'frp')"

    print("=" * 75)
    print("Xiaomi Smart Clock GPT Partition Modification Utility")
    print(f"Action: {mode_desc} | Dry Run: {args.dry_run}")
    print("=" * 75)

    p_ok = patch_gpt_file(p_in, p_out, restore=args.restore, is_backup=False, in_place=args.in_place, dry_run=args.dry_run)
    b_ok = patch_gpt_file(b_in, b_out, restore=args.restore, is_backup=True, in_place=args.in_place, dry_run=args.dry_run)

    if p_ok and b_ok:
        print("=" * 75)
        print(f"[SUCCESS] {mode_desc} completed with bit-perfect CRC32 validation!")
        sys.exit(0)
    else:
        print("=" * 75)
        print(f"[FAILURE] {mode_desc} aborted due to errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
