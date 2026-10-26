"""roteiro — as 30 telas do painel, na ordem da história (docs/perguntas.md e o mockup do Figma, rodada 3).

Cada tela: código (nome da página no PBIR e prefixo de visuais e medidas), nome curto, pergunta (o título da tela, na
voz de quem assiste), ato, se é escura (capa e encerramento), o filtro que a tela tem (só onde muda a leitura, pedido
do Alisson em 23/10/2026) e a linha de fonte do rodapé.

O número que o leitor vê ("14 · Quem vota") é a posição na lista, não o código: a tela T24 (quem vota em quem, pedida
em 23/10/2026 como tela própria para não poluir a 13) entra depois da T13 e as seguintes andam uma casa, sem trocar os
códigos de páginas, visuais, medidas e marcadores que já existem. Do mesmo jeito, a T25 (quem falta e onde, o segundo
painel da ausência com filtro cruzado, pedido em 23/10/2026) entra logo depois da T06 e vira a 07. A T26 (o debate da
Globo de 23/10, o último do 2º turno, pedido no próprio dia: uma tela que fica pronta antes dos números e se preenche
pelo arquivo dados/pbi/debate_globo.csv) entra logo depois da T07, o debate da Band: as duas telas de debate ficam
coladas, com as abas "Debate Band" e "Debate Globo" (pedido do dono, 23/10/2026).

Ordem em cinco atos, do antes para o depois (23/10/2026, aprovada pelo dono: "remanejar a ordem dos painéis, para o
que foi pré primeiro turno, pós, e então os debates"): I · Antes da urna (quem são os dois e as pesquisas), II · O 1º
turno (o resultado), III · O mapa, IV · O 2º turno (os votos dos outros, as pesquisas, os dois debates colados, buscas,
redes e a apuração) e V · Explore você mesmo. Buscas e Redes vêm depois dos debates porque o filtro de período delas
é contado em volta dos dois. Ajuste do mesmo dia (pedido do dono: "o segundo turno deve ficar por último, pós
simulador e antes do encerramento"): o Explore você mesmo vira o ato IV e o 2º turno, o V, logo antes do encerramento.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tela:
    codigo: str
    nome: str
    pergunta: str
    ato: str
    escura: bool = False
    filtro: str | None = None          # None · "UF" · "Município" · "Zona" · "Período" (debates do 2º turno)
    fonte: str = "Fonte: TSE e IBGE · resultado de 22/10/2026"

    @property
    def numero(self) -> str:
        """Número da tela para o leitor: a posição no roteiro (00 = capa)."""
        return f"{TELAS.index(self):02d}"

    @property
    def titulo_pagina(self) -> str:
        return f"{self.numero} {self.nome}"


TELAS = [
    Tela("T00", "Capa", "A eleição de 2026, do primeiro ao segundo turno, município por município.", "Abertura", escura=True,
         fonte="Fonte: TSE e IBGE · 1º turno (04/10) e 2º turno (25/10/2026)"),
    # I · Antes da urna: quem são os dois e o que as pesquisas diziam
    Tela("T02", "Lula · quem é", "Quem é Luiz Inácio Lula da Silva?", "I · Antes da urna",
         fonte="Fontes: Presidência da República, Senado, TSE · fotos redesenhadas em traço (créditos no cartão)"),
    Tela("T04", "Flávio · quem é", "Quem é Flávio Bolsonaro?", "I · Antes da urna",
         fonte="Fontes: Senado, Alerj, TSE · fotos redesenhadas em traço (créditos no cartão)"),
    Tela("T10", "Pesquisas", "O que as pesquisas diziam antes da urna?", "I · Antes da urna",
         fonte="Fonte: pesquisas registradas no TSE (levantamento de 22/10/2026) e resultado do TSE"),
    # II · O 1º turno: o resultado
    # "Resultado", não "Placar" (pedido do dono, 24/10/2026: tirar "placar" do painel e dos vídeos)
    Tela("T01", "Resultado", "Quem venceu o 1º turno, e por quanto?", "II · O 1º turno", filtro="UF"),
    Tela("T03", "Votos de Lula", "Onde estão os votos de Lula?", "II · O 1º turno", filtro="UF"),
    Tela("T05", "Votos de Flávio", "Onde estão os votos de Flávio?", "II · O 1º turno", filtro="UF"),
    Tela("T06", "Ausência", "Quantos brasileiros não escolheram ninguém?", "II · O 1º turno", filtro="UF",
         fonte="Fonte: TSE · comparecimento, brancos e nulos do 1º turno, 2006 a 2026"),
    Tela("T25", "Quem falta", "Quem mais falta às urnas, e onde?", "II · O 1º turno", filtro="UF",
         fonte="Fonte: TSE · comparecimento por município (2006 a 2026) e perfil do eleitor por idade (2014 a 2026)"),
    # III · O mapa: onde e em quem o voto mudou
    Tela("T11", "Virada", "Onde os votos mudaram de lado?", "III · O mapa", filtro="UF"),
    Tela("T12", "Estados", "Como cada estado se moveu?", "III · O mapa"),
    Tela("T13", "Perfil", "Em que tipo de cidade Lula perdeu mais?", "III · O mapa", filtro="UF",
         fonte="Fontes: TSE e IBGE (Censo 2022: população e renda domiciliar per capita)"),
    Tela("T24", "Quem vota", "Quem vota em Lula e quem vota em Flávio?", "III · O mapa",
         fonte="Fontes: TSE (resultado e perfil do eleitorado), IBGE (Censo 2022), Portal da Transparência (Bolsa "
               "Família, ago/2026), Atlas do Desenvolvimento Humano (IDHM 2010) e Datafolha"),
    Tela("T14", "Série", "Como o PT chegou até aqui, de 2006 a 2026?", "III · O mapa", filtro="UF"),
    Tela("T15", "Minha cidade", "Como votou a minha cidade?", "III · O mapa", filtro="Município"),
    # IV · Explore você mesmo
    Tela("T19", "Explorador", "Onde está a minha pergunta? Explore os 5.571 municípios", "IV · Explore você mesmo"),
    # zona eleitoral, o nome oficial da Justiça Eleitoral, no lugar de escola (pedido do dono, 24/10/2026)
    Tela("T20", "Zona eleitoral", "Como votou cada zona eleitoral da cidade?", "IV · Explore você mesmo",
         filtro="Zona",
         fonte="Fontes: TSE (votação por seção, somada por zona eleitoral, e cadastro de locais de votação) e IBGE "
               "(malha municipal) · 27 capitais, as 6 maiores que viraram e Contagem (MG)"),
    Tela("T21", "20 anos", "Como o mapa mudou em 20 anos?", "IV · Explore você mesmo"),
    Tela("T22", "Simulador", "E se os eleitores dos outros candidatos tivessem escolhido diferente?", "IV · Explore você mesmo",
         fonte="Simulação a partir do 1º turno (TSE); não é previsão"),
    # V · O 2º turno: os votos dos outros, as pesquisas, os dois debates colados, buscas e redes, a apuração
    Tela("T16", "Os outros", "Em quem os eleitores dos outros candidatos diziam votar?", "V · O 2º turno",
         fonte="Fontes: pesquisas registradas no TSE que publicaram o cruzamento · imprensa (apoios)"),
    Tela("T17", "2º turno", "O que as pesquisas diziam, e o que a urna mostrou?", "V · O 2º turno", filtro="Período",
         fonte="Fontes: pesquisas registradas no TSE e relatórios dos institutos · TSE, resultado final de 25/10/2026"),
    Tela("T07", "Debate Band", "O que mudou depois do debate na Band?", "V · O 2º turno",
         fonte="Fontes: emissoras, Kantar Ibope (via imprensa) e pesquisas registradas no TSE"),
    Tela("T26", "Debate Globo", "O último debate mudou alguma coisa?", "V · O 2º turno",
         fonte="Fontes: TV Globo e imprensa (fatos do debate), Kantar IBOPE, Google Trends, Bites e pesquisas registradas "
               "no TSE · cada número com a hora em que chegou"),
    Tela("T08", "Buscas", "O que o Brasil perguntou ao Google?", "V · O 2º turno", filtro="Período",
         fonte="Fonte: Google Trends (índice relativo 0–100) · consultas de 22 a 24/10/2026"),
    Tela("T09", "Redes", "Quem dominou as redes?", "V · O 2º turno", filtro="Período",
         fonte="Fontes: Bites, Quaest, Social Blade, Datrix e Biblioteca de Anúncios da Meta"),
    Tela("T18", "Apuração", "Como foi a apuração do 2º turno?", "V · O 2º turno", filtro="UF",
         fonte="Fonte: TSE · API pública de divulgação dos resultados · totalização final de 25/10/2026, 23h26"),
    Tela("T27", "De onde vieram", "De onde vieram os votos que elegeram Lula?", "V · O 2º turno", filtro="UF",
         fonte="Fontes: TSE · 1º e 2º turnos de 2026, sem exterior · IBGE, Censo 2022"),
    Tela("T28", "Onde Flávio perdeu", "Onde Flávio perdeu a eleição?", "V · O 2º turno", filtro="UF",
         fonte="Fontes: TSE · 1º e 2º turnos de 2026 e 2º turno de 2022, sem exterior · IBGE, Censo 2022"),
    Tela("T29", "História do PT", "Como o voto no PT chegou ao recorde?", "V · O 2º turno",
         fonte="Fonte: TSE · eleições presidenciais de 1989 a 2026 (resultados por UF)"),
    Tela("T23", "Encerramento", "E o que fica desta eleição?", "Fim", escura=True,
         fonte="Vizu Dados · vizudados.com.br · dados e código em github.com/vizudados/eleicoes-2026"),
]
POR_CODIGO = {t.codigo: t for t in TELAS}


def numero(codigo: str) -> str:
    """Número que o leitor vê para o código de uma tela (ex.: numero("T18") == "19")."""
    return POR_CODIGO[codigo].numero


def anterior(t: Tela) -> Tela | None:
    i = TELAS.index(t)
    return TELAS[i - 1] if i > 0 else None


def proxima(t: Tela) -> Tela | None:
    i = TELAS.index(t)
    return TELAS[i + 1] if i + 1 < len(TELAS) else None
