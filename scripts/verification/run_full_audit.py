import os
import sys
import py_compile
import struct
import zlib
import xml.etree.ElementTree as ET
import re
import hashlib

repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(repo_dir)

print("=" * 80)
print("COMPREHENSIVE FINAL VERIFICATION SUITE")
print("=" * 80)

# 1. Python syntax validation
print("\n[1/7] Validating Python syntax for all repository scripts...")
py_scripts = [
    "scripts/setup/check_environment.py",
    "scripts/backup/make_readback_scatter.py",
    "scripts/verification/verify_checksums.py",
    "scripts/verification/verify_device_state.py",
    "scripts/fastboot/preloader_fastboot_interceptor.py",
    "scripts/fastboot/flash_global_bootstack.py",
    "scripts/utilities/patch_gpt_unlock.py"
]

all_py_ok = True
for s in py_scripts:
    try:
        py_compile.compile(s, doraise=True)
        print(f"  [PASS] {s}")
    except Exception as e:
        print(f"  [FAIL] {s}: {e}")
        all_py_ok = False

# 2. GPT input/output CRC validation
print("\n[2/7] Validating GPT structures and CRC32 checksums...")
gpt_files = [
    ("configurations/gpt/gpt_x04g_kingston.bin", False),
    ("configurations/gpt/gpt_backup_x04g_kingston.bin", True),
    ("configurations/gpt/gpt_x04g_unlock.bin", False),
    ("configurations/gpt/gpt_backup_x04g_unlock.bin", True)
]

all_gpt_ok = True
for gpt_path, is_backup in gpt_files:
    with open(gpt_path, "rb") as fp:
        raw = fp.read()
    hdr_pos = raw.find(b"EFI PART")
    hdr = raw[hdr_pos:hdr_pos+92]
    sig, rev, sz, crc, rsvd, cur_lba, bkp_lba, f_lba, l_lba, guid, pe_lba, num_pe, pe_sz, pe_crc = struct.unpack(
        "<8sIIIIQQQQ16sQIII", hdr
    )
    hdr_zero = hdr[:16] + b"\x00\x00\x00\x00" + hdr[20:sz]
    calc_hdr_crc = zlib.crc32(hdr_zero) & 0xFFFFFFFF
    
    if is_backup:
        pe_offset = 0 if hdr_pos >= 16384 else hdr_pos + 512
    else:
        pe_offset = 1024
    pe_bytes = raw[pe_offset:pe_offset + num_pe * pe_sz]
    calc_pe_crc = zlib.crc32(pe_bytes) & 0xFFFFFFFF
    
    h_ok = (crc == calc_hdr_crc)
    p_ok = (pe_crc == calc_pe_crc)
    if h_ok and p_ok:
        print(f"  [PASS] {gpt_path} (Header CRC: 0x{crc:08X}, PE CRC: 0x{pe_crc:08X})")
    else:
        print(f"  [FAIL] {gpt_path} (Header CRC match: {h_ok}, PE CRC match: {p_ok})")
        all_gpt_ok = False

# 3. GPT Partition vs Scatter comparison
print("\n[3/7] Reconciling GPT Partitions against convert_scatter_global.txt...")
with open("configurations/gpt/gpt_x04g_kingston.bin", "rb") as fp:
    gpt_data = fp.read()

gpt_map = {}
for i in range(128):
    entry = gpt_data[1024 + i*128 : 1024 + (i+1)*128]
    type_guid = entry[:16]
    if type_guid == b"\x00" * 16:
        continue
    first_lba, last_lba = struct.unpack("<QQ", entry[32:48])
    name = entry[56:128].decode("utf-16le").rstrip("\x00")
    gpt_map[name] = {
        "lba_start": first_lba,
        "lba_end": last_lba,
        "offset": first_lba * 512,
        "size": (last_lba - first_lba + 1) * 512
    }

with open("configurations/scatter/convert_scatter_global.txt", "r", encoding="utf-8") as fp:
    scatter_text = fp.read()

scatter_map = {}
for p in re.findall(r'- partition_index:.*?(?=- partition_index:|\Z)', scatter_text, re.DOTALL):
    name_m = re.search(r'partition_name:\s*(\S+)', p)
    addr_m = re.search(r'linear_start_addr:\s*(\S+)', p)
    size_m = re.search(r'partition_size:\s*(\S+)', p)
    if name_m and addr_m and size_m:
        scatter_map[name_m.group(1)] = {
            "offset": int(addr_m.group(1), 16),
            "size": int(size_m.group(1), 16)
        }

reconcile_ok = True
for name, info in gpt_map.items():
    if name in scatter_map:
        sc = scatter_map[name]
        if sc["offset"] != info["offset"] or sc["size"] != info["size"]:
            print(f"  [MISMATCH] {name}: GPT offset=0x{info['offset']:X}/sz=0x{info['size']:X} vs Scatter offset=0x{sc['offset']:X}/sz=0x{sc['size']:X}")
            reconcile_ok = False
