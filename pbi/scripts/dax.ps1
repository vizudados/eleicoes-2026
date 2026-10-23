# dax.ps1 - executa uma consulta DAX (ou DMV) no motor local do Power BI Desktop (projeto Eleicoes 2026)
# via ADOMD.NET e grava o resultado em ARQUIVO UTF-8 sem BOM. Adaptado do kit da casa
# (producao\scripts\dax.ps1; a origem fica intocada). ASCII puro de proposito: o console usa cp850.
#
# Uso (o resultado vai sempre para arquivo; o stdout so traz um resumo ASCII):
#   pwsh -NoProfile -File dax.ps1 -QueryFile consulta.dax -Out saida.json
#   pwsh -NoProfile -File dax.ps1 -Query 'EVALUATE ROW("x", 1)' -Out saida.tsv
# Parametros:
#   -Port <n>          porta do msmdsrv; omitido = le ..\qa\porta.txt (gravado por desktop.ps1)
#   -Query / -QueryFile  texto da consulta, ou arquivo UTF-8 com ela (prefira arquivo: aspas)
#   -Out <arq>         .json (tipado, sem perda) ou .tsv (texto escapado, reversivel)
#   -Timeout <s>       limite da consulta em segundos (padrao 300)
# Formato .json:
#   ok:   {"ok":true,"porta":N,"ms":N,"resultados":[{"colunas":[..],"tipos":[..],"linhas":[[..],..]}]}
#   erro: {"ok":false,"porta":N,"ms":N,"etapa":"conexao|consulta","erro":"<mensagem do motor>",
#          "detalhes":[{"mensagem":..,"codigo":..,"linha":..,"coluna":..}]}
#   datas saem em ISO sem fuso (yyyy-MM-ddTHH:mm:ss[.fffffff]); numeros com ponto; NaN/Infinity como texto.
# Formato .tsv: cabecalho + linhas; \ vira \\ , TAB vira \t , CR vira \r , LF vira \n (reversivel);
#   varios EVALUATE saem separados por uma linha "#resultado N"; em erro grava <Out>.erro.txt.
# Codigos de saida: 0 ok | 1 uso ou ambiente | 2 erro do motor (sintaxe, nome...) | 3 conexao ou porta.
# Somente leitura: nao chama SaveChanges, nao executa TMSL. Para refresh use desktop.ps1 -Acao refresh.
param(
  [int]$Port,
  [string]$Query,
  [string]$QueryFile,
  [string]$Out,
  [int]$Timeout = 300
)
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$Inv = [Globalization.CultureInfo]::InvariantCulture
$Utf8 = New-Object Text.UTF8Encoding($false)
$DllPadrao = Join-Path $env:USERPROFILE '.nuget\packages\microsoft.analysisservices.adomdclient.netcore.retail.amd64\19.84.1\lib\netcoreapp3.0\Microsoft.AnalysisServices.AdomdClient.dll'
$Dll = if ($env:VIZU_ADOMD_DLL) { $env:VIZU_ADOMD_DLL } else { $DllPadrao }

function Sair([int]$codigo, [string]$msg) {
  Write-Output $msg
  exit $codigo
}

if (-not $Out) { Sair 1 'uso: dax.ps1 (-Query "<dax>" | -QueryFile <arq>) -Out <saida.json|saida.tsv> [-Port n] [-Timeout s]' }
$Modo = [IO.Path]::GetExtension($Out).ToLowerInvariant()
if ($Modo -ne '.json' -and $Modo -ne '.tsv') { Sair 1 ('-Out precisa terminar em .json ou .tsv: ' + $Out) }
if ($QueryFile) {
  if (-not (Test-Path -LiteralPath $QueryFile)) { Sair 1 ('arquivo de consulta nao existe: ' + $QueryFile) }
  $Query = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $QueryFile).Path, [Text.Encoding]::UTF8)
}
if (-not $Query -or -not $Query.Trim()) { Sair 1 'consulta vazia (use -Query ou -QueryFile)' }
$Out = [IO.Path]::GetFullPath($Out)
$PastaOut = Split-Path -Parent $Out
if (-not (Test-Path -LiteralPath $PastaOut)) { New-Item -ItemType Directory -Force -Path $PastaOut | Out-Null }

$JsonOpts = [System.Text.Json.JsonSerializerOptions]::new()
$JsonOpts.Encoder = [System.Text.Encodings.Web.JavaScriptEncoder]::UnsafeRelaxedJsonEscaping

