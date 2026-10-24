"""Tabelas da campanha: pesquisas, debates, buscas no Google, redes, anúncios, trajetória dos candidatos, transferência
de votos, rejeição e apoios. Fonte: os levantamentos de dados/bruto (cada linha com a URL da fonte), exportados para
dados/pbi por pipeline/exportar_pbi.py."""

from gerar_modelo import col, tabela_csv

FONTE = col("fonte_url", "Fonte", descricao="URL da fonte da linha.", oculta=True)
OBS = col("observacao", "Observação", descricao="Nota do levantamento (método, ressalva).", oculta=True)

TABELAS = [
    tabela_csv(
        "Pesquisa", "Pesquisas de intenção de voto registradas no TSE, 1º e 2º turno (cenário), em votos totais ou "
                    "válidos, de agosto a outubro de 2026.",
        "dados/pbi/pesquisa.csv",
        [col("id", "Id", tipo="int", descricao="Identificador da linha.", oculta=True, formato="0"),
         col("cenario", "Cenário", descricao="1º turno ou 2º turno (Lula × Flávio)."),
         col("instituto", "Instituto", descricao="Instituto de pesquisa."),
         col("contratante", "Contratante", descricao="Quem contratou.", oculta=True),
         col("campo_inicio", "Campo início", tipo="date", descricao="Início do campo.", oculta=True),
         col("campo_fim", "Campo fim", tipo="date", descricao="Fim do campo (a data da pesquisa no painel)."),
         col("divulgacao", "Divulgação", tipo="date", descricao="Data de divulgação.", oculta=True),
         col("registro_tse", "Registro", descricao="Registro no TSE.", oculta=True),
         col("amostra", "Amostra", tipo="int", descricao="Entrevistas.", oculta=True),
         col("margem_pp", "Margem", tipo="number", descricao="Margem de erro (p.p.).", oculta=True, formato="0.0"),
         col("modo", "Modo", descricao="Presencial, telefone, online.", oculta=True),
         col("tipo", "Tipo", descricao="totais ou validos.", oculta=True),
         col("lula", "Lula", tipo="number", descricao="% de Lula.", oculta=True, formato="0.0"),
         col("flavio", "Flavio", tipo="number", descricao="% de Flávio.", oculta=True, formato="0.0"),
         col("cury", "Cury", tipo="number", descricao="% de Augusto Cury.", oculta=True, formato="0.0"),
         col("renan", "Renan", tipo="number", descricao="% de Renan Santos.", oculta=True, formato="0.0"),
         col("outros", "Outros", tipo="number", descricao="% dos demais candidatos.", oculta=True, formato="0.0"),
         col("brancos_nulos", "BrancosNulos", tipo="number", descricao="% brancos e nulos.", oculta=True,
             formato="0.0"),
         col("indecisos", "Indecisos", tipo="number", descricao="% indecisos.", oculta=True, formato="0.0"),
         col("momento", "Momento", descricao="No 2º turno: antes_1turno ou apos_1turno.", oculta=True),
         FONTE],
        oculta=True),
    tabela_csv(
        "Debate", "Os debates presidenciais de 2026 marcados por emissoras: realizados, cancelados, quem foi e quem "
                  "faltou, audiência.",
        "dados/pbi/debate.csv",
        [col("data", "Data", tipo="date", descricao="Data do debate."),
         col("turno", "Turno", tipo="int", descricao="Turno.", formato="0"),
         col("emissora", "Emissora", descricao="Emissora ou pool."),
         col("pool", "Pool", descricao="Veículos do pool.", oculta=True),
         col("participantes", "Participantes", descricao="Quem participou.", oculta=True),
         col("ausentes", "Ausentes", descricao="Quem faltou.", oculta=True),
         col("mediacao", "Mediação", descricao="Mediadores.", oculta=True),
         col("audiencia_pontos_gsp", "Audiência", tipo="number", descricao="Pontos de audiência na Grande SP.",
             oculta=True, formato="0.0"),
         col("audiencia_fonte", "Fonte da audiência", descricao="De onde vem a audiência.", oculta=True),
         col("pico_streaming", "Pico no streaming", tipo="number", descricao="Pico simultâneo no YouTube.",
             oculta=True, formato="#,0"),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Trends tempo", "Google Trends: índice relativo (0–100) por dia ou hora de cada série (candidatos como tópico "
                        "T2 ou termo T1, buscas de serviço S1/S2, termos gerais E1, Central C1, horas H1/H2).",
        "dados/pbi/trends_tempo.csv",
        [col("data", "DataTexto", descricao="Data (aaaa-mm-dd) ou data e hora (aaaa-mm-dd hh:mm).", oculta=True),
         col(None, "Momento", tipo="datetime", descricao="Data e hora da observação.", oculta=True,
             formato="dd/MM/yyyy HH:mm"),
         col("termo", "Série", descricao="Termo e consulta, ex.: 'Lula [tópico | T2]'."),
         col("indice", "Índice", tipo="int", descricao="Índice relativo 0–100 dentro da consulta.", oculta=True,
             formato="0"),
         col("granularidade", "Granularidade", descricao="diária ou hora.", oculta=True),
         FONTE, OBS],
        oculta=True,
        passos='    Final = Table.AddColumn({entrada}, "Momento", each DateTime.FromText(if Text.Length([DataTexto]) = 10 '
               'then [DataTexto] & " 00:00" else [DataTexto], [Format = "yyyy-MM-dd HH:mm", Culture = "en-US"]), '
               'type datetime)'),
    tabela_csv(
        "Trends UF", "Google Trends por UF: índice 0–100 e participação % de cada candidato nas buscas, no período "
                     "todo (01/08–22/10) e no 2º turno.",
        "dados/pbi/trends_uf.csv",
        [col("uf", "UF", descricao="Sigla da UF.", oculta=True),
         col("termo", "Série", descricao="Candidato, tipo de consulta e medida."),
         col("indice", "Índice", tipo="int", descricao="Índice ou participação (%).", oculta=True, formato="0"),
         col("periodo", "Período", descricao="Período da consulta."),
         FONTE],
        oculta=True),
    tabela_csv(
        "Trends UF tempo", "Google Trends por UF, dia a dia (consulta U2, 23/10/2026: Lula × Flávio como tópicos, uma "
                           "consulta por UF, 01/08 a 23/10, 23/10 parcial). O índice 0–100 é relativo dentro da "
                           "consulta de cada UF e não se compara entre UFs; 0 é volume abaixo do mínimo do Google (ou a "
                           "lacuna de 19 a 21/09), com nota em Observação. A consulta nacional (uf = BR) fica fora: a "
                           "curva do Brasil segue a T2 de 'Trends tempo'.",
        "dados/pbi/trends_uf_tempo.csv",
        [col("uf", "UF", descricao="Sigla da UF da consulta.", oculta=True),
         col("data", "Data", tipo="date", descricao="Dia da observação.", oculta=True),
         col("termo", "Série", descricao="Termo e consulta: 'Lula [tópico | U2]' ou 'Flávio Bolsonaro [tópico | U2]'."),
         col("indice", "Índice", tipo="int", descricao="Índice relativo 0–100 dentro da consulta da UF.", oculta=True,
             formato="0"),
         FONTE, OBS],
        oculta=True, filtro='[UF] <> "BR"'),
    tabela_csv(
        "Seguidores", "Seguidores dos candidatos por rede e data (Social Blade, Datrix); brancos onde não há total "
                      "publicado.",
        "dados/pbi/seguidores.csv",
        [col("candidato", "Candidato", descricao="Candidato."),
         col("plataforma", "Plataforma", descricao="Rede social."),
         col("data", "Data", tipo="date", descricao="Data da contagem."),
         col("seguidores", "Seguidores", tipo="number", descricao="Seguidores.", oculta=True, formato="#,0"),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Monitoramento", "Métricas de monitoramento digital: interações, ganho de seguidores, índice de popularidade "
                         "digital (Quaest), canais, por estudo e período.",
        "dados/pbi/monitoramento.csv",
        [col("estudo", "Estudo", descricao="Estudo e quem divulgou."),
         col("periodo_inicio", "Início", tipo="date", descricao="Início do período.", oculta=True),
         col("periodo_fim", "Fim", tipo="date", descricao="Fim do período.", oculta=True),
         col("metrica", "Métrica", descricao="O que foi medido."),
         col("candidato", "Candidato", descricao="Candidato."),
         col("valor", "Valor", tipo="number", descricao="Valor medido.", oculta=True, formato="#,0.0"),
         col("unidade", "Unidade", descricao="Unidade do valor.", oculta=True),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Anúncios", "Gasto com anúncios (Biblioteca de Anúncios da Meta e prestação de contas ao TSE).",
        "dados/pbi/anuncios.csv",
        [col("candidato_ou_partido", "Anunciante", descricao="Página ou candidatura."),
         col("plataforma", "Plataforma", descricao="Plataforma ou base."),
         col("periodo", "Período", descricao="Período."),
         col("valor_reais", "Valor", tipo="number", descricao="R$.", oculta=True, formato="#,0"),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Trajetória", "Os marcos da trajetória política de Lula e de Flávio, com a foto histórica (redesenhada em "
                      "traço) quando há foto de licença aberta.",
        "dados/pbi/trajetoria.csv",
        [col("candidato", "Candidato", descricao="Lula ou Flávio."),
         col("ordem", "Ordem", tipo="int", descricao="Ordem cronológica do marco.", formato="0"),
         col("data", "Data", descricao="Data do marco (aaaa ou aaaa-mm-dd)."),
         col("ano", "Ano", tipo="int", descricao="Ano do marco.", formato="0"),
         col("titulo", "Título", descricao="Título curto do marco."),
         col("texto", "Texto", descricao="O que aconteceu (até ~200 caracteres)."),
         col("foto", "Foto", descricao="Nome da foto redesenhada (sem extensão); vazio quando não há foto livre."),
         col("foto_autor", "Autor da foto", descricao="Autor da foto original.", oculta=True),
         col("foto_licenca", "Licença da foto", descricao="Licença da foto original.", oculta=True),
         col("foto_ano", "Ano da foto", descricao="Quando a foto foi feita.", oculta=True),
         FONTE],
        oculta=True),
    tabela_csv(
        "Transferência", "Para onde vão, no 2º turno, os eleitores de cada candidato do 1º turno, segundo as "
                         "pesquisas que publicaram o cruzamento (votos totais).",
        "dados/pbi/transferencia.csv",
        [col("instituto", "Instituto", descricao="Instituto."),
         col("divulgacao", "Divulgação", tipo="date", descricao="Data de divulgação."),
         col("campo_inicio", "Campo início", tipo="date", descricao="Início do campo.", oculta=True),
         col("campo_fim", "Campo fim", tipo="date", descricao="Fim do campo.", oculta=True),
         col("registro_tse", "Registro", descricao="Registro no TSE.", oculta=True),
         col("segmento_1turno", "Segmento", descricao="Voto declarado no 1º turno (Cury, Renan, Caiado, …)."),
         col("n_segmento", "N", tipo="number", descricao="Entrevistas no segmento (quando publicado).", oculta=True,
             formato="#,0"),
         col("lula", "Lula", tipo="number", descricao="% que vai para Lula.", oculta=True, formato="0.0"),
         col("flavio", "Flavio", tipo="number", descricao="% que vai para Flávio.", oculta=True, formato="0.0"),
         col("branco_nulo_nao_vota", "BrancoNulo", tipo="number", descricao="% branco, nulo ou não vota.",
             oculta=True, formato="0.0"),
         col("nao_sabe", "NaoSabe", tipo="number", descricao="% não sabe.", oculta=True, formato="0.0"),
         col("base", "Base", descricao="Base do percentual (totais).", oculta=True),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Rejeição", "Rejeição de cada candidato por instituto e data (a pergunta muda entre institutos: não forma "
                    "série única).",
        "dados/pbi/rejeicao.csv",
        [col("instituto", "Instituto", descricao="Instituto."),
         col("divulgacao", "Divulgação", tipo="date", descricao="Data de divulgação."),
         col("candidato", "Candidato", descricao="Candidato."),
         col("rejeicao", "Rejeicao", tipo="number", descricao="% de rejeição.", oculta=True, formato="0.0"),
         col("segmento", "Segmento", descricao="Segmento (total ou recorte).", oculta=True),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Apoio", "Apoios declarados no 2º turno: candidatos derrotados, partidos e governadores, com data e citação.",
        "dados/pbi/apoio.csv",
        [col("quem", "Quem", descricao="Pessoa ou partido."),
         col("cargo_ou_partido", "Cargo", descricao="Cargo ou partido."),
         col("posicao", "Posição", descricao="Lula, Flávio, neutro, liberou…"),
         col("data", "Data", tipo="date", descricao="Data do anúncio."),
         col("citacao_curta", "Citação", descricao="Citação curta."),
         FONTE, OBS],
        oculta=True),
    tabela_csv(
        "Local Contagem", "Os locais de votação de Contagem (MG) em 2018, 2022 e 2026: votos do PT e do principal "
                          "adversário, válidos, seções, bairro, coordenadas e posição no mapa da tela da escola.",
        "dados/pbi/local_contagem.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", formato="0"),
         col("NR_ZONA", "Zona", tipo="int", descricao="Zona eleitoral.", formato="0"),
         col("NR_LOCAL_VOTACAO", "Local", tipo="int", descricao="Número do local de votação.", formato="0"),
         col("NM_LOCAL_VOTACAO", "Nome do local", descricao="Nome do local como o TSE escreve no ano."),
         col("DS_LOCAL_VOTACAO_ENDERECO", "Endereço", descricao="Endereço.", oculta=True),
         col("pt", "VotosPT", tipo="int", descricao="Votos do candidato do PT.", oculta=True),
         col("adv", "VotosAdversario", tipo="int", descricao="Votos do principal adversário.", oculta=True),
         col("validos", "Validos", tipo="int", descricao="Votos válidos.", oculta=True),
         col("secoes", "Seções", tipo="int", descricao="Seções no local.", oculta=True),
         col("nome_2022", "Escola", descricao="Nome do local em 2022 (chave visível entre os anos)."),
         col("bairro", "Bairro", descricao="Bairro."),
         col("lat", "Latitude", tipo="number", descricao="Latitude.", oculta=True, formato="0.00000",
             categoria="Latitude"),
         col("lon", "Longitude", tipo="number", descricao="Longitude.", oculta=True, formato="0.00000",
             categoria="Longitude"),
         col("eleitores_2022", "Eleitores 2022", tipo="number", descricao="Eleitores do local em 2022.",
             oculta=True, formato="#,0"),
         col("px", "PX", tipo="number", descricao="Posição horizontal no mapa da tela (% da largura).", oculta=True,
             formato="0.00"),
         col("py", "PY", tipo="number", descricao="Posição vertical no mapa da tela (% da altura).", oculta=True,
             formato="0.00")],
        oculta=True),
]

RELACOES = [
    ("Trends UF", "UF", "UF", "UF"),
    # o estado clicado nos cartões da T08 (filtro cruzado em UF[UF]) chega à curva diária do estado
    ("Trends UF tempo", "UF", "UF", "UF"),
]
