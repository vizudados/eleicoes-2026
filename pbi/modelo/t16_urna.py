"""T16 · inferência nacional desconectada; não representa trajetórias individuais.

Publicar dados/pbi/t16_urna.csv antes de integrar. Descoberta automática pelo
gerador de modelo; nenhuma relação com UF, Município, Transferência ou Apoio.
"""
from gerar_modelo import col, tabela_csv

TABELAS = [tabela_csv(
    "T16 Urna",
    "Estimativas nacionais sem exterior. Grão: série × origem × destino × método. "
    "Fluxo em % da origem; Entre quem foi votar em % dos retornantes estimados, incluindo branco/nulo; "
    "Pesquisa em % do segmento entrevistado (faixa entre institutos, não IC); Diagnóstico na unidade do destino. "
    "Tabela intencionalmente desconectada. Fonte: pipeline/exportar_t16_urna.py.",
    "dados/pbi/t16_urna.csv",
    [col("serie", "Série"), col("origem", "Origem"), col("destino", "Destino"), col("metodo", "Método"),
     *[col(origem, nome, tipo="number", oculta=True, descricao=descricao) for origem, nome, descricao in [
         ("media", "Média", "Centro em pontos percentuais (0–100), ou valor do diagnóstico."),
         ("inferior", "Inferior", "Limite inferior do intervalo próprio do método; pesquisa: mínimo entre institutos."),
         ("superior", "Superior", "Limite superior do intervalo próprio do método; pesquisa: máximo entre institutos."),
         ("votos", "Votos", "Média de votos estimados; ausente para pesquisa/diagnóstico."),
         ("inferior_votos", "Votos inferior", "Quantil 2,5% dos votos estimados."),
         ("superior_votos", "Votos superior", "Quantil 97,5% dos votos estimados."),
         ("base", "Base", "Total observado da origem; retornantes: base estimada; pesquisa: institutos.")]],
     col("tipo_intervalo", "Tipo de intervalo", oculta=True)], oculta=True)]
