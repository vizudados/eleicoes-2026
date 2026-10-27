# -*- coding: utf-8 -*-
"""desenho_t02_t04 — telas 02 (Lula · quem é) e 04 (Flávio · quem é): MESMA geometria e MESMO gerador, o lado é
parâmetro (neutralidade: as mesmas contas, os mesmos blocos, o mesmo peso). Dono: agente das telas 01–06.

    python -I -X utf8 pbi/scripts/desenho_t02_t04.py    # grava pbi/dax/T02 Lula · quem é/… e T04 Flávio · quem é/…

O módulo também monta as declarações das duas páginas (declarar_quem_e), chamado por paginas/t02_*.py e t04_*.py.

A tela: à esquerda a ficha (nome, partido, desde quando está na vida pública, o 1º turno de 2026); no centro o retrato
em traço olhando para a tela; à direita a cena do comício (a partir de foto real, com data e local) presa com fita;
embaixo, a protagonista: a trajetória política, uma régua do tempo com os marcos nos anos reais. Os cartões dos marcos
ficam em vagas iguais (nunca colidem) e um fio liga cada cartão ao seu ponto na régua. Passar o mouse num cartão abre o
dossiê "polaroide": a foto da época redesenhada em traço, presa com fita, a data, o texto, a legenda e o crédito.
Marco sem foto de licença aberta: a cena da época recriada como ILUSTRAÇÃO em traço (desenhos.csv, tipo = ilustração),
com lápis no lugar da câmera no cartão, "Na ilustração:" no dossiê e crédito "Ilustração … recriada de registros da época".
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import RAIZ, URL_MIDIA, Gravador, dax  # noqa: E402
from momento_eleicao import segundo, soma_uf  # noqa: E402

TR = "'Trajetória'"
CU = "'Candidato UF'"

LADOS = {
    "T02": dict(pasta="T02 Lula · quem é", cand="Lula", completo="Luiz Inácio Lula da Silva", rot="Lula · PT · 13",
                numero=13, cls="lula", hex="#B8322A", hexesc="#8E2620", retrato="retrato-lula-vermelho_escuro",
                comicio="comicio-lula-tinta",
                cred_retrato="Retrato em traço a partir da foto oficial (Ricardo Stuckert/Palácio do Planalto, "
                             "CC BY 2.0)",
                tooltip="ttT02Marco", ordem_tt=120),
    "T04": dict(pasta="T04 Flávio · quem é", cand="Flávio", completo="Flávio Bolsonaro", rot="Flávio · PL · 22",
                numero=22, cls="flavio", hex="#2B5797", hexesc="#1D3C6E", retrato="retrato-flavio-azul_escuro",
                foto_posicao_tooltip="50% 40%",
                comicio="comicio-flavio-tinta",
                cred_retrato="Retrato em traço a partir da foto oficial (Agência Senado)",
                tooltip="ttT04Marco", ordem_tt=140),
}
# geometria comum às duas telas (área de conteúdo x 150–1770, y 140–1000)
TOPO = (150, 140, 1620, 480)              # ficha + retrato + comício
TRAJ = (150, 636, 1620, 364)              # régua do tempo (protagonista)
TT_W, TT_H = 640, 400                     # dossiê polaroide
REGUA_Y, REGUA_X0, REGUA_W = 296, 30, 1560


def desenhos_csv() -> dict[str, dict]:
    """Legenda e crédito curto de cada desenho (dados/bruto/trajetoria/desenhos.csv), pelo nome do arquivo."""
    arq = RAIZ / "dados" / "bruto" / "trajetoria" / "desenhos.csv"
    saida = {}
    with arq.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            saida[Path(r["arquivo_web"]).stem] = r
    return saida


def literal(texto: str) -> str:
    return '"' + texto.replace('"', '""') + '"'


def ilustracoes() -> list[str]:
    """Desenhos que são ILUSTRAÇÃO recriada (marco sem foto de licença aberta), não redesenho de foto real."""
    return sorted(k for k, v in desenhos_csv().items() if v.get("tipo") == "ilustração")


def em_ilustracoes(coluna: str) -> str:
    """Condição DAX 'a coluna é uma ilustração recriada'. Sem nenhuma, a lista leva um nome que nunca existe (vale
    também como filtro do CALCULATE, onde FALSE () não é aceito)."""
    nomes = ilustracoes() or ["(nenhuma)"]
    return f"{coluna} IN {{ {', '.join(literal(n) for n in nomes)} }}"


# ---------------------------------------------------------------------------------------------------- contas
def contas(P: str, L: dict, G: Gravador) -> None:
    c = G.conta
    cand = literal(L["cand"])
    filtro = f"REMOVEFILTERS ( {TR} ), {TR}[Candidato] = {cand}"
    c(f"{P} · Trajetória · marcos", f"Quantos marcos a trajetória de {L['cand']} tem.",
      f"CALCULATE ( COUNTROWS ( {TR} ), {filtro} )", "0", "dados/pbi/trajetoria.csv = 10")
    c(f"{P} · Trajetória · marcos com foto", f"Quantos marcos de {L['cand']} têm foto da época redesenhada (sem "
      "contar as ilustrações recriadas).",
      f'CALCULATE ( COUNTROWS ( {TR} ), {filtro}, {TR}[Foto] <> "", NOT ( {em_ilustracoes(f"{TR}[Foto]")} ) )', "0",
      "Lula 8 · Flávio 10 (dados/pbi/trajetoria.csv; desenhos.csv, tipo = foto)")
    c(f"{P} · Trajetória · marcos ilustrados", f"Quantos marcos de {L['cand']} não têm foto de licença aberta e "
      "mostram a cena da época recriada em ilustração.",
      f"CALCULATE ( COUNTROWS ( {TR} ), {filtro}, {em_ilustracoes(f'{TR}[Foto]')} )", "0",
      "Lula 2 · Flávio 0 (desenhos.csv, tipo = ilustração)")
    c(f"{P} · Trajetória · primeiro ano", f"Ano do primeiro marco de {L['cand']}.",
      f"CALCULATE ( MIN ( {TR}[Ano] ), {filtro} )", "0", "Lula 1975 · Flávio 2002")
    c(f"{P} · Trajetória · último ano", f"Ano do último marco de {L['cand']}.",
      f"CALCULATE ( MAX ( {TR}[Ano] ), {filtro} )", "0", "2026")
    c(f"{P} · Trajetória · segundo ano", f"Ano do segundo marco mais antigo de {L['cand']} (onde a régua retoma "
      "quando o primeiro marco fica longe dos outros e a régua ganha um corte).",
      f"VAR _p = [{P} · Trajetória · primeiro ano] RETURN CALCULATE ( MIN ( {TR}[Ano] ), {filtro}, {TR}[Ano] > _p )",
      "0", "Lula 1980 · Flávio 2016")
    c(f"{P} · anos de vida pública", "Anos do primeiro marco até a eleição de 2026.",
      f"2026 - [{P} · Trajetória · primeiro ano]", "0", "Lula 51 · Flávio 24")
    # do marco da linha (item: 'Trajetória'[Título])
    c(f"{P} · Trajetória · ordem", "Posição cronológica do marco da linha (1 = o mais antigo).",
      f"SELECTEDVALUE ( {TR}[Ordem] )", "0")
    c(f"{P} · Trajetória · ano", "Ano do marco da linha.", f"SELECTEDVALUE ( {TR}[Ano] )", "0")
    c(f"{P} · Trajetória · data", "Data do marco da linha; vazio quando a fonte só dá o ano.", dax(f"""
        VAR _d = SELECTEDVALUE ( {TR}[Data] )
        RETURN
            IF ( LEN ( _d ) = 10, DATE ( VALUE ( LEFT ( _d, 4 ) ), VALUE ( MID ( _d, 6, 2 ) ), VALUE ( RIGHT ( _d, 2 ) ) ) )
        """), "dd/mm/yyyy")
    c(f"{P} · Trajetória · tempo", "Momento do marco da linha em anos decimais (ano + fração do ano; meio do ano "
      "quando a fonte só dá o ano). Posição do ponto na régua.", dax(f"""
        VAR _a = [{P} · Trajetória · ano]
        VAR _d = [{P} · Trajetória · data]
        RETURN
            IF ( ISBLANK ( _d ), _a + 0.5, _a + DIVIDE ( _d - DATE ( _a, 1, 1 ), 365 ) )
        """), "0.00")
    c(f"{P} · Trajetória · título", "Título curto do marco da linha.", f"SELECTEDVALUE ( {TR}[Título] )", "texto")
    c(f"{P} · Trajetória · texto do marco", "O que aconteceu no marco da linha (até ~200 caracteres).",
      f"SELECTEDVALUE ( {TR}[Texto] )", "texto")
    c(f"{P} · Trajetória · foto", "Nome do desenho da foto do marco da linha; vazio quando não há foto livre.",
      f"SELECTEDVALUE ( {TR}[Foto] )", "texto")
    c(f"{P} · Trajetória · tem foto", "1 quando o marco da linha tem desenho: foto da época redesenhada ou, sem foto "
      "de licença aberta, ilustração recriada.",
      f'IF ( SELECTEDVALUE ( {TR}[Foto] ) <> "", 1, 0 )', "0")
    c(f"{P} · Trajetória · é ilustração", "1 quando o desenho do marco da linha é ilustração recriada da época (não há "
      "foto de licença aberta). Fonte: dados/bruto/trajetoria/desenhos.csv, coluna tipo.", dax(f"""
        VAR _f = [{P} · Trajetória · foto]
        RETURN
            IF ( {em_ilustracoes('_f')}, 1, 0 )
        """), "0")
    # legenda e crédito do desenho (dados/bruto/trajetoria/desenhos.csv; reserva: autor e licença da tabela)
    mapa = {k: v for k, v in desenhos_csv().items() if v["candidato"].startswith(L["cand"])}
    casos_leg = "".join(f",\n        {literal(k)}, {literal(v['legenda'])}" for k, v in sorted(mapa.items())
                        if "/trajetoria/" in v["arquivo_web"])
    casos_cred = "".join(f",\n        {literal(k)}, {literal(v['credito_curto'])}" for k, v in sorted(mapa.items())
                         if "/trajetoria/" in v["arquivo_web"])
    c(f"{P} · Trajetória · legenda da foto", "Onde e quando a foto original do marco da linha foi feita (pode ser de "
      "outro momento que o do marco). Fonte: dados/bruto/trajetoria/desenhos.csv.", dax(f"""
        VAR _f = [{P} · Trajetória · foto]
        RETURN
            SWITCH (
                _f{casos_leg},
                BLANK ()
            )
        """), "texto")
    c(f"{P} · Trajetória · crédito da foto", "Crédito curto do desenho e da foto original do marco da linha. Fonte: "
      "dados/bruto/trajetoria/desenhos.csv; na falta, autor e licença da tabela Trajetória.", dax(f"""
        VAR _f = [{P} · Trajetória · foto]
        VAR _reserva =
            "Desenho a partir de foto de " & SELECTEDVALUE ( {TR}[Autor da foto] ) & " ("
                & SELECTEDVALUE ( {TR}[Licença da foto] ) & ")"
        RETURN
            IF (
                _f <> "",
                SWITCH (
                    _f{casos_cred.replace(chr(10) + "        ", chr(10) + "                ")},
                    _reserva
                )
            )
        """), "texto")
    # o 1º turno de 2026 (resultado nacional, com o exterior)
    c(f"{P} · votos 2026", f"Votos de {L['cand']} no 1º turno de 2026, no Brasil (com o exterior).",
      f"CALCULATE ( SUM ( {CU}[Votos] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026, {CU}[Número] = {L['numero']} )",
      "#,0", "paginas[1].candidatos")
    c(f"{P} · % 2026", f"Parcela de {L['cand']} nos votos válidos do 1º turno de 2026, no Brasil (0–1).", dax(f"""
        DIVIDE (
            [{P} · votos 2026],
            CALCULATE ( SUM ( {CU}[Votos] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026 )
        )
        """), "0.0%", "Lula 45,2% · Flávio 47,0%")
    c(f"{P} · posição 2026", f"Colocação de {L['cand']} no 1º turno de 2026, no Brasil.", dax(f"""
        VAR _v = [{P} · votos 2026]
        VAR _todos =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( {CU}[Número] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026 ),
                "@v", CALCULATE ( SUM ( {CU}[Votos] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026 )
            )
        RETURN
            1 + COUNTROWS ( FILTER ( _todos, [@v] > _v ) )
        """), "0", "Lula 2 · Flávio 1")
    # Preserva o último registro do Pré no CSV; o desfecho só substitui sua leitura no Pós.
    _contas_pos(P, L, G)


def _contas_pos(P, L, G):
    c = G.conta
    col = 'VotosPT' if P == 'T02' else 'VotosAdversario'
    votos_pre = f"CALCULATE ( SUM ( {CU}[Votos] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026, {CU}[Número] = {L['numero']} )"
    c(f'{P} · votos 2026', 'Votos nacionais no turno escolhido, incluindo exterior.',
      segundo(votos_pre, soma_uf(col, remover_uf=True)), '#,0')
    validos_pre = f"CALCULATE ( SUM ( {CU}[Votos] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2026 )"
    c(f'{P} · % 2026', 'Parcela nos válidos do turno escolhido, incluindo exterior.',
      f'DIVIDE ( [{P} · votos 2026], {segundo(validos_pre, soma_uf("Validos", remover_uf=True))} )', '0.00%')
    c(f'{P} · posição 2026', 'Colocação nacional no turno escolhido.',
      segundo('2' if P == 'T02' else '1', '1' if P == 'T02' else '2'), '0')
    c(f'{P} · desfecho', '1 no último marco, somente depois da eleição.',
      f'INT ( [Eleição · pós] = 1 && SELECTEDVALUE ( {TR}[Ordem] ) = 10 )', '0')
    c(f'{P} · destaque do marco', 'O marco do recorde recebe maior destaque, por pedido do dono.',
      f'[{P} · desfecho]' if P == 'T02' else '0', '0')
    titulo = 'Reeleito com recorde histórico' if P == 'T02' else 'Ficou em segundo lugar'
    # Texto a partir do mesmo CSV que alimenta UF segundo turno, conferido antes de emitir.
    with (RAIZ / 'dados/pbi/uf_2turno.csv').open(encoding='utf-8-sig') as f:
        rows = [r for r in csv.DictReader(f) if r['ano'] == '2026']
    pt = sum(int(r['pt']) for r in rows); adv = sum(int(r['adv']) for r in rows)
    total = sum(int(r['validos']) for r in rows)
    assert pt == 64256232 and adv == 59826041 and pt - adv == 4430191
    numero = lambda v: f'{v:,}'.replace(',', '.')
    pct = lambda v: f'{100*v/total:.2f}'.replace('.', ',') + '%'
    texto = (f'Foi reeleito em 25/10/2026 com {numero(pt)} votos ({pct(pt)} dos válidos), '
             'o maior total de uma candidatura presidencial em um turno no Brasil. Fonte: TSE.' if P == 'T02' else
             f'Terminou o 2º turno de 25/10/2026 em 2º lugar, com {numero(adv)} votos '
             f'({pct(adv)} dos válidos). Lula foi reeleito. Fonte: TSE.')
    assert len(texto) <= 220 and len(titulo.split()) <= 6
    # Sem foto nova licenciada, mantém foto vazia no desfecho; nunca reaproveita foto de outra data como 25/10.
    pos = imagens_pos().get(P, {})
    for nome, pre, post in [
        ('título', f'SELECTEDVALUE ( {TR}[Título] )', literal(titulo)),
        ('texto do marco', f'SELECTEDVALUE ( {TR}[Texto] )', literal(texto)),
        ('foto', f'SELECTEDVALUE ( {TR}[Foto] )', literal(pos.get('arquivo', ''))),
    ]:
        c(f'{P} · Trajetória · {nome}', 'Último marco responde ao Antes/Depois; os demais ficam intactos.',
          f'IF ( [{P} · desfecho] = 1, {post}, {pre} )', 'texto')
    c(f'{P} · Trajetória · data', 'Data real do marco, 25/10/2026 no desfecho.', dax(f'''
        VAR _d = SELECTEDVALUE ( {TR}[Data] )
        RETURN IF ( [{P} · desfecho] = 1, DATE ( 2026, 10, 25 ),
            IF ( LEN ( _d ) = 10, DATE ( VALUE ( LEFT ( _d, 4 ) ), VALUE ( MID ( _d, 6, 2 ) ), VALUE ( RIGHT ( _d, 2 ) ) ) ) )
        '''), 'dd/mm/yyyy')
    c(f'{P} · Trajetória · tem foto', 'Foto licenciada efetivamente disponível para o marco.',
      f'INT ( LEN ( [{P} · Trajetória · foto] ) > 0 )', '0')
    # Metadados antigos já têm seu SWITCH; acrescenta somente o último registro.
    for nome, campo in [('legenda da foto', 'legenda'), ('crédito da foto', 'credito')]:
        arq = G.raiz / 'Contas' / f'{P} · Trajetória · {nome}.dax'
        original = arq.read_text(encoding='utf-8').split('*/', 1)[1].strip()
        c(f'{P} · Trajetória · {nome}', 'Legenda e crédito com data real da foto; adaptação CC BY-SA 4.0.',
          f'IF ( [{P} · desfecho] = 1, {literal(pos.get(campo, ""))}, {original} )', 'texto')
    if not pos:
        c(f'{P} · Trajetória · marcos com foto', 'Contagem exclui o desfecho sem foto licenciada.',
          segundo('8' if P == 'T02' else '10', '7' if P == 'T02' else '9'), '0')


def imagens_pos():
    import json
    arq = RAIZ / 'dados/bruto/trajetoria/pos_eleicao.json'
    return json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else {}


# ---------------------------------------------------------------------------------------------------- desenho
def desenho(P: str, L: dict, G: Gravador) -> None:
    pos = imagens_pos().get(P)
    foto_posicao = L.get('foto_posicao_tooltip', '15% 50%')
    G.desenho(f'{P} · Cena · HTML', 'Cena em traço e legenda real correspondentes ao momento escolhido.',
              segundo(literal(cena_html(L)), literal(cena_html(L, pos=pos, depois=True))))
    G.desenho(f'{P} · Cena · ALT', 'Descrição acessível do retrato e da imagem escolhida.', segundo(
        literal(f"Retrato oficial de {L['completo']} em traço. {desenhos_csv()[L['comicio']]['legenda']}."),
        literal(f"Retrato oficial de {L['completo']} em traço. " +
                (pos['legenda'] + '.' if pos else 'Foto após o resultado sem licença aberta confirmada.'))))
    G.desenho(f"{P} · Ficha · HTML", f"Ficha de {L['cand']} (alto à esquerda da tela): desde quando está na vida "
              "pública, o 1º turno de 2026 e quantos marcos a linha do tempo tem (com foto da época e em ilustração "
              "recriada). Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _desde = [{P} · Trajetória · primeiro ano]
        VAR _anos = [{P} · anos de vida pública]
        VAR _votos = [{P} · votos 2026]
        VAR _pct = [{P} · % 2026]
        VAR _pos = [{P} · posição 2026]
        VAR _posEleicao = [Eleição · pós]
        VAR _marcos = [{P} · Trajetória · marcos]
        VAR _fotos = [{P} · Trajetória · marcos com foto]
        VAR _ilus = [{P} · Trajetória · marcos ilustrados]
        -- 2 · Textos
        VAR _txtVotos = @MI(_votos)@
        VAR _txtPct = IF ( _posEleicao = 1, FORMAT ( _pct, "0.00%" ), @PCT(_pct)@ )
        VAR _turno = IF ( _posEleicao = 1, "2º", "1º" )
        VAR _resultado = IF ( _posEleicao = 1 && _pos = 1, "{"reeleito" if P == "T02" else "eleito"}", _pos & "º lugar" )
        VAR _txtFotos =
            SWITCH (
                TRUE (),
                _fotos = _marcos, "todos com foto da época",
                _fotos = 0, "nenhum com foto da época",
                _fotos = 1, "1 com foto da época",
                _fotos & " com foto da época"
            )
        VAR _txtIlus =
            SWITCH ( _ilus, 0, "", 1, ", 1 em ilustração recriada", ", " & _ilus & " em ilustração recriada" )
        -- 4 · Marcação
        VAR _html =
            "<div class='tela fc'>"
                & "<div class='lin sobe d3'><div class='rot'>Na vida pública desde</div>"
                & "<div class='val'><span class='nc'>" & _desde & "</span><small>há <span>" & _anos & "</span> anos</small></div></div>"
                & "<div class='lin sobe d4'><div class='rot'>No " & _turno & " turno de 2026</div>"
                & "<div class='val'><span class='{L['cls']}'>" & _txtVotos & "</span><small>de votos · " & _txtPct
                & " · " & _resultado & "</small></div></div>"
                & "<div class='lin sobe d5'><div class='rot'>Na linha do tempo abaixo</div>"
                & "<div class='val'><span>" & _marcos & "</span><small>marcos, " & _txtFotos & _txtIlus
                & "</small></div></div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho(f"{P} · Ficha · ALT", "Texto para leitor de tela da ficha.", dax(f"""
        LEFT (
            "{L['completo']}, na vida pública desde " & [{P} · Trajetória · primeiro ano] & ". No " & [Eleição · turno] & "º turno de 2026, "
                & @MI([{P} · votos 2026])@ & " de votos (" & IF ( [Eleição · pós] = 1, FORMAT ( [{P} · % 2026], "0.00%" ), @PCT([{P} · % 2026])@ ) & "), "
                & IF ( [Eleição · pós] = 1 && [{P} · posição 2026] = 1, "{"reeleito" if P == "T02" else "eleito"}", [{P} · posição 2026] & "º lugar" ) & ".",
            250
        )
        """))
    # régua do tempo: uma entrada por marco
    G.desenho(f"{P} · Trajetória · HTML", "Um marco da trajetória (uma entrada por marco, granularidade "
              "'Trajetória'[Título]): o cartão na sua vaga (câmera se tem foto da época, lápis se é ilustração "
              "recriada), o fio até o ponto no ano real e, no 1º marco, a régua com os anos. Só lê contas; posições "
              "são geometria.", dax(f"""
        -- 1 · Leituras
        VAR _ordem = [{P} · Trajetória · ordem]
        VAR _n = [{P} · Trajetória · marcos]
        VAR _tempo = [{P} · Trajetória · tempo]
        VAR _ano = [{P} · Trajetória · ano]
        VAR _tit = [{P} · Trajetória · título]
        VAR _temFoto = [{P} · Trajetória · tem foto]
        VAR _ilus = [{P} · Trajetória · é ilustração]
        VAR _ini = [{P} · Trajetória · primeiro ano]
        VAR _fim = [{P} · Trajetória · último ano]
        VAR _destaque = [{P} · destaque do marco]
        -- 2 · Textos
        VAR _txtTit = @ESC(_tit)@
        VAR _icone =
            SWITCH (
                TRUE (),
                _ilus = 1,
                    "<svg class='cam' viewBox='0 0 20 16' aria-label='ilustração recriada da época'><path d='M3,14 L4,10 L13,2 L16,5 L7,13 Z'/><path d='M4,10 L7,13'/></svg>",
                _temFoto = 1,
                    "<svg class='cam' viewBox='0 0 20 16' aria-label='tem foto da época'><path d='M2,4 H6 L8,2 H12 L14,4 H18 V14 H2 Z'/><circle cx='10' cy='9' r='3'/></svg>",
                ""
            )
        VAR _cab =
            "<div class='cab'><span class='sob'>Trajetória política · " & _n & " marcos</span>"
                & "<span class='dica'>passe o mouse num marco para ver a foto da época, redesenhada em traço</span></div>"
        -- 3 · Geometria (régua em y {REGUA_Y}, de x {REGUA_X0} a {REGUA_X0 + REGUA_W}; vagas iguais para os cartões)
        -- com o 1º marco a mais de 8 anos do 2º (Flávio: 2002 e depois 2016), a régua ganha um corte: um trecho curto
        -- em volta do 1º marco, o sinal de corte e o resto da régua do 2º marco ao fim, para os fios não se cruzarem
        VAR _seg = [{P} · Trajetória · segundo ano]
        VAR _corte = _seg - _ini > 8 -- geometria
        VAR _t0 = FLOOR ( _ini - 1, 5 ) -- geometria
        VAR _t1 = CEILING ( _fim + 2, 5 ) -- geometria
        VAR _escala = DIVIDE ( {REGUA_W}, _t1 - _t0 ) -- geometria
        VAR _wa = 200 -- geometria
        VAR _vao = 44 -- geometria
        VAR _a0 = _ini - 1.5 -- geometria
        VAR _a1 = _ini + 1.5 -- geometria
        VAR _b0 = _seg - 1 -- geometria
        VAR _b1 = _fim + 1 -- geometria
        VAR _xb = {REGUA_X0} + _wa + _vao -- geometria
        VAR _eb = DIVIDE ( {REGUA_W} - _wa - _vao, _b1 - _b0 ) -- geometria
        VAR _xd =
            IF (
                _corte,
                IF ( _tempo <= _a1, {REGUA_X0} + ( _tempo - _a0 ) * DIVIDE ( _wa, _a1 - _a0 ), _xb + ( _tempo - _b0 ) * _eb ), -- geometria
                {REGUA_X0} + ( _tempo - _t0 ) * _escala
            ) -- geometria
        VAR _xs = ( _ordem - 0.5 ) * DIVIDE ( 1620, _n ) -- geometria
        VAR _txd = @CSS(_xd)@ -- geometria
        VAR _txs = @CSS(_xs)@ -- geometria
        VAR _fio =
            "M" & _txs & IF ( _destaque = 1, ",232 L", ",176 L" ) & _txs & IF ( _destaque = 1, ",242 L", ",200 L" ) & _txd & ",262 L" & _txd & ",{REGUA_Y - 9}" -- geometria
        VAR _atraso = MIN ( _ordem + 4, 16 ) -- geometria
        VAR _anosInteira = SELECTCOLUMNS ( GENERATESERIES ( _t0, _t1, 5 ), "@a", [Value], "@c", 0 ) /* lista */
        VAR _anosCorte =
            UNION (
                ROW ( "@a", _ini, "@c", 1 ),
                SELECTCOLUMNS ( GENERATESERIES ( CEILING ( _b0, 5 ), FLOOR ( _b1, 5 ), 5 ), "@a", [Value], "@c", 1 )
            ) /* lista */
        VAR _anos = UNION ( _anosInteira, _anosCorte ) /* lista de marcas geométricas */
        VAR _marcas =
            CONCATENATEX (
                _anos,
                VAR _x =
                    @CSS(IF ( _corte, IF ( [@a] <= _a1, {REGUA_X0} + ( [@a] - _a0 ) * DIVIDE ( _wa, _a1 - _a0 ), _xb + ( [@a] - _b0 ) * _eb ), {REGUA_X0} + ( [@a] - _t0 ) * _escala ))@ -- geometria
                RETURN
                    IF ( [@c] = IF ( _corte, 1, 0 ),
                        "<line x1='" & _x & "' y1='{REGUA_Y - 6}' x2='" & _x & "' y2='{REGUA_Y + 6}'/>"
                            & "<text x='" & _x & "' y='{REGUA_Y + 28}'>" & [@a] & "</text>" ),
                "",
                [@a], ASC
            )
        -- 4 · Marcação
        VAR _regua =
            IF (
                _ordem = 1,
                _cab
                    & "<svg class='regua' width='1620' height='364' viewBox='0 0 1620 364'>"
                    & IF (
                        _corte,
                        "<line class='eixo traco' pathLength='1' x1='{REGUA_X0}' y1='{REGUA_Y}' x2='" & @CSS({REGUA_X0} + _wa)@ & "' y2='{REGUA_Y}'/>"
                            & "<line class='eixo traco' pathLength='1' x1='" & @CSS(_xb)@ & "' y1='{REGUA_Y}' x2='{REGUA_X0 + REGUA_W}' y2='{REGUA_Y}'/>"
                            & "<g class='corte'><line x1='" & @CSS({REGUA_X0} + _wa + 12)@ & "' y1='{REGUA_Y + 8}' x2='" & @CSS({REGUA_X0} + _wa + 20)@ & "' y2='{REGUA_Y - 8}'/>"
                            & "<line x1='" & @CSS({REGUA_X0} + _wa + 24)@ & "' y1='{REGUA_Y + 8}' x2='" & @CSS({REGUA_X0} + _wa + 32)@ & "' y2='{REGUA_Y - 8}'/></g>",
                        "<line class='eixo traco' pathLength='1' x1='{REGUA_X0}' y1='{REGUA_Y}' x2='{REGUA_X0 + REGUA_W}' y2='{REGUA_Y}'/>"
                    )
                    & "<g class='anos entra d4'>" & _marcas & "</g></svg>"
            )
        VAR _html =
            "<div class='tela m'>" & _regua
                & "<svg class='liga' width='1620' height='364' viewBox='0 0 1620 364'>"
                & "<path class='fio traco d" & _atraso & "' pathLength='1' d='" & _fio & "'/>"
                & "<circle class='ponto brota d" & _atraso & "' cx='" & _txd & "' cy='{REGUA_Y}' r='" & IF ( _destaque = 1, "12", "7" ) & "'/></svg>"
                & "<div class='alvo card " & IF ( _destaque = 1, "recorde ", "" ) & "sobe d" & _atraso & "' style='left:" & @CSS(_xs - 76)@ & "px'>"
                & "<div class='ano nc'>" & _ano & _icone & "</div>"
                & "<div class='tt'>" & _txtTit & "</div>" & IF ( _destaque = 1, "<div class='mao nota-recorde'>recorde</div>" ) & "</div>"
            & "</div>"
        RETURN
            IF ( NOT ISBLANK ( _ordem ), _html )
        """))
    G.desenho(f"{P} · Trajetória · ALT", "Texto para leitor de tela da linha do tempo.", dax(f"""
        LEFT (
            "Linha do tempo da trajetória política de {L['cand']}: " & [{P} · Trajetória · marcos] & " marcos, de "
                & [{P} · Trajetória · primeiro ano] & " a " & [{P} · Trajetória · último ano]
                & ". Passe o mouse num marco para ver a foto da época e o que aconteceu.",
            250
        )
        """))
    # dossiê polaroide (página de tooltip)
    G.desenho(f"{P} · Tooltip marco · HTML", "Dossiê do marco (polaroide presa com fita): a foto da época redesenhada "
              "em traço ou, sem foto de licença aberta, a cena recriada em ilustração (reserva: um ícone e a nota "
              "'sem foto de licença aberta'), a data, o título, o texto, a legenda e o crédito. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _tit = [{P} · Trajetória · título]
        VAR _txt = [{P} · Trajetória · texto do marco]
        VAR _ano = [{P} · Trajetória · ano]
        VAR _data = [{P} · Trajetória · data]
        VAR _foto = [{P} · Trajetória · foto]
        VAR _temFoto = [{P} · Trajetória · tem foto]
        VAR _ilus = [{P} · Trajetória · é ilustração]
        VAR _leg = [{P} · Trajetória · legenda da foto]
        VAR _cred = [{P} · Trajetória · crédito da foto]
        -- 2 · Textos
        VAR _txtData =
            IF (
                ISBLANK ( _data ),
                FORMAT ( _ano, "0" ),
                IF ( DAY ( _data ) = 1, "1º", FORMAT ( _data, "d" ) ) & FORMAT ( _data, " ""de"" mmmm ""de"" yyyy" )
            )
        VAR _icone =
            SWITCH (
                TRUE (),
                SEARCH ( "sindicato", _tit, 1, 0 ) > 0, "megafone",
                SEARCH ( "campanha", _tit, 1, 0 ) > 0, "megafone",
                SEARCH ( "fundação", _tit, 1, 0 ) > 0, "pessoas",
                SEARCH ( "Disputa", _tit, 1, 0 ) > 0, "urna",
                "jornal"
            )
        VAR _srcIcone = "{URL_MIDIA}/arte/icones/" & _icone & "-tinta.png"
        VAR _quadro =
            IF (
                _temFoto = 1,
                "<img class='foto' alt='' style='" & IF ( [{P} · desfecho] = 1, "object-position:{foto_posicao}", "" ) & "' src='{URL_MIDIA}/trajetoria/" & @ESC(_foto)@ & ".png' data-reserva='"
                    & _srcIcone & "'/>",
                "<img class='foto reserva' alt='' src='" & _srcIcone & "'/>"
                    & "<div class='sem mao'>sem foto de licença aberta</div>"
            )
        VAR _rodape =
            IF ( _temFoto = 1, "<div class='nota lg'><b>" & IF ( _ilus = 1, "Na ilustração:", "Na foto:" ) & "</b> "
                & @ESC(_leg)@ & "</div>"
                & "<div class='nota cr'>" & @ESC(_cred)@ & "</div>" )
        -- 4 · Marcação
        VAR _html =
            "<div class='tt2" & IF ( [{P} · desfecho] = 1, " final", "" ) & "'>"
                & "<div class='pol'>" & _quadro & "<div class='ano mao nc'>" & _ano & "</div>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/></div>"
                & "<div class='col'><div class='rot {L['cls']}-esc sobe'>" & _txtData & "</div>"
                & "<div class='man sobe d1'>" & @ESC(_tit)@ & "</div>"
                & "<div class='txt sobe d2'>" & @ESC(_txt)@ & "</div>"
                & IF ( _temFoto = 1, "<div class='pe sobe d3'>" & _rodape & "</div>" ) & "</div>"
            & "</div>"
        RETURN
            IF ( NOT ISBLANK ( _tit ), _html )
        """))
    G.desenho(f"{P} · Tooltip marco · ALT", "Texto para leitor de tela do dossiê do marco.", dax(f"""
        LEFT (
            [{P} · Trajetória · ano] & " · " & [{P} · Trajetória · título] & ": " & [{P} · Trajetória · texto do marco],
            250
        )
        """))


