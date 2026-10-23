"""desenho_exterior — o tooltip rico do exterior, país a país (pedido do Alisson, 23/10/2026: "na questão do exterior,
seria bom colocarmos um tooltip rico apenas pra ele, informando por país o percentual de cada um"). Dono: main.

Grava em pbi/dax/_Exterior/Desenho:
  Exterior · 1º turno · HTML   1º turno de 2026 por país (Lula × Flávio, válidos, variação da margem desde 2022);
                               telas 12 (Estados) e 22 (Simulador)
  Exterior · ao vivo · HTML    a apuração do 2º turno por país (Lula × Flávio, % de seções); antes dos primeiros votos,
                               o 1º turno com o aviso "antes da apuração" — tela 18
  Exterior · simulador · HTML  o 1º turno por país com o 2º turno do exterior no cenário escolhido no topo — tela 22
  Exterior · alvo · HTML       o alvo transparente que abre o tooltip sobre a linha ou o quadrado do exterior
  e os ALT de cada um.

    python -I -X utf8 pbi/scripts/desenho_exterior.py
"""

from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "dax" / "_Exterior" / "Desenho"
DOBRA = r"_Exterior\Desenho"
TOP = 12


def gravar(nome, descricao, expressao):
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / f"{nome}.dax").write_text(
        f"/*\n@pasta: {DOBRA}\n@formato: texto\n@descricao: {descricao}\n*/\n{expressao.strip()}\n", encoding="utf-8")


