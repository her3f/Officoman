# Package every built app into dist/ and refresh the download page.
#
#   pwsh -File tools/package_all.ps1            # all four
#   pwsh -File tools/package_all.ps1 podium     # one
#
# Assumes tools/build_windows.ps1 has already produced the executables in the
# shared CARGO_TARGET_DIR.

param(
    [ValidateSet('nib', 'tally', 'podium', 'sheaf')]
    [string[]]$Apps = @('nib', 'tally', 'podium', 'sheaf'),
    [string]$Python = 'python',
    [string]$ReleaseDir = $(if ($env:CARGO_TARGET_DIR) { Join-Path $env:CARGO_TARGET_DIR 'release' } else { Join-Path $env:USERPROFILE 'build\whiteoffice-target\release' })
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$release = $ReleaseDir
if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) { throw "Python not found: $Python" }

# Preflight every requested app before changing any package.
foreach ($app in $Apps) {
    if (-not (Test-Path (Join-Path $release "$app.exe"))) { throw "Missing build: $app.exe in $release" }
}

foreach ($app in $Apps) {
    & $python (Join-Path $root 'tools\package_windows.py') $app --release-dir $release
    if ($LASTEXITCODE -ne 0) { throw "Packaging $app failed with exit code $LASTEXITCODE" }
}

Write-Host ""
Write-Host "refreshing the site's download page"
& $python (Join-Path $root 'tools\build_docs.py') --refresh-releases
if ($LASTEXITCODE -ne 0) { throw 'Site generation failed' }
& $python (Join-Path $root 'tools\make_feed.py')
if ($LASTEXITCODE -ne 0) { throw 'Release feed generation failed' }

# The launcher verifies every download against this file, so the release must carry it.
$sums = Join-Path $root 'dist\SHA256SUMS.txt'
$lines = Get-ChildItem (Join-Path $root 'dist') -File |
    Where-Object { $_.Extension -in '.msi', '.zip' -or $_.Name.EndsWith('.tar.gz') } |
    Sort-Object Name |
    ForEach-Object { "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name }
$lines | Set-Content -Path $sums -Encoding ascii
Write-Host ("wrote dist\SHA256SUMS.txt with " + $lines.Count + " entries")
