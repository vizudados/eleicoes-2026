# desktop.ps1 - controla SO a instancia do Power BI Desktop do projeto Eleicoes 2026 (kit da casa, Vizu Dados).
# Regras (brief B9, L046): so o agente modelo abre e fecha o Desktop; janela minimizada; nunca encerra
# uma instancia que nao seja a do projeto (confere titulo da janela ou linha de comando); nao salva pelo Desktop.
# ASCII puro de proposito (console cp850).
#
# Uso:
#   pwsh -NoProfile -File desktop.ps1 -Acao checar          (confere o projeto em disco; nunca abre o Desktop)
#   pwsh -NoProfile -File desktop.ps1 -Acao abrir  [-Reabrir] [-SemRefresh] [-Espera 360]
#   pwsh -NoProfile -File desktop.ps1 -Acao porta
#   pwsh -NoProfile -File desktop.ps1 -Acao refresh         (TMSL full + contagem de linhas por tabela)
#   pwsh -NoProfile -File desktop.ps1 -Acao foto   [-Saida qa\desktop\foto.png]
#   pwsh -NoProfile -File desktop.ps1 -Acao fechar          (so a instancia do projeto, sem salvar; apaga qa\porta.txt)
#   pwsh -NoProfile -File desktop.ps1 -Acao listar          (lista os PBIDesktop abertos, sem tocar em nada)
#   pwsh -NoProfile -File desktop.ps1 -Acao minimizar       (minimiza so a janela do projeto)
# Opcoes: -Pbip <arq.pbip> (padrao ..\pbip\projeto - Painel de Operacao.pbip) | -Titulo <trecho da janela> | -ArquivoPorta <txt>
#         -SaidaContagem <json> (refresh: grava as contagens; padrao qa\modelo\refresh-<data>.json)
# Codigos de saida: 0 ok | 1 instancia nao encontrada ou tempo esgotado | 2 erro (uso, motor, refresh, projeto recusado).
param(
  [string]$Acao,
  [string]$Pbip,
  [string]$Titulo,
  [string]$Saida,
  [string]$ArquivoPorta,
  [string]$SaidaContagem,
  [int]$Espera = 360,
  [switch]$Reabrir,
  [switch]$SemRefresh,
  [int]$Cdp = 0
)
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
if (-not $Pbip) { $Pbip = (Get-ChildItem -LiteralPath (Join-Path $Raiz 'pbip') -Filter '*.pbip' | Select-Object -First 1).FullName }
$Pbip = [IO.Path]::GetFullPath($Pbip)
if (-not $Titulo) { $Titulo = [IO.Path]::GetFileNameWithoutExtension($Pbip) }
$ArqPorta = if ($ArquivoPorta) { [IO.Path]::GetFullPath($ArquivoPorta) } else { Join-Path $Raiz 'qa\porta.txt' }
$DllPadrao = Join-Path $env:USERPROFILE '.nuget\packages\microsoft.analysisservices.adomdclient.netcore.retail.amd64\19.84.1\lib\netcoreapp3.0\Microsoft.AnalysisServices.AdomdClient.dll'
$Dll = if ($env:BEV_ADOMD_DLL) { $env:BEV_ADOMD_DLL } else { $DllPadrao }

function Ascii([string]$s) {
  if ($null -eq $s) { return '' }
  return [Text.RegularExpressions.Regex]::Replace($s, '[^\x20-\x7E]', '?')
}
function Sair([int]$codigo, [string]$msg) { Write-Host $msg; exit $codigo }