function JStr([string]$s) {
  if ($null -eq $s) { return 'null' }
  return [System.Text.Json.JsonSerializer]::Serialize($s, [string], $JsonOpts)
}

function Format-Json($v) {
  if ($null -eq $v -or $v -is [DBNull]) { return 'null' }
  if ($v -is [string]) { return (JStr $v) }
  if ($v -is [bool]) { if ($v) { return 'true' } else { return 'false' } }
  if ($v -is [datetime]) { return '"' + $v.ToString('yyyy-MM-ddTHH:mm:ss.FFFFFFF', $Inv) + '"' }
  if ($v -is [double] -or $v -is [single]) {
    if ([double]::IsNaN($v) -or [double]::IsInfinity($v)) { return '"' + $v.ToString($Inv) + '"' }
    return $v.ToString('R', $Inv)
  }
  if ($v -is [decimal] -or $v -is [int64] -or $v -is [int32] -or $v -is [int16] -or $v -is [byte] -or $v -is [uint64] -or $v -is [uint32]) {
    return $v.ToString($Inv)
  }
  return (JStr ([string]$v))
}

function Format-Tsv($v) {
  if ($null -eq $v -or $v -is [DBNull]) { return '' }
  if ($v -is [bool]) { if ($v) { return 'true' } else { return 'false' } }
  if ($v -is [datetime]) { return $v.ToString('yyyy-MM-ddTHH:mm:ss.FFFFFFF', $Inv) }
  if ($v -is [double] -or $v -is [single]) { return $v.ToString('R', $Inv) }
  if ($v -is [IFormattable]) { $s = $v.ToString($null, $Inv) } else { $s = [string]$v }
  return $s.Replace('\', '\\').Replace("`t", '\t').Replace("`r", '\r').Replace("`n", '\n')
}

function Get-Detalhes($ex) {
  # percorre a cadeia de excecoes; AdomdErrorResponseException traz Errors com Location (linha/coluna)
  $itens = New-Object System.Collections.Generic.List[string]
  $msgMotor = $null
  $e = $ex
  while ($null -ne $e) {
    $errs = $null
    try { $errs = $e.Errors } catch { $errs = $null }
    if ($null -ne $errs) {
      foreach ($er in $errs) {
        $linha = 'null'; $coluna = 'null'
        try {
          $loc = $er.Location
          if ($null -ne $loc) { $linha = [string]$loc.StartLine; $coluna = [string]$loc.StartColumn }
        } catch { }
        $cod = 'null'
        try { $cod = [string][int64]$er.ErrorCode } catch { }
        $itens.Add('{"mensagem":' + (JStr $er.Message) + ',"codigo":' + $cod + ',"linha":' + $linha + ',"coluna":' + $coluna + '}')
        if (-not $msgMotor) { $msgMotor = $er.Message }
      }
    }
    if (-not $msgMotor -and $e.GetType().FullName -like 'Microsoft.AnalysisServices*') { $msgMotor = $e.Message }
    $ultimo = $e
    $e = $e.InnerException
  }
  if (-not $msgMotor) { $msgMotor = $ultimo.Message }
  return @{ mensagem = $msgMotor; json = ('[' + ($itens -join ',') + ']'); tipo = $ultimo.GetType().FullName }
}

function Gravar-Erro([string]$etapa, $ex, [int]$ms, [int]$codigo) {
  $d = Get-Detalhes $ex
  if ($Modo -eq '.json') {
    $txt = '{"ok":false,"porta":' + $Port + ',"ms":' + $ms + ',"etapa":' + (JStr $etapa) + ',"erro":' + (JStr $d.mensagem) + ',"tipo":' + (JStr $d.tipo) + ',"detalhes":' + $d.json + '}'
    [IO.File]::WriteAllText($Out, $txt, $Utf8)
    $onde = $Out
  } else {
    if (Test-Path -LiteralPath $Out) { Remove-Item -LiteralPath $Out -Force }
    $onde = $Out + '.erro.txt'
    [IO.File]::WriteAllText($onde, ($etapa + "`n" + $d.mensagem + "`n" + $d.json + "`n"), $Utf8)
  }
  # a mensagem do motor pode ter acentos: vai inteira no arquivo; no console so o essencial em ASCII
  $ascii = [Text.RegularExpressions.Regex]::Replace($d.mensagem, '[^\x20-\x7E]', '?')
  if ($ascii.Length -gt 400) { $ascii = $ascii.Substring(0, 400) + '...' }
  Sair $codigo ('ERRO ' + $etapa + ' (porta ' + $Port + '): ' + $ascii + ' -> ' + $onde)
}

# porta
if (-not $Port) {
  $arqPorta = Join-Path $Raiz 'qa\porta.txt'
  if (-not (Test-Path -LiteralPath $arqPorta)) { Sair 3 ('sem -Port e sem ' + $arqPorta + ': rode desktop.ps1 -Acao porta (ou -Acao abrir)') }
  $txtPorta = (Get-Content -LiteralPath $arqPorta -Raw)
  $m = [regex]::Match([string]$txtPorta, '\d+')
  if (-not $m.Success) { Sair 3 ('porta.txt sem numero: ' + $arqPorta) }
  $Port = [int]$m.Value
}

if (-not (Test-Path -LiteralPath $Dll)) { Sair 1 ('DLL do ADOMD nao encontrada: ' + $Dll + ' (defina VIZU_ADOMD_DLL)') }
Add-Type -Path $Dll

$t0 = [Diagnostics.Stopwatch]::StartNew()
$cn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
try {
  $cn.Open()
} catch {
  Gravar-Erro 'conexao' $_.Exception ([int]$t0.ElapsedMilliseconds) 3
}
try {
  $cmd = $cn.CreateCommand()
  $cmd.CommandText = $Query
  $cmd.CommandTimeout = $Timeout
  try {
    $rd = $cmd.ExecuteReader()
  } catch {
    Gravar-Erro 'consulta' $_.Exception ([int]$t0.ElapsedMilliseconds) 2
  }
  $corpo = New-Object Text.StringBuilder
  $nRes = 0; $nLinhasTotal = 0; $resumo = @()
  try {
    do {
      $nRes++
      $n = $rd.FieldCount
      $cols = @(); $tipos = @()
      for ($i = 0; $i -lt $n; $i++) {
        $cols += $rd.GetName($i)
        $tp = $null
        try { $tp = $rd.GetFieldType($i) } catch { $tp = $null }
        if ($null -ne $tp) { $tipos += $tp.Name } else { $tipos += 'Object' }
      }
      $nLinhas = 0
      if ($Modo -eq '.json') {
        if ($nRes -gt 1) { [void]$corpo.Append(',') }
        [void]$corpo.Append('{"colunas":[').Append((($cols | ForEach-Object { JStr $_ }) -join ',')).Append('],"tipos":[')
        [void]$corpo.Append((($tipos | ForEach-Object { JStr $_ }) -join ',')).Append('],"linhas":[')
        while ($rd.Read()) {
          if ($nLinhas -gt 0) { [void]$corpo.Append(',') }
          [void]$corpo.Append('[')
          for ($i = 0; $i -lt $n; $i++) {
            if ($i -gt 0) { [void]$corpo.Append(',') }
            [void]$corpo.Append((Format-Json $rd.GetValue($i)))
          }
          [void]$corpo.Append(']')
          $nLinhas++
        }
        [void]$corpo.Append(']}')
      } else {
        if ($nRes -gt 1) { [void]$corpo.Append('#resultado ' + $nRes + "`n") }
        [void]$corpo.Append((($cols | ForEach-Object { Format-Tsv $_ }) -join "`t")).Append("`n")
        while ($rd.Read()) {
          $vals = New-Object string[] $n
          for ($i = 0; $i -lt $n; $i++) { $vals[$i] = Format-Tsv $rd.GetValue($i) }
          [void]$corpo.Append(($vals -join "`t")).Append("`n")
          $nLinhas++
        }
      }
      $nLinhasTotal += $nLinhas
      $resumo += ('{0}x{1}' -f $nLinhas, $n)
    } while ($rd.NextResult())
    $rd.Close()
  } catch {
    Gravar-Erro 'consulta' $_.Exception ([int]$t0.ElapsedMilliseconds) 2
  }
  $ms = [int]$t0.ElapsedMilliseconds
  if ($Modo -eq '.json') {
    $txt = '{"ok":true,"porta":' + $Port + ',"ms":' + $ms + ',"resultados":[' + $corpo.ToString() + ']}'
  } else {
    $txt = $corpo.ToString()
  }
  [IO.File]::WriteAllText($Out, $txt, $Utf8)
  $erroVelho = $Out + '.erro.txt'
  if (Test-Path -LiteralPath $erroVelho) { Remove-Item -LiteralPath $erroVelho -Force }
  Write-Output ('ok porta=' + $Port + ' ms=' + $ms + ' resultados=' + $nRes + ' (' + ($resumo -join ', ') + ') -> ' + $Out)
} finally {
  if ($cn.State -eq 'Open') { $cn.Close() }
}
exit 0
