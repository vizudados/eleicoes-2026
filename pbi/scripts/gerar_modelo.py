"""Gera o modelo semântico do painel Eleições 2026 (pbi/pbip/Eleicoes.SemanticModel, TMDL) a partir das declarações.

- Tabelas, parâmetros e relações: módulos pbi/modelo/*.py (cada um define TABELAS e, se quiser, RELACOES e EXPRESSOES).
  As tabelas de dados leem os CSV de dados/pbi (pipeline/exportar_pbi.py) e da apuração (apuracao/coletar.py) pelo
  endereço raw do repositório público vizudados/eleicoes-2026; nada lê disco local.
- Medidas: pbi/dax/**/*.dax, um arquivo por medida (formato de dax_para_tmdl.py), gravadas em _Medidas.tmdl.

    python -I -X utf8 pbi/scripts/gerar_modelo.py             grava (só o que mudou)
    python -I -X utf8 pbi/scripts/gerar_modelo.py --conferir  diz o que mudaria (0 mudam = idempotente)

Identificadores (lineageTag, logicalId) saem de uuid5 sobre o nome do objeto: a mesma declaração gera os mesmos bytes.
Rode com o Desktop FECHADO neste projeto (o Desktop sobrescreve o TMDL quando salva).
"""

import argparse
import importlib.util
import json
import sys
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax_para_tmdl  # noqa: E402

PBI = AQUI.parent
RAIZ = PBI.parent
MODELO = PBI / "pbip" / "Eleicoes.SemanticModel"
DECLARACOES = PBI / "modelo"
DAX = PBI / "dax"
ESPACO = uuid.UUID("5b0c7e2a-1f0d-4f53-9a51-2c3b8e6d2026")

TIPO_TMDL = {"text": "string", "int": "int64", "number": "double", "date": "dateTime", "datetime": "dateTime",
             "bool": "boolean"}
TIPO_M = {"text": "type text", "int": "Int64.Type", "number": "type number", "date": "type date",
          "datetime": "type datetime", "bool": "type logical"}
FORMATO = {"int": "#,0", "number": "#,0.00", "date": "dd/MM/yyyy", "datetime": "dd/MM/yyyy HH:mm"}


def tag(*partes):
    return str(uuid.uuid5(ESPACO, "|".join(partes)))


def q(nome):
    return nome if nome.isidentifier() and nome.isascii() else "'" + nome.replace("'", "''") + "'"


def recuo(texto, n):
    return "\n".join(("\t" * n + linha) if linha.strip() else "" for linha in texto.strip("\n").splitlines())


def doc(texto, n=0):
    return "\t" * n + "/// " + " ".join(str(texto).split())


# ---------------------------------------------------------------------------------------------------------------------
# Ajudantes para as declarações (importados pelos módulos de pbi/modelo)
# ---------------------------------------------------------------------------------------------------------------------

def col(origem, nome=None, tipo="text", descricao="", oculta=False, formato=None, ordenar_por=None, agregar="none",
        categoria=None):
    """Coluna de tabela CSV: `origem` é o cabeçalho no CSV; `nome` o nome no modelo (padrão: o mesmo)."""
    if not (nome or origem):
        raise SystemExit("coluna sem nome")
    return {"origem": origem, "nome": nome or origem, "tipo": tipo, "descricao": descricao or (nome or origem),
            "oculta": oculta, "formato": formato, "ordenar_por": ordenar_por, "agregar": agregar,
            "categoria": categoria}


