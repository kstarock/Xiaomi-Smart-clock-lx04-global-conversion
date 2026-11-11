@echo off
setlocal enabledelayedexpansion
REM ==============================================================================
REM Xiaomi Smart Clock LX04 -> X04G Fastboot Core Bootchain Flashing Script
REM Flashes verified Global Android 10 bootloader, kernel, DTBO, and AVB components.
REM DO NOT FLASH super.bin HERE (super.bin must be flashed via SP Flash Tool).
REM ==============================================================================

echo ==============================================================================
echo Xiaomi Smart Clock Global Android 10 Fastboot Bootchain Flasher
echo ==============================================================================

REM 1. Device detection
echo [*] Checking Fastboot device connectivity...
fastboot devices > fastboot_device_check.tmp 2>&1
set /p DEVICE_LINE=<fastboot_device_check.tmp
del fastboot_device_check.tmp 2>nul

if "%DEVICE_LINE%"=="" (
    echo.
    echo [ERROR] No device detected in Fastboot mode!
    echo Please ensure the clock is connected and in Fastboot mode.
    pause
    exit /b 1
)
echo [OK] Detected Fastboot device: %DEVICE_LINE%

REM 2. Strict bootloader unlock check
echo [*] Checking bootloader unlock state...
fastboot getvar unlocked > fastboot_unlock_check.tmp 2>&1
findstr /i "unlocked: yes" fastboot_unlock_check.tmp >nul
if errorlevel 1 (
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo [HARD STOP] Bootloader is LOCKED!
    type fastboot_unlock_check.tmp
    del fastboot_unlock_check.tmp 2>nul
    echo.
    echo Flashing unsigned Global firmware to a locked bootloader is rejected by
    echo Little Kernel and will fail or cause partition corruption.
    echo You MUST perform Phase 4 (FRP de-mask and 'fastboot oem unlock') first.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pause
    exit /b 1
)
del fastboot_unlock_check.tmp 2>nul
echo [OK] Bootloader is confirmed UNLOCKED ('unlocked: yes').

REM 3. Pre-flight file validation
echo [*] Validating required firmware images...
set "MISSING=0"
for %%F in (firmware\dtbo.bin firmware\vbmeta.bin firmware\vbmeta_system.bin firmware\vbmeta_vendor.bin firmware\boot.bin firmware\recovery.bin firmware\cache.bin firmware\metadata.bin firmware\md_udc.bin firmware\para.bin) do (
    if not exist "%%F" (
        echo [ERROR] Missing required file: %%F
        set "MISSING=1"
    )
)
if "%MISSING%"=="1" (
    echo.
    echo [ERROR] Pre-flight check failed! One or more required images are missing.
    echo Aborting before touching any partitions.
    pause
    exit /b 1
)
echo [OK] All required firmware images are present.

REM 4. User confirmation
echo.
echo WARNING: This operation will overwrite device partitions and wipe userdata.
set /p CONFIRM="Type 'YES' to proceed with flashing: "
if not "%CONFIRM%"=="YES" (
    echo Aborted by user. No partitions were modified.
    pause
    exit /b 0
)

REM 5. Flashing sequence
echo.
echo [*] Flashing DTBO overlay...
fastboot flash dtbo firmware\dtbo.bin || goto :error

echo [*] Flashing AVB 2.0 signatures...
fastboot flash vbmeta firmware\vbmeta.bin || goto :error
fastboot flash vbmeta_system firmware\vbmeta_system.bin || goto :error
fastboot flash vbmeta_vendor firmware\vbmeta_vendor.bin || goto :error

echo [*] Flashing Global Android 10 Kernel...
fastboot flash boot firmware\boot.bin || goto :error

echo [*] Flashing Global Android 10 Recovery...
fastboot flash recovery firmware\recovery.bin || goto :error

echo [*] Flashing auxiliary partitions...
fastboot flash cache firmware\cache.bin || goto :error
fastboot flash metadata firmware\metadata.bin || goto :error
fastboot flash md_udc firmware\md_udc.bin || goto :error
fastboot flash para firmware\para.bin || goto :error

echo [*] Erasing userdata...
fastboot erase userdata || goto :erase_error

echo.
echo ==============================================================================
echo [SUCCESS] Core Global Android 10 bootchain successfully flashed!
echo.
echo CRITICAL MANDATORY NEXT STEP:
echo DO NOT REBOOT INTO ANDROID YET!
echo You MUST now flash 'super.bin' contiguously via SP Flash Tool.
echo ==============================================================================
pause
goto :eof

:erase_error
echo.
echo [ERROR] Failed to erase 'userdata' partition!
echo Device cannot boot into Android without clean userdata.
pause
exit /b 1

:error
echo.
echo [ERROR] Fastboot flash command failed! Please inspect the error message above.
pause
exit /b 1
