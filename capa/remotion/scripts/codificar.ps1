# Gera os arquivos finais da capa em docs/midia/capa a partir da sequência PNG que o Remotion renderizou (out/seq).
# Uso (na pasta capa/remotion):
#   npx remotion render src/index.ts Capa out/seq --sequence --image-format=png
#   pwsh -NoProfile -File scripts/codificar.ps1 [-Crf 10] [-Vp9Taxa 2600k]
# Cor: tudo em BT.709, faixa limitada (tv), marcado no arquivo; o fundo #1C1915 decodifica a ±1 nível.
param([int]$Crf = 10, [string]$Vp9Taxa = '2600k')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path $PSScriptRoot -Parent
$destino = (Resolve-Path (Join-Path $raiz '..\..\docs\midia\capa')).Path
$seq = Join-Path $raiz 'out\seq\element-%03d.png'
$vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
$tmp = Join-Path $raiz 'out\vp9'

# MP4 · H.264 High, yuv420p, faststart (toca enquanto baixa)
ffmpeg -v error -y -framerate 30 -i $seq -vf $vf -c:v libx264 -preset slow -tune animation -crf $Crf -profile:v high `
  -x264-params 'colorprim=bt709:transfer=bt709:colormatrix=bt709' -color_range tv -movflags +faststart -an `
  (Join-Path $destino 'capa.mp4')

# WebM · VP9 em duas passadas
ffmpeg -v error -y -framerate 30 -i $seq -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 1 -passlogfile $tmp -an -f null NUL
ffmpeg -v error -y -framerate 30 -i $seq -vf $vf -c:v libvpx-vp9 -b:v $Vp9Taxa -deadline good -cpu-used 1 -row-mt 1 `
  -tile-columns 2 -g 150 -pass 2 -passlogfile $tmp -colorspace bt709 -color_primaries bt709 -color_trc bt709 `
  -color_range tv -an (Join-Path $destino 'capa.webm')

# Pôster (último quadro, também para movimento reduzido) e quadro inicial, JPEG qualidade 85
$ultimo = (Get-ChildItem (Join-Path $raiz 'out\seq') -Filter 'element-*.png' | Sort-Object Name | Select-Object -Last 1).FullName
$primeiro = Join-Path $raiz 'out\seq\element-000.png'
python -I -c "import sys; from PIL import Image; [Image.open(a).convert('RGB').save(b, quality=85, subsampling=0, optimize=True, progressive=True) for a, b in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4]))]" `
  $ultimo (Join-Path $destino 'capa-final.jpg') $primeiro (Join-Path $destino 'capa-inicio.jpg')

Get-ChildItem $destino -File | Where-Object Extension -in '.mp4', '.webm', '.jpg' |
  ForEach-Object { '{0,-16} {1,8:N0} KB' -f $_.Name, ($_.Length / 1KB) }
