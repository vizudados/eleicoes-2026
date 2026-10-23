# parametro.ps1 - troca o valor de um parametro M do modelo aberto no Desktop (TOM) e atualiza as tabelas pedidas.
# Uso: pwsh -NoProfile -File parametro.ps1 -Nome pPastaApuracao -Valor "dados/apuracao/ensaio-1turno" -Tabelas "Apuração Brasil","Apuração UF"
# So mexe no modelo em memoria do Desktop deste projeto (porta em qa\porta.txt); nada e salvo em disco.
param([Parameter(Mandatory)][string]$Nome, [Parameter(Mandatory)][string]$Valor, [string[]]$Tabelas = @())
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$porta = (Get-Content -LiteralPath (Join-Path $Raiz 'qa\porta.txt') -Raw).Trim()
$dll = Join-Path $env:USERPROFILE '.nuget\packages\microsoft.analysisservices.netcore.retail.amd64\19.84.1\lib\netcoreapp3.0'
Add-Type -Path (Join-Path $dll 'Microsoft.AnalysisServices.Core.dll')
Add-Type -Path (Join-Path $dll 'Microsoft.AnalysisServices.Tabular.dll')
$s = New-Object Microsoft.AnalysisServices.Tabular.Server
$s.Connect("Data Source=localhost:$porta")
try {
  $m = $s.Databases[0].Model
  $e = $m.Expressions[$Nome]
  if (-not $e) { throw "parametro $Nome nao existe" }
  $e.Expression = [regex]::Replace($e.Expression, '^"[^"]*"', ('"' + $Valor + '"'))
  foreach ($t in $Tabelas) { $m.Tables[$t].RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full) }
  [void]$m.SaveChanges()
  Write-Host ("ok: $Nome = $Valor; atualizadas: " + ($Tabelas -join ', '))
} finally { $s.Disconnect() }
