"""Tabelas da tela 20 · Escola (dono: tela 20), em 34 cidades desde 23/10/2026 (as 27 capitais, as 6 maiores que
trocaram Lula por Flávio e Contagem; a tela abre no Rio de Janeiro). Leem dados/pbi/t20_locais.csv e
dados/pbi/t20_cidades.csv (pipeline/exportar_t20.py). As três ficam sem relação, de propósito:

- T20 Local: um local de votação de 2026 por linha (11.881), com os votos de 2026, 2022 e 2018 do mesmo local e a
  posição no mapa da própria cidade. Local é a chave (única no modelo inteiro, ordenada por Id: todo ALL ou RANKX sobre
  Local leva 'T20 Local'[Id], porque o Power BI põe a coluna de ordenação no grão); Nome é o que a tela mostra.
- T20 Cidade: uma linha por cidade com o que a tela lê por cidade (locais de 2022, a escola de exemplo, a moldura do
  mapa, o contorno simplificado e os rótulos de bairro).
- T20 Filtro: o filtro da tela, uma árvore só (VizuFilter em modo caminho; regra do dono de 23/10/2026: "se resolve a
  questão da hierarquia jogando o filtro no último na hierarquia"): uma linha por local, "Cidade e escola › Rio de
  Janeiro (RJ) › Escola Municipal Aleksander Henryks Laks". O filtro cai na escola (a folha): marcar a cidade (o nó)
  marca todas as escolas dela = a tela vai para a cidade; marcar uma escola = a cidade dela e a escola na ficha; uma
  cidade por vez (exclusiveRoots). As medidas leem a escolha ([T20 · cidade (código)], [T20 · escola do filtro],
  [T20 · escolas no filtro]); a cidade filtra os locais pela medida (o local fora da cidade devolve vazio), não por
  relação.
"""

from gerar_modelo import col, tabela, tabela_csv

SEPARADOR = " › "        # o mesmo de general.pathSeparator do VizuFilter (paginas/t20_escola.py)
RAIZ = "Cidade e zona"  # a raiz única da árvore (o mesmo nome vai em general.exclusiveRoots)


def _votos(sigla, ano, quem):
    return col(f"{sigla}_{ano}", f"{quem}{ano}", tipo="int", oculta=True,
               descricao=f"{'Votos do PT' if quem == 'VotosPT' else 'Votos do adversário principal' if quem == 'VotosAdv' else 'Votos válidos'} "
                         f"no local em {ano}" + ("" if ano == 2026 else " (soma das seções do mesmo zona + número; vazio "
                                                                    "quando o local não existia)") + ".")


# a chave Local só vem escrita no CSV quando difere do nome (nome repetido em outra cidade ganha " · Cidade (UF)")
_CHAVE = """    ComChave = Table.AddColumn({entrada}, "LocalChave",
        each if [Local] = null or [Local] = "" then [Nome] else [Local], type text),
    SemVazia = Table.RemoveColumns(ComChave, {"Local"}),
    Final = Table.RenameColumns(SemVazia, {{"LocalChave", "Local"}})"""


def _m_filtro() -> str:
    return f"""let
    LocFonte = fxCsv("dados/pbi/t20_locais.csv", ","),
    Loc = Table.TransformColumnTypes(
        Table.SelectColumns(LocFonte, {{"id", "cod_ibge", "nome", "ordem_nome"}}, MissingField.UseNull),
        {{{{"id", Int64.Type}}, {{"cod_ibge", type text}}, {{"nome", type text}}, {{"ordem_nome", Int64.Type}}}}, "en-US"),
    CidFonte = fxCsv("dados/pbi/t20_cidades.csv", ","),
    Cid = Table.TransformColumnTypes(
        Table.SelectColumns(CidFonte, {{"cod_ibge", "cidade", "ordem"}}, MissingField.UseNull),
        {{{{"cod_ibge", type text}}, {{"cidade", type text}}, {{"ordem", Int64.Type}}}}, "en-US"),
    // uma folha por local: a cidade é o nó do meio (Contagem primeiro, as outras em ordem alfabética) e as escolas,
    // em ordem alfabética dentro dela
    ComCidade = Table.Join(Loc, "cod_ibge", Table.RenameColumns(Cid, {{{{"cod_ibge", "cod_cidade"}}}}), "cod_cidade",
        JoinKind.Inner),
    Escolas = Table.FromRecords(List.Transform(Table.ToRecords(ComCidade), each [
        Caminho = "{RAIZ}{SEPARADOR}" & [cidade] & "{SEPARADOR}" & [nome], CodIBGE = [cod_ibge], IdLocal = [id],
        Ordem = [ordem] * 10000 + [ordem_nome]])),
    Final = Table.TransformColumnTypes(Escolas, {{{{"Caminho", type text}}, {{"CodIBGE", type text}},
        {{"IdLocal", Int64.Type}}, {{"Ordem", Int64.Type}}}})
in
    Final"""