def m_csv(arquivo, colunas, separador=",", horas=(), filtro=None, passos=""):
    """Power Query de um CSV do repositório (RelativePath sob pRepositorioRaw), com tipos en-US e nomes do modelo.
    `horas` = colunas de texto dd/MM/aaaa HH:mm:ss convertidas por fxHora; `filtro` = expressão each; `passos` = M
    extra que recebe a tabela no passo Nomes e devolve em Final."""
    fontes = [c for c in colunas if c["origem"]]          # origem None = coluna derivada nos `passos`
    tipos = ", ".join(f'{{"{c["origem"]}", {TIPO_M["text" if c["nome"] in horas else c["tipo"]]}}}' for c in fontes)
    nomes = ", ".join(f'{{"{c["origem"]}", "{c["nome"]}"}}' for c in fontes if c["origem"] != c["nome"])
    manter = ", ".join(f'"{c["origem"]}"' for c in fontes)
    linhas = [
        "let",
        f'    Fonte = fxCsv("{arquivo}", "{separador}"),',
        f"    Colunas = Table.SelectColumns(Fonte, {{{manter}}}, MissingField.UseNull),",
        f'    Tipos = Table.TransformColumnTypes(Colunas, {{{tipos}}}, "en-US"),',
        f"    Nomes = Table.RenameColumns(Tipos, {{{nomes}}}),",
    ]
    ultimo = "Nomes"
    if horas:
        conv = ", ".join(f'{{"{h}", fxHora, type nullable datetime}}' for h in horas)
        linhas.append(f"    Horas = Table.TransformColumns({ultimo}, {{{conv}}}),")
        ultimo = "Horas"
    if filtro:
        linhas.append(f"    Filtro = Table.SelectRows({ultimo}, each {filtro}),")
        ultimo = "Filtro"
    if passos:
        linhas.append(passos.replace("{entrada}", ultimo).rstrip().rstrip(",") + ",")
        ultimo = "Final"
    linhas[-1] = linhas[-1].rstrip(",")
    linhas += ["in", f"    {ultimo}"]
    return "\n".join(linhas)


def tabela(nome, descricao, colunas, m, oculta=False):
    return {"nome": nome, "descricao": descricao, "colunas": colunas, "m": m, "oculta": oculta}


def tabela_csv(nome, descricao, arquivo, colunas, oculta=False, **kw):
    return tabela(nome, descricao, colunas, m_csv(arquivo, colunas, **kw), oculta)


# ---------------------------------------------------------------------------------------------------------------------
# Parâmetros e funções comuns
# ---------------------------------------------------------------------------------------------------------------------

PARAMETROS = [
    ("pRepositorioRaw", "https://raw.githubusercontent.com/vizudados/eleicoes-2026/main", None,
     "Endereço raw do repositório público vizudados/eleicoes-2026 (branch main): todos os dados do painel e os "
     "arquivos que o coletor da apuração grava a cada coleta."),
    ("pPastaApuracao", "dados/apuracao", ["dados/apuracao", "dados/apuracao/ensaio-1turno"],
     "Pasta da apuração no repositório: dados/apuracao é o 2º turno ao vivo; dados/apuracao/ensaio-1turno é o 1º "
     "turno encerrado, que serve para conferir as contas contra o resultado oficial."),
]

FUNCOES = [
    ("fxCsv",
     "Lê um CSV do repositório (caminho relativo a pRepositorioRaw) e promove o cabeçalho. A apuração passa um "
     "carimbo na consulta para furar o cache de 5 minutos do raw do GitHub; os demais arquivos mudam pouco.",
     """
(caminho as text, optional separador as nullable text) as table =>
    let
        Ao_vivo = Text.StartsWith(caminho, "dados/apuracao"),
        Opcoes = if Ao_vivo
            then [RelativePath = caminho,
                  Query = [t = DateTimeZone.ToText(DateTimeZone.UtcNow(), [Format = "yyyyMMddHHmmss", Culture = "en-US"])]]
            else [RelativePath = caminho],
        Bruto = Csv.Document(Web.Contents(pRepositorioRaw, Opcoes),
            [Delimiter = if separador = null then "," else separador, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
        Cabecalho = Table.PromoteHeaders(Bruto, [PromoteAllScalars = true])
    in
        Cabecalho
"""),
    ("fxJson",
     "Lê um JSON do repositório (caminho relativo a pRepositorioRaw), com carimbo para furar o cache do raw.",
     """
(caminho as text) as any =>
    Json.Document(Web.Contents(pRepositorioRaw, [RelativePath = caminho,
        Query = [t = DateTimeZone.ToText(DateTimeZone.UtcNow(), [Format = "yyyyMMddHHmmss", Culture = "en-US"])]]))
"""),
    ("fxHora",
     "Converte a hora que o TSE e o coletor escrevem (dd/MM/aaaa HH:mm:ss, horário de Brasília) em data e hora; vazio "
     "vira nulo (antes da primeira divulgação).",
     """
(texto as nullable text) as nullable datetime =>
    if texto = null or texto = "" then null
    else DateTime.FromText(texto, [Format = "dd/MM/yyyy HH:mm:ss", Culture = "pt-BR"])
"""),
]


