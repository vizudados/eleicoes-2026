"""Pede ao Power BI a atualização do modelo semântico depois de cada coleta (API REST, entidade de serviço).

Variáveis de ambiente (segredos do GitHub): PBI_TENANT_ID, PBI_CLIENT_ID, PBI_CLIENT_SECRET, PBI_WORKSPACE_ID,
PBI_DATASET_ID. A entidade de serviço precisa estar habilitada no locatário e ser membro do workspace.
Limite: em capacidade Pro são 8 atualizações agendadas por dia (as pela API contam); em PPU/Premium/Fabric não há esse
teto para atualizações pela API — para a noite da eleição, use um workspace PPU ou Fabric.
"""
import json
import os
import sys
import urllib.parse
import urllib.request


def token():
    corpo = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": os.environ["PBI_CLIENT_ID"],
        "client_secret": os.environ["PBI_CLIENT_SECRET"],
        "scope": "https://analysis.windows.net/powerbi/api/.default"}).encode()
    url = f"https://login.microsoftonline.com/{os.environ['PBI_TENANT_ID']}/oauth2/v2.0/token"
    with urllib.request.urlopen(urllib.request.Request(url, data=corpo), timeout=30) as r:
        return json.load(r)["access_token"]


# Só as quatro tabelas da apuração (atualização avançada, PPU/Premium/Fabric): segundos em vez de recarregar o painel
# inteiro. Em Pro a atualização avançada não existe: cai para a atualização comum do modelo.
TABELAS = ["Apuração Brasil", "Apuração UF", "Apuração histórico", "Apuração status"]


def pedir(url, corpo, chave):
    pedido = urllib.request.Request(url, data=json.dumps(corpo).encode(),
                                    headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return r.status


def atualizar():
    url = (f"https://api.powerbi.com/v1.0/myorg/groups/{os.environ['PBI_WORKSPACE_ID']}"
           f"/datasets/{os.environ['PBI_DATASET_ID']}/refreshes")
    chave = token()
    avancada = {"type": "full", "commitMode": "transactional", "retryCount": 1,
                "objects": [{"table": t} for t in TABELAS]}
    try:
        print(f"atualização das tabelas da apuração pedida: HTTP {pedir(url, avancada, chave)}")
        return
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        if e.code != 400 or "progress" in msg.lower():
            # 400 com "refresh already in progress" não é falha: a próxima coleta pede de novo.
            print(f"Power BI respondeu {e.code}: {msg}", file=sys.stderr)
            return
    try:
        print(f"atualização comum pedida: HTTP {pedir(url, {'notifyOption': 'NoNotification'}, chave)}")
    except urllib.error.HTTPError as e:
        print(f"Power BI respondeu {e.code}: {e.read().decode()[:300]}", file=sys.stderr)


if __name__ == "__main__":
    atualizar()
