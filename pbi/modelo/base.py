"""Tabelas do resultado eleitoral: UF, Ano, Município, Município ano, Candidato ano, Candidato UF, Comparecimento ano e
Abstenção perfil. Fonte: dados/pbi (pipeline/exportar_pbi.py), lidos do repositório no GitHub."""

from gerar_modelo import col, tabela, tabela_csv

# Grade do mapa de quadrados (coluna, linha), igual à da tela 18 do Figma; ZZ (exterior) no canto de cima à direita.
GRADE = {"RR": (1, 0), "AP": (3, 0), "ZZ": (5, 0), "AM": (1, 1), "PA": (2, 1), "MA": (3, 1), "CE": (4, 1),
         "RN": (5, 1), "AC": (0, 2), "RO": (1, 2), "TO": (2, 2), "PI": (3, 2), "PE": (4, 2), "PB": (5, 2),
         "MT": (1, 3), "GO": (2, 3), "BA": (3, 3), "SE": (4, 3), "AL": (5, 3), "MS": (1, 4), "DF": (2, 4),
         "MG": (3, 4), "ES": (4, 4), "PR": (1, 5), "SP": (2, 5), "RJ": (3, 5), "SC": (1, 6), "RS": (1, 7)}
UFS = [("AC", "Acre", "Norte"), ("AL", "Alagoas", "Nordeste"), ("AM", "Amazonas", "Norte"), ("AP", "Amapá", "Norte"),
       ("BA", "Bahia", "Nordeste"), ("CE", "Ceará", "Nordeste"), ("DF", "Distrito Federal", "Centro-Oeste"),
       ("ES", "Espírito Santo", "Sudeste"), ("GO", "Goiás", "Centro-Oeste"), ("MA", "Maranhão", "Nordeste"),
       ("MG", "Minas Gerais", "Sudeste"), ("MS", "Mato Grosso do Sul", "Centro-Oeste"),
       ("MT", "Mato Grosso", "Centro-Oeste"), ("PA", "Pará", "Norte"), ("PB", "Paraíba", "Nordeste"),
       ("PE", "Pernambuco", "Nordeste"), ("PI", "Piauí", "Nordeste"), ("PR", "Paraná", "Sul"),
       ("RJ", "Rio de Janeiro", "Sudeste"), ("RN", "Rio Grande do Norte", "Nordeste"), ("RO", "Rondônia", "Norte"),
       ("RR", "Roraima", "Norte"), ("RS", "Rio Grande do Sul", "Sul"), ("SC", "Santa Catarina", "Sul"),
       ("SE", "Sergipe", "Nordeste"), ("SP", "São Paulo", "Sudeste"), ("TO", "Tocantins", "Norte")]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul", "Exterior"]
# O filtro de estado das telas (24/10/2026, regra L134 do dono: "se resolve a questão da hierarquia jogando o filtro no
# último na hierarquia"): Região › Estado num caminho só, o campo do VizuFilter em modo caminho; marcar a região marca os
# estados dela. O mesmo separador de general.pathSeparator em paginas/casca.py.
SEPARADOR_CAMINHO = " › "
# Artigo de cada UF para as frases do recorte ("na Bahia", "no Pará", "em Minas Gerais"; "da Bahia", "de Goiás"): "a",
# "o" ou "" (sem artigo). As regiões (e o exterior) levam "o": "no Nordeste", "no exterior".
ARTIGO = {"AC": "o", "AL": "", "AM": "o", "AP": "o", "BA": "a", "CE": "o", "DF": "o", "ES": "o", "GO": "", "MA": "o",
          "MG": "", "MS": "", "MT": "", "PA": "o", "PB": "a", "PE": "", "PI": "o", "PR": "o", "RJ": "o", "RN": "o",
          "RO": "", "RR": "", "RS": "o", "SC": "", "SE": "", "SP": "", "TO": "o", "ZZ": "o"}


