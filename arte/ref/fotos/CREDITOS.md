# Créditos das fotos de referência (usadas só como referência para o retrato em traço)

- `lula-oficial.jpg` — "Foto oficial de Luiz Inácio Lula da Silva (ombros)", Palácio do Planalto (Ricardo Stuckert/PR),
  16/02/2023, CC BY 2.0. https://commons.wikimedia.org/wiki/File:Foto_oficial_de_Luiz_In%C3%A1cio_Lula_da_Silva_(ombros).jpg
- `flavio-oficial.jpg` — "Foto oficial do senador Flávio Bolsonaro (v. AgSen)", Agência Senado, 01/02/2019, uso livre com
  crédito. https://commons.wikimedia.org/wiki/File:Foto_oficial_do_senador_Fl%C3%A1vio_Bolsonaro_(v._AgSen).jpg

No painel: "Retratos em traço a partir de fotos oficiais (Palácio do Planalto, CC BY 2.0; Agência Senado)".

## Desenhos a partir de fotos reais (comícios e linha do tempo), 23/10/2026

Os comícios das páginas "quem é" e as 16 fotos dos marcos da trajetória foram redesenhados em traço pelo Codex CLI
local (prompts em `arte/prompts-fotos/`, referências 4:5 em `arte/ref/recortes/`). Fotos originais, autores e
licenças: `dados/bruto/trajetoria/trajetoria.json` e `FONTES.md`; crédito de cada desenho, por arquivo web:
`dados/bruto/trajetoria/desenhos.csv` (gerado por `pipeline/creditos_desenhos.py`).

- **Licença dos desenhos: CC BY-SA 4.0, todos.** É obrigatória para os derivados de fotos CC BY-SA 4.0 (as 4 do Flickr
  Lula Oficial na linha do tempo, o comício de Lula e as 3 da Agência Senado de 2025–2026 de Flávio). Para os derivados
  de fotos CC BY (Agência Senado 2019–2022, Planalto, Governo do RJ, Agência Brasil 2003/2006) e de domínio público, a
  mesma licença foi escolhida para tratar os dois candidatos igual; o crédito da foto vai sempre junto.
- **Crédito curto** (até 90 caracteres, na legenda do painel): "Desenho CC BY-SA 4.0 a partir de foto de
  Ricardo Stuckert/Lula Oficial (CC BY-SA 4.0)". A coluna `legenda` traz a data e o local reais da foto.
- **Comícios:** Lula, ato de 11/10/2026 na Av. Paulista (`lula-comicio-2026-2.jpg`, Ricardo Stuckert/Lula Oficial,
  CC BY-SA 4.0); Flávio, ato de 7 de Setembro de 2021 na Av. Paulista (`flavio-comicio-2021-1.jpg`, Isac Nóbrega/PR,
  CC BY 2.0). No desenho de Flávio, o outro participante da foto ficou de fora, para o enquadramento ficar igual ao de
  Lula (candidato em meio corpo num terço do quadro, multidão no resto).
- No rodapé ou no "ⓘ" do painel: "Desenhos em traço a partir de fotos de Ricardo Stuckert/Lula Oficial, Agência Senado,
  Agência Brasil, Palácio do Planalto, Governo do RJ, Consulado dos EUA e Família Bolsonaro; desenhos sob CC BY-SA 4.0.
  Créditos por imagem em dados/bruto/trajetoria/desenhos.csv."
