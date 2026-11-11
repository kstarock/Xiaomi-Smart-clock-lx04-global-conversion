# Troubleshooting Guide: Xiaomi Smart Clock LX04 -> X04G

This guide covers diagnostic procedures, error code lookups, driver issues, and operational solutions encountered during the conversion.

---

## 1. Fastboot & USB Connection Issues

### Issue: `python preloader_fastboot_interceptor.py` times out without catching the device
- **Symptom:** Script prints `Monitoring COM5...` but device boots past preloader without acknowledging `b"FASTBOOT"`.
- **Root Cause:** Incorrect COM port number, or USB cable was plugged in before running the script.
- **Solution:**
  1. Open Windows Device Manager.
  2. Unplug the clock.
  3. Re-plug the clock while watching Device Manager -> "Ports (COM & LPT)". Note the COM port number (e.g. `COM3`, `COM5`, `COM7`).
  4. Edit `scripts/fastboot/preloader_fastboot_interceptor.py` or run with `--port COMx`:
     ```powershell
     python scripts/fastboot/preloader_fastboot_interceptor.py --port COM5
     ```
  5. **Run the script FIRST**, then plug in the USB cable to catch the 500ms handshake window.

### Issue: `fastboot devices` returns nothing after Preloader handshake
- **Symptom:** Script outputs `ACK RECEIVED: TOOBTSAF!`, but `fastboot devices` shows an empty list.
- **Root Cause:** Fastboot USB driver missing or bound to generic USB device.
- **Solution:**
  1. Open Windows Device Manager.
  2. Look for "Android" or "Other Devices" with a yellow exclamation mark.
  3. Right-click -> Update Driver -> Browse my computer -> Let me pick from a list -> Android Device -> "Android Bootloader Interface" or "Android Composite ADB Interface".
  4. See detailed instructions in [`prerequisites/DRIVER_SETUP.md`](../prerequisites/DRIVER_SETUP.md).

---

## 2. Bootloader Unlocking Issues

### Issue: `FAILED (remote: Unlock operation is not allowed)`
- **Symptom:** Executing `fastboot flashing unlock` fails with "Unlock operation is not allowed".
- **Root Cause:** The `frp` partition is still named `frp` in the active GPT, and byte `0x0FFFFC` is `0x00`.
- **Solution:**
  1. Re-flash `configurations/spft/download_gpt_unlock.xml` via SP Flash Tool.
  2. This de-masks partition 12 to `frpx`.
  3. Re-enter Fastboot mode and verify with:
     ```powershell
     fastboot getvar partition-type:frpx
     ```
     If it returns `(bootloader) partition-type:frpx: raw data`, the de-masked GPT is active and unlocking will succeed.

### Issue: Fastboot unlock prompt appears on LCD, but pressing `+` does not confirm
- **Symptom:** Screen displays *"press + to unlock"*, but nothing happens when pressing Volume+.
- **Root Cause:** Button debounce delay or wrong button pressed.
- **Solution:**
  - The physical `+` button is the Volume Up button on top of the clock.
  - Press and hold firmly for 1.5 seconds.
  - Fastboot terminal will respond with `OKAY [ 12.xxx s ]`.

---

## 3. SP Flash Tool Error Codes

### `STATUS_ERR_PMT_CHANGED_FOR_ROM (0xC0040003)`
- **Meaning:** The partition layout in the scatter file differs from the GPT on the eMMC.
- **Fix:** Do NOT use "Format All". Flash the synthesized Kingston GPT (`configurations/spft/download_gpt_unlock.xml`) using `Download Only` mode.

### `STATUS_DA_HASH_MISMATCH (0xC0070004)`
- **Meaning:** Using a modified or unauthorized Download Agent binary.
- **Fix:** Use only the authentic signed `DA_Mi_Hikaru-resign.bin` with `auth_sv5.auth`.

### `STATUS_SEC_IMGHDR_TYPE_MISMATCH (0xC0020029)`
- **Meaning:** Attempting to flash modern Android 10 AVB images (`boot.bin`, `recovery.bin`) via SP Flash Tool DA.
- **Fix:** Modern AVB boot images must be flashed via Fastboot, NOT via SP Flash Tool.

---

## 4. Bootloops & Recovery Fallback

### Issue: Red State warning appears, then device boots directly into Android Recovery
```text
xiaomi/mico_x04g/mico_x04g
10/QP1A.190711.020/1.7.5
user /release-keys
can't load android system your data may be corrupt
```
- **Scenario A: If you just flashed `super.bin` via Fastboot:**
  - This is the **Fastboot multi-chunk write bug**. LK overwrote offset 0, destroying `/system`.
  - Re-flash `super.bin` contiguously using SP Flash Tool and `download_super_contiguous.xml`.
- **Scenario B: If you already flashed `super.bin` via SP Flash Tool:**
  - This is **normal on first boot**! The `/data` partition contains old encryption keys.
  - Highlight **Factory data reset** using volume buttons, press Power/Mute to confirm.
  - Recovery will format `/data` with fresh Android 10 keys. Reboot system now -> Global Android 10 will boot cleanly!
