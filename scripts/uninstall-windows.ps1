$ErrorActionPreference = "Stop"

$InstallDir = Join-Path $env:LOCALAPPDATA "QuotaSignal"
$Shortcut = Join-Path ([Environment]::GetFolderPath("Startup")) "QuotaSignal.lnk"

# A running tray keeps files in the virtual environment locked, so stop it first.
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'quotasignal.exe'" |
  Where-Object { $_.CommandLine -like "*quotasignal*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

if (Test-Path $Shortcut) { Remove-Item $Shortcut }
if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }
Write-Host "QuotaSignal is removed."
