"""29 · Encerramento: hemiciclo, resultado e achados; entrada exclusivamente em CSS.

O mapa ocupa o centro antes dos resultados. O recorte CSS diminui antes da
entrada dos números, protegendo o texto também se o vídeo carregar atrasado.
"""
import json
from pathlib import Path
import estilo
import roteiro
import pbip_lib as lib
from pbip_lib import Visual
from paginas.casca import corpo_casca

P = 'T23'
CSS = 'Estilo · CSS'
C = estilo.COR
MIDIA = 'https://vizudados.github.io/eleicoes-2026/midia'
VERSAO_MIDIA = 'hemiciclo-r3'
REMOTION = Path(__file__).resolve().parents[3] / 'capa/remotion'
ROTEIRO = json.loads((REMOTION / 'src/encerramento/roteiro.json').read_text(encoding='utf-8'))
TEMPOS = ROTEIRO['html']
# Título, geometria e atalhos. O HTML e os botões nativos usam a mesma lista.
GRUPOS = ROTEIRO['grupos']


def _linhas():
    return [(cod, dica, x, y+30+i*h, w, h) for _, x, y, w, h, itens in GRUPOS
            for i, (cod, dica) in enumerate(itens)]


def _caixa(nome):
    x, y, w, h = ROTEIRO['textos'][nome]
    return f'position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'


def _recorte(rect):
    return (f"inset({rect['y']}px {1920-rect['x']-rect['largura']}px "
            f"{1080-rect['y']-rect['altura']}px {rect['x']}px)")


def corpo():
    atrasos = ''.join(f'.fx .fx-{nome}{{animation-delay:{tempo}s}}' for nome, tempo in TEMPOS.items())
    css = (
        '.fx{color:var(--creme)}'
        '.fx video,.fx .poster{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover;pointer-events:none}'
        '.fx .poster{display:block}'
        f'.fx .sobe{{animation-duration:{ROTEIRO["entrada"]}s}}'
        f'.fx video{{visibility:hidden;clip-path:{_recorte(ROTEIRO["areaGrafica"])};'
        f'animation:fxRecorte {ROTEIRO["fecharRecorte"]}s step-end both,fxVideo {ROTEIRO["parado"]}s step-end both}}'
        f'@keyframes fxRecorte{{from{{clip-path:{_recorte(ROTEIRO["recorteInicial"])}}}}}'
        '@keyframes fxVideo{from{visibility:visible}}'
        + atrasos
        + f'.fx .tg{{{_caixa("titulo")}text-align:center;font-size:66px;font-weight:700;letter-spacing:-.035em;line-height:1.1}}'
        f'.fx .bl.esq{{{_caixa("resultadoEsquerda")}}}'
        f'.fx .bl.dir{{{_caixa("resultadoDireita")}text-align:right}}'
        '.fx .bl .rot{color:var(--areia);font-size:15px;line-height:19px}'
        '.fx .bl .etapa{font-size:13px;margin-top:9px;letter-spacing:.10em;line-height:17px}'
        '.fx .bl .v{font-size:76px;line-height:1;margin:10px 0}'
        '.fx .flavio-c{color:var(--azul-claro)}.fx .lula-c{color:var(--rosa)}'
        '.fx .bl .p{font-size:22px;font-weight:500;line-height:28px}'
        '.fx .primeiro{font-size:16px;color:var(--areia);margin-top:18px;line-height:24px}'
        '.fx .primeiro .num{font-size:20px;line-height:1.2}'
        '.fx .selo-eleito{display:inline-block;font-family:var(--mao);font-size:26px;line-height:1;'
        'border:1.5px solid var(--areia);padding:3px 12px 5px;margin-top:8px;transform:rotate(-4deg)}'
        f'.fx .escala{{{_caixa("escala")}text-align:center;font-size:16px;line-height:22px;color:var(--areia)}}'
        '.fx .grupo{position:absolute;font-size:13px;line-height:18px;letter-spacing:.10em;color:var(--areia);'
        f'height:{ROTEIRO["alturaCabecalhoGrupo"]}px;'
        'font-weight:650;border-bottom:1px solid var(--grafite);padding-bottom:7px}'
        '.fx .linha{position:absolute;display:flex;gap:14px;padding:6px 0;font-size:15px;line-height:20px}'
        '.fx .linha b{font-size:15px;color:var(--areia);min-width:28px}'
        f'.fx .fecho{{{_caixa("fecho")}font-size:21px;line-height:28px;font-weight:500}}'
        f'.fx .fontes{{{_caixa("fontes")}font-size:11px;line-height:14px;color:var(--areia)}}'
        '@media(prefers-reduced-motion:reduce){.fx video{display:none}.fx .sobe{animation:none!important}}'
        '@media print{.fx video{display:none}.fx .sobe{animation:none!important}}'
    )
    midia = f'{MIDIA}/encerramento/encerramento'
    poster = f'{midia}-final.jpg?v={VERSAO_MIDIA}'
    return (
        f"<style>{css}</style><div class='tela fx'>"
        f"<img class='poster' alt='' src='{poster}'/>"
        f"<video autoplay muted playsinline preload='auto' aria-hidden='true' tabindex='-1' poster='{poster}'>"
        f"<source src='{midia}.mp4?v={VERSAO_MIDIA}' type='video/mp4'/>"
        f"<source src='{midia}.webm?v={VERSAO_MIDIA}' type='video/webm'/></video>"
        "<div class='tg sobe fx-titulo'>Da zona eleitoral ao resultado.</div>"
        "<div class='escala sobe fx-escala'>Cada ponto cheio representa 50 mil votos.</div>"
        "<div class='fecho sobe fx-fecho'>O voto de perto, do Brasil à sua cidade.</div>"
        "<div class='fontes sobe fx-fecho'>Fontes e limites em cada tela · dados e código abertos · desenhos em traço, créditos no i.</div>"
        + corpo_resumo(embutido=True) + '{{content}}</div>'
        # A casca fica acima do vídeo no mesmo template; sem script de movimento.
        + corpo_casca(roteiro.POR_CODIGO[P]).replace('{{content}}', '')
    )


