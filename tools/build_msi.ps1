# Build Windows MSI installers from the portable builds in dist/.
#
#   pwsh -File tools/build_msi.ps1
#
# Needs the WiX 5 command line tool and its UI extension:
#   dotnet tool install --global wix --version 5.0.2
#   (the extension is fetched from NuGet into a folder first; WiX stopped bundling it)
#
# WiX 7 is deliberately not used: it requires accepting the Open Source Maintenance
# Fee agreement, which is the project owner's decision, not this script's.

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root 'dist'
$env:PATH = "$env:USERPROFILE\.dotnet\tools;$env:PATH"

$extDll = "$env:TEMP\wixui\wixext5\WixToolset.UI.wixext.dll"
if (-not (Test-Path $extDll)) {
    $nupkg = "$env:TEMP\wixui.nupkg"
    if (-not (Test-Path $nupkg)) {
        curl.exe -sS -L --fail -o $nupkg 'https://www.nuget.org/api/v2/package/WixToolset.UI.wixext/5.0.2'
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($nupkg, "$env:TEMP\wixui")
}

$apps = @(
    @{ slug = 'nib';    ver = '0.15.0' },
    @{ slug = 'tally';  ver = '0.16.0' },
    @{ slug = 'podium'; ver = '0.15.0' },
    @{ slug = 'sheaf';  ver = '0.18.0' }
)

foreach ($a in $apps) {
    $name = (Get-Culture).TextInfo.ToTitleCase($a.slug)
    $bin = Join-Path $dist "$name-$($a.ver)-windows-x64"
    if (-not (Test-Path (Join-Path $bin "$($a.slug).exe"))) {
        Write-Host "skip $($a.slug) (no portable build)"
        continue
    }
    $ico = Join-Path $root "apps\$($a.slug)\assets\app-icon\$($a.slug).ico"
    $wxs = Join-Path $root "apps\$($a.slug)\packaging\windows\$($a.slug).wxs"
    $out = Join-Path $dist "$name-$($a.ver)-windows-x64.msi"

    Write-Host "=== $name $($a.ver) ==="
    & wix build $wxs -arch x64 -ext $extDll `
        -d "Version=$($a.ver)" -d "BinDir=$bin" -d "IconPath=$ico" `
        -o $out 2>&1 | Select-Object -Last 6

    if (Test-Path $out) {
        Write-Host ("    {0}  {1:n1} MB" -f (Split-Path $out -Leaf), ((Get-Item $out).Length / 1MB))
    }
    else { Write-Host "    FAILED" }
}