TABELAS = [
    tabela_csv(
        "T20 Local", "Os locais de votação de 2026 das 34 cidades da tela 20 (as 27 capitais, as 6 maiores que trocaram "
                     "Lula por Flávio e Contagem), um por linha, com os votos de presidente (1º turno) de 2026, 2022 e "
                     "2018 do mesmo local (zona + número) e a posição no mapa da própria cidade. Nome legível no lugar "
                     "das maiúsculas do TSE.",
        "dados/pbi/t20_locais.csv",
        [col("id", "Id", tipo="int", descricao="Identificador do local (Contagem primeiro: 1…112).", oculta=True,
             formato="0"),
         col("cod_ibge", "CodIBGE", descricao="Código IBGE da cidade do local.", oculta=True),
         col("cidade", "Cidade", descricao="Cidade do local, com a UF: Contagem (MG)."),
         col("uf", "UF", descricao="Sigla da UF da cidade.", oculta=True),
         col("local", "Local", descricao="Chave do local, única no modelo inteiro: o nome; repetido em outra cidade, "
             "com a cidade junto. A tela mostra Nome.", ordenar_por="Id"),
         col("nome", "Nome", descricao="Nome legível do local (escola); único na cidade (repetido ganha o número)."),
         col("bairro", "Bairro", descricao="Bairro do local (cadastro do TSE de 2022)."),
         col("zona", "Zona", tipo="int", descricao="Zona eleitoral.", oculta=True, formato="0"),
         col("numero", "Número", tipo="int", descricao="Número do local na zona.", oculta=True, formato="0"),
         col("secoes", "Seções", tipo="int", descricao="Seções no local em 2026.", oculta=True),
         _votos("pt", 2026, "VotosPT"), _votos("adv", 2026, "VotosAdv"), _votos("validos", 2026, "Validos"),
         _votos("pt", 2022, "VotosPT"), _votos("adv", 2022, "VotosAdv"), _votos("validos", 2022, "Validos"),
         _votos("pt", 2018, "VotosPT"), _votos("adv", 2018, "VotosAdv"), _votos("validos", 2018, "Validos"),
         col("px", "PX", tipo="number", descricao="Posição horizontal no mapa da cidade (% da moldura); vazio fora "
             "do mapa.", oculta=True, formato="0.00"),
         col("py", "PY", tipo="number", descricao="Posição vertical no mapa da cidade (% da moldura); vazio fora do "
             "mapa.", oculta=True, formato="0.00"),
         col("fora_mapa", "Fora do mapa", descricao="Por que o local não aparece no mapa: 'sem endereço' (sem "
             "coordenada no cadastro do TSE) ou 'fora do recorte' (longe da mancha urbana, nas cidades em recorte); "
             "vazio no mapa.", oculta=True),
         col("pos_queda", "PosQueda", tipo="int", descricao="Posição do local na lista da cidade, da maior queda da "
             "margem de Lula 2022 → 2026 à maior alta (os locais novos no fim, por nome).", oculta=True, formato="0"),
         col("ordem_nome", "OrdemNome", tipo="int", descricao="Ordem alfabética do local na cidade (o filtro).",
             oculta=True, formato="0")],
        oculta=False, passos=_CHAVE),
    tabela_csv(
        "T20 Cidade", "As 34 cidades da tela 20, uma por linha: os locais de 2022 (os do próprio ano), a escola de "
                      "exemplo da ficha e o mapa (moldura, contorno da malha do IBGE simplificado, mapinha do recorte, "
                      "rótulos de bairro).",
        "dados/pbi/t20_cidades.csv",
        [col("cod_ibge", "CodIBGE", descricao="Código IBGE da cidade.", oculta=True),
         col("cod_tse", "CodTSE", descricao="Código do município no TSE.", oculta=True),
         col("uf", "UF", descricao="Sigla da UF.", oculta=True),
         col("nome", "Nome", descricao="Nome da cidade, sem a UF.", oculta=True),
         col("cidade", "Cidade", descricao="Nome da cidade com a UF: Contagem (MG).", ordenar_por="Ordem"),
         col("grupo", "Grupo", descricao="Por que a cidade está na tela: capital, virou (uma das 6 maiores que "
             "trocaram Lula por Flávio) ou início (Contagem).", oculta=True),
         col("ordem", "Ordem", tipo="int", descricao="Ordem no filtro: Contagem primeiro, as outras em ordem "
             "alfabética.", oculta=True, formato="0"),
         col("locais_2022", "Locais2022", tipo="int", descricao="Locais de votação da cidade em 2022, como o TSE os "
             "listou naquele ano.", oculta=True),
         col("lula_2022", "Lula2022", tipo="int", descricao="Locais de 2022 (os do próprio ano) em que Lula teve mais "
             "votos que Jair Bolsonaro.", oculta=True),
         col("id_exemplo", "IdExemplo", tipo="int", descricao="Id do local da ficha quando nada foi escolhido: a "
             "escola que virou com mais votos válidos (ou, sem nenhuma que virou, a de maior queda).", oculta=True,
             formato="0"),
         col("exemplo", "Exemplo", descricao="Por que o exemplo: virou ou queda.", oculta=True),
         col("recorte", "Recorte", tipo="int", descricao="1 quando o mapa mostra só a mancha urbana (cidade de "
             "território grande), com o mapinha da cidade inteira no canto.", oculta=True, formato="0"),
         col("espaco", "Espaço", tipo="number", descricao="Mediana da distância entre locais vizinhos no mapa, em % da "
             "largura da moldura (dá o tamanho dos pontos).", oculta=True, formato="0.00"),
         col("canto", "Canto", descricao="Canto do mapinha do recorte (so, se, no, ne).", oculta=True),
         col("bairros", "Bairros", descricao="Rótulos de bairro do mapa: NOME@x@y separados por |, em % da moldura.",
             oculta=True),
         col("moldura", "Moldura", descricao="O retângulo do recorte no mapinha: x y largura altura (0–100).",
             oculta=True),
         col("contorno", "Contorno", descricao="Caminho SVG do contorno da cidade em % da moldura (viewBox 0 0 100 "
             "100).", oculta=True),
         col("inteiro", "Inteiro", descricao="Caminho SVG da cidade inteira no mapinha (viewBox 0 0 100 100); vazio "
             "fora do recorte.", oculta=True)],
        oculta=False),
    tabela(
        "T20 Filtro", "O filtro da tela 20 (VizuFilter em árvore, um campo só): uma linha por local de votação, "
                      "Cidade e escola › Contagem (MG) › nome. O filtro cai na escola; marcar a cidade marca as "
                      "escolas dela. Sem relação: as medidas leem a escolha.",
        [col("Caminho", descricao="Cidade e escola › cidade › escola: o campo do VizuFilter em modo caminho.",
             ordenar_por="Ordem"),
         col("CodIBGE", descricao="Código IBGE da cidade do local.", oculta=True),
         col("IdLocal", tipo="int", descricao="Id do local (T20 Local[Id]).", oculta=True, formato="0"),
         col("Ordem", tipo="int", descricao="Ordem do caminho na árvore: as cidades na ordem do filtro (Contagem "
             "primeiro) e as escolas em ordem alfabética dentro da cidade.", oculta=True, formato="0")],
        _m_filtro(), renomeada=True),
]

