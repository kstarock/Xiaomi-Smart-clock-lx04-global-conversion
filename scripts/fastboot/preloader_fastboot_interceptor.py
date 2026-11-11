#!/usr/bin/env python3
"""
preloader_fastboot_interceptor.py - Win32 low-latency Preloader Fastboot Interceptor.
Part of the Xiaomi Smart Clock LX04 China-to-Global Conversion Suite.

Catches the MediaTek MT8167 Preloader during its ~500ms startup handshake window
and commands Little Kernel (LK) directly into Fastboot mode without hardware disassembly.
Uses native 64-bit Windows kernel32 serial APIs for minimal latency without pyserial.
"""

import sys
import os
import time
import shutil
import subprocess
import argparse
import ctypes
from ctypes import wintypes

# Win32 Constants
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

# Serial DCB Constants
CBR_115200 = 115200
NOPARITY = 0
ONESTOPBIT = 0
DTR_CONTROL_ENABLE = 1
RTS_CONTROL_ENABLE = 1

# Setup Win32 kernel32 function prototypes
kernel32 = ctypes.windll.kernel32

# CreateFileW
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE
]
kernel32.CreateFileW.restype = wintypes.HANDLE

# CloseHandle
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

# ReadFile
kernel32.ReadFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID
]
kernel32.ReadFile.restype = wintypes.BOOL

# WriteFile
kernel32.WriteFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPCVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID
]
kernel32.WriteFile.restype = wintypes.BOOL

# GetLastError
kernel32.GetLastError.argtypes = []
kernel32.GetLastError.restype = wintypes.DWORD

class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", wintypes.DWORD),
        ("ReadTotalTimeoutMultiplier", wintypes.DWORD),
        ("ReadTotalTimeoutConstant", wintypes.DWORD),
        ("WriteTotalTimeoutMultiplier", wintypes.DWORD),
        ("WriteTotalTimeoutConstant", wintypes.DWORD),
    ]

kernel32.SetCommTimeouts.argtypes = [wintypes.HANDLE, ctypes.POINTER(COMMTIMEOUTS)]
kernel32.SetCommTimeouts.restype = wintypes.BOOL

