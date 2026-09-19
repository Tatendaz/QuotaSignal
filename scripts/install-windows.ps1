$ErrorActionPreference = "Stop"

$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$InstallDir = Join-Path $env:LOCALAPPDATA "CodexUsage"
$VenvDir = Join-Path $InstallDir "venv"

py -m venv $VenvDir
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install --upgrade pip
& (Join-Path $VenvDir "Scripts\python.exe") -m pip install "$RepoDir[menu]"

$Startup = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $Startup "Codex Usage.lnk"
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $VenvDir "Scripts\pythonw.exe"
$Shortcut.Arguments = "-m codex_usage.cli tray"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Show shared ChatGPT and Codex quota"
$Shortcut.Save()

& (Join-Path $VenvDir "Scripts\codex-usage.exe") --check
Start-Process -FilePath $Shortcut.TargetPath -ArgumentList $Shortcut.Arguments
Write-Host "Codex Usage is installed and starts automatically when you sign in."