def molde(fonte):
    """fonte = 'turno1' (Exterior país, 2026, com variação desde 2022) ou 'vivo' (Apuração exterior)."""
    if fonte == "turno1":
        paises = "CALCULATETABLE ( VALUES ( 'Exterior país'[País] ), 'Exterior país'[Ano] = 2026 )"
        col = "'Exterior país'[País]"
        v, l, f = "[Exterior · válidos]", "[Exterior · Lula %]", "[Exterior · Flávio %]"
        extra = '"@d", [Exterior · variação da margem]'
        resto_v = "CALCULATE ( SUM ( 'Exterior país'[Validos] ), 'Exterior país'[Ano] = 2026, TREATAS ( _resto, 'Exterior país'[País] ) )"
        resto_l = "CALCULATE ( SUM ( 'Exterior país'[VotosPT] ), 'Exterior país'[Ano] = 2026, TREATAS ( _resto, 'Exterior país'[País] ) )"
        resto_f = "CALCULATE ( SUM ( 'Exterior país'[VotosAdversario] ), 'Exterior país'[Ano] = 2026, TREATAS ( _resto, 'Exterior país'[País] ) )"
        rotulo = ('"EXTERIOR · 1º TURNO DE 2026 · " & [Exterior · cidades] & " CIDADES EM " & [Exterior · países] '
                  '& " PAÍSES"')
        coluna3 = "2022→26"
        celula3 = ('"<span class=\'dv " & IF ( [@d] < 0, "neg", "pos" ) & "\'>" & IF ( ISBLANK ( [@d] ), "novo", '
                   'FORMAT ( [@d], "+0.0;−0.0;0.0" ) ) & "</span>"')
        lula_n, flavio_n = "[Exterior · países com Lula à frente]", "[Exterior · países com Flávio à frente]"
        sem_n, sem_txt = "[Exterior · países sem vencedor]", '"empate ou nenhum voto válido"'
        total_v, total_l, total_f = "[Exterior · válidos]", "[Exterior · Lula %]", "[Exterior · Flávio %]"
        nota_pe = ('"2022→26: variação da margem do PT de 2022 (Lula × Bolsonaro) para 2026 (Lula × Flávio), em '
                   'pontos; negativa, na direção do adversário."')
    else:
        paises = "VALUES ( 'Apuração exterior'[País] )"
        col = "'Apuração exterior'[País]"
        v, l, f = "[Apuração exterior · válidos]", "[Apuração exterior · Lula %]", "[Apuração exterior · Flávio %]"
        extra = '"@s", [Apuração exterior · seções %]'
        resto_v = "CALCULATE ( SUM ( 'Apuração exterior'[Validos] ), TREATAS ( _resto, 'Apuração exterior'[País] ) )"
        resto_l = "CALCULATE ( SUM ( 'Apuração exterior'[LulaVotos] ), TREATAS ( _resto, 'Apuração exterior'[País] ) )"
        resto_f = "CALCULATE ( SUM ( 'Apuração exterior'[FlavioVotos] ), TREATAS ( _resto, 'Apuração exterior'[País] ) )"
        rotulo = ('"EXTERIOR AO VIVO · " & [Apuração · turno] & "º TURNO · " '
                  '& FORMAT ( [Apuração exterior · seções %] * 100, "0" ) & "% DAS SEÇÕES · " '
                  '& [Apuração exterior · países] & " PAÍSES"')
        coluna3 = "SEÇÕES"
        celula3 = '"<span class=\'dv\'>" & FORMAT ( [@s] * 100, "0" ) & "%</span>"'
        lula_n, flavio_n = "[Apuração exterior · países com Lula à frente]", "[Apuração exterior · países com Flávio à frente]"
        sem_n = "[Apuração exterior · países sem vencedor]"
        sem_txt = ('IF ( [Apuração exterior · seções %] >= 1, "empate ou nenhum voto válido", '
                   '"empate ou nenhum voto apurado ainda" )')
        total_v, total_l, total_f = ("[Apuração exterior · válidos]", "[Apuração exterior · Lula %]",
                                     "[Apuração exterior · Flávio %]")
        nota_pe = ('"Países pelos votos válidos já apurados" & IF ( [Apuração · turno] = 2, "; no 2º turno, Lula e '
                   'Flávio somam 100%.", "; no 1º turno, o resto é dos outros candidatos." )')
    return f"""
-- 1 · Leituras: os países com mais votos válidos (os {TOP} maiores) e o resto somado
VAR _paises = {paises}
VAR _t =
    ADDCOLUMNS ( _paises, "@v", {v}, "@l", {l}, "@f", {f}, {extra} )
VAR _top = TOPN ( {TOP}, FILTER ( _t, [@v] > 0 ), [@v], DESC, {col}, ASC )
VAR _topR = ADDCOLUMNS ( _top, "@i", RANKX ( _top, [@v],, DESC, DENSE ) )
VAR _resto = EXCEPT ( _paises, SELECTCOLUMNS ( _top, "País", {col} ) )
VAR _nResto = COUNTROWS ( _resto ) + 0
VAR _rv = {resto_v}
VAR _rl = DIVIDE ( {resto_l}, _rv )
VAR _rf = DIVIDE ( {resto_f}, _rv )
VAR _tl = {total_l}
VAR _tf = {total_f}
-- 2 · Desenho
VAR _linhas =
    CONCATENATEX (
        _topR,
        "<div class='lp sobe d" & MIN ( 16, [@i] + 3 ) & "'><span class='pn'><b>" & {col} & "</b><i>"
            & FORMAT ( [@v], "#,0" ) & IF ( [@v] = 1, " voto", " votos" ) & "</i></span>"
            & "<span class='vl'>" & FORMAT ( [@l] * 100, "0" ) & "%</span>"
            & "<span class='br'><i class='bl barra-x' style='width:" & FORMAT ( [@l] * 100, "0.0##", "en-US" )
            & "%'></i><i class='bf barra-x-dir' style='width:" & FORMAT ( [@f] * 100, "0.0##", "en-US" ) & "%'></i></span>"
            & "<span class='vf'>" & FORMAT ( [@f] * 100, "0" ) & "%</span>"
            & {celula3} & "</div>",
        "", [@v], DESC
    )
VAR _outros =
    IF (
        _nResto > 0,
        "<div class='outros sobe d16'>Outros " & _nResto & IF ( _nResto = 1, " país", " países" ) & " · "
            & FORMAT ( _rv, "#,0" ) & " votos · Lula " & FORMAT ( _rl * 100, "0" ) & "% × Flávio "
            & FORMAT ( _rf * 100, "0" ) & "%</div>"
    )
VAR _nl = {lula_n}
VAR _nf = {flavio_n}
VAR _ns = {sem_n}
RETURN
    "<div class='tela tx'><div class='fita'></div>"
        & "<div class='rot topo-rot'>" & {rotulo} & "</div>"
        & "<div class='topo'><div class='c'><span class='num lula'>" & FORMAT ( _tl * 100, "0.0" ) & "%</span>"
        & "<span class='rot lula-esc'>LULA</span></div><div class='c'><span class='num flavio'>"
        & FORMAT ( _tf * 100, "0.0" ) & "%</span><span class='rot flavio-esc'>FLÁVIO</span></div>"
        & "<div class='c tot'><span class='num'>" & FORMAT ( {total_v}, "#,0" ) & "</span>"
        & "<span class='rot'>VOTOS VÁLIDOS</span></div></div>"
        & "<div class='mao'>Lula na frente em " & _nl & IF ( _nl = 1, " país", " países" ) & ", Flávio em " & _nf
        & "</div>"
        & "<div class='cab rot'><span>PAÍS</span><span>LULA</span><span></span><span>FLÁVIO</span><span>{coluna3}</span></div>"
        & "<div class='lista'>" & _linhas & "</div>" & _outros
        & "<div class='pe nota'>" & IF ( _ns > 0, "Nos outros " & _ns & IF ( _ns = 1, " país, ", " países, " )
        & {sem_txt} & ". " ) & {nota_pe} & "</div></div>"
"""