# ---------------------------------------------------------------------------------------------------- página
def cena_html(L, pos=None, depois=False):
    from html import escape
    if depois and not pos:
        return ("<div class='cena'><div class='papel cena-pendente'><span class='mao'>"
                "Foto com licença aberta ainda não disponível</span></div></div>")
    row = pos if depois else desenhos_csv()[L['comicio']]
    nome = row['arquivo'] if depois else L['comicio']
    pasta = 'trajetoria' if depois else 'comicio'
    leg = row['legenda']
    cred = row['credito'] if depois else row['credito_curto']
    reserva = '' if depois else f" data-reserva='{URL_MIDIA}/arte/{nome}.png'"
    return (f"<div class='cena sobe d6'><div class='papel'><img class='ce' alt='{escape(leg, quote=True)}' "
            f"src='{URL_MIDIA}/{pasta}/{nome}.png'{reserva}/></div>"
            f"<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
            f"<div class='leg'><div class='mao'>{escape(leg)}</div><div class='nota'>{escape(cred)}</div></div></div>")


JS_RESERVA = ("<script>(function(){try{var W=window,D=document;var f=function(i){if(i.__res){return;}i.__res=1;"
              "var t=function(){var r=i.getAttribute('data-reserva');if(r&&i.getAttribute('src')!==r){"
              "i.setAttribute('src',r);i.classList.add('reserva');}};if(i.complete&&i.naturalWidth===0){t();}"
              "else{i.addEventListener('error',t);}};var p=function(){var l=D.querySelectorAll('img[data-reserva]');"
              "for(var k=0;k<l.length;k++){f(l[k]);}};p();if(!W.__resObs&&W.MutationObserver){W.__resObs=1;"
              "new W.MutationObserver(p).observe(D.body,{childList:true,subtree:true});}}catch(x){}})();</script>")