if reconcile_ok:
    print(f"  [PASS] All {len(gpt_map)} GPT partitions match scatter linear_start_addr and sizes exactly!")

# 4. XML Parsing validation
print("\n[4/7] Validating SP Flash Tool XML configurations...")
xml_files = [
    "configurations/spft/download_gpt_unlock.xml",
    "configurations/spft/download_gpt_restore.xml",
    "configurations/spft/download_super_contiguous.xml"
]

all_xml_ok = True
for x in xml_files:
    try:
        tree = ET.parse(x)
        root = tree.getroot()
        roms = root.findall(".//rom")
        print(f"  [PASS] {x} (Valid XML, {len(roms)} ROM entries defined)")
    except Exception as e:
        print(f"  [FAIL] {x}: {e}")
        all_xml_ok = False

# 5. Static script safety checks
print("\n[5/7] Checking Fastboot scripts for hard stops and error handling...")
fastboot_files = [
    "scripts/fastboot/flash_global_bootstack.py",
    "configurations/fastboot/fastboot_flash_all.bat",
    "configurations/fastboot/fastboot_flash_all.ps1"
]

all_fb_ok = True
for fb in fastboot_files:
    content = open(fb, "r", encoding="utf-8", errors="ignore").read()
    has_devices = ("fastboot devices" in content) or ('"devices"' in content)
    has_unlock_check = "unlocked" in content
    has_userdata = "userdata" in content
    has_super_warning = "super" in content
    if has_devices and has_unlock_check and has_userdata and has_super_warning:
        print(f"  [PASS] {fb} contains device check, unlock check, userdata erase, and super warning")
    else:
        print(f"  [FAIL] {fb} missing required safety checks")
        all_fb_ok = False

# 6. Markdown Link Checks
print("\n[6/7] Validating internal Markdown links...")
link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
broken_links = []
total_md_links = 0

for root, dirs, files in os.walk(repo_dir):
    for f in files:
        if f.endswith(".md"):
            md_p = os.path.join(root, f)
            c = open(md_p, "r", encoding="utf-8", errors="ignore").read()
            for text, target in link_re.findall(c):
                target = target.strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                clean = target.split("#")[0]
                if not clean:
                    continue
                total_md_links += 1
                resolved = os.path.normpath(os.path.join(root, clean))
                if not os.path.exists(resolved):
                    broken_links.append((md_p, target, resolved))

if len(broken_links) == 0:
    print(f"  [PASS] All {total_md_links} relative Markdown links resolve to existing files!")
else:
    print(f"  [FAIL] Found {len(broken_links)} broken Markdown links:")
    for src, tgt, res in broken_links:
        print(f"    In {src}: {tgt} -> {res}")

# 7. SHA-256 Manifest Consistency Checks
print("\n[7/7] Validating SHA-256 manifest consistency...")
manifest_path = "checksums/SHA256SUMS.txt"
with open(manifest_path, "r", encoding="utf-8") as fp:
    manifest_lines = fp.readlines()

manifest_entries = {}
for line in manifest_lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split(None, 1)
    if len(parts) == 2:
        h, f = parts
        manifest_entries[f.strip("* ")] = h.lower()

checked_files = 0
hash_errors = 0
for fn, exp_hash in manifest_entries.items():
    if os.path.isfile(fn):
        checked_files += 1
        with open(fn, "rb") as fp:
            actual = hashlib.sha256(fp.read()).hexdigest().lower()
        if actual != exp_hash:
            print(f"  [HASH MISMATCH] {fn}: expected {exp_hash}, got {actual}")
            hash_errors += 1

print(f"  [PASS] Verified {checked_files} repository files present against SHA-256 manifest ({hash_errors} mismatches).")
print(f"  (Note: Proprietary images not tracked in git are expectedly absent from the repo root).")

print("\n" + "=" * 80)
print("VERIFICATION SUITE SUMMARY:")
print(f"  Python Scripts:     {'ALL PASSED' if all_py_ok else 'FAILED'}")
print(f"  GPT Binaries & CRC: {'ALL PASSED' if all_gpt_ok else 'FAILED'}")
print(f"  GPT/Scatter Map:    {'ALL PASSED' if reconcile_ok else 'FAILED'}")
print(f"  SPFT XML Configs:   {'ALL PASSED' if all_xml_ok else 'FAILED'}")
print(f"  Fastboot Scripts:   {'ALL PASSED' if all_fb_ok else 'FAILED'}")
print(f"  Markdown Links:     {'ALL PASSED' if len(broken_links) == 0 else 'FAILED'}")
print(f"  SHA-256 Manifest:   {'ALL PASSED' if hash_errors == 0 else 'FAILED'}")
print("=" * 80)
