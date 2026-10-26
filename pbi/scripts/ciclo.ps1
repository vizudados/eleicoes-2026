# ciclo.ps1 - integra o projeto no Power BI Desktop: fecha a instancia do projeto (sem salvar), regera estilo, modelo e
# relatorio, confere o TMDL, reabre com refresh e a porta de depuracao 9347 (cdp.py) e deixa a janela maximizada.
# ASCII puro de proposito (console cp850).
# Uso: pwsh -NoProfile -File pbi\scripts\ciclo.ps1 [-SemModulo t21_vinte_anos,t22_simulador] [-Minimizar]
param([string[]]$SemModulo = @(), [switch]$Minimizar)
$ErrorActionPreference = 'Stop'
$S = $PSScriptRoot
$Pbi = Split-Path -Parent $S
Set-Location $Pbi
& pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $S 'desktop.ps1') -Acao fechar
python -X utf8 (Join-Path $S 'estilo.py')
if ($LASTEXITCODE -ne 0) { throw 'estilo.py falhou' }
python -I -X utf8 (Join-Path $S 'gerar_modelo.py') | Select-Object -Last 1
if ($LASTEXITCODE -ne 0) { throw 'gerar_modelo.py falhou' }
& pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $S 'lint_tmdl.ps1') -Pasta 'pbip\Eleicoes.SemanticModel\definition' -Saida 'qa\modelo\lint.json'
if ($LASTEXITCODE -ne 0) { throw 'lint do TMDL reprovou (qa\modelo\lint.json)' }
$args2 = @('-X', 'utf8', (Join-Path $S 'montar_pbip.py'), '--aplicar')
foreach ($m in $SemModulo) { $args2 += @('--sem-modulo', $m) }
python @args2 2>&1 | Select-Object -Last 4
if ($LASTEXITCODE -ne 0) { throw 'montar_pbip.py falhou' }
& pwsh -NoProfile -ExecutionPolicy Bypass -File (Join-Path $S 'desktop.ps1') -Acao abrir -Cdp 9347 -Espera 400 2>&1 | Select-Object -First 6
if ($LASTEXITCODE -ne 0) { throw 'o Desktop nao abriu ou o refresh falhou' }
if (-not $Minimizar) {
  Add-Type -Namespace Ciclo -Name W -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int c);'
  $p = Get-Process -Name PBIDesktop | Where-Object { $_.MainWindowTitle -like '*Eleicoes*' } | Select-Object -First 1
  if ($p) { [void][Ciclo.W]::ShowWindowAsync($p.MainWindowHandle, 3) }
}
Write-Host 'ciclo ok'