def m_uf():
    linhas = sorted(UFS, key=lambda u: (REGIOES.index(u[2]), u[1])) + [("ZZ", "Exterior", "Exterior")]
    corpo = ",\n        ".join(
        f'{{"{s}", "{n}", "{r}", {REGIOES.index(r) + 1}, {i + 1}, "{"Exterior" if s == "ZZ" else "UF"}", '
        f'{GRADE[s][0]}, {GRADE[s][1]}, "{r if s == "ZZ" else r + SEPARADOR_CAMINHO + n}", "{ARTIGO[s]}"}}'
        for i, (s, n, r) in enumerate(linhas))
    return f"""let
    UFs = #table(
        type table [UF = text, Nome = text, Regiao = text, RegiaoOrdem = Int64.Type, Ordem = Int64.Type, Tipo = text,
                    GradeColuna = Int64.Type, GradeLinha = Int64.Type, Caminho = text, Artigo = text],
        {{
        {corpo}
        }}
    )
in
    UFs"""


# Quem foi o candidato do PT e o principal adversário (o mais votado fora do PT) em cada 1º turno.
ANOS = [(2006, "Lula", "Geraldo Alckmin", "PSDB"), (2010, "Dilma Rousseff", "José Serra", "PSDB"),
        (2014, "Dilma Rousseff", "Aécio Neves", "PSDB"), (2018, "Fernando Haddad", "Jair Bolsonaro", "PSL"),
        (2022, "Lula", "Jair Bolsonaro", "PL"), (2026, "Lula", "Flávio Bolsonaro", "PL")]


def m_ano():
    corpo = ",\n        ".join(f'{{{a}, "{a}", "{pt}", "{adv}", "{p}"}}' for a, pt, adv, p in ANOS)
    return f"""let
    Anos = #table(
        type table [Ano = Int64.Type, AnoTexto = text, CandidatoPT = text, Adversario = text, AdversarioPartido = text],
        {{
        {corpo}
        }}
    )
in
    Anos"""