def _css_topo(L: dict) -> str:
    return (
        ".qe{color:var(--tinta)}"
        ".qe .rotc{position:absolute;left:0;top:22px}"
        ".qe h1{position:absolute;left:0;top:50px;width:560px;margin:0;font-size:48px;font-weight:700;"
        "letter-spacing:-.025em;line-height:1.06}"
        ".qe .cred{position:absolute;left:0;top:394px;width:540px}"
        ".qe .ret{position:absolute;left:610px;top:-6px;width:400px;height:476px;object-fit:contain;"
        "object-position:50% 100%}"
        ".qe .cena{position:absolute;left:1052px;top:26px;width:568px;transform:rotate(1.2deg);"
        "transform-origin:50% 0}"
        ".qe .cena .papel{background:var(--branco);padding:12px 12px 14px 12px;"
        "box-shadow:0 1px 0 var(--areia),3px 6px 14px rgba(28,25,21,.12)}"
        ".qe .cena img.ce{display:block;width:544px;height:363px;object-fit:cover;object-position:50% 40%;"
        "background:var(--papel)}"
        ".qe .cena .fita{position:absolute;left:236px;top:-20px;width:110px;transform:rotate(-4deg);opacity:.9}"
        ".qe .cena .leg{position:absolute;left:0;top:400px;width:568px;transform:rotate(-1.2deg);"
        "transform-origin:0 0}"
        ".qe .cena .leg .mao{font-size:26px;color:var(--tinta);line-height:1.1}"
        ".qe .cena .leg .nota{margin-top:4px}"
        ".qe .cena-pendente{height:389px;display:flex;align-items:center;justify-content:center;padding:50px;text-align:center}"
    )


