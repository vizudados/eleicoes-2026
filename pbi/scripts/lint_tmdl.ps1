# lint_tmdl.ps1 - lint OFFLINE do TMDL de um SemanticModel pelo TOM (TmdlSerializer), sem Power BI Desktop.
# Kit da casa (Vizu Dados).
# ASCII puro de proposito (mesma regra dos .ps1 do kit).
#
# Uso:
#   pwsh -NoProfile -File lint_tmdl.ps1 -Pasta <...SemanticModel\definition> -Saida <resultado.json>
#
# O que prova: o TMDL parseia no mesmo TOM que o Desktop usa (19.84.1 netcore, cache NuGet local), toda
# referencia por nome resolve (sortByColumn, relacionamentos, hierarquias) e as regras abaixo passam.
# O que NAO prova: DAX e M (so o motor valida) - isso fica para o smoke test no Desktop.
# Regras extras: relacao many->one com filtro de direcao unica e tipos iguais nas duas pontas; nome de medida
# unico no modelo e diferente de qualquer coluna; medida com expressao nao vazia; tabela de dados com particao M;
# coluna de tabela M com sourceColumn; grupo de calculo exige discourageImplicitMeasures.
# Saida: JSON (UTF-8 sem BOM) com ok, erros, avisos e resumo. Codigo 0 = ok, 2 = erro.
param(
  [Parameter(Mandatory = $true)][string]$Pasta,
  [Parameter(Mandatory = $true)][string]$Saida
)
$ErrorActionPreference = 'Stop'
$lib = Join-Path $env:USERPROFILE '.nuget\packages\microsoft.analysisservices.netcore.retail.amd64\19.84.1\lib\netcoreapp3.0'
if ($env:BEV_TOM_LIB) { $lib = $env:BEV_TOM_LIB }

function Gravar($obj, [int]$codigo) {
  $json = $obj | ConvertTo-Json -Depth 8
  $dir = Split-Path -Parent $Saida
  if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [IO.File]::WriteAllText($Saida, $json, (New-Object Text.UTF8Encoding($false)))
  Write-Host ('lint_tmdl: ok=' + $obj.ok + ' erros=' + @($obj.erros).Count + ' avisos=' + @($obj.avisos).Count)
  exit $codigo
}

$erros = New-Object System.Collections.Generic.List[string]
$avisos = New-Object System.Collections.Generic.List[string]
try {
  Add-Type -Path (Join-Path $lib 'Microsoft.AnalysisServices.Core.dll')
  Add-Type -Path (Join-Path $lib 'Microsoft.AnalysisServices.Tabular.dll')
} catch {
  Gravar ([ordered]@{ ok = $false; erros = @('TOM nao carregou: ' + $_.Exception.Message); avisos = @(); resumo = $null }) 2
}
try {
  $db = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder($Pasta)
} catch {
  $e = $_.Exception
  $msgs = @()
  while ($e) { $msgs += $e.Message; $e = $e.InnerException }
  Gravar ([ordered]@{ ok = $false; erros = @('TMDL nao parseia: ' + ($msgs -join ' | ')); avisos = @(); resumo = $null }) 2
}

$m = $db.Model
$tipoRel = [Microsoft.AnalysisServices.Tabular.SingleColumnRelationship]
$many = [Microsoft.AnalysisServices.Tabular.RelationshipEndCardinality]::Many
$one = [Microsoft.AnalysisServices.Tabular.RelationshipEndCardinality]::One
$umaDirecao = [Microsoft.AnalysisServices.Tabular.CrossFilteringBehavior]::OneDirection

