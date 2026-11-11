# Contributing to the LX04 Conversion Project

We welcome contributions from embedded Linux engineers, Android ROM developers, and hardware hackers.

---

## Contribution Guidelines

1. **Evidence-Based Standards:**
   Every pull request modifying flashing sequences, scatter files, or partition geometry must cite verifiable evidence:
   - SHA-256 checksums of tested images.
   - Exact tool versions used.
   - Console logs or readback confirmations.
   - Classification as **[VERIFIED]**, **[REPORTED]**, **[INFERRED]**, or **[UNKNOWN]**.

2. **Zero Proprietary Firmware Inclusion:**
   Never submit PRs containing extracted OEM `.bin` or `.img` files from official firmware archives. Only submit scripts, configuration templates, documentation, or diff patches.

3. **Code Quality Requirements for Scripts:**
   - Python 3.8+ compatibility with zero mandatory external pip dependencies wherever possible (use standard library and Win32 ctypes).
   - Strict input validation before any USB or COM write operation.
   - Clear console logging with explicit error messages and non-zero exit codes on failure.

4. **Testing Checklist:**
   Before submitting, ensure all Python scripts pass syntax validation:
   ```powershell
   python -m py_compile scripts/**/*.py
   ```
