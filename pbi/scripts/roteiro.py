"""roteiro — as 25 telas do painel, na ordem da história (docs/perguntas.md e o mockup do Figma, rodada 3).

Cada tela: código (nome da página no PBIR e prefixo de visuais e medidas), nome curto, pergunta (o título da tela, na
voz de quem assiste), ato, se é escura (capa e encerramento), o filtro que a tela tem (só onde muda a leitura, pedido
do Alisson em 23/10/2026) e a linha de fonte do rodapé.

O número que o leitor vê ("14 · Quem vota") é a posição na lista, não o código: a tela T24 (quem vota em quem, pedida
em 23/10/2026 como tela própria para não poluir a 13) entra depois da T13 e as seguintes andam uma casa, sem trocar os
códigos de páginas, visuais, medidas e marcadores que já existem.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tela:
    codigo: str
    nome: str
    pergunta: str
    ato: str
    escura: bool = False
    filtro: str | None = None          # None · "UF" · "Município" · "Local"
    fonte: str = "Fonte: TSE e IBGE · resultado de 22/10/2026"

    @property
    def numero(self) -> str:
        """Número da tela para o leitor: a posição no roteiro (00 = capa)."""
        return f"{TELAS.index(self):02d}"

    @property
    def titulo_pagina(self) -> str:
        return f"{self.numero} {self.nome}"


TELAS = [
    Tela("T00", "Capa", "Afinal, qual Brasil foi às urnas no 1º turno?", "Abertura", escura=True),
    Tela("T01", "Placar", "Quem venceu o 1º turno, e por quanto?", "I · O resultado", filtro="UF"),
    Tela("T02", "Lula · quem é", "Quem é Luiz Inácio Lula da Silva?", "I · O resultado",
         fonte="Fontes: Presidência da República, Senado, TSE · fotos redesenhadas em traço (créditos no cartão)"),
    Tela("T03", "Lula", "Onde estão os votos de Lula?", "I · O resultado", filtro="UF"),
    Tela("T04", "Flávio · quem é", "Quem é Flávio Bolsonaro?", "I · O resultado",
         fonte="Fontes: Senado, Alerj, TSE · fotos redesenhadas em traço (créditos no cartão)"),
    Tela("T05", "Flávio", "Onde estão os votos de Flávio?", "I · O resultado", filtro="UF"),
    Tela("T06", "Ausência", "Quantos brasileiros não escolheram ninguém?", "I · O resultado", filtro="UF",
         fonte="Fonte: TSE · comparecimento e perfil do eleitor, 2006 a 2026"),
    Tela("T07", "Debate", "O que mudou depois do debate na Band?", "II · A campanha",
         fonte="Fontes: emissoras, Kantar Ibope (via imprensa) e pesquisas registradas no TSE"),
    Tela("T08", "Buscas", "O que o Brasil perguntou ao Google?", "II · A campanha",
         fonte="Fonte: Google Trends (índice relativo 0–100) · consultas de 22/10/2026"),
    Tela("T09", "Redes", "Quem dominou as redes?", "II · A campanha",
         fonte="Fontes: Bites, Quaest, Social Blade, Datrix e Biblioteca de Anúncios da Meta"),
    Tela("T10", "Pesquisas", "O que as pesquisas diziam antes da urna?", "II · A campanha",
         fonte="Fonte: pesquisas registradas no TSE (levantamento de 22/10/2026) e resultado do TSE"),
    Tela("T11", "Virada", "Onde os votos mudaram de lado?", "III · O mapa", filtro="UF"),
    Tela("T12", "Estados", "Como cada estado se moveu?", "III · O mapa"),
    Tela("T13", "Perfil", "Em que tipo de cidade Lula perdeu mais?", "III · O mapa", filtro="UF",
         fonte="Fontes: TSE e IBGE (Censo 2022: população e renda domiciliar per capita)"),
    Tela("T24", "Quem vota", "Quem vota em Lula e quem vota em Flávio?", "III · O mapa",
         fonte="Fontes: TSE (resultado e perfil do eleitorado), IBGE (Censo 2022), Portal da Transparência (Bolsa "
               "Família, ago/2026), Atlas do Desenvolvimento Humano (IDHM 2010) e Datafolha"),
    Tela("T14", "Série", "Como o PT chegou até aqui, de 2006 a 2026?", "III · O mapa", filtro="UF"),
    Tela("T15", "Minha cidade", "Como votou a minha cidade?", "Epílogo", filtro="Município"),
    Tela("T16", "Os outros", "Para onde vão os votos dos outros candidatos?", "Epílogo",
         fonte="Fontes: pesquisas registradas no TSE que publicaram o cruzamento · imprensa (apoios)"),
    Tela("T17", "2º turno", "E agora, o que as pesquisas dizem do 2º turno?", "Epílogo",
         fonte="Fonte: pesquisas registradas no TSE e relatórios dos institutos (rejeição) · levantamento de 22/10/2026"),
    Tela("T18", "Apuração", "Quem está na frente na apuração do 2º turno?", "Epílogo", filtro="UF",
         fonte="Fonte: TSE · API pública de divulgação dos resultados, coletada a cada minuto"),
    Tela("T19", "Explorador", "Onde está a minha pergunta? Explore os 5.571 municípios", "IV · Explore você mesmo"),
    Tela("T20", "Escola", "Como votou cada escola de Contagem?", "IV · Explore você mesmo", filtro="Local",
         fonte="Fonte: TSE · votação por seção e locais de votação de Contagem (MG)"),
    Tela("T21", "20 anos", "Como o mapa mudou em 20 anos?", "IV · Explore você mesmo"),
    Tela("T22", "Simulador", "E se os eleitores dos outros candidatos escolherem?", "IV · Explore você mesmo",
         fonte="Simulação a partir do 1º turno (TSE); não é previsão"),
    Tela("T23", "Encerramento", "O que os números dizem, afinal?", "Fim", escura=True,
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
