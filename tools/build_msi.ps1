# Build Windows MSI installers from the portable builds in dist/.
#
#   pwsh -File tools/build_msi.ps1
#
# Needs the WiX 5 command line tool and two extensions:
#   dotnet tool install --global wix --version 5.0.2
#   (UI and Util are fetched from NuGet into %TEMP%; WiX no longer bundles them)
#
# WiX 7 is deliberately not used: it requires accepting the Open Source Maintenance
# Fee agreement, which is the project owner's decision, not this script's.
#
# Each app's .wxs wants slightly different inputs:
#   nib   needs a licence RTF and a folder of notices
#   sheaf needs an OCR models folder and an extra UI fragment

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root 'dist'
$env:PATH = "$env:USERPROFILE\.dotnet\tools;$env:PATH"

function Get-WixExtension([string]$id) {
    $dir = "$env:TEMP\wixext-$id"
    $dll = Get-ChildItem $dir -Recurse -Filter "$id.dll" -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
    if ($dll) { return $dll }
    if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
    $nupkg = "$env:TEMP\$id.nupkg"
    if (-not (Test-Path $nupkg)) {
        curl.exe -sS -L --fail -o $nupkg "https://www.nuget.org/api/v2/package/WixToolset.$id.wixext/5.0.2"
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($nupkg, $dir)
    return (Get-ChildItem $dir -Recurse -Filter "$id.dll" | Select-Object -First 1 -ExpandProperty FullName)
}

$uiExt = Get-WixExtension 'UI'
$utilExt = Get-WixExtension 'Util'

$notices = Join-Path $dist 'notices'
$models = Join-Path $dist 'models'

$apps = @(
    @{ slug = 'nib';    ver = '0.15.0'; extra = @('-d', "LicenseRtf=$notices\License.rtf", '-d', "AppNoticesDir=$notices"); sources = @() },
    @{ slug = 'tally';  ver = '0.16.0'; extra = @(); sources = @() },
    @{ slug = 'podium'; ver = '0.15.0'; extra = @(); sources = @() },
    @{ slug = 'sheaf';  ver = '0.18.0'; extra = @('-d', "ModelsDir=$models"); sources = @((Join-Path $root 'apps\sheaf\packaging\windows\installer-ui.wxs')) }
)

foreach ($a in $apps) {
    $bin = Join-Path $dist "$($a.slug)-$($a.ver)-windows-x64"
    if (-not (Test-Path (Join-Path $bin "$($a.slug).exe"))) {
        Write-Host "skip $($a.slug) (no portable build)"
        continue
    }
    $ico = Join-Path $root "apps\$($a.slug)\assets\app-icon\$($a.slug).ico"
    $wxs = Join-Path $root "apps\$($a.slug)\packaging\windows\$($a.slug).wxs"
    $out = Join-Path $dist "$($a.slug)-$($a.ver)-windows-x64.msi"

    Write-Host "=== $($a.slug) $($a.ver) ==="
    $wixArgs = @($wxs) + $a.sources + @(
        '-arch', 'x64', '-ext', $uiExt, '-ext', $utilExt,
        '-d', "Version=$($a.ver)",
        '-d', "BinDir=$bin",
        '-d', "IconPath=$ico"
    ) + $a.extra + @('-o', $out)

    $output = & wix build @wixArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        $output | Select-Object -Last 8 | ForEach-Object { "    $_" }
    }

    if (Test-Path $out) {
        Write-Host ("    {0}  {1:n1} MB" -f (Split-Path $out -Leaf), ((Get-Item $out).Length / 1MB))
    }
    else { Write-Host "    FAILED" }
}
