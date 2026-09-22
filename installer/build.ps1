# Собирает PresetGenius-Setup-1.0.0.exe (Standalone и/или VST3).
$ErrorActionPreference = "Stop"
$InstallerDir = $PSScriptRoot
$Root = Resolve-Path (Join-Path $InstallerDir "..")
$Stage = Join-Path $InstallerDir "staging"
$Cache = Join-Path $InstallerDir "cache"
$Version = "1.0.0"

New-Item -ItemType Directory -Force -Path $Cache, (Join-Path $Stage "licenses") | Out-Null

$Standalone = Join-Path $Root "synth\vital\plugin\builds\vs17\x64\Release\Standalone Plugin\Vial.exe"
$Vst3 = Join-Path $Root "synth\vital\plugin\builds\vs17\x64\Release\VST3\Vial.vst3"
if (-not (Test-Path $Standalone)) { throw "Standalone is not built: $Standalone" }
if (-not (Test-Path $Vst3)) { throw "VST3 is not built: $Vst3" }
Copy-Item $Standalone (Join-Path $Stage "PresetGenius.exe") -Force
Copy-Item $Vst3 (Join-Path $Stage "PresetGenius.vst3") -Force

Copy-Item (Join-Path $InstallerDir "files\*") $Stage -Force
$env:WAVETABLE_DIR = Join-Path $Stage "wavetables"
& (Join-Path $Root ".venv\Scripts\python.exe") (Join-Path $InstallerDir "make_wavetables.py")
if ($LASTEXITCODE -ne 0) { throw "Failed to build wavetables" }
Copy-Item (Join-Path $Root "synth\vital\LICENSE") (Join-Path $Stage "licenses\GPL-3.0.txt") -Force
Copy-Item (Join-Path $Root "ml\syntheon\LICENSE") (Join-Path $Stage "licenses\Syntheon-Apache-2.0.txt") -Force

function Copy-Tree($From, $To, [string[]]$ExcludeDirs) {
  New-Item -ItemType Directory -Force -Path $To | Out-Null
  $xd = @(".git", "__pycache__", ".github", ".pytest_cache", "docs", "test", "dexed") + $ExcludeDirs
  & robocopy $From $To /E /NFL /NDL /NJH /NJS /nc /ns /np /XD @xd /XF "Syntheon_Demo.ipynb" | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed: $From -> $To ($LASTEXITCODE)" }
}

Remove-Item -Recurse -Force (Join-Path $Stage "ml"), (Join-Path $Stage "redist") -ErrorAction SilentlyContinue
Copy-Tree (Join-Path $Root "server") (Join-Path $Stage "server")
Copy-Tree (Join-Path $Root "ml\syntheon") (Join-Path $Stage "ml\syntheon")
Copy-Tree (Join-Path $Root "ml\text2preset") (Join-Path $Stage "ml\text2preset")
$Bank = Join-Path $Root "ml\output\bank"
if (-not (Test-Path (Join-Path $Bank "embeddings.npy"))) { throw "Preset bank is missing. Run: python ml/text2preset/build_bank.py --n 500" }
Copy-Tree $Bank (Join-Path $Stage "ml\output\bank")

# В каждом пресете свой кусок white noise (~120 КБ). Для звука патча он не нужен,
# а установщик из-за него не сжимается. Оставляем один общий sample.
$Py = Join-Path $Root ".venv\Scripts\python.exe"
& $Py -c @"
import json
path = r'$Stage\ml\output\bank\presets.jsonl'
lines = [ln for ln in open(path, encoding='utf-8') if ln.strip()]
sample = json.loads(json.loads(lines[0])['preset'])['settings']['sample']
out = []
for ln in lines:
    wrap = json.loads(ln)
    preset = json.loads(wrap['preset'])
    preset['settings']['sample'] = sample
    wrap['preset'] = json.dumps(preset, ensure_ascii=False)
    out.append(json.dumps(wrap, ensure_ascii=False))
open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('slim presets MB', round(sum(len(x) for x in out) / 1e6, 1))
"@
if ($LASTEXITCODE -ne 0) { throw "Failed to slim preset bank" }

$Iscc = @(
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
  "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) { throw "Inno Setup 6 is not installed." }

& $Iscc "/DStage=$Stage" "/DVersion=$Version" (Join-Path $InstallerDir "PresetGenius.iss")
if ($LASTEXITCODE -ne 0) { throw "ISCC failed: $LASTEXITCODE" }

$Setup = Join-Path $InstallerDir "output\PresetGenius-Setup-$Version.exe"
Write-Host "OK $Setup"
Get-Item $Setup | Select-Object FullName, @{n="MB";e={[math]::Round($_.Length/1MB,1)}}