TABELAS = [
    tabela("UF", "As 27 UFs e o exterior (ZZ): sigla, nome, região, ordem e a posição no mapa de quadrados. O filtro "
                 "de UF das telas filtra esta tabela; sem filtro, as contas mostram o Brasil.",
           [col("UF", descricao="Sigla da UF (ZZ = exterior).", ordenar_por="Ordem"),
            col("Nome", descricao="Nome da UF.", ordenar_por="Ordem"),
            col("Regiao", "Região", descricao="Norte, Nordeste, Centro-Oeste, Sudeste, Sul; Exterior.",
                ordenar_por="RegiaoOrdem"),
            col("RegiaoOrdem", tipo="int", descricao="Ordem das regiões, do Norte ao Sul.", oculta=True, formato="0"),
            col("Ordem", tipo="int", descricao="Ordem de exibição: região, depois o nome; o exterior por último.",
                oculta=True, formato="0"),
            col("Tipo", descricao="UF ou Exterior; as contagens de UFs só contam Tipo = UF.", oculta=True),
            col("GradeColuna", tipo="int", descricao="Coluna no mapa de quadrados (0 = Acre).", oculta=True,
                formato="0"),
            col("GradeLinha", tipo="int", descricao="Linha no mapa de quadrados (0 = Roraima, Amapá e exterior).",
                oculta=True, formato="0"),
            col("Caminho", descricao="Região › Estado ('Nordeste › Bahia'): o campo do filtro de estado das telas "
                "(VizuFilter em árvore, modo caminho). O filtro cai no estado; marcar a região marca os estados dela. "
                "O exterior fica fora do filtro.", ordenar_por="Ordem"),
            col("Artigo", descricao="Artigo da UF nas frases do recorte: 'a' (na Bahia), 'o' (no Pará) ou vazio (em "
                "Minas Gerais). Lido pelas medidas Recorte · em e Recorte · de.", oculta=True)],
           m_uf()),
    tabela("Ano", "As seis eleições presidenciais de 2006 a 2026 (1º turno), com o candidato do PT e o principal "
                  "adversário (o mais votado fora do PT) de cada uma.",
           [col("Ano", tipo="int", descricao="Ano da eleição.", formato="0"),
            col("AnoTexto", "Ano (texto)", descricao="Ano como texto, para eixo e rótulo.", ordenar_por="Ano"),
            col("CandidatoPT", "Candidato do PT", descricao="Candidato do PT no 1º turno."),
            col("Adversario", "Adversário", descricao="Mais votado fora do PT no 1º turno."),
            col("AdversarioPartido", "Partido do adversário", descricao="Partido do adversário.")],
           m_ano()),
    tabela_csv(
        "Município", "Os 5.571 municípios do IBGE com população e renda domiciliar per capita do Censo 2022, porte, "
                     "quinto de renda e o centro do município projetado no quadro 1000 × 1000 dos mapas do painel.",
        "dados/pbi/municipio.csv",
        [col("cd_ibge", "CodIBGE", descricao="Código IBGE de 7 dígitos (chave)."),
         col("cd_tse", "CodTSE", tipo="int", descricao="Código do município no TSE.", oculta=True, formato="0"),
         col("nome", "Município", descricao="Nome do município."),
         col("uf", "UF", descricao="Sigla da UF; liga com a dimensão UF.", oculta=True),
         col("regiao", "Região", descricao="Região do município.", oculta=True),
         col("rotulo", "Rótulo", descricao="Nome (UF), único: o que a busca e as listas mostram."),
         col("populacao", "População", tipo="int", descricao="População residente, Censo 2022.", agregar="sum"),
         col("renda_pc", "Renda per capita", tipo="number", descricao="Rendimento domiciliar per capita médio "
             "(R$/mês), Censo 2022.", formato="#,0"),
         col("porte", "Porte", descricao="Faixa de população (até 10 mil … mais de 1 milhão).",
             ordenar_por="PorteOrdem"),
         col("porte_ordem", "PorteOrdem", tipo="int", descricao="Ordem do porte.", oculta=True, formato="0"),
         col("quinto", "Quinto de renda", descricao="Quinto dos municípios pela renda per capita (cada quinto tem "
             "1.114 cidades).", ordenar_por="QuintoOrdem"),
         col("quinto_ordem", "QuintoOrdem", tipo="int", descricao="Ordem do quinto (1 = mais pobres).", oculta=True,
             formato="0"),
         col("lon", "Longitude", tipo="number", descricao="Longitude do centro do município.", oculta=True,
             formato="0.00000", categoria="Longitude"),
         col("lat", "Latitude", tipo="number", descricao="Latitude do centro do município.", oculta=True,
             formato="0.00000", categoria="Latitude"),
         col("x", "X", tipo="number", descricao="Centro projetado no quadro 1000 × 1000 dos mapas (x).", oculta=True,
             formato="0.00"),
         col("y", "Y", tipo="number", descricao="Centro projetado no quadro 1000 × 1000 dos mapas (y, para baixo).",
             oculta=True, formato="0.00")]),
    tabela_csv(
        "Município ano", "Município × eleição (1º turno, 2006–2026): votos do PT, do principal adversário e dos "
                         "demais, válidos, aptos, comparecimento, abstenção, brancos e nulos. Sem o exterior.",
        "dados/pbi/municipio_ano.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("cd_ibge", "CodIBGE", descricao="Código IBGE do município.", oculta=True),
         col("pt", "VotosPT", tipo="int", descricao="Votos do candidato do PT.", oculta=True),
         col("adv", "VotosAdversario", tipo="int", descricao="Votos do principal adversário (o mais votado fora do "
             "PT; em 2026, Flávio Bolsonaro).", oculta=True),
         col("demais", "VotosDemais", tipo="int", descricao="Votos dos demais candidatos.", oculta=True),
         col("validos", "Validos", tipo="int", descricao="Votos válidos.", oculta=True),
         col("aptos", "Aptos", tipo="int", descricao="Eleitores aptos.", oculta=True),
         col("comparecimento", "Comparecimento", tipo="int", descricao="Eleitores que votaram.", oculta=True),
         col("abstencoes", "Abstencoes", tipo="int", descricao="Eleitores que faltaram.", oculta=True),
         col("brancos", "Brancos", tipo="int", descricao="Votos em branco.", oculta=True),
         col("nulos", "Nulos", tipo="int", descricao="Votos nulos.", oculta=True)],
        oculta=True),
    tabela_csv(
        "Candidato ano", "Resultado nacional de cada candidato nos 1º turnos de 2006 a 2026 (com o exterior), como o "
                         "TSE totaliza.",
        "dados/pbi/candidato_ano.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("numero", "Número", tipo="int", descricao="Número do candidato.", formato="0"),
         col("nome", "Candidato", descricao="Nome de urna, abreviado."),
         col("partido", "Partido", descricao="Sigla do partido."),
         col("votos", "Votos", tipo="int", descricao="Votos no 1º turno.", oculta=True),
         col("validos", "ValidosAno", tipo="int", descricao="Votos válidos do ano (o mesmo em todas as linhas).",
             oculta=True),
         col("posicao", "Posição", tipo="int", descricao="Colocação no 1º turno.", formato="0")],
        oculta=True),
    tabela_csv(
        "Candidato UF", "Votos de cada candidato por UF (e exterior, ZZ) nos 1º turnos de 2022 e 2026.",
        "dados/pbi/candidato_uf.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("uf", "UF", descricao="Sigla da UF (ZZ = exterior).", oculta=True),
         col("numero", "Número", tipo="int", descricao="Número do candidato.", formato="0"),
         col("nome", "Candidato", descricao="Nome de urna, abreviado."),
         col("partido", "Partido", descricao="Sigla do partido."),
         col("votos", "Votos", tipo="int", descricao="Votos no 1º turno.", oculta=True)],
        oculta=True),
    tabela_csv(
        "Comparecimento ano", "Brasil × eleição: aptos, comparecimento, abstenção, brancos e nulos (1º turno, com o "
                              "exterior e voto em trânsito).",
        "dados/pbi/comparecimento_ano.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("aptos", "Aptos", tipo="int", descricao="Eleitores aptos.", oculta=True),
         col("comparecimento", "Comparecimento", tipo="int", descricao="Eleitores que votaram.", oculta=True),
         col("abstencoes", "Abstencoes", tipo="int", descricao="Eleitores que faltaram.", oculta=True),
         col("brancos", "Brancos", tipo="int", descricao="Votos em branco.", oculta=True),
         col("nulos", "Nulos", tipo="int", descricao="Votos nulos.", oculta=True)],
        oculta=True),
    tabela_csv(
        "Abstenção perfil", "Abstenção por perfil do eleitor (faixa etária, escolaridade, gênero…) no Brasil, "
                            "2014–2026, do perfil de comparecimento e abstenção do TSE.",
        "dados/pbi/abstencao_perfil.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("dimensao", "Dimensão", descricao="Recorte: faixa etária, escolaridade, gênero, estado civil…"),
         col("categoria", "Categoria", descricao="Categoria do recorte, como o TSE escreve."),
         col("aptos", "Aptos", tipo="int", descricao="Eleitores aptos na categoria.", oculta=True),
         col("comparecimento", "Comparecimento", tipo="int", descricao="Votaram.", oculta=True),
         col("abstencao", "Abstencao", tipo="int", descricao="Faltaram.", oculta=True)],
        oculta=True),
]

