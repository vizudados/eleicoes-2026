// Apuração ao vivo — lê os arquivos que o GitHub Actions grava em dados/apuracao/ (apuracao/coletar.py).
// Parâmetro pRepositorioRaw = "https://raw.githubusercontent.com/vizudados/eleicoes-2026/main" (repositório público).
// O raw do GitHub tem cache de ~5 min; o parâmetro de carimbo evita cache do lado do Power BI.
// Três consultas: ApuracaoUF (uma linha por UF + BR), ApuracaoHistorico (curva da noite) e ApuracaoStatus.

// ApuracaoUF
let
    Fonte = Csv.Document(
        Web.Contents(pRepositorioRaw, [RelativePath = "dados/apuracao/ufs.csv",
                                       Query = [t = Text.From(DateTime.LocalNow())]]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"uf", type text}, {"atualizado_tse", type text}, {"secoes_pct", type number},
        {"eleitorado", Int64.Type}, {"comparecimento", Int64.Type}, {"abstencao", Int64.Type},
        {"abstencao_pct", type number}, {"brancos", Int64.Type}, {"nulos", Int64.Type}, {"validos", Int64.Type},
        {"lula_votos", Int64.Type}, {"lula_pct", type number}, {"flavio_votos", Int64.Type},
        {"flavio_pct", type number}, {"lider", type text}, {"diferenca_votos", Int64.Type}}, "en-US")
in
    Tipos

// ApuracaoHistorico
// let
//     Fonte = Csv.Document(Web.Contents(pRepositorioRaw, [RelativePath = "dados/apuracao/historico.csv",
//                          Query = [t = Text.From(DateTime.LocalNow())]]), [Delimiter = ",", Encoding = 65001]),
//     Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
//     Tipos = Table.TransformColumnTypes(Cabecalho, {{"secoes_pct", type number}, {"lula_pct", type number},
//              {"flavio_pct", type number}, {"lula_votos", Int64.Type}, {"flavio_votos", Int64.Type}}, "en-US")
// in
//     Tipos

// ApuracaoStatus
// let
//     Json = Json.Document(Web.Contents(pRepositorioRaw, [RelativePath = "dados/apuracao/ultimo.json",
//                          Query = [t = Text.From(DateTime.LocalNow())]])),
//     Linha = #table({"status", "atualizado_tse", "coletado_em", "turno"},
//                    {{Json[status], Json[atualizado_tse], Json[coletado_em], Json[turno]}})
// in
//     Linha
