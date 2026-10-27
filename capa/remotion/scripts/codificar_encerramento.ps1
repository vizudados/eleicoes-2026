# Codifica só o Encerramento; não altera a capa nem apaga sequências.
# Execute depois do render com --gl=angle, a partir de capa/remotion.
param([ValidateRange(0, 51)][int]$Crf = 10, [ValidatePattern('^[1-9][0-9]*[kKmM]?$')][string]$Vp9Taxa = '2600k')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot -Parent
$destino = (Resolve-Path (Join-Path $raiz '..\..\docs\midia\encerramento')).Path
$pastaSeq = Join-Path $raiz 'out\seq-encerramento-r2'
$quadros = 450 # 15 s a 30 fps, conforme src/encerramento/roteiro.json
$arquivos = @(Get-ChildItem -LiteralPath $pastaSeq -Filter 'element-*.png' -File)
if ($arquivos.Count -ne $quadros) { throw "Sequência incompleta: esperado $quadros PNGs, encontrado $($arquivos.Count)." }
for ($i = 0; $i -lt $quadros; $i++) {
  $quadro = Join-Path $pastaSeq ('element-{0:000}.png' -f $i)
  if (-not (Test-Path -LiteralPath $quadro -PathType Leaf)) { throw "Quadro ausente: $quadro" }
}
$inicioParado = Join-Path $pastaSeq 'element-360.png'
$ultimo = Join-Path $pastaSeq 'element-449.png'
$primeiro = Join-Path $pastaSeq 'element-000.png'
$hashParado = (Get-FileHash -LiteralPath $inicioParado -Algorithm SHA256).Hash
for ($i = 361; $i -lt $quadros; $i++) {
  $quadro = Join-Path $pastaSeq ('element-{0:000}.png' -f $i)
  if ((Get-FileHash -LiteralPath $quadro -Algorithm SHA256).Hash -ne $hashParado) {
    throw "Encerramento ainda se move no quadro $i; rever render antes de codificar."
  }
}
$seq = Join-Path $pastaSeq 'element-%03d.png'
$vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
$tmp = Join-Path $raiz 'out\vp9-encerramento-r2'

ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libx264 -preset slow -tune animation -crf $Crf -profile:v high `
  -x264-params 'colorprim=bt709:transfer=bt709:colormatrix=bt709' -color_range tv -movflags +faststart -an `
  (Join-Path $destino 'encerramento.mp4')
if ($LASTEXITCODE -ne 0) { throw "Falha no MP4 (ffmpeg $LASTEXITCODE)." }

ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 1 -passlogfile $tmp -an -f null NUL
if ($LASTEXITCODE -ne 0) { throw "Falha na primeira passada VP9 (ffmpeg $LASTEXITCODE)." }
ffmpeg -v error -y -framerate 30 -start_number 0 -i $seq -frames:v $quadros -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 2 -passlogfile $tmp -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -color_range tv -an (Join-Path $destino 'encerramento.webm')
if ($LASTEXITCODE -ne 0) { throw "Falha no WebM (ffmpeg $LASTEXITCODE)." }

python -I -X utf8 -c "import sys; from PIL import Image; [Image.open(a).convert('RGB').save(b, quality=85, subsampling=0, optimize=True, progressive=True) for a, b in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4]))]" `
  $ultimo (Join-Path $destino 'encerramento-final.jpg') $primeiro (Join-Path $destino 'encerramento-inicio.jpg')
if ($LASTEXITCODE -ne 0) { throw "Falha nos pôsteres JPEG (Python $LASTEXITCODE)." }

Get-ChildItem -LiteralPath $destino -Filter 'encerramento*' -File | Where-Object Extension -in '.mp4', '.webm', '.jpg' |
  ForEach-Object { '{0,-25} {1,8:N0} KB' -f $_.Name, ($_.Length / 1KB) }
