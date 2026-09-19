$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $env:LOCALAPPDATA "QuotaSignal"
$Shortcut = Join-Path ([Environment]::GetFolderPath("Startup")) "QuotaSignal.lnk"

if (Test-Path $Shortcut) { Remove-Item $Shortcut }
if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }
Write-Host "QuotaSignal is removed. Quit the tray icon if it is still running."