def _css_ficha(L: dict) -> str:
    return (
        ".fc{pointer-events:none}"
        ".fc .lin{position:relative;width:540px;border-top:1px dashed var(--areia);padding:10px 0 12px 0}"
        ".fc .lin:first-child{margin-top:0}"
        ".fc .val{display:flex;align-items:baseline;gap:12px;margin-top:4px}"
        ".fc .val>span{font-size:30px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}"
        ".fc .val small{font-size:16px;color:var(--grafite)}"
        ".fc .val small span{font-size:16px}"
    )


def _css_traj(L: dict) -> str:
    c = L["hex"]
    return (
        ".m{pointer-events:none}"
        ".m .cab{position:absolute;left:0;top:0;width:1620px;display:flex;justify-content:space-between;"
        "align-items:baseline}"
        ".m .cab .dica{font-size:15px;color:var(--cinza)}"
        ".m>svg{position:absolute;left:0;top:0;pointer-events:none}"
        ".m .regua .eixo{stroke:var(--tinta);stroke-width:1.6}"
        ".m .regua .corte line{stroke:var(--tinta);stroke-width:1.6;stroke-linecap:round}"
        ".m .regua .anos line{stroke:var(--grafite);stroke-width:1.2}"
        ".m .regua .anos text{font-family:var(--fonte);font-size:13px;fill:var(--cinza);text-anchor:middle}"
        f".m .fio{{fill:none;stroke:var(--areia);stroke-width:1.4;stroke-linejoin:round;transition:stroke .15s}}"
        f".m .ponto{{fill:{c};stroke:var(--papel);stroke-width:2.5;transition:r .15s}}"
        ".m .card{position:absolute;top:52px;width:152px;height:124px;padding:8px 8px 6px 8px;pointer-events:auto;"
        "cursor:default;border-radius:2px;transition:background .15s,box-shadow .15s,opacity .15s}"
        f".m .card .ano{{font-size:26px;font-weight:700;letter-spacing:-.02em;color:{c};line-height:1;"
        "display:flex;align-items:center;gap:8px}"
        f".m .card .cam{{width:18px;height:15px;fill:none;stroke:{c};stroke-width:1.5;stroke-linejoin:round}}"
        ".m .card .tt{margin-top:8px;font-size:15px;line-height:1.32;color:var(--tinta);display:-webkit-box;"
        "-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}"
        ".m .card:hover{background:var(--branco);box-shadow:0 0 0 1.2px var(--areia),2px 4px 10px rgba(28,25,21,.1)}"
        ".m .card.recorde{height:180px;background:#E9B5AA44;border:1px solid #B8322A;padding:10px}"
        ".m .recorde .tt{font-weight:600;-webkit-line-clamp:5}"
        ".m .nota-recorde{font-size:31px;color:#8E2620;line-height:1;transform:rotate(-7deg);margin-top:10px}"
        ".m:has(.card:hover) .fio{stroke:var(--tinta);stroke-width:2}"
        ".m:has(.card:hover) .ponto{r:10}"
        "#htmlContent:has(.card:hover) .m:not(:has(.card:hover)) .card,"
        "#htmlContent:has(.card:hover) .m:not(:has(.card:hover)) .liga{opacity:.35}"
    )


