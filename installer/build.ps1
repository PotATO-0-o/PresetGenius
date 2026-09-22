# Собирает PresetGenius-Setup-1.0.0.exe (Standalone и/или VST3).
$ErrorActionPreference = "Stop"
$InstallerDir = $PSScriptRoot
$Root = Resolve-Path (Join-Path $InstallerDir "..")
$Stage = Join-Path $InstallerDir "staging"
$Cache = Join-Path $InstallerDir "cache"
$Version = "1.0.0"

$VcRedist = Get-ChildItem "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Redist\MSVC" -Recurse -Filter "vc_redist.x64.exe" |
  Where-Object { $_.FullName -notmatch '\\v143\\' } |
  Select-Object -First 1 -ExpandProperty FullName
if (-not $VcRedist) { throw "vc_redist.x64.exe not found. Install Visual Studio Build Tools." }
$VcDir = Split-Path $VcRedist -Parent

New-Item -ItemType Directory -Force -Path $Cache, (Join-Path $Stage "redist"), (Join-Path $Stage "licenses") | Out-Null

$PythonExe = Join-Path $Cache "python-3.11.9-amd64.exe"
if (-not (Test-Path $PythonExe)) {
  Write-Host "Downloading Python 3.11.9..."
  Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $PythonExe
}
Copy-Item $PythonExe (Join-Path $Stage "redist\python-3.11.9-amd64.exe") -Force

$Standalone = Join-Path $Root "synth\vital\plugin\builds\vs17\x64\Release\Standalone Plugin\Vial.exe"
$Vst3 = Join-Path $Root "synth\vital\plugin\builds\vs17\x64\Release\VST3\Vial.vst3"
if (-not (Test-Path $Standalone)) { throw "Standalone is not built: $Standalone" }
if (-not (Test-Path $Vst3)) { throw "VST3 is not built: $Vst3" }
Copy-Item $Standalone (Join-Path $Stage "PresetGenius.exe") -Force
Copy-Item $Vst3 (Join-Path $Stage "PresetGenius.vst3") -Force

Copy-Item (Join-Path $InstallerDir "files\*") $Stage -Force
Copy-Item (Join-Path $Root "synth\vital\LICENSE") (Join-Path $Stage "licenses\GPL-3.0.txt") -Force
Copy-Item (Join-Path $Root "ml\syntheon\LICENSE") (Join-Path $Stage "licenses\Syntheon-Apache-2.0.txt") -Force

function Copy-Tree($From, $To) {
  New-Item -ItemType Directory -Force -Path $To | Out-Null
  & robocopy $From $To /E /NFL /NDL /NJH /NJS /nc /ns /np /XD .git __pycache__ .github .pytest_cache | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed: $From -> $To ($LASTEXITCODE)" }
}

Copy-Tree (Join-Path $Root "server") (Join-Path $Stage "server")
Copy-Tree (Join-Path $Root "ml\syntheon") (Join-Path $Stage "ml\syntheon")
Copy-Tree (Join-Path $Root "ml\text2preset") (Join-Path $Stage "ml\text2preset")
$Bank = Join-Path $Root "ml\output\bank"
if (-not (Test-Path (Join-Path $Bank "embeddings.npy"))) { throw "Preset bank is missing. Run: python ml/text2preset/build_bank.py --n 500" }
Copy-Tree $Bank (Join-Path $Stage "ml\output\bank")

$Iscc = @(
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
  "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) { throw "Inno Setup 6 is not installed." }

& $Iscc "/DStage=$Stage" "/DRedist=$VcDir" "/DVersion=$Version" (Join-Path $InstallerDir "PresetGenius.iss")
if ($LASTEXITCODE -ne 0) { throw "ISCC failed: $LASTEXITCODE" }

$Setup = Join-Path $InstallerDir "output\PresetGenius-Setup-$Version.exe"
Write-Host "OK $Setup"
Get-Item $Setup | Select-Object FullName, @{n="MB";e={[math]::Round($_.Length/1MB,1)}}
