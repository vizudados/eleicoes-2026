"""Escreve dados/bruto/trajetoria/desenhos.csv: crédito e licença de cada desenho em traço feito a partir de foto real
e de cada ILUSTRAÇÃO RECRIADA (marco sem foto de licença aberta: a cena da época desenhada sem copiar foto nenhuma).

Os desenhos (comícios e marcos da linha do tempo) são obra derivada das fotos. Os derivados de fotos CC BY-SA 4.0
TÊM de sair sob CC BY-SA 4.0; para tratar os dois candidatos igual, todos os desenhos saem sob CC BY-SA 4.0
(permitido também para os derivados de CC BY e de domínio público), sempre com o crédito da foto.

Autor, licença e endereço da foto vêm de dados/bruto/trajetoria/trajetoria.json; a legenda traz a data e o local
reais da FOTO (que às vezes não é o dia do marco: ver FONTES.md). Coluna `tipo`: "foto" (desenho a partir de foto real)
ou "ilustração" (chave `ilustracao` do JSON; foto_original/autor/licenca_foto são os da foto usada SÓ para o rosto).

Uso: python -I -X utf8 pipeline/creditos_desenhos.py
"""
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados" / "bruto" / "trajetoria"
LICENCA_DESENHO = "CC BY-SA 4.0"

# Autor e licença curtos (para o crédito de até 90 caracteres), por foto.
CURTO = {
    "lula-1986-constituinte": ("Senado Federal/Agência Senado", "CC BY 2.0"),
    "lula-2002-posse": ("Marcello Casal Jr./Agência Brasil", "CC BY 3.0 BR"),
    "lula-2006-reeleicao": ("Marcello Casal Jr./Agência Brasil", "CC BY 3.0 BR"),
    "lula-2018-prisao": ("Ricardo Stuckert/Lula Oficial", "CC BY-SA 4.0"),
    "lula-2021-anulacao": ("Ricardo Stuckert/Lula Oficial", "CC BY-SA 4.0"),
    "lula-2022-eleicao": ("Ricardo Stuckert/Lula Oficial", "CC BY-SA 4.0"),
    "lula-2026-primeiro-turno": ("Ricardo Stuckert/Lula Oficial", "CC BY-SA 4.0"),
    "flavio-2002-alerj": ("Governo do Estado do RJ/Seap", "CC BY 2.0 BR"),
    "flavio-2016-prefeitura": ("Família Bolsonaro/Flickr", "domínio público"),
    "flavio-2018-senado": ("Consulado dos EUA no Rio", "domínio público"),
    "flavio-2019-posse": ("Edilson Rodrigues/Agência Senado", "CC BY 2.0"),
    "flavio-2020-denuncia": ("Pedro França/Agência Senado", "CC BY 2.0"),
    "flavio-2022-arquivamento": ("Edilson Rodrigues/Agência Senado", "CC BY 2.0"),
    "flavio-2025-csp": ("Edilson Rodrigues/Agência Senado", "CC BY-SA 4.0"),
    "flavio-2025-precandidatura": ("Andressa Anholete/Agência Senado", "CC BY-SA 4.0"),
    "flavio-2026-primeiro-turno": ("Carlos Moura/Agência Senado", "CC BY-SA 4.0"),
    "lula-1989-presidencia": ("CEDI/Câmara dos Deputados", "CC BY 2.0"),
    "flavio-2022-campanha": ("Geraldo Magela/Agência Senado", "CC BY 2.0"),
    "lula-comicio-2026-2": ("Ricardo Stuckert/Lula Oficial", "CC BY-SA 4.0"),
    "flavio-comicio-2021-1": ("Isac Nóbrega/PR", "CC BY 2.0"),
}