$tabelas = @()
$nomesMedidas = @{}
$nomesColunas = @{}
$temGrupo = $false
foreach ($t in $m.Tables) {
  $parts = @($t.Partitions | ForEach-Object { [string]$_.SourceType })
  $tabelas += [ordered]@{
    nome = $t.Name; oculta = $t.IsHidden; colunas = $t.Columns.Count; medidas = $t.Measures.Count
    particoes = $parts; grupoCalculo = ($null -ne $t.CalculationGroup)
    itens = @(if ($t.CalculationGroup) { $t.CalculationGroup.CalculationItems | ForEach-Object { $_.Name } })
    colunasOcultas = @($t.Columns | Where-Object { $_.IsHidden -and $_.Type -ne 'RowNumber' }).Count
    dataCategory = $t.DataCategory
  }
  if ($t.CalculationGroup) { $temGrupo = $true }
  foreach ($c in $t.Columns) {
    if ([string]$c.Type -eq 'RowNumber') { continue }
    $nomesColunas[($t.Name + '|' + $c.Name).ToLowerInvariant()] = $true
    if ($parts -contains 'M' -and [string]$c.Type -eq 'Data' -and -not $c.SourceColumn) {
      $erros.Add('coluna sem sourceColumn: ' + $t.Name + '.' + $c.Name)
    }
    if ($c.SortByColumn -and $c.SortByColumn.Table.Name -ne $t.Name) {
      $erros.Add('sortByColumn fora da tabela: ' + $t.Name + '.' + $c.Name)
    }
  }
  foreach ($x in $t.Measures) {
    $k = $x.Name.ToLowerInvariant()
    if ($nomesMedidas.ContainsKey($k)) { $erros.Add('medida repetida: ' + $x.Name) }
    $nomesMedidas[$k] = $t.Name
    if ([string]::IsNullOrWhiteSpace($x.Expression)) { $erros.Add('medida sem expressao: ' + $x.Name) }
    if (-not $x.Description) { $avisos.Add('medida sem descricao: ' + $x.Name) }
  }
}
foreach ($k in $nomesMedidas.Keys) {
  foreach ($c in $nomesColunas.Keys) {
    if ($c.Split('|')[1] -eq $k) { $erros.Add('medida com nome de coluna: ' + $k + ' (' + $c + ')') }
  }
}
if ($temGrupo -and -not $m.DiscourageImplicitMeasures) { $erros.Add('grupo de calculo exige discourageImplicitMeasures') }

$relacoes = @()
foreach ($r in $m.Relationships) {
  $s = $r -as $tipoRel
  if (-not $s) { $erros.Add('relacao que nao e de coluna unica: ' + $r.Name); continue }
  $de = $s.FromColumn; $para = $s.ToColumn
  if (-not $de -or -not $para) { $erros.Add('relacao com coluna nao resolvida: ' + $r.Name); continue }
  if ($de.DataType -ne $para.DataType) { $erros.Add('relacao com tipos diferentes: ' + $r.Name + ' (' + $de.DataType + ' x ' + $para.DataType + ')') }
  if ($s.FromCardinality -ne $many -or $s.ToCardinality -ne $one) { $erros.Add('relacao que nao e many->one: ' + $r.Name) }
  # excecao declarada: a ponte do seletor de socio (dSocioEscolha -> dSocio) filtra nos dois sentidos
  if ($s.CrossFilteringBehavior -ne $umaDirecao -and $r.Name -ne 'rel_dSocioEscolha_Socio_dSocio') { $erros.Add('relacao sem direcao unica: ' + $r.Name) }
  if (-not $s.IsActive) { $avisos.Add('relacao inativa: ' + $r.Name) }
  $relacoes += [ordered]@{
    nome = $r.Name; de = ($de.Table.Name + '[' + $de.Name + ']'); para = ($para.Table.Name + '[' + $para.Name + ']')
    filtro = [string]$s.CrossFilteringBehavior; ativa = $s.IsActive
  }
}

$resumo = [ordered]@{
  compatibilidade = $db.CompatibilityLevel
  cultura = $m.Culture
  discourageImplicitMeasures = $m.DiscourageImplicitMeasures
  tabelas = $tabelas
  relacoes = $relacoes
  expressoes = @($m.Expressions | ForEach-Object { $_.Name })
  culturas = @($m.Cultures | ForEach-Object { $_.Name })
  medidas = $nomesMedidas.Count
}
$ok = ($erros.Count -eq 0)
Gravar ([ordered]@{ ok = $ok; erros = @($erros); avisos = @($avisos); resumo = $resumo }) ($(if ($ok) { 0 } else { 2 }))

