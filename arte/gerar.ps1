# Arte do mockup Eleições 2026 · desenho em traço pelo Codex CLI local (image_gen nativo).
# Regra geral do Alisson: imagem só pelo Codex; nada de Magnific/Firefly sem pedido explícito.
# Uso: pwsh -NoProfile -File arte/gerar.ps1 -Nome regiao-sudeste [-Vez 1] [-SemRef] [-Foto lula]   (em segundo plano)
# -Foto: anexa arte\ref\fotos\<foto>-ref.jpg como Image 1 (a referência de estilo vira Image 2).
param([Parameter(Mandatory)][string]$Nome, [int]$Vez = 1, [switch]$SemRef, [string]$Foto)
$ErrorActionPreference = 'Stop'
$t = $PSScriptRoot
$cx = Join-Path (Get-AppxPackage -Name 'OpenAI.Codex').InstallLocation 'app\resources\codex.exe'
$log = Join-Path $t "logs\codex-$Nome-$Vez.log"
$prompt = (Get-Content (Join-Path $t 'codex-instrucao.md') -Raw) + "`n" + (Get-Content (Join-Path $t "prompt-$Nome.txt") -Raw)
$refs = @()
if ($Foto) { $refs += @('-i', (Join-Path $t "ref\fotos\$Foto-ref.jpg")) }
if (-not $SemRef) { $refs += @('-i', (Join-Path $t 'ref\estilo-traco.png')) }
$inicio = Get-Date
$prompt | & $cx exec --skip-git-repo-check -C $t -s workspace-write -c 'model_reasoning_effort="medium"' @refs -o (Join-Path $t "logs\resposta-$Nome-$Vez.txt") - 2>&1 | Out-File -Encoding utf8 $log
$seg = [int]((Get-Date) - $inicio).TotalSeconds
$m = Select-String -Path $log -Pattern 'session id: ([0-9a-f-]+)' | Select-Object -First 1
if (-not $m) { "Sem session id; veja logs\codex-$Nome-$Vez.log ($seg s)" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt"); exit 1 }
$sid = $m.Matches[0].Groups[1].Value
$pngs = @(Get-ChildItem (Join-Path $env:USERPROFILE ".codex\generated_images\$sid") -Filter '*.png' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime)
if ($pngs.Count -eq 0) { "Sem PNG na sessão $sid; veja logs\codex-$Nome-$Vez.log ($seg s)" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt"); exit 1 }
$i = 0
foreach ($p in $pngs) { $i++; Copy-Item -LiteralPath $p.FullName -Destination (Join-Path $t "candidatas\$Nome-$Vez-$i.png") -Force }
"OK $Nome vez $Vez · sessão $sid · $($pngs.Count) imagem(ns) · $seg s" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt")