class DCB(ctypes.Structure):
    _fields_ = [
        ("DCBlength", wintypes.DWORD),
        ("BaudRate", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("wReserved", wintypes.WORD),
        ("XonLim", wintypes.WORD),
        ("XoffLim", wintypes.WORD),
        ("ByteSize", ctypes.c_byte),
        ("Parity", ctypes.c_byte),
        ("StopBits", ctypes.c_byte),
        ("XonChar", ctypes.c_char),
        ("XoffChar", ctypes.c_char),
        ("ErrorChar", ctypes.c_char),
        ("EofChar", ctypes.c_char),
        ("EvtChar", ctypes.c_char),
        ("wReserved1", wintypes.WORD),
    ]

kernel32.GetCommState.argtypes = [wintypes.HANDLE, ctypes.POINTER(DCB)]
kernel32.GetCommState.restype = wintypes.BOOL

kernel32.SetCommState.argtypes = [wintypes.HANDLE, ctypes.POINTER(DCB)]
kernel32.SetCommState.restype = wintypes.BOOL

def open_port(port_name):
    """Attempt to open COM port with 64-bit handle verification."""
    h = kernel32.CreateFileW(
        port_name,
        GENERIC_READ | GENERIC_WRITE,
        0,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None
    )
    if h == INVALID_HANDLE_VALUE:
        err = kernel32.GetLastError()
        return None, err
    return h, 0

def configure_port(h):
    """Set 115200 baud, 8N1, and aggressive low-latency timeouts."""
    dcb = DCB()
    dcb.DCBlength = ctypes.sizeof(DCB)
    if kernel32.GetCommState(h, ctypes.byref(dcb)):
        dcb.BaudRate = CBR_115200
        dcb.ByteSize = 8
        dcb.Parity = NOPARITY
        dcb.StopBits = ONESTOPBIT
        # Binary mode + enable DTR and RTS
        dcb.flags = 0x0001 | (DTR_CONTROL_ENABLE << 4) | (RTS_CONTROL_ENABLE << 12)
        kernel32.SetCommState(h, ctypes.byref(dcb))

    timeouts = COMMTIMEOUTS(20, 0, 20, 0, 100)
    kernel32.SetCommTimeouts(h, ctypes.byref(timeouts))

def close_port(h):
    if h and h != INVALID_HANDLE_VALUE:
        kernel32.CloseHandle(h)

def read_bytes(h, max_len=64):
    buf = ctypes.create_string_buffer(max_len)
    bytes_read = wintypes.DWORD(0)
    res = kernel32.ReadFile(h, buf, max_len, ctypes.byref(bytes_read), None)
    if res and bytes_read.value > 0:
        return buf.raw[:bytes_read.value]
    return b""

def write_bytes(h, data):
    bytes_written = wintypes.DWORD(0)
    res = kernel32.WriteFile(h, data, len(data), ctypes.byref(bytes_written), None)
    return bool(res and bytes_written.value == len(data))

def get_system_com_ports():
    """Retrieve active COM ports from Windows Registry SERIALCOMM map."""
    ports = []
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
        for i in range(winreg.QueryInfoKey(key)[1]):
            _, val_data, _ = winreg.EnumValue(key, i)
            ports.append(val_data)
        winreg.CloseKey(key)
    except Exception:
        pass
    return ports

def main():
    parser = argparse.ArgumentParser(description="Intercept MediaTek Preloader and force Fastboot mode.")
    parser.add_argument("--port", default="COM5", help="Target COM port (e.g., COM5, COM3)")
    parser.add_argument("--auto-detect", action="store_true", help="Monitor Windows registry and intercept any newly plugged COM port")
    parser.add_argument("--timeout", type=int, default=180, help="Monitoring timeout in seconds (default: 180)")
    parser.add_argument("--fastboot", default="fastboot", help="Path to fastboot executable")
    args = parser.parse_args()

    fastboot_cmd = shutil.which(args.fastboot) or args.fastboot

    print("=" * 70)
    print("MediaTek Preloader Fastboot Interceptor (Win32 Low-Latency)")
    print("=" * 70)

    if args.auto_detect:
        initial_ports = set(get_system_com_ports())
        print(f"[*] Auto-detect mode ACTIVE. Initial COM ports on system: {list(initial_ports) or 'None'}")
        print("[*] Waiting for new MediaTek VCOM port to appear...")
    else:
        print(f"[*] Monitoring explicit port: {args.port}")

    print(f"[*] Timeout: {args.timeout} seconds")
    print("[*] ACTION REQUIRED: Plug the Micro-USB cable into your clock now!")
    print("    (If already plugged in, power-cycle by replugging USB)")
    print("-" * 70)

    start_time = time.time()
    got_ack = False

    while time.time() - start_time < args.timeout:
        candidate_ports = []
        if args.auto_detect:
            current_ports = set(get_system_com_ports())
            new_ports = list(current_ports - initial_ports)
            if new_ports:
                candidate_ports = new_ports
            else:
                candidate_ports = list(current_ports)
        else:
            candidate_ports = [args.port]

        for port_name in candidate_ports:
            target_path = rf"\\.\{port_name}"
            h, err = open_port(target_path)
            if h is not None:
                print(f"[{time.strftime('%H:%M:%S')}] Detected active port: {port_name}!")
                configure_port(h)

                # Send FASTBOOT token loop during handshake window
                t0 = time.time()
                while time.time() - t0 < 3.0:
                    write_bytes(h, b"FASTBOOT")
                    time.sleep(0.01)
                    resp = read_bytes(h, 64)
                    if resp:
                        print(f"    Preloader raw response: {resp}")
                        if b"TOOBTSAF" in resp or b"FASTBOOT" in resp:
                            print("\n" + "=" * 70)
                            print(">>> [SUCCESS] ACK RECEIVED: TOOBTSAF! <<<")
                            print(">>> MediaTek Preloader accepted Fastboot redirection! <<<")
                            print("=" * 70)
                            got_ack = True
                            break

                # Send disconnect command to finalize handoff
                write_bytes(h, b"DISCONNECT")
                close_port(h)

                if got_ack:
                    break
                else:
                    print(f"[-] Handshake on {port_name} did not ACK, continuing scan...")
            else:
                if err == 5:
                    # Access denied -> port exists but locked by another program
                    pass

        if got_ack:
            break
        time.sleep(0.05)

    if not got_ack:
        print("\n[ERROR] Monitoring timed out without catching Preloader.")
        print("Troubleshooting:")
        print("  1. Ensure MediaTek USB VCOM driver is installed in Device Manager.")
        print("  2. Ensure SP Flash Tool or any serial terminal is NOT holding the port open.")
        print("  3. Check Device Manager to confirm which COM port is assigned upon USB plug-in.")
        sys.exit(1)

    # Device is switching USB controller to Android Fastboot interface
    print("[*] Waiting 4 seconds for USB Fastboot enumeration...")
    time.sleep(4.0)

    print("[*] Verifying Fastboot USB connection...")
    for attempt in range(1, 9):
        try:
            res = subprocess.run([fastboot_cmd, "devices"], capture_output=True, text=True, timeout=5)
            out = res.stdout.strip()
            if out:
                print(f"[OK] Fastboot connection confirmed on attempt #{attempt}:")
                print(f"     Device: {out}")
                print("-" * 70)
                print("[READY] Device is now confirmed in Fastboot mode! You can proceed to next step.")
                sys.exit(0)
        except Exception:
            pass
        print(f"    Check #{attempt}/8: Waiting for fastboot devices enumeration...")
        time.sleep(1.5)

    print("\n[ERROR] Preloader accepted FASTBOOT command, but 'fastboot devices' failed to enumerate.")
    print("Troubleshooting:")
    print("  1. Open Device Manager -> Look for 'Android' or 'Unknown Device' with a yellow exclamation mark.")
    print("  2. Install the Google Android Bootloader Interface driver.")
    print("  3. Run 'fastboot devices' manually in PowerShell/cmd.")
    sys.exit(2)

if __name__ == "__main__":
    main()
