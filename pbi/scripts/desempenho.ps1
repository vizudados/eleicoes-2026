# desempenho.ps1 - mede no motor do Desktop do projeto o tempo de cada consulta de uma lista (JSON), numa conexao so.
# Entrada: arquivo JSON [{ "chave": "...", "consulta": "EVALUATE ..." }]; saida: JSON com ms (frio e quente), linhas e
# caracteres devolvidos. Frio = depois de limpar o cache do motor (ClearCache); quente = a mesma consulta de novo.
# Uso: pwsh -NoProfile -File desempenho.ps1 -Entrada consultas.json -Saida tempos.json
param([Parameter(Mandatory)][string]$Entrada, [Parameter(Mandatory)][string]$Saida)
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$porta = (Get-Content -LiteralPath (Join-Path $Raiz 'qa\porta.txt') -Raw).Trim()
$dll = Join-Path $env:USERPROFILE '.nuget\packages\microsoft.analysisservices.adomdclient.netcore.retail.amd64\19.84.1\lib\netcoreapp3.0\Microsoft.AnalysisServices.AdomdClient.dll'
Add-Type -Path $dll
$itens = Get-Content -LiteralPath $Entrada -Raw -Encoding utf8 | ConvertFrom-Json
$cn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$porta")
$cn.Open()
$cmd = $cn.CreateCommand(); $cmd.CommandTimeout = 600
$cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
$rd = $cmd.ExecuteReader(); $db = $null; while ($rd.Read()) { $db = [string]$rd.GetValue(0) }; $rd.Close()
$limpa = '<ClearCache xmlns="http://schemas.microsoft.com/analysisservices/2003/engine"><Object><DatabaseID>' + $db + '</DatabaseID></Object></ClearCache>'
function Medir([string]$q) {
  $cmd.CommandText = $q
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $rd = $cmd.ExecuteReader(); $n = 0; $chars = 0
  while ($rd.Read()) { $n++; for ($i = 0; $i -lt $rd.FieldCount; $i++) { $v = $rd.GetValue($i); if ($v -is [string]) { $chars += $v.Length } } }
  $rd.Close(); $sw.Stop()
  return @($sw.Elapsed.TotalMilliseconds, $n, $chars)
}
$res = @()
foreach ($it in $itens) {
  $r = [ordered]@{ chave = $it.chave; frio = $null; quente = $null; linhas = $null; caracteres = $null; erro = $null }
  try {
    $cmd.CommandText = $limpa; [void]$cmd.ExecuteNonQuery()
    $a = Medir $it.consulta; $b = Medir $it.consulta
    $r.frio = [math]::Round($a[0]); $r.quente = [math]::Round($b[0]); $r.linhas = $a[1]; $r.caracteres = $a[2]
  } catch { $e = $_.Exception; while ($e.InnerException) { $e = $e.InnerException }; $r.erro = $e.Message }
  $res += [pscustomobject]$r
}
$cn.Close()
[IO.File]::WriteAllText($Saida, (ConvertTo-Json -InputObject $res -Depth 4), (New-Object Text.UTF8Encoding($false)))
Write-Host ("medidas " + $res.Count + " consultas -> " + $Saida)