# Desconectada, como as demais tabelas T20. As contas aplicam ano e a chave da zona.
TABELAS.append(tabela_csv(
    "T20 Zona turno", "Segundo turno observado nas 34 cidades: 319 zonas em 2018 e 2022 e 320 em 2026. "
    "2018 foi extraído do ZIP presidencial BR; zona ausente num ano permanece vazia. Posição cartográfica é a referência "
    "dos locais de 2026/1º turno, sem inferir endereço ou local de votação do 2º turno.",
    "dados/pbi/t20_zonas_turno.csv",
    [col("id", "IdLocal", tipo="int", oculta=True, formato="0"),
     col("cd_ibge", "CodIBGE", oculta=True), col("zona", "Zona", tipo="int", oculta=True, formato="0"),
     col("ano", "Ano", tipo="int", oculta=True, formato="0"),
     col("turno", "Turno", tipo="int", oculta=True, formato="0"),
     *[col(origem, nome, tipo="int", oculta=True) for origem, nome in
       [("pt", "VotosPT"), ("adv", "VotosAdv"), ("validos", "Validos"), ("secoes", "Seções"),
        ("locais", "Locais"), ("aptos", "Aptos"), ("comparecimento", "Comparecimento"),
        ("abstencoes", "Abstencoes"), ("brancos", "Brancos"), ("nulos", "Nulos")]]], oculta=True))
