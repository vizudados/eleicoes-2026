"""Vigia da apuração (roda no GitHub Actions, workflow `vigia`): confere se a coleta está viva sem depender de computador
ligado.

Confere: (1) a idade do último commit de dados/apuracao/ultimo.json; (2) as últimas execuções do workflow `apuracao`;
(3) se a API do TSE responde. Coleta parada há mais de LIMITE minutos e nenhuma execução em curso → dispara o
`apuracao` de novo. Falha repetida ou coleta que não volta → grava problema=1 em $GITHUB_OUTPUT, e o workflow chama o
agente (Claude) para diagnosticar e corrigir. Usa o `gh` com o GITHUB_TOKEN do próprio workflow.

    python -I apuracao/vigiar.py
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

REPO = os.environ.get("GITHUB_REPOSITORY", "vizudados/eleicoes-2026")
LIMITE = 12  # minutos sem commit de dados com o cron a cada 5 min
TSE = "https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.json"


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def minutos_desde(iso):
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() / 60


def main():
    problemas, notas = [], []
    # 1 · dados frescos
    ult = json.loads(gh("api", f"repos/{REPO}/commits?path=dados/apuracao/ultimo.json&per_page=1"))
    idade = minutos_desde(ult[0]["commit"]["committer"]["date"]) if ult else 999
    notas.append(f"último commit de dados há {idade:.0f} min")
    # 2 · execuções do coletor
    runs = json.loads(gh("run", "list", "-R", REPO, "--workflow", "apuracao.yml", "--limit", "6",
                         "--json", "status,conclusion,createdAt,databaseId"))
    rodando = any(r["status"] in ("queued", "in_progress") for r in runs)
    recentes = [r for r in runs if r["status"] == "completed" and minutos_desde(r["createdAt"]) < 40]
    falhas = [r for r in recentes if r["conclusion"] not in ("success", "skipped", "cancelled")]
    notas.append(f"coletor: {len(recentes)} execuções em 40 min, {len(falhas)} com falha, rodando agora: {rodando}")
    # 3 · TSE
    try:
        req = urllib.request.Request(TSE, headers={"User-Agent": "VizuDados-Vigia/1.0 (+https://vizudados.com.br)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            br = json.loads(r.read().decode("utf-8"))
        notas.append(f"TSE ok · seções {br['s'].get('pst', '?')}% · {br.get('dt', '')} {br.get('ht', '')}")
    except Exception as e:  # noqa: BLE001 — o vigia relata qualquer falha de rede
        notas.append(f"TSE sem resposta: {e}")
    if idade > LIMITE and not rodando:
        # uma execução longa (a corrente da noite: ela mesma passa o bastão à seguinte até a meia-noite)
        gh("workflow", "run", "apuracao.yml", "-R", REPO, "-f", "eleicao=6258", "-f", "repetir=200")
        notas.append("coleta parada: lancei uma execução longa do apuracao")
    if len(falhas) >= 2:
        problemas.append(f"{len(falhas)} execuções do coletor falharam nos últimos 40 min (ids "
                         + ", ".join(str(r["databaseId"]) for r in falhas) + ")")
    if idade > 3 * LIMITE:
        problemas.append(f"dados parados há {idade:.0f} min mesmo com o coletor disparado")
    resumo = " · ".join(notas + problemas)
    print(resumo)
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a", encoding="utf-8") as f:
        f.write(f"problema={'1' if problemas else '0'}\n")
        f.write(f"resumo={resumo}\n")
    with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a", encoding="utf-8") as f:
        f.write("### Vigia da apuração\n\n" + "\n".join(f"- {n}" for n in notas + problemas) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
