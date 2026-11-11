# Frequently Asked Questions (FAQ)

### Q: Why convert the LX04 to Global X04G firmware?
**A:** The Chinese LX04 firmware is permanently locked to mainland China Xiaomi servers and supports only Mandarin Chinese XiaoAI voice control. The Global X04G firmware runs official Android 10 with multilingual system UI (English, Spanish, etc.), Google Assistant, and standard international time and weather services.

### Q: Does this require opening the clock or soldering?
**A:** **NO.** No physical disassembly, case opening, or soldering is required. The procedure is executed entirely over the external Micro-USB port using our low-latency Preloader serial handshake hook.

### Q: Will my Wi-Fi MAC address and Bluetooth be preserved?
**A:** **YES.** By strictly following our guide, your unique device calibration and RF parameters in `proinfo` and `nvram` remain untouched on the eMMC. These two partitions are confirmed preserved original factory partitions sharing identical physical byte offsets across both Chinese and Global layouts. (Note: Stock Chinese firmware had no `nvdata` partition; under Global Android 10, the newly defined `nvdata` partition at `0x0B340000` is formatted as ext4 and populated from preserved `nvram` on first boot, an **[INFERRED]** mechanism based on standard MediaTek Android 10 architecture).

### Q: What hardware features work after conversion?
**A:** The following 7 hardware subsystems and smart features have been directly tested and confirmed operational by the device owner on physical hardware (Kingston 4GB eMMC unit):
- Android 10 operating system boot and stability
- 3.97-inch IPS LCD display (800x480 WVGA)
- Capacitive touchscreen digitizer
- Wi-Fi 2.4 GHz 802.11 b/g/n
- Bluetooth 5.0 LE
- Neodymium speaker & Class-D audio amplifier
- Far-field dual-microphone array (verified via live Google Assistant voice recognition)
- Xiaomi companion app device detection

### Q: Does Google Assistant work?
**A:** **YES (Verified by Owner).** Google Assistant voice recognition and spoken responses have been confirmed functional through physical testing on the converted unit. Tested commands include:
1. **Weather:** Inquired about current weather conditions; Assistant correctly recognized the query and replied with a spoken weather forecast.
2. **Current Time:** Asked for the current time; Assistant responded with the accurate local time.
3. **Alarm Setting:** Commanded Assistant to set an alarm; voice prompt was processed and the alarm was successfully created.
*(Note: These tests verify core Assistant functionality on one physical development unit; every possible third-party integration has not been exhaustively evaluated).*

### Q: Why do I see a "Red State" or "Orange State" message on boot?
**A:** This is standard MediaTek behavior when the bootloader is unlocked. Android Verified Boot (AVB) notifies the user that the device is running in unlocked mode. It is purely cosmetic and disappears after 5 seconds.

### Q: Can I take official OTA updates after conversion?
**A:** Official over-the-air (OTA) updates have not been tested post-conversion. While an unlocked bootloader and altered partition layout typically prevent official OTAs from applying cleanly, the OTA engine remains untested. Users should disable automatic updates in Developer Options as a precaution.

### Q: Can I revert back to the Chinese firmware?
**A:** **YES.** As long as you perform the mandatory backup in Step 1, you can re-flash your original Chinese backup dumps at any time using SP Flash Tool.
