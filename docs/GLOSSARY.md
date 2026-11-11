# Technical Glossary of MediaTek & Android Firmware Terms

### AVB (Android Verified Boot)
The Google security subsystem (AVB 2.0) that cryptographically verifies the integrity of Android partitions (`boot`, `dtbo`, `system`, `vendor`) using cryptographic hash trees and RSA signature descriptors stored in `vbmeta.bin`.

### BROM (BootROM)
A hardcoded read-only memory block embedded directly in the MediaTek MT8167 silicon die. It executes the very first instruction upon power-on, verifies the signature of the preloader stored in eMMC `BOOT1`, and provides low-level USB recovery communication.

### DA (Download Agent)
A specialized binary (`DA_Mi_Hikaru-resign.bin`) sent over USB to DRAM/SRAM during flashing. Stage 1 DA initializes basic hardware and External Memory Interface (EMI) DRAM timings; Stage 2 DA handles low-level eMMC read, write, and erase transactions.

### DTBO (Device Tree Blob Overlay)
A binary file containing hardware description nodes (GPIO pin muxes, panel timings, I2C addresses) dynamically applied by Little Kernel over the primary Linux Device Tree Blob.

### eMMC (embedded MultiMediaCard)
The integrated flash memory IC (Kingston 4GB `M62704`) containing hardware boot partitions (`BOOT1`, `BOOT2`, `RPMB`) and the main user-addressable flash blocks (`USER`).

### Fastboot
An Android diagnostic and flashing protocol exposed by Little Kernel (`lk.bin`) over USB. Used to flash kernel, recovery, and AVB partitions once the bootloader is unlocked.

### FRP (Factory Reset Protection)
An Android security partition containing a bitflag at offset `0x0FFFFC`. When set to 0, OEM bootloader unlocking is blocked; when the partition is absent or de-masked (`frpx`), Little Kernel defaults to allowing unlocking.

### GFH (Generic File Header)
MediaTek's proprietary binary container header (magic `0x58881688`) prepended to bootloader binaries (`preloader`, `lk`, `logo`, `tee`) containing image type, DRAM load address, and cryptographic signature descriptors.

### LK (Little Kernel)
MediaTek's secondary bootloader (`lk.bin`), loaded into DRAM by the preloader. Responsible for initializing display controllers, rendering splash screens, verifying AVB signatures, handling Fastboot commands, and booting Linux.

### NVRAM / NVDATA
Non-Volatile RAM storage containing unique hardware calibration: Wi-Fi MAC addresses, Bluetooth identifiers, and radio frequency power lookup tables. Must never be erased.

### Preloader
The first-stage bootloader stored in eMMC `BOOT1`. Initializes DRAM timings and clocks, and can be intercepted via serial tokens (`b"FASTBOOT"`) to force entry into Fastboot mode.

### Scatter File
A structured plaintext configuration file (`MT8167_Android_scatter.txt`) used by SP Flash Tool to map binary image files to exact eMMC sector ranges and partition names.

### SP Flash Tool
MediaTek's official host-side flashing software used to communicate with BROM and DA over USB serial COM ports to read, write, and format raw eMMC flash blocks.

### Super Partition
A contiguous block partition in Android 10+ Dynamic Partitions architecture containing multiple logical sub-volumes (`system`, `vendor`, `product`).
