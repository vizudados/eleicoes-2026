# Variante de gerar-ref.ps1 para COLORIR um desenho em traço já aprovado (a Lia do vídeo), pelo Codex CLI local.
# Regra geral do Alisson: imagem só pelo Codex; nada de Magnific/Firefly sem pedido explícito.
# Uso (em segundo plano): pwsh -NoProfile -File arte/gerar-cor.ps1 -Nome lia-cor-busto [-Vez 1] -Refs 'candidatas\lia-teste-busto-1-1.png;ref\lia\lia-mestre.png'
# -Refs: o desenho em traço (Image 1) e a referência de cor (Image 2), separados por ';' (caminhos relativos a arte\).
# Prompt: arte\codex-instrucao-cor.md (traço mantido + cor em aguada) + arte\prompts-fotos\prompt-<Nome>.txt.
# Saída: arte\candidatas\<Nome>-<Vez>-<i>.png. Sem a referência de estilo preto e branco (ela mandaria tirar a cor).
param([Parameter(Mandatory)][string]$Nome, [int]$Vez = 1, [Parameter(Mandatory)][string]$Refs)
$ErrorActionPreference = 'Stop'
$t = $PSScriptRoot
$cx = Join-Path (Get-AppxPackage -Name 'OpenAI.Codex').InstallLocation 'app\resources\codex.exe'
$log = Join-Path $t "logs\codex-$Nome-$Vez.log"
$prompt = (Get-Content (Join-Path $t 'codex-instrucao-cor.md') -Raw) + "`n" + (Get-Content (Join-Path $t "prompts-fotos\prompt-$Nome.txt") -Raw)
$imgs = @()
foreach ($r in ($Refs -split ';' | Where-Object { $_.Trim() })) {
    $p = Join-Path $t $r.Trim()
    if (-not (Test-Path -LiteralPath $p)) { throw "Referência não encontrada: $p" }
    $imgs += @('-i', $p)
}
$inicio = Get-Date
$prompt | & $cx exec --skip-git-repo-check -C $t -s workspace-write -c 'model_reasoning_effort="medium"' @imgs -o (Join-Path $t "logs\resposta-$Nome-$Vez.txt") - 2>&1 | Out-File -Encoding utf8 $log
$seg = [int]((Get-Date) - $inicio).TotalSeconds
$m = Select-String -Path $log -Pattern 'session id: ([0-9a-f-]+)' | Select-Object -First 1
if (-not $m) { "Sem session id; veja logs\codex-$Nome-$Vez.log ($seg s)" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt"); exit 1 }
$sid = $m.Matches[0].Groups[1].Value
$pngs = @(Get-ChildItem (Join-Path $env:USERPROFILE ".codex\generated_images\$sid") -Filter '*.png' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime)
if ($pngs.Count -eq 0) { "Sem PNG na sessão $sid; veja logs\codex-$Nome-$Vez.log ($seg s)" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt"); exit 1 }
$i = 0
foreach ($p in $pngs) { $i++; Copy-Item -LiteralPath $p.FullName -Destination (Join-Path $t "candidatas\$Nome-$Vez-$i.png") -Force }
"OK $Nome vez $Vez · sessão $sid · $($pngs.Count) imagem(ns) · $seg s" | Tee-Object -FilePath (Join-Path $t "logs\tempo-$Nome-$Vez.txt")
