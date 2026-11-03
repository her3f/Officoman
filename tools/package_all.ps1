# Package every built app into dist/ and refresh the download page.
#
#   pwsh -File tools/package_all.ps1            # all four
#   pwsh -File tools/package_all.ps1 podium     # one
#
# Assumes tools/build_windows.ps1 has already produced the executables in the
# shared CARGO_TARGET_DIR.

param([string[]]$Apps = @('nib', 'tally', 'podium', 'sheaf'))

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$python = 'C:\Users\Her3f\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$release = 'C:\Users\Her3f\build\officoman-target\release'

foreach ($app in $Apps) {
    if (-not (Test-Path (Join-Path $release "$app.exe"))) {
        Write-Host "skip $app (not built)"
        continue
    }
    & $python (Join-Path $root 'tools\package_windows.py') $app --release-dir $release
}

Write-Host ""
Write-Host "refreshing the site's download page"
& $python (Join-Path $root 'tools\build_docs.py')