# ---------------------------------------------------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------------------------------------------------

def carregar_declaracoes():
    tabelas, relacoes, expressoes = [], [], []
    for arq in sorted(DECLARACOES.glob("*.py")):
        if arq.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"modelo_{arq.stem}", arq)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tabelas += getattr(mod, "TABELAS", [])
        relacoes += getattr(mod, "RELACOES", [])
        expressoes += getattr(mod, "EXPRESSOES", [])
    nomes = [t["nome"] for t in tabelas]
    repetidas = {n for n in nomes if nomes.count(n) > 1}
    if repetidas:
        raise SystemExit(f"tabela declarada mais de uma vez: {sorted(repetidas)}")
    return tabelas, relacoes, expressoes


def tmdl_tabela(t):
    nome = t["nome"]
    linhas = [doc(t["descricao"]), f"table {q(nome)}"]
    if t.get("oculta"):
        linhas.append("\tisHidden")
    linhas += [f"\tlineageTag: {tag('tabela', nome)}", ""]
    for c in t["colunas"]:
        linhas.append(doc(c["descricao"], 1))
        linhas.append(f"\tcolumn {q(c['nome'])}")
        linhas.append(f"\t\tdataType: {TIPO_TMDL[c['tipo']]}")
        if c["oculta"]:
            linhas.append("\t\tisHidden")
        formato = c["formato"] if c["formato"] is not None else FORMATO.get(c["tipo"])
        if formato:
            linhas.append(f"\t\tformatString: {formato}")
        linhas.append(f"\t\tlineageTag: {tag('coluna', nome, c['nome'])}")
        if c.get("categoria"):
            linhas.append(f"\t\tdataCategory: {c['categoria']}")
        linhas.append(f"\t\tsummarizeBy: {c['agregar']}")
        linhas.append(f"\t\tsourceColumn: {c['nome']}")
        if c["ordenar_por"]:
            linhas.append(f"\t\tsortByColumn: {q(c['ordenar_por'])}")
        linhas += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    linhas += [f"\tpartition {q(nome)} = m", "\t\tmode: import", "\t\tsource =", recuo(t["m"], 4), "",
               "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(linhas)


def tmdl_expressoes(extras):
    linhas = []
    for nome, valor, lista, descricao in PARAMETROS:
        meta = "IsParameterQuery = true, "
        if lista:
            meta += "List = {" + ", ".join(f'"{v}"' for v in lista) + f'}}, DefaultValue = "{valor}", '
        meta += 'Type = "Text", IsParameterQueryRequired = true'
        linhas += [doc(descricao), f'expression {nome} = "{valor}" meta [{meta}]',
                   f"\tlineageTag: {tag('expressao', nome)}", "", "\tannotation PBI_ResultType = Text", ""]
    for nome, descricao, corpo in FUNCOES:
        linhas += [doc(descricao), f"expression {nome} =", recuo(corpo, 2), f"\tlineageTag: {tag('expressao', nome)}",
                   "", "\tannotation PBI_ResultType = Function", ""]
    for nome, descricao, corpo, tipo in extras:
        linhas += [doc(descricao), f"expression {nome} =", recuo(corpo, 2), f"\tlineageTag: {tag('expressao', nome)}",
                   "", f"\tannotation PBI_ResultType = {tipo}", ""]
    return "\n".join(linhas)


def tmdl_modelo(tabelas, extras):
    ordem = ([p[0] for p in PARAMETROS] + [f[0] for f in FUNCOES] + [e[0] for e in extras]
             + [t["nome"] for t in tabelas])
    linhas = [doc("Eleições 2026 · o que os números dizem (Vizu Dados). Dados lidos do repositório público "
                  "vizudados/eleicoes-2026 no GitHub (dados/pbi e dados/apuracao). Gerado por "
                  "pbi/scripts/gerar_modelo.py; medidas em pbi/dax."),
              "model Model", "\tculture: pt-BR", "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
              "\tdiscourageImplicitMeasures", "\tsourceQueryCulture: pt-BR", "\tvalueFilterBehavior: independent",
              "\tdataAccessOptions", "\t\tfastCombine", "\t\tlegacyRedirects", "",
              "annotation __PBI_TimeIntelligenceEnabled = 0", "",
              "annotation PBI_QueryOrder = " + json.dumps(ordem, ensure_ascii=False, separators=(",", ":")), "",
              'annotation PBI_ProTooling = ["DevMode"]', ""]
    linhas += [f"ref table {q(t['nome'])}" for t in tabelas] + ["ref table _Medidas", "", "ref cultureInfo pt-BR", ""]
    return "\n".join(linhas)


def tmdl_relacoes(relacoes, tabelas):
    cols = {(t["nome"], c["nome"]) for t in tabelas for c in t["colunas"]}
    linhas = []
    for r in relacoes:
        de_t, de_c, para_t, para_c = r[:4]
        opcoes = r[4] if len(r) > 4 else {}
        for par in ((de_t, de_c), (para_t, para_c)):
            if par not in cols:
                raise SystemExit(f"relação com coluna inexistente: {par}")
        linhas.append(f"relationship {tag('relacao', de_t, de_c, para_t, para_c)}")
        if opcoes.get("ambas"):
            linhas.append("\tcrossFilteringBehavior: bothDirections")
        if opcoes.get("inativa"):
            linhas.append("\tisActive: false")
        linhas += [f"\tfromColumn: {q(de_t)}.{q(de_c)}", f"\ttoColumn: {q(para_t)}.{q(para_c)}", ""]
    return "\n".join(linhas)


def platform(tipo, nome):
    return {"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": tipo, "displayName": nome},
            "config": {"version": "2.0", "logicalId": tag("logico", tipo, nome)}}


