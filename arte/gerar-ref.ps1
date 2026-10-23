# Variante de gerar.ps1 para REDESENHAR FOTOS REAIS em traço (comícios e marcos da linha do tempo), pelo Codex CLI local.
# Regra geral do Alisson: imagem só pelo Codex; nada de Magnific/Firefly sem pedido explícito.
# Uso (em segundo plano): pwsh -NoProfile -File arte/gerar-ref.ps1 -Nome lula-2002-posse [-Vez 1] -Refs 'ref\recortes\lula-2002-posse.jpg'
# -Refs: uma ou mais imagens separadas por ';' (caminhos relativos a arte\), anexadas como Image 1, Image 2...;
#        a referência de estilo (ref\estilo-traco.png) vai sempre por último.
# Prompt: arte\codex-instrucao.md + arte\prompts-fotos\prompt-<Nome>.txt. Saída: arte\candidatas\<Nome>-<Vez>-<i>.png.
# Calibragem (23/10/2026):
# - Mandar o RECORTE 4:5 da foto (pipeline/preparar_arte.py --recortes) como Image 1: o desenho segue a composição dele.
# - Foto com rosto pequeno (posse 2019, entrevista 2021): 2ª foto da mesma época só para a fisionomia (Image 2).
# - Não nomear a pessoa; descrever idade, cabelo, roupa e gesto. Pedir "no dense cross-hatching on the skin" (sem isso
#   os retratos em close saem com o rosto carregado) e "the jersey/mask/megaphone has no text" (o modelo escreve KN95 etc.).
# - No máximo ~6 gerações simultâneas na máquina: com 10 o codex.exe travou (erro 1450 do Windows, sem PNG).
param([Parameter(Mandatory)][string]$Nome, [int]$Vez = 1, [Parameter(Mandatory)][string]$Refs)
$ErrorActionPreference = 'Stop'
$t = $PSScriptRoot
$cx = Join-Path (Get-AppxPackage -Name 'OpenAI.Codex').InstallLocation 'app\resources\codex.exe'
$log = Join-Path $t "logs\codex-$Nome-$Vez.log"
$prompt = (Get-Content (Join-Path $t 'codex-instrucao.md') -Raw) + "`n" + (Get-Content (Join-Path $t "prompts-fotos\prompt-$Nome.txt") -Raw)
$imgs = @()
foreach ($r in ($Refs -split ';' | Where-Object { $_.Trim() })) {
    $p = Join-Path $t $r.Trim()
    if (-not (Test-Path -LiteralPath $p)) { throw "Referência não encontrada: $p" }
    $imgs += @('-i', $p)
}
$imgs += @('-i', (Join-Path $t 'ref\estilo-traco.png'))
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
