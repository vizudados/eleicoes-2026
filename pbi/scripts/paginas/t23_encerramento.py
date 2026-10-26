"""29 · Encerramento — par escuro da capa, resultado dos dois turnos e achados dos cinco atos.

Resultado espelhado: Flávio à esquerda, Lula à direita, mesmos tamanhos; segundo turno maior, primeiro menor.
Cada achado tem um atalho à origem. Geometria compartilhada com o gerador desenho_t23.py.
O centro fecha a eleição com a diferença nacional e a participação nos dois turnos, incluindo exterior.
"""
import estilo
import roteiro
import pbip_lib as lib
from pbip_lib import Visual

P = 'T23'
CSS = 'Estilo · CSS'
C = estilo.COR
# título, x, y, largura, altura de linha, [(código, dica)]. Caixas de clique e HTML usam a mesma lista.
GRUPOS = [
    ('I · ANTES DA URNA', 150, 590, 440, 64, [('T10', 'Pesquisas diante da urna do primeiro turno')]),
    ('II · O 1º TURNO', 150, 716, 440, 64, [('T01', 'A vantagem de Flávio no primeiro turno'),
                                          ('T06', 'Quem não compareceu')]),
    ('III · O MAPA', 650, 590, 440, 64, [('T11', 'Municípios que mudaram de lado'),
                                     ('T13', 'O crescimento em cada tipo de cidade')]),
    ('IV · EXPLORE VOCÊ MESMO', 650, 780, 440, 64, [('T19', 'Explore o voto na sua cidade')]),
    ('V · O 2º TURNO · CLIQUE NO ACHADO', 1180, 590, 590, 70, [
        ('T17', 'Pesquisas e resultado final'), ('T18', 'A noite da apuração'),
        ('T27', 'Os ganhos observados entre os turnos'), ('T28', 'As viradas de municípios e estados'),
        ('T29', 'História do PT e recorde de votos')]),
]


def _linhas():
    return [(cod, dica, x, y+30+i*h, w, h) for _, x, y, w, h, itens in GRUPOS
            for i, (cod, dica) in enumerate(itens)]


def corpo():
    css = (".fx{color:var(--creme)}"
           ".fx .tg{position:absolute;left:150px;top:145px;width:1620px;text-align:center;"
           "font-size:72px;font-weight:700;letter-spacing:-.035em;line-height:1.1}"
           ".fx .bl{position:absolute;top:280px;width:420px}.fx .bl.esq{left:140px}.fx .bl.dir{left:1360px;text-align:right}"
           ".fx .bl .rot{color:var(--areia);font-size:15px}.fx .bl .etapa{font-size:13px;margin-top:9px;letter-spacing:.10em}"
           ".fx .bl .v{font-size:76px;margin:10px 0}.fx .flavio-c{color:var(--azul-claro)}.fx .lula-c{color:var(--rosa)}"
           ".fx .bl .p{font-size:22px;font-weight:500}.fx .primeiro{font-size:16px;color:var(--areia);margin-top:18px}"
           ".fx .primeiro .num{font-size:20px;line-height:1.2}.fx .selo-eleito{display:inline-block;font-family:var(--mao);"
           "font-size:26px;line-height:1;border:1.5px solid var(--areia);padding:3px 12px 5px;margin-top:14px;transform:rotate(-4deg)}"
           ".fx .grupo{position:absolute;font-size:13px;letter-spacing:.10em;color:var(--areia);font-weight:650;"
           "border-bottom:1px solid var(--grafite);padding-bottom:9px}"
           ".fx .linha{position:absolute;display:flex;gap:14px;padding:8px 0;font-size:16px;line-height:1.45}"
           ".fx .linha b{font-size:15px;color:var(--areia);min-width:28px;padding-top:1px}"
           ".fx .fecho{position:absolute;left:150px;top:928px;width:940px;font-size:23px;font-weight:500}"
           ".fx .fontes{position:absolute;left:150px;top:970px;width:940px;font-size:12px;color:var(--areia)}")
    return (f"<style>{css}</style><div class='tela fx'><div class='tg sobe'>Da zona eleitoral ao resultado.</div>"
            "<div class='fecho sobe d12'>O voto de perto, do Brasil à sua cidade.</div>"
            "<div class='fontes'>Fontes e limites em cada tela · dados e código abertos · desenhos em traço, créditos no i.</div>"
            + corpo_resumo(embutido=True) + "{{content}}</div>")


def corpo_resumo(embutido=False):
    css = (".resumo-final{color:var(--creme);text-align:center}"
           ".resumo-final .rot{font-size:13px;color:var(--areia)}"
           ".resumo-final .diferenca{font-size:64px;line-height:1.1;margin-top:8px;font-weight:700}"
           ".resumo-final .de{font-size:16px;line-height:22px}"
           ".resumo-final .risco-fecho{height:12px;margin:4px auto 10px}"
           ".resumo-final .abst{font-size:16px;line-height:32px;white-space:nowrap;color:var(--areia)}"
           ".resumo-final .abst .num{font-size:22px;color:var(--creme)}"
           ".resumo-final .comparecimento{font-size:16px;line-height:34px;color:var(--areia)}"
           ".resumo-final .comparecimento .num{font-size:24px;color:var(--creme)}")
    if embutido:
        css += '.fx .resumo-final{position:absolute;inset:auto;left:620px;top:292px;width:680px;height:245px}'
    x,y = (840,416) if embutido else (220,124)
    risco = (f"<svg width='240' height='12' style='position:absolute;left:{x}px;top:{y}px' aria-hidden='true'>"
             f"{estilo.defs_rabisco('rb23fecho', 1.2)}<path d='M3,6 Q82,2 128,6 T237,5' pathLength='1' "
             f"class='traco' filter='url(#rb23fecho)' fill='none' stroke='{C['creme']}' stroke-width='1.6'/></svg>")
    return f"<style>{css}</style>{risco}" + ('' if embutido else '{{content}}')


def declarar(ctx):
    itens = [Visual(P, lib.visual_html('T23_Fecho_Html', 0, 0, 1920, 1080, 'T23 · Achados · HTML',
        folha_de_estilo=CSS, modelo_corpo=corpo(), alt=lib.medida('T23 · Achados · ALT'),
        z=lib.CAMADAS['conteudo'], tab=100))]
    for cod, texto, x, y, w, h in _linhas():
        itens.append(Visual(P, lib.visual_botao(f'T23_Fecho_Ir{cod[1:]}', x-5, y, w+10, h,
            lib.acao_bookmark(f'{cod}_CHEGADA_01'), dica=f'Voltar à tela {roteiro.numero(cod)}: {texto}',
            z=lib.CAMADAS['acao'], tab=200+int(cod[1:]), realce=C['creme'], realce_transp=(92, 86))))
    return itens
