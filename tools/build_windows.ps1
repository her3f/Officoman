# Build the four apps for Windows x64 with the MinGW-w64 toolchain.
#
# The projects are MSVC-first upstream, but this machine has no Visual Studio build
# tools, so the whole host toolchain is GNU (rustup toolchain
# stable-x86_64-pc-windows-gnu) with winlibs MinGW-w64 providing the linker.
#
# A single CARGO_TARGET_DIR is shared by all four so the very large dependency tree
# is compiled once instead of four times.
#
#   pwsh -File tools/build_windows.ps1               # all four apps
#   pwsh -File tools/build_windows.ps1 -Apps nib      # one app

param(
    [ValidateSet('podium', 'nib', 'tally', 'sheaf')]
    [string[]]$Apps = @('podium', 'nib', 'tally', 'sheaf'),
    [string]$Mingw = (Join-Path $env:USERPROFILE 'tools\mingw64'),
    [string]$TargetDir = $(if ($env:CARGO_TARGET_DIR) { $env:CARGO_TARGET_DIR } else { Join-Path $env:USERPROFILE 'build\whiteoffice-target' })
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$env:PATH = "$mingw\bin;$env:USERPROFILE\.cargo\bin;$env:PATH"
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) { throw 'cargo is not installed or not on PATH' }
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
$env:CARGO_TARGET_DIR = (Resolve-Path -LiteralPath $TargetDir).Path

$failed = @()
foreach ($app in $Apps) {
    $dir = Join-Path $root "apps\$app"
    if (-not (Test-Path $dir)) { throw "Missing app directory: $dir" }

    Write-Host "=== building $app ==="
    $log = Join-Path $root "_build_$app.log"
    Push-Location $dir
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & cargo +stable-x86_64-pc-windows-gnu build --locked --release -p $app -p "$app-cli" 2>&1 |
            Tee-Object -FilePath $log
        $code = $LASTEXITCODE
    }
    finally { Pop-Location }
    $sw.Stop()

    if ($code -eq 0) {
        Write-Host ("    OK in {0:n1} min" -f $sw.Elapsed.TotalMinutes)
        $exe = Join-Path $env:CARGO_TARGET_DIR "release\$app.exe"
        if (Test-Path $exe) {
            Write-Host ("    {0}  {1:n1} MB" -f $exe, ((Get-Item $exe).Length / 1MB))
        }
    }
    else {
        Write-Host "    FAILED (exit $code) - see $log"
        Get-Content -LiteralPath $log -Tail 25 | ForEach-Object { "      $_" }
        $failed += $app
    }
}

Write-Host ""
if ($failed.Count -eq 0) { Write-Host "all builds succeeded"; exit 0 }
else { Write-Host ("failed: " + ($failed -join ', ')); exit 1 }