function Carregar-Win32 {
  if (-not ('VizuDesktop.Api' -as [type])) {
    Add-Type -Namespace VizuDesktop -Name Api -MemberDefinition @"
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
[DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
[DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int cmd);
public struct RECT { public int Left, Top, Right, Bottom; }
"@
  }
}

function Get-Instancias {
  # todos os PBIDesktop; projeto = titulo da janela contem $Titulo OU a linha de comando traz o .pbip
  $linhas = @{}
  foreach ($c in @(Get-CimInstance Win32_Process -Filter "Name='PBIDesktop.exe'" -Property ProcessId, CommandLine -ErrorAction SilentlyContinue)) {
    $linhas[[int]$c.ProcessId] = [string]$c.CommandLine
  }
  $lista = @()
  foreach ($p in @(Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue)) {
    $t = [string]$p.MainWindowTitle
    $cl = [string]$linhas[[int]$p.Id]
    $porTitulo = $t.IndexOf($Titulo, [StringComparison]::OrdinalIgnoreCase) -ge 0
    $porLinha = $cl.IndexOf($Pbip, [StringComparison]::OrdinalIgnoreCase) -ge 0
    $lista += [pscustomobject]@{
      Id = $p.Id; Titulo = $t; Inicio = $p.StartTime; Janela = $p.MainWindowHandle
      Projeto = ($porTitulo -or $porLinha); PorTitulo = $porTitulo; PorLinha = $porLinha; Linha = $cl
    }
  }
  return , $lista
}

function Avisar-Outras($instancias) {
  foreach ($o in @($instancias | Where-Object { -not $_.Projeto })) {
    Write-Host ('aviso: outro Power BI Desktop aberto (pid ' + $o.Id + ', janela "' + (Ascii $o.Titulo) + '") - nao sera tocado')
  }
}

function Get-ProjetoUnico($instancias) {
  $doProjeto = @($instancias | Where-Object { $_.Projeto } | Sort-Object Inicio -Descending)
  if ($doProjeto.Count -gt 1) {
    Write-Host ('aviso: ' + $doProjeto.Count + ' janelas do projeto abertas (pids ' + (($doProjeto | ForEach-Object { $_.Id }) -join ', ') + '); uso a mais recente')
  }
  if ($doProjeto.Count -eq 0) { return $null }
  return $doProjeto[0]
}

function Get-Processos { return @(Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, Name, CommandLine, CreationDate) }

function Get-Descendentes([int]$raiz, $procs) {
  # 26/09/2026: filho legitimo = ParentProcessId igual E criado depois do pai. O Windows reaproveita PID: um processo cujo
  # pai ja morreu pode apontar para um PID reusado por outro programa. Nunca inclui outro PBIDesktop.exe (instancia de
  # outra sessao, de outro projeto). Caso real numa sessao paralela, avisado por mensagem.
  $saida = New-Object System.Collections.Generic.List[object]
  $vistos = New-Object System.Collections.Generic.HashSet[int]
  $criado = @{}
  foreach ($p in $procs) { $criado[[int]$p.ProcessId] = $p.CreationDate }
  $fila = New-Object System.Collections.Generic.Queue[int]
  $fila.Enqueue($raiz); [void]$vistos.Add($raiz)
  while ($fila.Count -gt 0) {
    $pai = $fila.Dequeue()
    $tPai = $criado[$pai]
    foreach ($p in $procs) {
      $id = [int]$p.ProcessId
      if ([int]$p.ParentProcessId -ne $pai) { continue }
      if ([string]$p.Name -ieq 'PBIDesktop.exe') { continue }
      if ($tPai -and $p.CreationDate -and ($p.CreationDate -lt $tPai)) { continue }
      if ($vistos.Add($id)) { $saida.Add($p); $fila.Enqueue($id) }
    }
  }
  return $saida.ToArray()
}

function Get-Motor([int]$pidDesktop) {
  # msmdsrv descendente do PBIDesktop; sem parentesco visivel, so aceita o par se houver um de cada
  $procs = Get-Processos
  $m = @(Get-Descendentes $pidDesktop $procs | Where-Object { $_.Name -eq 'msmdsrv.exe' })
  if ($m.Count -ge 1) { return $m[0] }
  $todos = @($procs | Where-Object { $_.Name -eq 'msmdsrv.exe' })
  $desks = @($procs | Where-Object { $_.Name -eq 'PBIDesktop.exe' })
  if ($todos.Count -eq 1 -and $desks.Count -eq 1) {
    Write-Host 'aviso: msmdsrv sem parentesco visivel; unico motor e unico Desktop, aceitei o par'
    return $todos[0]
  }
  return $null
}

function Get-PortaMotor($motor) {
  $porta = $null
  $c = @(Get-NetTCPConnection -OwningProcess ([int]$motor.ProcessId) -State Listen -ErrorAction SilentlyContinue |
         Where-Object { $_.LocalAddress -in @('127.0.0.1', '::1', '0.0.0.0', '::') })
  if ($c.Count -gt 0) { $porta = [int]$c[0].LocalPort }
  $m = [regex]::Match([string]$motor.CommandLine, '-s\s+"([^"]+)"')
  if ($m.Success) {
    $arq = Join-Path $m.Groups[1].Value 'msmdsrv.port.txt'
    if (Test-Path -LiteralPath $arq) {
      $bytes = [IO.File]::ReadAllBytes($arq) | Where-Object { $_ -ne 0 }
      $txt = [Text.Encoding]::ASCII.GetString([byte[]]$bytes)
      $mm = [regex]::Match($txt, '\d+')
      if ($mm.Success) {
        $pArq = [int]$mm.Value
        if ($porta -and $pArq -ne $porta) { Write-Host ('aviso: porta em escuta ' + $porta + ' difere de msmdsrv.port.txt (' + $pArq + ')') }
        if (-not $porta) { $porta = $pArq }
      }
    }
  }
  return $porta
}

function Carregar-Adomd {
  if (-not ('Microsoft.AnalysisServices.AdomdClient.AdomdConnection' -as [type])) {
    if (-not (Test-Path -LiteralPath $Dll)) { Sair 2 ('DLL do ADOMD nao encontrada: ' + $Dll + ' (defina BEV_ADOMD_DLL)') }
    Add-Type -Path $Dll
  }
}

function Get-EstadoModelo([int]$porta) {
  Carregar-Adomd
  $cn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$porta")
  try {
    $cn.Open()
    $cmd = $cn.CreateCommand(); $cmd.CommandTimeout = 60
    $cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
    $rd = $cmd.ExecuteReader(); $cat = $null
    while ($rd.Read()) { $cat = [string]$rd.GetValue(0) }
    $rd.Close()
    $tabs = @()
    if ($cat) {
      $cmd.CommandText = 'SELECT [Name] FROM $SYSTEM.TMSCHEMA_TABLES'
      $rd = $cmd.ExecuteReader()
      while ($rd.Read()) { $tabs += [string]$rd.GetValue(0) }
      $rd.Close()
    }
    return [pscustomobject]@{ Catalogo = $cat; Tabelas = $tabs }
  } catch {
    return $null
  } finally {
    if ($cn.State -eq 'Open') { $cn.Close() }
  }
}

function Invoke-Refresh([int]$porta, [string]$arqContagem) {
  Carregar-Adomd
  $cn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$porta")
  $cn.Open()
  try {
    $cmd = $cn.CreateCommand(); $cmd.CommandTimeout = 1800
    $cmd.CommandText = 'SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS'
    $rd = $cmd.ExecuteReader(); $db = $null
    while ($rd.Read()) { $db = [string]$rd.GetValue(0) }
    $rd.Close()
    if (-not $db) { Write-Host 'refresh FALHOU: o motor nao tem catalogo'; return $false }
    $ok = $false; $segundos = $null; $erro = $null
    $t0 = Get-Date
    $cmd.CommandText = '{"refresh":{"type":"full","objects":[{"database":"' + $db + '"}]}}'
    try {
      [void]$cmd.ExecuteNonQuery()
      $ok = $true
      $segundos = [int]((Get-Date) - $t0).TotalSeconds
      Write-Host ('refresh ok em ' + $segundos + ' s (catalogo ' + $db + ')')
    } catch {
      $e = $_.Exception; while ($e.InnerException) { $e = $e.InnerException }
      $erro = [string]$e.Message
      Write-Host ('refresh FALHOU: ' + (Ascii $erro))
    }
    $cmd.CommandText = 'SELECT [Name] FROM $SYSTEM.TMSCHEMA_TABLES'
    $rd = $cmd.ExecuteReader(); $tabs = @()
    while ($rd.Read()) { $tabs += [string]$rd.GetValue(0) }
    $rd.Close()
    $contagens = [ordered]@{}
    foreach ($t in ($tabs | Sort-Object)) {
      $cmd.CommandText = 'EVALUATE ROW("n", COUNTROWS(''' + $t.Replace("'", "''") + '''))'
      try {
        $rd = $cmd.ExecuteReader(); $n = $null
        while ($rd.Read()) { $n = $rd.GetValue(0) }
        $rd.Close()
        Write-Host ('  ' + (Ascii $t) + ' = ' + $n)
        $contagens[$t] = $n
      } catch {
        Write-Host ('  ' + (Ascii $t) + ' = (erro na contagem)')
        $contagens[$t] = $null
      }
    }
    if ($arqContagem) {
      $pasta = Split-Path -Parent $arqContagem
      if (-not (Test-Path -LiteralPath $pasta)) { New-Item -ItemType Directory -Force -Path $pasta | Out-Null }
      $doc = [ordered]@{ quando = (Get-Date).ToString('s'); porta = $porta; catalogo = $db; ok = $ok; segundos = $segundos; erro = $erro; linhas = $contagens }
      [IO.File]::WriteAllText($arqContagem, ($doc | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
      Write-Host ('contagens gravadas em ' + $arqContagem)
    }
    return $ok
  } finally {
    if ($cn.State -eq 'Open') { $cn.Close() }
  }
}

function Confirmar-Porta($inst, [int]$esperaSeg) {
  $fim = (Get-Date).AddSeconds($esperaSeg)
  $motor = $null; $porta = $null; $estado = $null
  do {
    if (-not $motor) { $motor = Get-Motor $inst.Id }
    if ($motor -and -not $porta) { $porta = Get-PortaMotor $motor }
    if ($porta) {
      $estado = Get-EstadoModelo $porta
      if ($estado -and $estado.Catalogo -and $estado.Tabelas.Count -gt 0) { break }
    }
    if (-not (Get-Process -Id $inst.Id -ErrorAction SilentlyContinue)) {
      if (Test-Path -LiteralPath $ArqPorta) { Remove-Item -LiteralPath $ArqPorta -Force }
      Write-Host ('o Desktop (pid ' + $inst.Id + ') fechou durante a espera')
      return $null
    }
    Start-Sleep -Seconds 3
  } while ((Get-Date) -lt $fim)
  if (-not ($estado -and $estado.Catalogo -and $estado.Tabelas.Count -gt 0)) {
    if (Test-Path -LiteralPath $ArqPorta) { Remove-Item -LiteralPath $ArqPorta -Force }
    $m = if ($motor) { 'msmdsrv ' + $motor.ProcessId } else { 'sem msmdsrv filho' }
    $d = if ($estado -and $estado.Catalogo) { 'catalogo sem tabelas' } elseif ($porta) { 'motor sem modelo' } else { 'sem porta' }
    Write-Host ('tempo esgotado esperando o modelo do projeto (pid ' + $inst.Id + ', ' + $m + ', porta ' + $porta + ', ' + $d + ', janela "' + (Ascii $inst.Titulo) + '")')
    return $null
  }
  $pasta = Split-Path -Parent $ArqPorta
  if (-not (Test-Path -LiteralPath $pasta)) { New-Item -ItemType Directory -Force -Path $pasta | Out-Null }
  Set-Content -LiteralPath $ArqPorta -Value ([string]$porta) -Encoding ascii
  Write-Host ('porta=' + $porta + ' pid=' + $inst.Id + ' msmdsrv=' + $motor.ProcessId + ' catalogo=' + $estado.Catalogo + ' tabelas=' + $estado.Tabelas.Count + ' -> ' + $ArqPorta)
  return $porta
}

function Fechar-Projeto($instancias) {
  $doProjeto = @($instancias | Where-Object { $_.Projeto })
  if ($doProjeto.Count -eq 0) { return 0 }
  $procs = Get-Processos
  foreach ($inst in $doProjeto) {
    $desc = Get-Descendentes $inst.Id $procs
    # confere de novo antes de encerrar: o mesmo pid ainda e um PBIDesktop reconhecido como projeto
    $todas = Get-Instancias
    $agora = @($todas | Where-Object { $_.Id -eq $inst.Id -and $_.Projeto })
    if ($agora.Count -eq 1) {
      Stop-Process -Id $inst.Id -Force -ErrorAction SilentlyContinue
      foreach ($d in $desc) { Stop-Process -Id ([int]$d.ProcessId) -Force -ErrorAction SilentlyContinue }
      $fim = (Get-Date).AddSeconds(30)
      while ((Get-Process -Id $inst.Id -ErrorAction SilentlyContinue) -and (Get-Date) -lt $fim) { Start-Sleep -Milliseconds 500 }
      Write-Host ('fechada sem salvar: pid ' + $inst.Id + ' (+' + $desc.Count + ' processo(s) filho(s))')
    }
  }
  if (Test-Path -LiteralPath $ArqPorta) { Remove-Item -LiteralPath $ArqPorta -Force }
  return $doProjeto.Count
}

function Minimizar($inst) {
  Carregar-Win32
  $h = [IntPtr]$inst.Janela
  if ($h -ne [IntPtr]::Zero) { [void][VizuDesktop.Api]::ShowWindowAsync($h, 6) }   # SW_MINIMIZE
}

function Tirar-Foto($inst, [string]$arq) {
  # fotografa SO a janela do projeto (PrintWindow); se estiver minimizada, restaura sem ativar e minimiza de novo
  Add-Type -AssemblyName System.Drawing
  Carregar-Win32
  [void][VizuDesktop.Api]::SetProcessDPIAware()
  $h = [IntPtr]$inst.Janela
  if ($h -eq [IntPtr]::Zero) { Write-Host 'a instancia do projeto nao tem janela principal'; return }
  $estavaMin = [VizuDesktop.Api]::IsIconic($h)
  if ($estavaMin) { [void][VizuDesktop.Api]::ShowWindowAsync($h, 4); Start-Sleep -Milliseconds 1500 }   # SW_SHOWNOACTIVATE
  $rc = New-Object VizuDesktop.Api+RECT
  [void][VizuDesktop.Api]::GetWindowRect($h, [ref]$rc)
  $w = $rc.Right - $rc.Left; $a = $rc.Bottom - $rc.Top
  if ($w -le 0 -or $a -le 0) { Write-Host 'janela sem area visivel'; return }
  $bmp = New-Object System.Drawing.Bitmap $w, $a
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $hdc = $g.GetHdc()
  $ok = [VizuDesktop.Api]::PrintWindow($h, $hdc, 2)
  $g.ReleaseHdc($hdc)
  $pasta = Split-Path -Parent $arq
  if (-not (Test-Path -LiteralPath $pasta)) { New-Item -ItemType Directory -Force -Path $pasta | Out-Null }
  $bmp.Save($arq, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  if ($estavaMin) { [void][VizuDesktop.Api]::ShowWindowAsync($h, 6) }
  Write-Host ('foto ' + $arq + ' ' + $w + 'x' + $a + ' PrintWindow=' + $ok + ' pid=' + $inst.Id)
}

function Get-CaminhosLongos([string]$pasta) {
  # L045: arquivo < 260 e pasta < 248 caracteres (caminho completo), senao o Desktop recusa o projeto
  $ofensores = @()
  $raiz = Get-Item -LiteralPath $pasta -Force
  $itens = @($raiz) + @(Get-ChildItem -LiteralPath $pasta -Recurse -Force -ErrorAction Stop)
  foreach ($item in $itens) {
    $n = $item.FullName.Length
    if ($item.PSIsContainer) {
      if ($n -ge 248) { $ofensores += ('  pasta ' + $n + ': ' + (Ascii $item.FullName)) }
    } elseif ($n -ge 260) {
      $ofensores += ('  arquivo ' + $n + ': ' + (Ascii $item.FullName))
    }
  }
  return , $ofensores
}

function Test-Projeto([string]$arqPbip) {
  # $null se o projeto pode ir para o Desktop; senao o motivo. Nada aqui abre o Desktop (L046).
  if (-not (Test-Path -LiteralPath $arqPbip -PathType Leaf)) { return ('PBIP nao existe: ' + $arqPbip) }
  $pasta = Split-Path -Parent $arqPbip
  $longos = Get-CaminhosLongos $pasta
  if ($longos.Count -gt 0) {
    return ('caminho longo demais para o Desktop (arquivo >= 260 ou pasta >= 248 caracteres): ' + $longos.Count +
            ' ofensor(es)' + [Environment]::NewLine + (($longos | Select-Object -First 25) -join [Environment]::NewLine))
  }
  try { $doc = Get-Content -LiteralPath $arqPbip -Raw | ConvertFrom-Json } catch { return ('.pbip nao e JSON valido: ' + $arqPbip) }
  $reports = @($doc.artifacts | Where-Object { $_.report -and $_.report.path } | ForEach-Object { $_.report.path })
  if ($reports.Count -eq 0) { return ('.pbip sem artefato report: ' + $arqPbip) }
  foreach ($r in $reports) {
    $pastaRep = Join-Path $pasta $r
    $pbir = Join-Path $pastaRep 'definition.pbir'
    if (-not (Test-Path -LiteralPath $pbir -PathType Leaf)) { return ('falta ' + $pbir) }
    try { $def = Get-Content -LiteralPath $pbir -Raw | ConvertFrom-Json } catch { return ('definition.pbir nao e JSON valido: ' + $pbir) }
    $ref = $def.datasetReference
    if (-not $ref -or -not $ref.byPath -or -not $ref.byPath.path) {
      return ('definition.pbir sem datasetReference.byPath (relatorio sem modelo local): ' + $pbir)
    }
    $sm = [IO.Path]::GetFullPath((Join-Path $pastaRep $ref.byPath.path))
    if (-not (Test-Path -LiteralPath $sm -PathType Container)) { return ('o SemanticModel referenciado nao existe: ' + $sm) }
    $pbism = Join-Path $sm 'definition.pbism'
    if (-not (Test-Path -LiteralPath $pbism -PathType Leaf)) { return ('falta definition.pbism no SemanticModel: ' + $pbism) }
    $tmdl = Join-Path $sm 'definition\model.tmdl'
    $bim = Join-Path $sm 'model.bim'
    if (-not (Test-Path -LiteralPath $tmdl) -and -not (Test-Path -LiteralPath $bim)) {
      return ('SemanticModel sem definition\model.tmdl nem model.bim: ' + $sm)
    }
    foreach ($obrig in @('definition\report.json', 'definition\version.json', 'definition\pages\pages.json')) {
      if (-not (Test-Path -LiteralPath (Join-Path $pastaRep $obrig))) { return ('Report incompleto, falta ' + (Join-Path $pastaRep $obrig)) }
    }
  }
  return $null
}

$acoes = @('abrir', 'fechar', 'porta', 'foto', 'refresh', 'checar', 'listar', 'minimizar')
if ($acoes -notcontains $Acao) { Sair 2 ('uso: desktop.ps1 -Acao ' + ($acoes -join '|') + ' [-Pbip arq] [-Titulo txt] [-Saida png] [-ArquivoPorta txt] [-Reabrir] [-SemRefresh] [-Espera s]') }

if ($Acao -eq 'checar') {
  $motivo = Test-Projeto $Pbip
  if ($motivo) { Sair 2 ('NAO abre: ' + $motivo) }
  Sair 0 ('ok: ' + $Pbip + ' tem Report com byPath, SemanticModel, definition.pbism, definicao do modelo e caminhos curtos')
}

$inst = Get-Instancias
if ($Acao -eq 'listar') {
  if ($inst.Count -eq 0) { Sair 0 'nenhum Power BI Desktop aberto' }
  foreach ($i in $inst) { Write-Host ('pid ' + $i.Id + ' projeto=' + $i.Projeto + ' janela="' + (Ascii $i.Titulo) + '"') }
  exit 0
}
Avisar-Outras $inst

switch ($Acao) {
  'porta' {
    $t = Get-ProjetoUnico $inst
    if (-not $t) {
      if (Test-Path -LiteralPath $ArqPorta) { Remove-Item -LiteralPath $ArqPorta -Force }
      Sair 1 ('o projeto nao esta aberto (nenhum PBIDesktop com "' + $Titulo + '" na janela nem o .pbip na linha de comando); ' + $ArqPorta + ' apagado')
    }
    if (-not (Confirmar-Porta $t 30)) { exit 1 }
  }
  'refresh' {
    $t = Get-ProjetoUnico $inst
    if (-not $t) { Sair 1 'o projeto nao esta aberto' }
    $porta = Confirmar-Porta $t 30
    if (-not $porta) { exit 1 }
    $arqC = if ($SaidaContagem) { [IO.Path]::GetFullPath($SaidaContagem) } else { Join-Path $Raiz ('qa\modelo\refresh-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json') }
    if (-not (Invoke-Refresh $porta $arqC)) { exit 2 }
  }
  'foto' {
    $t = Get-ProjetoUnico $inst
    if (-not $t) { Sair 1 'o projeto nao esta aberto' }
    if (-not $Saida) { $Saida = Join-Path $Raiz ('qa\desktop\foto-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.png') }
    Tirar-Foto $t ([IO.Path]::GetFullPath($Saida))
  }
  'minimizar' {
    $t = Get-ProjetoUnico $inst
    if (-not $t) { Sair 1 'o projeto nao esta aberto' }
    Minimizar $t
    Write-Host ('minimizada: pid ' + $t.Id)
  }
  'fechar' {
    $n = Fechar-Projeto $inst
    if ($n -eq 0) {
      if (Test-Path -LiteralPath $ArqPorta) { Remove-Item -LiteralPath $ArqPorta -Force }
      Write-Host 'o projeto nao estava aberto'
    }
  }
  'abrir' {
    $t = Get-ProjetoUnico $inst
    if ($t -and -not $Reabrir) {
      Write-Host ('o projeto ja esta aberto (pid ' + $t.Id + '); para recarregar do disco use -Reabrir (fecha SEM salvar)')
      Minimizar $t
      if (-not (Confirmar-Porta $t 60)) { exit 1 }
      exit 0
    }
    $motivo = Test-Projeto $Pbip
    if ($motivo) { Sair 2 ('recusado, o Desktop NAO foi aberto: ' + $motivo) }
    if ($t -and $Reabrir) { [void](Fechar-Projeto $inst); Start-Sleep -Seconds 3 }
    $antes = @(Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $t0 = Get-Date
    # L087: pelo alias da Store, com WebView2 proprio do projeto (so neste processo), para nao dividir o navegador
    # com outra instancia do Desktop aberta por outra sessao
    $alias = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\PBIDesktopStore.exe'
    $wv2 = Join-Path $env:USERPROFILE 'Microsoft\Power BI Desktop Store App\WebView2-Eleicoes2026'
    if (Test-Path -LiteralPath $alias) {
      $antigo = $env:WEBVIEW2_USER_DATA_FOLDER
      $antigoArgs = $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS
      $env:WEBVIEW2_USER_DATA_FOLDER = $wv2
      # -Cdp <porta> (so para provas, 20/10/2026, receita da casa): abre a porta de depuracao do navegador
      # desta instancia em 127.0.0.1, para pbi\qa\exporta\cdp_exporta.py pedir ao botao de PDF a imagem por dentro,
      # sem baixar. Vale so neste processo e na pasta de dados do projeto (L087); nada do sistema muda.
      if ($Cdp -gt 0) { $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = (($env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS + ' --remote-debugging-address=127.0.0.1 --remote-debugging-port=' + $Cdp).Trim()) }
      try { Start-Process -FilePath $alias -ArgumentList ('"' + $Pbip + '"') -WindowStyle Minimized }
      finally { $env:WEBVIEW2_USER_DATA_FOLDER = $antigo; $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = $antigoArgs }
    } else {
      Start-Process -FilePath $Pbip -WindowStyle Minimized
    }
    Write-Host ('abrindo (minimizado) ' + $Pbip)
    $nova = $null
    $fim = (Get-Date).AddSeconds($Espera)
    while (-not $nova -and (Get-Date) -lt $fim) {
      Start-Sleep -Seconds 3
      $nova = Get-ProjetoUnico (Get-Instancias)
    }
    if (-not $nova) { Sair 1 ('nenhuma instancia do projeto (janela ou linha de comando) apareceu em ' + $Espera + ' s') }
    if ($antes -contains $nova.Id) { Write-Host ('aviso: a janela do projeto esta num processo que ja existia (pid ' + $nova.Id + ')') }
    # a janela principal pode demorar a existir; minimiza assim que houver handle
    $fimJ = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $fimJ) {
      $todas = Get-Instancias
      $viva = @($todas | Where-Object { $_.Id -eq $nova.Id })
      if ($viva.Count -eq 1 -and [IntPtr]$viva[0].Janela -ne [IntPtr]::Zero) { Minimizar $viva[0]; break }
      Start-Sleep -Seconds 2
    }
    $restante = [int]([Math]::Max(60, $Espera - ((Get-Date) - $t0).TotalSeconds))
    $porta = Confirmar-Porta $nova $restante
    if (-not $porta) {
      $viva = Get-ProjetoUnico (Get-Instancias)
      if ($viva) {
        $arqFalha = if ($Saida) { [IO.Path]::GetFullPath($Saida) } else { Join-Path $Raiz ('qa\desktop\falha-abrir-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.png') }
        Tirar-Foto $viva $arqFalha
        Write-Host 'a instancia ficou aberta para leitura do erro; feche com -Acao fechar'
      }
      exit 1
    }
    Write-Host ('modelo carregado em ' + [int]((Get-Date) - $t0).TotalSeconds + ' s')
    # L097: o refresh so depois de o Desktop terminar o lote de carga (titulo da janela com o nome do projeto)
    $fimT = (Get-Date).AddSeconds(300)
    do {
      $viva = Get-ProjetoUnico (Get-Instancias)
      if ($viva -and $viva.PorTitulo) { break }
      Start-Sleep -Seconds 3
    } while ((Get-Date) -lt $fimT)
    if ($viva -and $viva.PorTitulo) { Write-Host ('relatorio carregado em ' + [int]((Get-Date) - $t0).TotalSeconds + ' s') }
    else { Write-Host 'aviso: o titulo da janela ainda nao trouxe o nome do projeto' }
    $viva = Get-ProjetoUnico (Get-Instancias)
    if ($viva) { Minimizar $viva }
    if (-not $SemRefresh) {
      Start-Sleep -Seconds 5
      $arqC = if ($SaidaContagem) { [IO.Path]::GetFullPath($SaidaContagem) } else { Join-Path $Raiz ('qa\modelo\refresh-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json') }
      if (-not (Invoke-Refresh $porta $arqC)) { exit 2 }
    }
  }
}
exit 0
