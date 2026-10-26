"""28 · História do PT — 1989–2026, turno decisivo nos estados e turnos separados no país.

Um protagonista: 27 UFs com play automático finito, régua clicável, vencedor real e intensidade pela distância
ao segundo colocado. Apoios: a série de votos das duas candidaturas e os denominadores históricos.
"""
import desenho_t29 as D
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

P = 'T29'
CSS = 'Estilo · CSS'
Z = lib.CAMADAS['conteudo']


def corpo():
    return ("<style>.h29 .man{font-size:35px;font-weight:650;line-height:1.15}.h29 .man .num{font-size:64px;font-weight:700}"
            ".h29 .txt{font-size:16px;margin-top:10px;line-height:1.5}"
            ".rot29 .sub{font-size:15px;line-height:1.4;color:var(--grafite);margin-top:12px}"
            ".rot29 .leg{display:flex;gap:24px;margin-top:14px;font-size:15px}"
            ".rot29 .leg i{display:inline-block;width:22px;height:3px;vertical-align:middle;margin-right:8px}"
            ".rot29 .mao{position:absolute;right:12px;top:188px;font-size:26px;transform:rotate(-4deg)}"
            ".contexto29{font-size:15px;line-height:1.55;color:var(--grafite)}"
            "</style>{{content}}")


def corpo_dossie():
    return ("<style>.dossier29{padding:28px 30px;color:var(--tinta);border:1px solid var(--areia);background:var(--papel)}"
            ".dossier29 .fita{position:absolute;top:0;left:230px;width:100px;height:15px;background:var(--areia);opacity:.7;transform:rotate(-3deg)}"
            ".dossier29 .rot{font-size:13px}.dossier29 h2{font-size:28px;margin:12px 0}.dossier29 p{font-size:15px;line-height:1.4;margin:10px 0}"
            ".dossier29 table{width:100%;border-collapse:collapse;font-size:15px;font-variant-numeric:tabular-nums}"
            ".dossier29 td,.dossier29 th{padding:5px 6px;border-bottom:1px solid var(--areia);text-align:right}"
            ".dossier29 td:first-child,.dossier29 th:first-child{text-align:left}.dossier29 .mao{font-size:26px;margin:12px 0}"
            ".dossier29 small{font-size:13px;color:var(--grafite)}.dossier29 .par{margin:20px 0}.dossier29 .par>*{display:block}"
            ".dossier29 .par strong{font-size:24px;margin:7px 0}.dossier29 .par span{font-size:15px}"
            "</style>{{content}}")


def declarar(ctx):
    mapa = lib.visual_deneb('T29_Mapa_Estados', 150, 290, D.MAPA_W, D.MAPA_H, 'spec/t29_mapa.json', [
        lib.campo_coluna('uf', 'UF', 'UF'),
        lib.campo_medida('serie', 'T29 · Mapa · série'),
        lib.campo_medida('quadros', 'T29 · Mapa · quadros')],
        alt=lib.medida('T29 · Mapa · ALT'), tooltip_pagina='ttT29Estado', z=Z+1, tab=120, renderizacao='canvas')
    mapa['visual']['objects']['dataLimit'] = [{'properties': {'enableIncrementalDataUpdates': lib.lit(True)}}]
    # ZZ pode chegar no dataset, mas não tem geometria e é excluído antes de desenhar. Contadores usam só as 27 UFs.
    return [
        Visual(P, lib.visual_html('T29_Resposta_Html', 150, 140, 1620, 130, 'T29 · Resposta · HTML',
            folha_de_estilo=CSS, modelo_corpo=corpo(), alt=lib.medida('T29 · Resposta · ALT'), z=Z, tab=100)),
        Visual(P, mapa),
        Visual(P, lib.visual_html('T29_Grafico_Titulo', 1020, 290, 750, 90, 'Casca · vazio', folha_de_estilo=CSS,
            modelo_corpo=corpo().replace('{{content}}', "<div class='tela rot29'><div class='rot'>VOTOS NO PAÍS · MESMA ESCALA NOS DOIS TURNOS</div>"
                "<div class='leg'><span><i style='background:var(--vermelho)'></i>PT</span>"
                "<span><i style='background:var(--azul)'></i>Principal adversário nacional</span></div></div>{{content}}"),
            alt='Votos do PT e do principal adversário, com tratamento e escala iguais.', z=Z, tab=130)),
        Visual(P, lib.visual_deneb('T29_Grafico_Votos', 1020, 385, 750, 510, 'spec/t29_votos.json', [
            lib.campo_coluna('ano', 'PT histórico Brasil', 'Ano'), lib.campo_coluna('turno', 'PT histórico Brasil', 'Turno'),
            lib.campo_medida('pt', 'T29 · PT votos'), lib.campo_medida('adv', 'T29 · adversário votos')],
            alt=lib.medida('T29 · Gráfico · ALT'), tooltip_pagina='ttT29Eleicao', z=Z+1, tab=140)),
        Visual(P, lib.visual_html('T29_Grafico_Recorde', 1510, 630, 255, 40, 'Casca · vazio', folha_de_estilo=CSS,
            modelo_corpo="<div class='tela mao' style='font-size:28px;text-align:right;transform:rotate(-4deg)'>recorde em votos ↘</div>{{content}}",
            alt='Recorde em votos no segundo turno de 2026.', z=Z+2, tab=142)),
        Visual(P, lib.visual_html('T29_Grafico_Notas', 1020, 880, 750, 45, 'Casca · vazio', folha_de_estilo=CSS,
            modelo_corpo="<div class='tela' style='font-size:14px;color:var(--grafite);line-height:1.5'>"
                "1994 e 1998: sem 2º turno. A queda de 2014 para 2018 aparece nos dois turnos.</div>{{content}}",
            alt='1994 e 1998 sem segundo turno; quedas preservadas.', z=Z, tab=145)),
        Visual(P, lib.visual_html('T29_Contexto_Html', 1020, 930, 750, 48, 'T29 · Contexto · HTML',
            folha_de_estilo=CSS, modelo_corpo=corpo(), alt=lib.medida('T29 · Contexto · ALT'), z=Z, tab=150)),
        Visual(P, lib.visual_html('T29_Fontes_Versoes', 1020, 982, 750, 18, 'Casca · vazio', folha_de_estilo=CSS,
            modelo_corpo="<div class='tela' style='font-size:13px;color:var(--cinza)'>Versões históricas do TSE: divergências documentadas no i.</div>{{content}}",
            alt='Versões oficiais históricas divergem; detalhes no i.', z=Z, tab=155)),
        *pagina_lib.tooltip('ttT29Estado', 'História do estado', 580, 710, 'T29 · Estado · HTML', ordem=390,
            folha_de_estilo=CSS, modelo_corpo=corpo_dossie()),
        *pagina_lib.tooltip('ttT29Eleicao', 'Duas candidaturas, mesma conta', 580, 480, 'T29 · Eleição · HTML', ordem=391,
            folha_de_estilo=CSS, modelo_corpo=corpo_dossie()),
    ]