# Data e local reais da foto (da descrição no trajetoria.json / FONTES.md).
LEGENDA = {
    "lula-1986-constituinte": "Assembleia Nacional Constituinte, Brasília, 1987–1988 (foto de arquivo)",
    "lula-2002-posse": "Posse no Palácio do Planalto, Brasília, 1º de janeiro de 2003",
    "lula-2006-reeleicao": "Depois de votar no 2º turno, São Bernardo do Campo (SP), 29 de outubro de 2006",
    "lula-2018-prisao": "Carregado por apoiadores, São Bernardo do Campo (SP), 7 de abril de 2018",
    "lula-2021-anulacao": "Encontro com movimentos sociais em Pernambuco, 16 de agosto de 2021",
    "lula-2022-eleicao": "Noite da eleição na Av. Paulista, São Paulo, 30 de outubro de 2022",
    "lula-2026-primeiro-turno": "Pronunciamento após o 1º turno, São Paulo, 4 de outubro de 2026",
    "flavio-2002-alerj": "Como deputado estadual do RJ, em formatura de grupamento da Seap, 17 de dezembro de 2014",
    "flavio-2016-prefeitura": "Como deputado estadual do RJ, 2015",
    "flavio-2018-senado": "Já eleito senador, Rio de Janeiro, 29 de novembro de 2018",
    "flavio-2019-posse": "Posse no plenário do Senado, Brasília, 1º de fevereiro de 2019",
    "flavio-2020-denuncia": "Entrevista no Senado, Brasília, 30 de novembro de 2021",
    "flavio-2022-arquivamento": "Entrevista no Senado, Brasília, 12 de maio de 2022",
    "flavio-2025-csp": "Reunião da Comissão de Segurança Pública do Senado, Brasília, 19 de agosto de 2025",
    "flavio-2025-precandidatura": "Comissão do Senado, Brasília, 3 de setembro de 2025",
    "flavio-2026-primeiro-turno": "Discurso no plenário do Senado, Brasília, 1º de setembro de 2026",
    "lula-1989-presidencia": "Homenagem do Diap a constituintes, Brasília, outubro de 1988",
    "flavio-2022-campanha": "Sabatina na Comissão de Relações Exteriores do Senado, Brasília, 22 de novembro de 2022",
    # ilustrações recriadas: a cena desenhada (não há foto)
    "lula-1975-sindicato": "Assembleia de metalúrgicos num estádio do ABC paulista, fim dos anos 1970 (cena recriada)",
    "lula-1980-fundacao-pt": "Fundação do PT no Colégio Sion, São Paulo, 10 de fevereiro de 1980 (cena recriada)",
    "lula-comicio-2026-2": "Ato na Av. Paulista, São Paulo, 11 de outubro de 2026",
    "flavio-comicio-2021-1": "Ato de 7 de Setembro de 2021, Av. Paulista, São Paulo",
}

VARIANTES_COMICIO = {"lula": ("tinta", "vermelho_escuro", "creme"), "flavio": ("tinta", "azul_escuro", "creme")}
FOTO_COMICIO = {"lula": "lula-comicio-2026-2", "flavio": "flavio-comicio-2021-1"}
CANDIDATO = {"lula": "Lula", "flavio": "Flávio Bolsonaro"}


# Ilustrações recriadas: o rosto vem de uma foto de outra ocasião (crédito obrigatório, CC BY), a cena não.
ROSTO = {
    "lula-1975-sindicato": ("CEDI/Câmara", "CC BY 2.0"),
    "lula-1980-fundacao-pt": ("CEDI/Câmara", "CC BY 2.0"),
}


def credito(nome):
    if nome in ROSTO:
        autor, licenca = ROSTO[nome]
        texto = f"Ilustração {LICENCA_DESENHO} recriada de registros da época; rosto: {autor} ({licenca})"
    else:
        autor, licenca = CURTO[nome]
        de = "do" if autor.startswith("Consulado") else "de"
        texto = f"Desenho {LICENCA_DESENHO} a partir de foto {de} {autor} ({licenca})"
    assert len(texto) <= 90, (nome, len(texto), texto)
    return texto


def linha(arquivo_web, quem, data, foto, nome, tipo="foto"):
    return {
        "arquivo_web": arquivo_web,
        "candidato": CANDIDATO[quem],
        "marco_data": data,
        "foto_original": foto["url_pagina"],
        "autor": foto["autor"],
        "licenca_foto": foto["licenca"],
        "licenca_desenho": f"{LICENCA_DESENHO} (https://creativecommons.org/licenses/by-sa/4.0/)",
        "credito_curto": credito(nome),
        "legenda": LEGENDA[nome],
        "tipo": tipo,
    }


def main():
    dados = json.loads((PASTA / "trajetoria.json").read_text(encoding="utf-8"))
    linhas = []
    for quem in ("lula", "flavio"):
        for marco in dados[quem]:
            foto, ilus = marco.get("foto"), marco.get("ilustracao")
            if foto:
                nome = foto["arquivo"].removesuffix(".jpg")
                linhas.append(linha(f"midia/trajetoria/{nome}.png", quem, marco["data"], foto, nome))
            elif ilus:
                nome = Path(ilus["arquivo"]).stem
                ref = ilus["referencia_rosto"]
                origem = {"url_pagina": ref["url_pagina"], "licenca": ref["licenca"],
                          "autor": f"{ilus['autor']}; rosto a partir de foto de {ref['autor']}"}
                linhas.append(linha(f"midia/trajetoria/{nome}.png", quem, marco["data"], origem, nome, "ilustração"))
    for quem in ("lula", "flavio"):
        nome = FOTO_COMICIO[quem]
        foto = next(f for f in dados["comicios"][quem] if f["arquivo"] == f"{nome}.jpg")
        for variante in VARIANTES_COMICIO[quem]:
            linhas.append(linha(f"midia/comicio/comicio-{quem}-{variante}.png", quem, foto["data"], foto, nome))
    destino = PASTA / "desenhos.csv"
    with destino.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0]), delimiter=";", lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{destino.relative_to(RAIZ)}: {len(linhas)} linhas")


if __name__ == "__main__":
    main()