def _css_tooltip(L: dict) -> str:
    return (
        ".tt2{position:fixed;inset:0;background:var(--papel);overflow:hidden}"
        ".tt2 .pol{position:absolute;left:26px;top:40px;width:250px;height:330px;background:var(--branco);"
        "transform:rotate(-2.5deg);box-shadow:0 1px 0 var(--areia),3px 6px 14px rgba(28,25,21,.14)}"
        ".tt2 .pol .foto{position:absolute;left:13px;top:13px;width:224px;height:280px;object-fit:cover;"
        "object-position:50% 30%;background:var(--papel)}"
        ".tt2 .pol .foto.reserva{object-fit:contain;padding:60px 46px 110px 46px}"
        ".tt2 .pol .sem{position:absolute;left:24px;right:24px;top:196px;text-align:center;font-size:26px;"
        "color:var(--grafite);line-height:1.05}"
        ".tt2 .pol .ano{position:absolute;left:0;right:0;bottom:4px;text-align:center;font-size:28px;"
        "color:var(--tinta)}"
        ".tt2 .pol .fita{position:absolute;left:70px;top:-18px;width:110px;transform:rotate(3deg);opacity:.92}"
        ".tt2 .col{position:absolute;left:304px;top:30px;width:310px}"
        ".tt2 .col .man{margin-top:6px;font-size:22px;line-height:1.2}"
        ".tt2 .col .txt{margin-top:10px;font-size:15px;line-height:1.42;color:var(--tinta)}"
        ".tt2 .col .pe{margin-top:12px;border-top:1px dashed var(--areia);padding-top:8px}"
        ".tt2 .col .nota{font-size:13px;line-height:1.35}.tt2 .col .lg{color:var(--grafite)}"
        ".tt2 .col .cr{margin-top:4px}"
        ".tt2.final .col{top:22px}.tt2.final .col .man{font-size:20px;line-height:1.15}"
        ".tt2.final .col .txt{font-size:14px;line-height:1.35;margin-top:8px}"
        ".tt2.final .col .pe{margin-top:8px;padding-top:6px}"
    )


