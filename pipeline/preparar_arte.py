"""Limpa os desenhos do Codex para o mockup: fundo transparente, tinta numa cor da paleta, recorte justo.

- Cenas e urna: `arte/candidatas/<nome>-1-1.png` -> `arte/limpos/<nome>.png` (tinta #1C1915, alfa pela escuridão).
- Rabiscos: a folha 4 × 3 vira 12 marcas soltas, em três tintas (tinta, vermelho, azul):
  `arte/limpos/rabiscos/<marca>-<cor>.png`.
- Fotos reais redesenhadas (comícios e marcos da linha do tempo): `--recortes` (referências 4:5 para o Codex),
  `--fotos` (limpos) e `--web` (docs/midia, PNG de paleta para o GitHub Pages).

Uso: python -I -X utf8 pipeline/preparar_arte.py [--recortes | --fotos | --web | --extras ... | --dossie | --icones | --candidatos]
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parent.parent
CANDIDATAS = RAIZ / "arte" / "candidatas"
LIMPOS = RAIZ / "arte" / "limpos"
TINTAS = {"tinta": (0x1C, 0x19, 0x15), "vermelho": (0xB8, 0x32, 0x2A), "azul": (0x2B, 0x57, 0x97)}
CREME = (0xE5, 0xDB, 0xC8)
CENAS = ["regiao-sudeste", "regiao-nordeste", "regiao-norte", "regiao-centro-oeste", "regiao-sul", "urna"]
MARCAS = ["oval", "elipse", "circulo", "retangulo",
          "seta-curva-direita", "seta-curva-esquerda", "seta-reta", "seta-s",
          "sublinhado", "sublinhado-duplo", "sublinhado-onda", "chave"]


def alfa_da_tinta(img, piso=28, teto=200):
    """Alfa = escuridão do pixel, com o papel (quase branco) zerado e o traço pleno a partir de `teto`."""
    cinza = np.asarray(img.convert("L"), dtype=np.float32)
    escuro = 255.0 - cinza
    alfa = np.clip((escuro - piso) / (teto - piso), 0, 1)
    return (alfa * 255).astype(np.uint8)


def pintar(alfa, cor):
    h, w = alfa.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = cor
    rgba[..., 3] = alfa
    return Image.fromarray(rgba, "RGBA")


def recortar(alfa, margem=16, minimo=8):
    ys, xs = np.nonzero(alfa > minimo)
    y0, y1 = max(0, ys.min() - margem), min(alfa.shape[0], ys.max() + margem + 1)
    x0, x1 = max(0, xs.min() - margem), min(alfa.shape[1], xs.max() + margem + 1)
    return alfa[y0:y1, x0:x1]


def limpar_cenas():
    LIMPOS.mkdir(parents=True, exist_ok=True)
    for nome in CENAS:
        alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{nome}-1-1.png")))
        destino = LIMPOS / f"{nome}.png"
        pintar(alfa, TINTAS["tinta"]).save(destino, optimize=True)
        print(f"{destino.name}: {alfa.shape[1]}×{alfa.shape[0]}")


DOSSIE = ["fita", "fita-diagonal", "clipe", "alfinete", "post-it", "ficha", "papel-rasgado", "orelha",
          "carimbo-redondo", "carimbo-retangular", "visto", "asterisco"]
ICONES = ["urna", "caixa-de-votos", "megafone", "microfone", "celular", "lupa", "tv-debate", "jornal",
          "escola", "casa", "pino", "calendario", "pessoas", "pessoa-duvida", "barras", "balanca"]


def separar_folha(origem, nomes, pasta, linhas, cores, dilatacao=22, piso=40, teto=170):
    """Recorta uma folha de elementos soltos (grade de `linhas` linhas) em PNGs, na ordem de leitura."""
    pasta.mkdir(parents=True, exist_ok=True)
    alfa = alfa_da_tinta(Image.open(CANDIDATAS / origem), piso=piso, teto=teto)
    # Junta os traços de cada elemento (a ponta da seta, as linhas do duplo) e separa os elementos entre si.
    rotulos, _ = ndimage.label(ndimage.binary_dilation(alfa > 20, iterations=dilatacao))
    caixas = ndimage.find_objects(rotulos)
    grandes = sorted([(c, (c[0].stop - c[0].start) * (c[1].stop - c[1].start)) for c in caixas],
                     key=lambda x: -x[1])[:len(nomes)]
    altura = alfa.shape[0]
    ordenadas = sorted((c for c, _ in grandes),
                       key=lambda c: (int(((c[0].start + c[0].stop) / 2) / (altura / linhas)), c[1].start))
    for nome, caixa in zip(nomes, ordenadas):
        pedaco = recortar(alfa[caixa], margem=10)
        for cor in cores:
            pintar(pedaco, TINTAS.get(cor, CREME)).save(pasta / f"{nome}-{cor}.png", optimize=True)
        print(f"{pasta.name}/{nome}: {pedaco.shape[1]}×{pedaco.shape[0]}")


def separar_rabiscos():
    separar_folha("rabiscos-1-1.png", MARCAS, LIMPOS / "rabiscos", 3, ["tinta", "vermelho", "azul"])


TINTAS_CANDIDATO = {"lula": ("vermelho_escuro", (0x8E, 0x26, 0x20)), "flavio": ("azul_escuro", (0x1D, 0x3C, 0x6E))}



def limpar_candidatos():
    """Retrato de cada candidato em três tintas: tinta, a cor dele (escura, para texto ≥ 4,5:1) e creme.

    O comício saiu daqui em 23/10/2026: agora é redesenho de foto real (ver `limpar_fotos`). As versões antigas,
    que não vieram de foto, estão em `arte/limpos/_antigas/`.
    """
    for quem, (nome_cor, rgb) in TINTAS_CANDIDATO.items():
        for peca in ("retrato",):
            alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{peca}-{quem}-1-1.png")))
            for sufixo, cor in (("tinta", TINTAS["tinta"]), (nome_cor, rgb), ("creme", CREME)):
                pintar(alfa, cor).save(LIMPOS / f"{peca}-{quem}-{sufixo}.png", optimize=True)
            print(f"{peca}-{quem}: {alfa.shape[1]}×{alfa.shape[0]}")


def limpar_extras(nomes):
    """Cenas avulsas (ex.: debate-palco) em tinta e em creme."""
    for nome in nomes:
        alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{nome}-1-1.png")))
        for sufixo, cor in (("tinta", TINTAS["tinta"]), ("creme", CREME)):
            pintar(alfa, cor).save(LIMPOS / f"{nome}-{sufixo}.png", optimize=True)
        print(f"{nome}: {alfa.shape[1]}×{alfa.shape[0]}")


# ---------------------------------------------------------------------------------------------------------------
# Desenhos a partir de FOTOS REAIS: comícios (fundo das páginas "quem é") e marcos da linha do tempo (polaroide).
# Fontes, autores e licenças: dados/bruto/trajetoria/trajetoria.json e FONTES.md; créditos dos desenhos:
# dados/bruto/trajetoria/desenhos.csv. Geração: arte/gerar-ref.ps1 (Codex CLI local), prompts em arte/prompts-fotos/.
# ---------------------------------------------------------------------------------------------------------------
HISTORICAS = RAIZ / "arte" / "ref" / "historicas"
RECORTES = RAIZ / "arte" / "ref" / "recortes"
WEB = RAIZ / "docs" / "midia"

# Recorte 4:5 de cada foto de marco (x0, y0, x1, y1, em px da foto salva): o candidato em busto ou meio corpo.
# O recorte vai ao Codex como Image 1, e o desenho segue a composição dele (enquadramento igual para os dois).
RECORTES_45 = {
    "lula-1986-constituinte": (230, 0, 868, 798),
    "lula-2002-posse": (200, 181, 1000, 1181),
    "lula-2006-reeleicao": (398, 0, 1427, 1286),
    "lula-2018-prisao": (385, 0, 1255, 1087),
    "lula-2021-anulacao": (0, 350, 1300, 1975),
    "lula-2022-eleicao": (467, 120, 1235, 1080),
    "lula-2026-primeiro-turno": (0, 0, 1023, 1279),
    "flavio-2002-alerj": (0, 0, 400, 500),
    "flavio-2016-prefeitura": (70, 0, 375, 381),
    "flavio-2018-senado": (0, 0, 800, 1000),
    "flavio-2019-posse": (640, 0, 1664, 1280),
    "flavio-2020-denuncia": (350, 100, 1230, 1200),
    "flavio-2022-arquivamento": (344, 0, 1368, 1280),
    "flavio-2025-csp": (260, 700, 1540, 2300),
    "flavio-2025-precandidatura": (0, 0, 993, 1241),
    "flavio-2026-primeiro-turno": (0, 0, 872, 1090),
}

# Desenho aprovado de cada foto (arquivo em arte/candidatas). Ao refazer (Vez 2, 3...), troque aqui.
ESCOLHIDAS = {nome: f"{nome}-1-1.png" for nome in RECORTES_45}
# Vez 2 com o prompt de hachura mais leve no rosto (a Vez 1 saiu com o rosto mais carregado que os demais).
ESCOLHIDAS["flavio-2025-precandidatura"] = "flavio-2025-precandidatura-2-1.png"
# Comício do Flávio: Vez 2, com a figura no mesmo tamanho da de Lula (na Vez 1 ele saiu menor, com a cabeça a 1/3 da altura).
COMICIOS = {"lula": "comicio-foto-lula-1-1.png", "flavio": "comicio-foto-flavio-2-1.png"}

TAMANHO_POLAROIDE = (1040, 1300)   # 4:5, o dobro do web (520 px)
TAMANHO_COMICIO = (1536, 1024)     # 3:2, o web sai com 1460 px


def fazer_recortes():
    """Recorta as fotos de marco em 4:5 (referência para o Codex) em arte/ref/recortes/."""
    RECORTES.mkdir(parents=True, exist_ok=True)
    for nome, caixa in RECORTES_45.items():
        foto = Image.open(HISTORICAS / f"{nome}.jpg").convert("RGB").crop(caixa)
        foto.save(RECORTES / f"{nome}.jpg", quality=92)
        print(f"recorte {nome}: {foto.width}×{foto.height}")


def tirar_ciscos(alfa, area_minima=12, limiar=40, raio=10):
    """Apaga pontinhos ISOLADOS: componentes com menos de `area_minima` px e nenhuma outra tinta a `raio` px.

    Pontilhado de sombra e linhas tracejadas (que têm tinta por perto) ficam.
    """
    tinta = alfa > limiar
    rotulos, n = ndimage.label(tinta)
    if n == 0:
        return alfa
    indices = np.arange(1, n + 1)
    areas = ndimage.sum(tinta, rotulos, index=indices)
    lado = 2 * raio + 1
    vizinhanca = ndimage.uniform_filter(tinta.astype(np.float32), size=lado) * lado * lado
    maximo_em_volta = ndimage.maximum(vizinhanca, rotulos, index=indices)
    pequenos = np.zeros(n + 1, dtype=bool)
    pequenos[1:] = (areas < area_minima) & (maximo_em_volta <= areas + 0.5)
    saida = alfa.copy()
    saida[pequenos[rotulos]] = 0
    # O antisserrilhado em volta do cisco apagado (abaixo do limiar) some junto.
    saida[(ndimage.binary_dilation(pequenos[rotulos], iterations=2)) & (alfa <= limiar)] = 0
    return saida


def enquadrar(alfa, tamanho, margem):
    """Ajusta o desenho (recortado justo) dentro de uma tela de `tamanho`, centrado, com `margem` px em volta."""
    justo = recortar(alfa, margem=0)
    w, h = tamanho
    escala = min((w - 2 * margem) / justo.shape[1], (h - 2 * margem) / justo.shape[0])
    novo = (max(1, round(justo.shape[1] * escala)), max(1, round(justo.shape[0] * escala)))
    reduzido = np.asarray(Image.fromarray(justo).resize(novo, Image.LANCZOS))
    tela = np.zeros((h, w), dtype=np.uint8)
    x0, y0 = (w - novo[0]) // 2, (h - novo[1]) // 2
    tela[y0:y0 + novo[1], x0:x0 + novo[0]] = reduzido
    return tela


# Retângulos (x0, y0, x1, y1, em px do PNG do Codex) apagados à mão: texto que o modelo pôs apesar do prompt.
APAGAR = {
    "lula-2021-anulacao-1-1.png": [(640, 684, 679, 708), (507, 692, 532, 714)],  # letras impressas na máscara
}


def alfa_da_foto(arquivo):
    alfa = alfa_da_tinta(Image.open(CANDIDATAS / arquivo))
    for x0, y0, x1, y1 in APAGAR.get(arquivo, []):
        alfa[y0:y1, x0:x1] = 0
    return tirar_ciscos(alfa)


def limpar_fotos():
    """Comícios (3:2) e marcos (4:5) redesenhados de foto real: fundo transparente, tinta lisa (sem halo)."""
    pasta = LIMPOS / "historicas"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, arquivo in ESCOLHIDAS.items():
        alfa = enquadrar(alfa_da_foto(arquivo), TAMANHO_POLAROIDE, margem=40)
        for sufixo, cor in (("tinta", TINTAS["tinta"]), ("creme", CREME)):
            pintar(alfa, cor).save(pasta / f"{nome}-{sufixo}.png", optimize=True)
        print(f"historicas/{nome}: {arquivo}")
    for quem, arquivo in COMICIOS.items():
        nome_cor, rgb = TINTAS_CANDIDATO[quem]
        alfa = enquadrar(alfa_da_foto(arquivo), TAMANHO_COMICIO, margem=20)
        for sufixo, cor in (("tinta", TINTAS["tinta"]), (nome_cor, rgb), ("creme", CREME)):
            pintar(alfa, cor).save(LIMPOS / f"comicio-{quem}-{sufixo}.png", optimize=True)
        print(f"comicio-{quem}: {arquivo}")


def salvar_web(alfa, cor, destino, largura, teto_kb, opcoes=(32, 24, 16, 12, 8)):
    """PNG de paleta para a web: uma cor só, alfa em degraus (como o pngquant), no menor nº de degraus que cabe."""
    altura = round(alfa.shape[0] * largura / alfa.shape[1])
    pequeno = np.asarray(Image.fromarray(alfa).resize((largura, altura), Image.LANCZOS)).astype(np.float32)
    destino.parent.mkdir(parents=True, exist_ok=True)
    for degraus in opcoes:
        indice = np.rint(pequeno / 255 * (degraus - 1)).astype(np.uint8)
        img = Image.fromarray(indice, "P")
        img.putpalette(list(cor) * degraus)
        transparencia = bytes(round(i * 255 / (degraus - 1)) for i in range(degraus))
        img.save(destino, optimize=True, transparency=transparencia)
        kb = destino.stat().st_size / 1024
        if kb <= teto_kb:
            break
    return largura, altura, degraus, kb


def exportar_web():
    """Versões web (GitHub Pages): polaroide 520 px (≤ 150 KB) e comício 1460 px (≤ 450 KB)."""
    for nome in ESCOLHIDAS:
        alfa = np.asarray(Image.open(LIMPOS / "historicas" / f"{nome}-tinta.png"))[..., 3]
        w, h, d, kb = salvar_web(alfa, TINTAS["tinta"], WEB / "trajetoria" / f"{nome}.png", 520, 150)
        print(f"web trajetoria/{nome}.png: {w}×{h}, {d} degraus, {kb:.0f} KB")
    for quem in COMICIOS:
        nome_cor, rgb = TINTAS_CANDIDATO[quem]
        for sufixo, cor in (("tinta", TINTAS["tinta"]), (nome_cor, rgb), ("creme", CREME)):
            alfa = np.asarray(Image.open(LIMPOS / f"comicio-{quem}-{sufixo}.png"))[..., 3]
            destino = WEB / "comicio" / f"comicio-{quem}-{sufixo}.png"
            # Mesmo nº de degraus para os dois candidatos (16 cabe nos 450 KB nos dois): mesma qualidade de traço.
            w, h, d, kb = salvar_web(alfa, cor, destino, 1460, 450, opcoes=(16, 12, 8))
            print(f"web comicio/{destino.name}: {w}×{h}, {d} degraus, {kb:.0f} KB")


if __name__ == "__main__":
    import sys
    if "--recortes" in sys.argv:
        fazer_recortes()
    elif "--fotos" in sys.argv:
        limpar_fotos()
    elif "--web" in sys.argv:
        exportar_web()
    elif "--extras" in sys.argv:
        limpar_extras(sys.argv[sys.argv.index("--extras") + 1:])
    elif "--dossie" in sys.argv:
        separar_folha("dossie-1-1.png", DOSSIE, LIMPOS / "dossie", 3, ["tinta", "creme"])
    elif "--icones" in sys.argv:
        separar_folha("icones-1-1.png", ICONES, LIMPOS / "icones", 4, ["tinta", "vermelho", "azul", "creme"], dilatacao=17)
    elif "--candidatos" in sys.argv:
        limpar_candidatos()
    else:
        limpar_cenas()
        separar_rabiscos()
        limpar_candidatos()
        limpar_fotos()
        exportar_web()
