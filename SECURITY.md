# Security Policy & Evidentiary Standards

## 1. Supported Scope
This repository provides reproducible instructions and open-source tooling specifically validated on:
- **Device Model:** Xiaomi Smart Clock (China variant: `LX04` / board: `mico_lx04`).
- **Target Firmware:** Xiaomi Smart Clock (Global variant: `X04G` / board: `mico_x04g` / Android 10 build `QP1A.190711.020 / 1.7.5 user/release-keys`).
- **SoC & Storage:** MediaTek MT8167A with Kingston 4GB eMMC 5.1 (`M62704`, `7,405,568` sectors).

Any other board revision or eMMC vendor CID (e.g. Samsung or Micron) requires independent partition geometry validation before flashing.

---

## 2. Responsible Disclosure & Hardware Integrity
If you discover a firmware security vulnerability, an overlooked hard-brick risk, or an error in partition boundary definitions:
1. **Do NOT open a public issue that encourages destructive behavior.**
2. Open a security advisory on GitHub or contact the maintainers via community channels.
3. Provide full technical details, including serial captures, partition readback hashes, and tool versions.

---

## 3. Privacy & Intellectual Property Safeguards
To comply with copyright laws and protect personal privacy:
- **No Private Keys:** No OEM RSA signing private keys are published or requested.
- **No Leaked Binaries:** Official firmware images must be extracted by users from verified vendor packages.
- **No PII or Identifiers:** Device serial numbers, factory barcodes, hardware MAC addresses, and private host directory paths must never be committed to this repository. All documentation uses sanitized placeholder values.
