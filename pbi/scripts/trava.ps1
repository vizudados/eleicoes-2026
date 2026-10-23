# trava.ps1 - trava do ciclo compartilhada entre sessoes e agentes (criacao atomica: dois donos nunca pegam juntos).
# Use SEMPRE antes de rodar o ciclo.ps1 ou fechar/abrir o Desktop do projeto. ASCII puro (console cp850).
#   pwsh -NoProfile -File pbi\scripts\trava.ps1 -Acao pegar  -Dono "nome-da-sessao"   (sai 1 se estiver com outro)
#   pwsh -NoProfile -File pbi\scripts\trava.ps1 -Acao soltar -Dono "nome-da-sessao"   (so solta a propria)
#   pwsh -NoProfile -File pbi\scripts\trava.ps1 -Acao ver                              (sai 0 = livre, 1 = ocupada)
param([ValidateSet('pegar', 'soltar', 'ver')][string]$Acao = 'ver', [string]$Dono = '')
$Raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Trava = Join-Path $Raiz 'pbi\qa\ciclo.lock'
switch ($Acao) {
  'ver' {
    if (Test-Path $Trava) { "ocupada: $((Get-Content $Trava -Raw).Trim())"; exit 1 }
    'livre'; exit 0
  }
  'pegar' {
    if (-not $Dono) { 'informe -Dono'; exit 2 }
    try {
      $fs = [IO.File]::Open($Trava, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
      $b = [Text.Encoding]::UTF8.GetBytes("$Dono | $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
      $fs.Write($b, 0, $b.Length); $fs.Close()
      "trava com $Dono"; exit 0
    } catch {
      $c = if (Test-Path $Trava) { (Get-Content $Trava -Raw).Trim() } else { '?' }
      "ocupada: $c"; exit 1
    }
  }
  'soltar' {
    if (-not (Test-Path $Trava)) { 'ja estava livre'; exit 0 }
    $c = (Get-Content $Trava -Raw).Trim()
    if (-not $Dono -or -not $c.StartsWith("$Dono |")) { "nao e sua: $c"; exit 1 }
    Remove-Item $Trava -Force; 'solta'; exit 0
  }
}