def declarar_quem_e(P: str) -> list:
    """Declarações da página P (T02 ou T04): os três visuais e a página de tooltip."""
    import pbip_lib as lib
    from pbip_lib import Pagina, Visual
    L = LADOS[P]
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    topo_fixo = (
        f"<style>{_css_topo(L)}</style><div class='tela qe'>"
        f"<div class='rot rotc {L['cls']}-esc sobe'>{L['rot'].upper()}</div>"
        f"<h1 class='sobe d1'>{L['completo']}</h1>"
        f"<img class='ret entra d2' alt='Retrato de {L['completo']} em traço' "
        f"src='{URL_MIDIA}/arte/{L['retrato']}.png'/>"
        f"<div class='nota cred'>{L['cred_retrato'].replace('CC BY ', 'CC&nbsp;BY&nbsp;')}</div></div>"
        "<div class='tela qe'>{{content}}</div>" + JS_RESERVA)
    ficha = (f"<style>{_css_ficha(L)}</style>" + "{{content}}")
    traj = (f"<style>{_css_traj(L)}</style>" + "{{content}}")
    filtro = lib.filtro_visual_categorico(f"traj{L['cand'].replace('á', 'a')}", "Trajetória", "Candidato", [L["cand"]])
    for f in filtro["filters"]:
        f["isHiddenInViewMode"] = True
        f["isLockedInViewMode"] = True
    tt = L["tooltip"]
    x, y, w, h = TOPO
    itens = [
        Visual(P, lib.visual_html(f"{P}_Quem_Html", x, y, w, h, f"{P} · Cena · HTML", folha_de_estilo=css, z=z, tab=100,
                                  alt=lib.medida(f"{P} · Cena · ALT"),
                                  modelo_corpo=topo_fixo)),
        Visual(P, lib.visual_html(f"{P}_Ficha_Html", 150, 140 + 128, 560, 250, f"{P} · Ficha · HTML",
                                  folha_de_estilo=css, z=z + 2, tab=110, alt=lib.medida(f"{P} · Ficha · ALT"),
                                  modelo_corpo=ficha)),
        Visual(P, lib.visual_html(f"{P}_Trajetoria_Marcos", *TRAJ, f"{P} · Trajetória · HTML", folha_de_estilo=css,
                                  z=z + 4, tab=200, alt=lib.medida(f"{P} · Trajetória · ALT"),
                                  granularidade=("Trajetória", "Título"), tooltip_pagina=tt, filtros=filtro,
                                  modelo_corpo=traj)),
        Pagina(lib.pagina_tooltip(tt, f"Marco · {L['cand']}", altura=TT_H, largura=TT_W), ordem=L["ordem_tt"]),
        Visual(tt, lib.visual_html(f"TT_{tt[2:]}_Conteudo", 0, 0, TT_W, TT_H, f"{P} · Tooltip marco · HTML",
                                   alt=lib.medida(f"{P} · Tooltip marco · ALT"), pagina_wh=(TT_W, TT_H),
                                   folha_de_estilo=css, filtros=filtro,
                                   modelo_corpo=f"<style>{_css_tooltip(L)}</style>" + "{{content}}" + JS_RESERVA)),
    ]
    return itens


def main() -> int:
    for P, L in LADOS.items():
        G = Gravador(L["pasta"])
        contas(P, L, G)
        desenho(P, L, G)
        apagados = G.limpar()
        print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
