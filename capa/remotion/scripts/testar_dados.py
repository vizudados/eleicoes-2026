"""Conferências da capa contra os CSVs de origem, sem render e sem alterar os dados."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

import pandas as pd

PROJETO = Path(__file__).resolve().parents[1]
RAIZ = PROJETO.parents[1]
spec = importlib.util.spec_from_file_location("preparar_dados", PROJETO / "scripts" / "preparar_dados.py")
preparar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparar)


class DadosDoisTurnos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads((PROJETO / "public" / "dados" / "capa.json").read_text(encoding="utf-8"))["municipios"]
        v1 = pd.read_csv(RAIZ / "dados" / "saida" / "votos_municipio.csv", dtype={"cd_ibge": str})
        cls.v1 = v1[v1.ano == 2026].groupby("cd_ibge")[["pt", "adv", "validos"]].sum()
        v2 = pd.read_csv(RAIZ / "dados" / "pbi" / "municipio_2turno.csv", dtype={"cd_ibge": str})
        cls.v2 = v2[v2.ano == 2026].set_index("cd_ibge")

    def test_cobertura_e_somas(self):
        m = self.m
        self.assertEqual(len(set(m["cd_ibge"])), 5570)
        self.assertTrue(all(len(v) == 5570 for v in m.values()))
        self.assertEqual(set(self.v2.index) - set(m["cd_ibge"]), {"5101837"})
        self.assertEqual(int(self.v2.loc["5101837", "validos"]), 3298)
        self.assertEqual(int(self.v2.validos.sum()), 123710622)
        self.assertEqual(sum(m["validos2"]), 123707324)
        self.assertEqual(sum(m["validos2"]), int(self.v2.validos.sum() - self.v2.loc["5101837", "validos"]))

    def test_margens_cores_raios_e_trocas_por_municipio(self):
        m = self.m
        vmax = self.v1.loc[m["cd_ibge"], "validos"].max()
        for i, cod in enumerate(m["cd_ibge"]):
            with self.subTest(cd_ibge=cod):
                a, b = self.v1.loc[cod], self.v2.loc[cod]
                m1 = (a.pt - a.adv) / a.validos
                m2 = (b.pt - b.adv) / b.validos
                self.assertAlmostEqual(m["m"][i], m1, delta=5.1e-9)
                self.assertAlmostEqual(m["m2"][i], m2, delta=5.1e-9)
                self.assertEqual(m["cor"][i], preparar.cor_margem(m1))
                self.assertEqual(m["cor2"][i], preparar.cor_margem(m2))
                self.assertEqual(m["validos"][i], int(a.validos))
                self.assertEqual(m["validos2"][i], int(b.validos))
                self.assertEqual(m["r"][i], round(1.05 + 1.9 * math.sqrt(a.validos / vmax), 2))
                esperado = 1 if a.pt < a.adv and b.pt > b.adv else -1 if a.pt > a.adv and b.pt < b.adv else 0
                self.assertEqual(m["troca"][i], esperado)
        self.assertEqual(m["troca"].count(1), 211)
        self.assertEqual(m["troca"].count(-1), 1)
        self.assertEqual([c for c, t in zip(m["cd_ibge"], m["troca"]) if t == -1], ["5221577"])

    def test_empates_nao_sao_troca(self):
        for votos in [(1, 1, 2, 1), (1, 1, 1, 2), (2, 1, 1, 1), (1, 2, 1, 1), (1, 1, 1, 1)]:
            self.assertEqual(preparar.direcao_troca(*votos), 0)
        self.assertEqual(preparar.direcao_troca(1, 2, 2, 1), 1)
        self.assertEqual(preparar.direcao_troca(2, 1, 1, 2), -1)

    def test_paleta_e_limites(self):
        for margem, cor in [(-1, "#3D69B3"), (-.6, "#3D69B3"), (0, "#CBBDA2"), (.6, "#BE3329"), (1, "#BE3329")]:
            self.assertEqual(preparar.cor_margem(margem), cor)
        for i, troca in enumerate(self.m["troca"]):
            if troca:
                x, y = self.m["x"][i], self.m["y"][i]
                # Todo o halo (raio 6,5 px) cabe na zona do mapa e fora das zonas do HTML.
                self.assertTrue(688 <= x - 6.5 and x + 6.5 <= 1232)
                self.assertTrue(303 <= y - 6.5 and y + 6.5 <= 863)


if __name__ == "__main__":
    unittest.main(verbosity=2)