def texto_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def todos_os_arquivos():
    tabelas, relacoes, extras = carregar_declaracoes()
    arqs = {}
    arqs[MODELO / "definition.pbism"] = texto_json({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}})
    arqs[MODELO / ".platform"] = texto_json(platform("SemanticModel", "Eleições 2026"))
    d = MODELO / "definition"
    arqs[d / "database.tmdl"] = "database\n\tcompatibilityLevel: 1606\n\n"
    arqs[d / "model.tmdl"] = tmdl_modelo(tabelas, extras)
    arqs[d / "expressions.tmdl"] = tmdl_expressoes(extras)
    arqs[d / "relationships.tmdl"] = tmdl_relacoes(relacoes, tabelas)
    arqs[d / "cultures" / "pt-BR.tmdl"] = "cultureInfo pt-BR\n\n"
    for t in tabelas:
        arqs[d / "tables" / f"{t['nome']}.tmdl"] = tmdl_tabela(t)
    medidas = dax_para_tmdl.coletar(DAX)
    arqs[d / "tables" / "_Medidas.tmdl"] = dax_para_tmdl.gerar(
        medidas, "_Medidas", "eleicoes-2026", "Medidas do painel: contas (todo número que o leitor vê) e desenho "
        "(HTML, ALT, specs). Gerada a partir de pbi/dax/**/*.dax por pbi/scripts/gerar_modelo.py; não edite à mão.")
    return arqs, len(tabelas), len(medidas)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--conferir", action="store_true")
    args = a.parse_args()
    arqs, n_tab, n_med = todos_os_arquivos()
    mudam = [p for p, txt in arqs.items() if not p.exists() or p.read_text(encoding="utf-8") != txt]
    atuais = {p for p in (MODELO / "definition").rglob("*") if p.is_file()} if (MODELO / "definition").exists() else set()
    sobram = sorted(atuais - set(arqs))
    for p in mudam:
        print(("muda  " if p.exists() else "novo  ") + str(p.relative_to(PBI)))
    for p in sobram:
        print("sobra " + str(p.relative_to(PBI)))
    if args.conferir:
        print(f"{n_tab} tabelas · {n_med} medidas · {len(mudam)} mudam · {len(sobram)} sobram")
        return 0
    for p, txt in arqs.items():
        if p in mudam:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(txt)
    for p in sobram:
        p.unlink()
    print(f"{n_tab} tabelas · {n_med} medidas · gravados {len(mudam)} · removidos {len(sobram)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