RELACOES = [
    ("Município", "UF", "UF", "UF"),
    ("Município ano", "CodIBGE", "Município", "CodIBGE"),
    ("Município ano", "Ano", "Ano", "Ano"),
    ("Candidato ano", "Ano", "Ano", "Ano"),
    ("Candidato UF", "UF", "UF", "UF"),
    ("Candidato UF", "Ano", "Ano", "Ano"),
    ("Comparecimento ano", "Ano", "Ano", "Ano"),
    ("Abstenção perfil", "Ano", "Ano", "Ano"),
]

# Brief P2: nacional com exterior; a medida escolhe explicitamente turno e abrangência.
TABELAS.append(tabela_csv(
    "Comparecimento turno", "Brasil por eleição, turno e abrangência, 2006–2026. Não somar as três abrangências: "
    "sem_exterior + exterior = com_exterior. Abstenções oficiais, sem derivar por subtração.",
    "dados/pbi/comparecimento_turno.csv",
    [col("ano", "Ano", tipo="int", formato="0", oculta=True),
     col("turno", "Turno", tipo="int", formato="0", oculta=True),
     col("abrangencia", "Abrangência", oculta=True),
     *[col(origem, nome, tipo="int", oculta=True) for origem, nome in
       [("aptos", "Aptos"), ("comparecimento", "Comparecimento"), ("abstencoes", "Abstencoes"),
        ("brancos", "Brancos"), ("nulos", "Nulos")]]], oculta=True))
RELACOES.append(("Comparecimento turno", "Ano", "Ano", "Ano"))
