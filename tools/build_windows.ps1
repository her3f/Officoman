# Build the four apps for Windows x64 with the MinGW-w64 toolchain.
#
# The projects are MSVC-first upstream, but this machine has no Visual Studio build
# tools, so the whole host toolchain is GNU (rustup toolchain
# stable-x86_64-pc-windows-gnu) with winlibs MinGW-w64 providing the linker.
#
# A single CARGO_TARGET_DIR is shared by all four so the very large dependency tree
# is compiled once instead of four times.
#
#   pwsh -File tools/build_windows.ps1 -Apps podium,nib,tally,sheaf

param([string[]]$Apps = @('podium', 'nib', 'tally', 'sheaf'))

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$mingw = 'C:\Users\Her3f\tools\mingw64'
$env:PATH = "$mingw\bin;$env:USERPROFILE\.cargo\bin;$env:PATH"
$env:CARGO_TARGET_DIR = 'C:\Users\Her3f\build\officoman-target'
New-Item -ItemType Directory -Force -Path $env:CARGO_TARGET_DIR | Out-Null

$failed = @()
foreach ($app in $Apps) {
    $dir = Join-Path $root "apps\$app"
    if (-not (Test-Path $dir)) { Write-Host "skip $app (missing)"; continue }

    Write-Host "=== building $app ==="
    Push-Location $dir
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $out = & cargo +stable-x86_64-pc-windows-gnu build --release -p $app -p "$app-cli" 2>&1
    $code = $LASTEXITCODE
    Pop-Location
    $sw.Stop()

    $log = Join-Path $root "_build_$app.log"
    $out | Set-Content -Path $log -Encoding utf8

    if ($code -eq 0) {
        Write-Host ("    OK in {0:n1} min" -f $sw.Elapsed.TotalMinutes)
        $exe = Join-Path $env:CARGO_TARGET_DIR "release\$app.exe"
        if (Test-Path $exe) {
            Write-Host ("    {0}  {1:n1} MB" -f $exe, ((Get-Item $exe).Length / 1MB))
        }
    }
    else {
        Write-Host "    FAILED (exit $code) - see $log"
        $out | Select-Object -Last 25 | ForEach-Object { "      $_" }
        $failed += $app
    }
}

Write-Host ""
if ($failed.Count -eq 0) { Write-Host "all builds succeeded" }
else { Write-Host ("failed: " + ($failed -join ', ')) }
