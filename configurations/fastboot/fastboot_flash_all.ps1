# ==============================================================================
# Xiaomi Smart Clock LX04 -> X04G Fastboot Core Bootchain Flashing Script
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "LX04 -> X04G Fastboot Bootchain Flasher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Device check
$dev = & fastboot devices
if (-not $dev) {
    Write-Host "[ERROR] No device detected in Fastboot mode!" -ForegroundColor Red
    Write-Host "Please ensure your clock is in Fastboot mode and USB is connected." -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Detected Device: $dev" -ForegroundColor Green

# 2. Strict unlock state verification
$unlocked = & fastboot getvar unlocked 2>&1 | Out-String
if ($unlocked -notmatch "unlocked:\s*yes") {
    Write-Host ""
    Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
    Write-Host "[HARD STOP] Device bootloader is LOCKED!" -ForegroundColor Red
    Write-Host "Output: $unlocked" -ForegroundColor Yellow
    Write-Host "Flashing unsigned Global firmware to a locked bootloader is rejected by" -ForegroundColor Red
    Write-Host "Little Kernel and will fail or cause partition corruption." -ForegroundColor Red
    Write-Host "You MUST perform Phase 4 (FRP de-mask and 'fastboot oem unlock') first." -ForegroundColor Red
    Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Bootloader is confirmed UNLOCKED ('unlocked: yes')" -ForegroundColor Green

# 3. Pre-flight file validation
$steps = @(
    @{ part = "dtbo";           file = "firmware/dtbo.bin" },
    @{ part = "vbmeta";         file = "firmware/vbmeta.bin" },
    @{ part = "vbmeta_system";  file = "firmware/vbmeta_system.bin" },
    @{ part = "vbmeta_vendor";  file = "firmware/vbmeta_vendor.bin" },
    @{ part = "boot";           file = "firmware/boot.bin" },
    @{ part = "recovery";       file = "firmware/recovery.bin" },
    @{ part = "cache";          file = "firmware/cache.bin" },
    @{ part = "metadata";       file = "firmware/metadata.bin" },
    @{ part = "md_udc";         file = "firmware/md_udc.bin" },
    @{ part = "para";           file = "firmware/para.bin" }
)

Write-Host "[*] Validating required firmware images..." -ForegroundColor Yellow
$missing = @()
foreach ($s in $steps) {
    if (-not (Test-Path $s.file)) {
        $missing += $s.file
    }
}
if ($missing.Count -gt 0) {
    Write-Host "[ERROR] Pre-flight check failed! Missing files:" -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "  - $m" -ForegroundColor Red
    }
    exit 1
}
Write-Host "[OK] All required firmware images are present on disk." -ForegroundColor Green

# 4. User confirmation
Write-Host ""
Write-Host "WARNING: This will overwrite boot partitions and wipe userdata." -ForegroundColor Yellow
$confirm = Read-Host "Type 'YES' to proceed with flashing"
if ($confirm -ne 'YES') {
    Write-Host "Aborted by user. No partitions were modified." -ForegroundColor Yellow
    exit 0
}

# 5. Flashing steps
foreach ($s in $steps) {
    Write-Host "[*] Flashing $($s.part) from $($s.file)..." -ForegroundColor Yellow
    & fastboot flash $s.part $s.file
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to flash $($s.part)! Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[*] Erasing userdata partition..." -ForegroundColor Yellow
& fastboot erase userdata
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to erase 'userdata'! Exit code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Device cannot boot cleanly into Android without userdata wipe." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "[SUCCESS] All Fastboot components written successfully!" -ForegroundColor Green
Write-Host "CRITICAL NEXT STEP:" -ForegroundColor Cyan
Write-Host "DO NOT REBOOT INTO ANDROID YET!" -ForegroundColor Red
Write-Host "Flash super.bin contiguously via SP Flash Tool before rebooting." -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