def corpo_resumo(embutido=False):
    css = (
        '.resumo-final{color:var(--creme);text-align:center;pointer-events:none}'
        f'.fx .linha-diferenca{{{_caixa("diferenca")}display:flex;align-items:center;justify-content:center;gap:16px}}'
        '.resumo-final .rot{font-size:12px;line-height:18px;color:var(--areia);white-space:nowrap}'
        '.resumo-final .aceno{display:block;font-size:15px;line-height:20px;font-weight:400;'
        'letter-spacing:0;text-transform:none;margin-top:3px}'
        '.resumo-final .diferenca{font-size:48px;line-height:54px;font-weight:700;white-space:nowrap}'
        '.resumo-final .de{font-size:14px;line-height:20px;white-space:nowrap}'
        f'.fx .participacao{{{_caixa("participacao")}display:flex;align-items:center;justify-content:center;gap:32px;white-space:nowrap}}'
        '.resumo-final .abst,.resumo-final .comparecimento{font-size:15px;line-height:28px;color:var(--areia)}'
        '.resumo-final .abst .num,.resumo-final .comparecimento .num{font-size:21px;color:var(--creme)}'
    )
    return f'<style>{css}</style>' + ('' if embutido else '{{content}}')


def declarar(ctx):
    itens = [Visual(P, lib.visual_html('T23_Fecho_Html', 0, 0, 1920, 1080, 'T23 · Achados · HTML',
        folha_de_estilo=CSS, modelo_corpo=corpo(), alt=lib.medida('T23 · Achados · ALT'),
        z=lib.CAMADAS['conteudo'], tab=100, movimento=False))]
    for cod, texto, x, y, w, h in _linhas():
        itens.append(Visual(P, lib.visual_botao(f'T23_Fecho_Ir{cod[1:]}', x-5, y, w+10, h,
            lib.acao_bookmark(f'{cod}_CHEGADA_01'), dica=f'Voltar à tela {roteiro.numero(cod)}: {texto}',
            z=lib.CAMADAS['acao'], tab=200+int(cod[1:]), realce=C['creme'], realce_transp=(92, 86))))
    return itens
