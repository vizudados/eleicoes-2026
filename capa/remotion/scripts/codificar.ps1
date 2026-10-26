# Gera capa-2t.* em docs/midia/capa a partir dos 630 PNGs de out/seq-2t; preserva capa.* e out/seq.
# Uso (na pasta capa/remotion):
#   npx remotion render src/index.ts Capa out/seq-2t --sequence --image-format=png
#   powershell -NoProfile -File scripts/codificar.ps1 [-Crf 10] [-Vp9Taxa 2600k]
# Cor: tudo em BT.709, faixa limitada (tv), marcado no arquivo; o fundo #1C1915 decodifica a ±1 nível.
param([ValidateRange(0, 51)][int]$Crf = 10, [ValidatePattern('^[1-9][0-9]*[kKmM]?$')][string]$Vp9Taxa = '2600k')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot -Parent
$destino = (Resolve-Path (Join-Path $raiz '..\..\docs\midia\capa')).Path
$pastaSeq = Join-Path $raiz 'out\seq-2t'
$quadros = 630 # 21 s a 30 fps, conforme src/tempo.ts
$arquivos = @(Get-ChildItem -LiteralPath $pastaSeq -Filter 'element-*.png' -File)
if ($arquivos.Count -ne $quadros) { throw "Sequência incompleta: esperado $quadros PNGs, encontrado $($arquivos.Count)." }
for ($i = 0; $i -lt $quadros; $i++) {
  $quadro = Join-Path $pastaSeq ('element-{0:000}.png' -f $i)
  if (-not (Test-Path -LiteralPath $quadro -PathType Leaf)) { throw "Quadro ausente: $quadro" }
}
# Confere o assentamento de toda a composição antes de publicar os novos arquivos.
$inicioParado = Join-Path $pastaSeq 'element-540.png'
$ultimo = Join-Path $pastaSeq 'element-629.png'
$primeiro = Join-Path $pastaSeq 'element-000.png'
$hashParado = (Get-FileHash -LiteralPath $inicioParado -Algorithm SHA256).Hash
for ($i = 541; $i -lt $quadros; $i++) {
  $quadro = Join-Path $pastaSeq ('element-{0:000}.png' -f $i)
  if ((Get-FileHash -LiteralPath $quadro -Algorithm SHA256).Hash -ne $hashParado) {
    throw "Assentamento divergente no quadro $i; rever render antes de codificar."
  }
}
$seq = Join-Path $pastaSeq 'element-%03d.png'
$vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
$tmp = Join-Path $raiz 'out\vp9-2t'

# MP4 · H.264 High, yuv420p, faststart (toca enquanto baixa)
ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libx264 -preset slow -tune animation -crf $Crf -profile:v high `
  -x264-params 'colorprim=bt709:transfer=bt709:colormatrix=bt709' -color_range tv -movflags +faststart -an `
  (Join-Path $destino 'capa-2t.mp4')
if ($LASTEXITCODE -ne 0) { throw "Falha ao codificar capa-2t.mp4 (ffmpeg $LASTEXITCODE)." }

# WebM · VP9 em duas passadas
ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 1 -passlogfile $tmp -an -f null NUL
if ($LASTEXITCODE -ne 0) { throw "Falha na primeira passada VP9 (ffmpeg $LASTEXITCODE)." }
ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 2 -passlogfile $tmp -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -color_range tv -an (Join-Path $destino 'capa-2t.webm')
if ($LASTEXITCODE -ne 0) { throw "Falha ao codificar capa-2t.webm (ffmpeg $LASTEXITCODE)." }

# Pôster (último quadro, também para movimento reduzido) e quadro inicial, JPEG qualidade 85
python -I -X utf8 -c "import sys; from PIL import Image; [Image.open(a).convert('RGB').save(b, quality=85, subsampling=0, optimize=True, progressive=True) for a, b in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4]))]" `
  $ultimo (Join-Path $destino 'capa-2t-final.jpg') $primeiro (Join-Path $destino 'capa-2t-inicio.jpg')
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar os JPEGs (Python $LASTEXITCODE)." }

Get-ChildItem -LiteralPath $destino -Filter 'capa-2t*' -File | Where-Object Extension -in '.mp4', '.webm', '.jpg' |
  ForEach-Object { '{0,-16} {1,8:N0} KB' -f $_.Name, ($_.Length / 1KB) }
