"""Tabela da tela T26 · Debate na Globo (a 20 na ordem do roteiro, logo depois da 19 · 2º turno): o último debate do 2º
turno, na TV Globo em 23/10/2026, numa tela que fica pronta antes dos números e se preenche quando o arquivo de dados
muda no repositório (o mesmo caminho da apuração ao vivo: o modelo lê o CSV pelo endereço raw do GitHub).

  T26 Debate Globo   dados/pbi/debate_globo.csv, escrito à mão a partir das fontes (dados/bruto/debate/FONTES.md, seção
                     "Debate da Globo, 23/10"): uma linha por fato ou número, com a situação, a hora esperada, a fonte
                     esperada e a fonte de verdade. Campo vazio = ainda não chegou (a tela mostra "aguardando"); nada é
                     estimado. Grupos: debate (situação, hora, onde passa, mediação, local, checagem), regra (os blocos),
                     presenca (Lula e Flávio) e metrica (os cinco cartões da noite: buscas, audiência, streaming, redes e
                     pesquisas; os números das pesquisas saem da tabela Pesquisa, com a mesma regra da tela 08).

Sem relação com as outras tabelas: as contas da tela leem esta tabela pela Chave e comparam com o debate da Band de 18/10
nas tabelas Debate, 'Trends tempo' e Monitoramento.
"""

from gerar_modelo import col, tabela_csv

TABELAS = [
    tabela_csv(
        "T26 Debate Globo", "O debate da Globo de 23/10/2026 (2º turno): uma linha por fato ou número, com a situação, "
                            "a hora esperada e a fonte. Vazio = ainda não chegou; nada estimado.",
        "dados/pbi/debate_globo.csv",
        [col("chave", "Chave", descricao="Identificador estável da linha (debate, presenca_lula, audiencia_previa…)."),
         col("grupo", "Grupo", descricao="debate · regra · presenca · metrica.", oculta=True),
         col("cartao", "Cartão", descricao="Cartão da noite a que a métrica pertence (buscas, audiencia, streaming, "
             "redes, pesquisas); vazio fora das métricas."),
         col("ordem", "Ordem", tipo="int", descricao="Ordem da linha (a dos cartões sai da menor ordem de cada um).",
             oculta=True, formato="0"),
         col("candidato", "Candidato", descricao="Lula ou Flávio nas linhas de um candidato; vazio nas outras.",
             oculta=True),
         col("rotulo", "Rótulo", descricao="Título que a tela mostra.", oculta=True),
         col("medida", "Medida", descricao="O que exatamente o número mede (a linha sob o título).", oculta=True),
         col("situacao", "Situação", descricao="debate: marcado, no_ar, realizado, adiado, cancelado · presenca: "
             "confirmada, a_confirmar, ausente · metrica: aguardando, publicado, nao_divulgado.", oculta=True),
         col("valor", "Valor", tipo="number", descricao="O número publicado (vazio enquanto não chega).", oculta=True,
             formato="#,0.0#"),
         col("texto", "Texto", descricao="Texto do fato (mediação, regras, histórico da presença, motivo de "
             "cancelamento ou ausência).", oculta=True),
         col("unidade", "Unidade", descricao="Unidade do valor.", oculta=True),
         col("esperado", "Esperado", descricao="Quando o número deve chegar, como a tela escreve.", oculta=True),
         col("previsto_para", "PrevistoTexto", descricao="Hora prevista (aaaa-mm-dd hh:mm, Brasília), como no CSV.",
             oculta=True),
         col(None, "Previsto", tipo="datetime", descricao="Hora prevista (início do debate, fim, chegada do número).",
             oculta=True, formato="dd/MM/yyyy HH:mm"),
         col("fonte_esperada", "Fonte esperada", descricao="De onde o número deve vir.", oculta=True),
         col("fonte", "Fonte", descricao="De onde veio (veículo e hora), quando chegou.", oculta=True),
         col("fonte_url", "URL", descricao="Link(s) da fonte, separados por ' , '.", oculta=True),
         col("atualizado_em", "Atualizado", descricao="Quando a linha foi atualizada (dd/mm/aaaa hh:mm).", oculta=True),
         col("observacao", "Observação", descricao="Ressalva de leitura (vai para o dossiê).", oculta=True)],
        oculta=True,
        passos='    Final = Table.AddColumn({entrada}, "Previsto", each if [PrevistoTexto] = null or [PrevistoTexto] = "" '
               'then null else DateTime.FromText([PrevistoTexto], [Format = "yyyy-MM-dd HH:mm", Culture = "en-US"]), '
               'type nullable datetime)'),
]
