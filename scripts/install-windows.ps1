$ErrorActionPreference = "Stop"

$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$InstallDir = Join-Path $env:LOCALAPPDATA "QuotaSignal"
$VenvDir = Join-Path $InstallDir "venv"

py -m venv $VenvDir
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install --upgrade pip
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install "$RepoDir[menu]"

$Startup = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $Startup "QuotaSignal.lnk"
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $VenvDir "Scripts\pythonw.exe"
$Shortcut.Arguments = "-m quotasignal.cli tray"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Show shared ChatGPT and Codex quota"
$Shortcut.Save()

$Legacy = Join-Path $Startup "Codex Usage.lnk"
if (Test-Path $Legacy) { Remove-Item $Legacy }

& (Join-Path $VenvDir "Scripts\quotasignal.exe") --check
if ($LASTEXITCODE -ne 0) { throw "QuotaSignal could not read the quota. Open Codex, sign in, and run this script again." }
Start-Process -FilePath $Shortcut.TargetPath -ArgumentList $Shortcut.Arguments
Write-Host "QuotaSignal is installed and starts automatically when you sign in."