def main():
    gravar("Exterior · 1º turno · HTML", "Tooltip rico do exterior no 1º turno de 2026: Lula × Flávio no exterior, os 12 "
           "países com mais votos (barra dos dois e variação da margem desde 2022) e o resto somado.", molde("turno1"))
    gravar("Exterior · 1º turno · ALT", "Texto alternativo do tooltip do exterior no 1º turno.", """
"Exterior, 1º turno de 2026: Lula " & FORMAT ( [Exterior · Lula %], "0.0%" ) & ", Flávio " & FORMAT ( [Exterior · Flávio %], "0.0%" )
    & ", em " & [Exterior · países] & " países; Lula à frente em " & [Exterior · países com Lula à frente] & "."
""")
    vivo = molde("vivo")
    gravar("Exterior · ao vivo · HTML", "Tooltip rico do exterior na apuração do 2º turno: Lula × Flávio por país, com a % "
           "de seções; antes dos primeiros votos, o 1º turno com o aviso de que a apuração ainda não começou.", f"""
IF (
    [Apuração exterior · válidos] = 0,
    SUBSTITUTE (
        [Exterior · 1º turno · HTML],
        "<div class='rot topo-rot'>EXTERIOR · 1º TURNO DE 2026",
        "<div class='aviso'>a apuração começa às 17h de 25/10; até lá, o voto do 1º turno</div><div class='rot topo-rot'>EXTERIOR · 1º TURNO DE 2026"
    ),
{vivo.strip()}
)""")
    gravar("Exterior · ao vivo · ALT", "Texto alternativo do tooltip do exterior na apuração.", """
IF (
    [Apuração exterior · válidos] = 0,
    "Exterior: a apuração começa às 17h de 25/10; no 1º turno, Lula " & FORMAT ( [Exterior · Lula %], "0.0%" ) & " e Flávio " & FORMAT ( [Exterior · Flávio %], "0.0%" ) & ".",
    "Exterior, apuração do 2º turno: Lula " & FORMAT ( [Apuração exterior · Lula %], "0.0%" ) & ", Flávio " & FORMAT ( [Apuração exterior · Flávio %], "0.0%" ) & "."
)
""")
    gravar("Exterior · simulador · HTML", "Tooltip rico do exterior na tela 22: o 2º turno do exterior no cenário escolhido "
           "e, abaixo, o 1º turno país a país.", """
VAR _l = [T22 · cenário · Lula %]
VAR _f = [T22 · cenário · Flávio %]
RETURN
    SUBSTITUTE (
        [Exterior · 1º turno · HTML],
        "<div class='rot topo-rot'>",
        "<div class='cen'><span class='rot'>NO SEU CENÁRIO, NO 2º TURNO</span><b class='lula-esc'>Lula "
            & FORMAT ( _l, "0.0%" ) & "</b><b class='flavio-esc'>Flávio " & FORMAT ( _f, "0.0%" ) & "</b></div>"
            & "<div class='rot topo-rot'>"
    )
""")
    gravar("Exterior · simulador · ALT", "Texto alternativo do tooltip do exterior no simulador.", """
"Exterior no cenário: Lula " & FORMAT ( [T22 · cenário · Lula %], "0.0%" ) & ", Flávio " & FORMAT ( [T22 · cenário · Flávio %], "0.0%" )
    & "; no 1º turno, Lula " & FORMAT ( [Exterior · Lula %], "0.0%" ) & " e Flávio " & FORMAT ( [Exterior · Flávio %], "0.0%" ) & "."
""")
    gravar("Exterior · alvo · HTML", "Alvo transparente sobre a linha ou o quadrado do exterior: abre o tooltip rico do "
           "exterior (o desenho de baixo continua o do visual da tela).", """
IF ( SELECTEDVALUE ( 'UF'[UF] ) = "ZZ", "<div class='tela ax'></div>" )
""")
    gravar("Exterior · alvo · ALT", "Texto alternativo do alvo do exterior.",
           '"Exterior: passe o mouse para ver o voto país a país."')
    print("desenho do exterior gravado")


if __name__ == "__main__":
    main()
