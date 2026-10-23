# Publicar no Power BI Service e ligar a apuração ao vivo

O painel funciona inteiro no Power BI Desktop. Para a tela 19 (Apuração) andar sozinha no Service na noite de 25/10, faltam quatro
passos que dependem de acesso de administrador (combinado para depois). Nada aqui precisa de gateway: todas as fontes
são o endereço público do GitHub.

## 1. Workspace com capacidade que aceite muitas atualizações

Pro tem teto de 8 atualizações por dia. Use um workspace **PPU, Premium ou Fabric** (a atualização avançada, só das
cinco tabelas da apuração, leva poucos segundos).

## 2. Publicar

Abra `pbi/pbip/Eleicoes.pbip` no Desktop e publique no workspace (Arquivo → Publicar). No Service, em Configurações do
modelo semântico → Credenciais da fonte de dados, deixe `https://raw.githubusercontent.com` como **Anônimo** e o nível
de privacidade **Público**. Rode uma atualização manual e confira a tela 19, Apuração (relógio até as 17h) e a capa (vídeo).

Recursos usados pelos visuais: o vídeo e as imagens vêm de `https://vizudados.github.io/eleicoes-2026/midia/…`
(GitHub Pages). Se o administrador do locatário bloquear visuais personalizados com acesso à web, liberar os três
visuais do relatório (HTML Content Standalone, Deneb Standalone e VizuFilter) em Portal do administrador → Visuais do
Power BI.

## 3. Entidade de serviço (o robô que pede a atualização)

1. Entra ID → Registros de aplicativo → Novo registro (ex.: `vizu-eleicoes-apuracao`). Anote o ID do locatário e o ID
   do aplicativo; crie um segredo do cliente.
2. Portal do administrador do Power BI → Configurações do locatário → "Entidades de serviço podem usar APIs do
   Power BI": habilitado (de preferência para um grupo de segurança que contém o aplicativo).
3. No workspace: Gerenciar acesso → adicionar o aplicativo como **Membro**.
4. IDs: o do workspace e o do modelo semântico estão na URL do Service
   (`/groups/<WORKSPACE_ID>/datasets/<DATASET_ID>`).

## 4. Segredos no GitHub

Em github.com/vizudados/eleicoes-2026 → Settings → Secrets and variables → Actions, criar:
`PBI_TENANT_ID`, `PBI_CLIENT_ID`, `PBI_CLIENT_SECRET`, `PBI_WORKSPACE_ID`, `PBI_DATASET_ID`.

Com eles, o workflow `apuracao` (a cada 5 minutos das 16h às 23h55 de 25/10, quatro coletas por execução) pede a
atualização das tabelas da apuração sempre que o TSE divulga números novos (`apuracao/atualizar_powerbi.py`).

## Ensaio antes de domingo

No Desktop, sem mexer no GitHub: troque o parâmetro `pPastaApuracao` para `dados/apuracao/ensaio-1turno` (Transformar
dados → Gerenciar parâmetros) e atualize; a tela 19 (Apuração) mostra o 1º turno encerrado com o carimbo "ENSAIO · 1º TURNO".
Volte para `dados/apuracao` antes de publicar.

O workflow também pode ser disparado à mão para testar o caminho inteiro (coleta, commit e pedido de atualização):

```bash
gh workflow run apuracao.yml -R vizudados/eleicoes-2026 -f eleicao=6258 -f repetir=1
```

Use sempre a eleição 6258 (2º turno) nesse teste: o coletor grava em `dados/apuracao`, a pasta que o painel lê.
