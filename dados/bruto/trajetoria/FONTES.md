# Trajetória política: fontes, licenças e lacunas

Levantamento feito em 22 e 23/10/2026 para as páginas de apresentação dos candidatos (mockup Power BI). Os dados estão em `trajetoria.json`. As fotos de referência ficam em `arte\ref\historicas\`.

- **Método:** as fotos foram buscadas na API do Wikimedia Commons (`prop=imageinfo&iiprop=url|size|extmetadata`), com User-Agent identificado. A licença de cada foto foi conferida no metadado e no template da página do arquivo. A licença dos perfis do Flickr foi conferida pelo oEmbed do próprio Flickr.
- **Downloads:** foi baixada a miniatura de cerca de 1.600 px, e o Commons entregou 1.920 px de largura. Quando o original era menor que isso, foi baixado o original. O PNG de 2016 foi salvo como JPG. Nenhum arquivo baixado foi aberto ou executado além da leitura da imagem.
- **Regras do texto:** são 10 marcos por candidato, com título de até 6 palavras e texto de até 220 caracteres (vão de 115 a 199). Todos estão no passado e não têm adjetivos. Os episódios judiciais aparecem com o desfecho. Cada candidato tem dois marcos judiciais: Lula tem a prisão e a anulação, e Flávio tem a denúncia e o arquivamento.
- **Resultado de 2026:** os números do 1º turno (04/10/2026) vieram do coordenador, já verificados: Flávio teve 47,03% e Lula, 45,16% dos votos válidos. O 2º turno é em 25/10/2026.

## Lula: marcos, fontes e fotos

| Data | Marco | Fonte do texto | Foto (arquivo · autor · licença) |
|---|---|---|---|
| 1975 | Preside o sindicato do ABC | [Biografia completa, Biblioteca da PR](https://www.gov.br/secretariageral/pt-br/centrais-de-conteudo/biblioteca-da-pr/galeria-dos-ex-presidentes/luiz-inacio-lula-da-silva/biografia-completa) e [biografia na Câmara](https://www.camara.leg.br/deputados/139289/biografia) | **sem foto** (ver lacunas) |
| 10/02/1980 | Participa da fundação do PT | Biografia completa da Biblioteca da PR: data, fundadores e prisão de 31 dias pela LSN | **sem foto** |
| 15/11/1986 | Eleito deputado federal constituinte | [Senado Notícias, 30/12/2002](https://www12.senado.leg.br/noticias/materias/2002/12/30/do-agreste-ao-planalto-central-a-trajetoria-do-novo-presidente-da-republica) | `lula-1986-constituinte.jpg` · Senado Federal/Agência Senado (foto de arquivo) · CC BY 2.0 · [Commons](https://commons.wikimedia.org/wiki/File:Serra,_Lula_e_outros_na_constituinte.jpg) |
| 17/12/1989 | Disputa a Presidência pela 1ª vez | [TSE, 90 anos da Justiça Eleitoral](https://www.tse.jus.br/comunicacao/noticias/2022/Fevereiro/90-anos-da-justica-eleitoral-12-eleicoes-presidenciais-ja-foram-realizadas-no-brasil-desde-1945) | **sem foto** |
| 27/10/2002 | Eleito presidente da República | [Senado Notícias, 31/12/2002](https://www12.senado.leg.br/noticias/materias/2002/12/31/congresso-nacional-dara-posse-ao-37-presidente-da-republica-do-brasil-501666600): 61,27% e 52.793.364 votos | `lula-2002-posse.jpg` · Marcello Casal Jr./Agência Brasil · uso livre com atribuição (Commons: CC BY 3.0 BR) · [Commons](https://commons.wikimedia.org/wiki/File:Lula_de_m%C3%A3os_dadas_com_FHC.jpg) |
| 29/10/2006 | Reeleito presidente da República | [Senado Notícias, 30/10/2006](https://www12.senado.leg.br/noticias/materias/2006/10/30/presidente-lula-e-reeleito-com-mais-de-58-milhoes-de-votos): 60,83% e 58.295.042 votos | `lula-2006-reeleicao.jpg` · Marcello Casal Jr./Agência Brasil · idem · [Commons](https://commons.wikimedia.org/wiki/File:Lula_vota_em_S%C3%A3o_Bernardo_do_Campo.jpg) |
| 07/04/2018 | Preso no caso do triplex | [Agência Brasil, 07/04/2018](https://agenciabrasil.ebc.com.br/politica/noticia/2018-04/lula-chega-policia-federal-em-curitiba-para-comecar-cumprir-pena) e [soltura, 08/11/2019](https://agenciabrasil.ebc.com.br/justica/noticia/2019-11/lula-deixa-carceragem-da-pf-em-curitiba) | `lula-2018-prisao.jpg` · Ricardo Stuckert/Lula Oficial · CC BY-SA 4.0 · [Commons](https://commons.wikimedia.org/wiki/File:Lula_carregado_por_multid%C3%A3o_no_dia_de_sua_pris%C3%A3o_(2018-04-07).jpg) |
| 08/03/2021 | STF anula as condenações | [STF, decisão de Fachin](https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=461870&ori=1) e [plenário confirma, 15/04/2021](https://portal.stf.jus.br/noticias/verNoticiaDetalhe.asp?idConteudo=464261&ori=1) | `lula-2021-anulacao.jpg` · Ricardo Stuckert/Lula Oficial · CC BY-SA 4.0 · [Commons](https://commons.wikimedia.org/wiki/File:Encontro_com_movimentos_sociais_em_Pernambuco.jpg) |
| 30/10/2022 | Eleito para o 3º mandato | [TSE, 100% das seções totalizadas](https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/100-das-secoes-totalizadas-confira-como-ficou-o-quadro-eleitoral-apos-o-2o-turno) | `lula-2022-eleicao.jpg` · Ricardo Stuckert/Lula Oficial · CC BY-SA 4.0 · [Commons](https://commons.wikimedia.org/wiki/File:30.10.2022-_Lula,_presidente_eleito,_discursa_na_Paulista_-_52467411262.jpg) |
| 04/10/2026 | Candidato à reeleição pelo PT | [TSE, 2º turno 2026](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/flavio-bolsonaro-e-lula-vao-disputar-o-2o-turno-para-a-presidencia-da-republica) e [convenção do PT, Agência Brasil, 02/08/2026](https://agenciabrasil.ebc.com.br/politica/noticia/2026-08/pt-oficializa-candidatura-de-lula-presidencia) | `lula-2026-primeiro-turno.jpg` · Ricardo Stuckert/Lula Oficial · CC BY-SA 4.0 · [Commons](https://commons.wikimedia.org/wiki/File:04.10.2026_-_Presidente_Lula_se_pronuncia_ap%C3%B3s_o_1%C2%BA_turno_das_elei%C3%A7%C3%B5es_(55568731647).jpg) |

## Flávio Bolsonaro: marcos, fontes e fotos

| Data | Marco | Fonte do texto | Foto (arquivo · autor · licença) |
|---|---|---|---|
| 06/10/2002 | Eleito deputado estadual no RJ | [Agência Brasil, perfil de 17/08/2026](https://agenciabrasil.ebc.com.br/politica/noticia/2026-08/filho-mais-velho-de-bolsonaro-flavio-disputa-presidencia-pelo-pl) e [Senado Notícias, 04/10/2026](https://www12.senado.leg.br/noticias/materias/2026/10/04/flavio-bolsonaro-e-lula-disputam-o-segundo-turno-das-eleicoes-para-presidente) | `flavio-2002-alerj.jpg` · Governo do Estado do RJ (SEAP) · CC BY 2.0 BR · **400×600 px** · [Commons](https://commons.wikimedia.org/wiki/File:Deputado_Estadual_Fl%C3%A1vio_Bolsonaro_em_formatura_do_grupamento_de_interven%C3%A7%C3%A3o_t%C3%A1tica.jpg) |
| 02/10/2016 | Disputa a Prefeitura do Rio | [Agência Brasil, 02/10/2016](https://agenciabrasil.ebc.com.br/politica/noticia/2016-10/crivella-e-freixo-vao-para-o-segundo-turno-no-rio-de-janeiro) | `flavio-2016-prefeitura.jpg` · Família Bolsonaro (Flickr) · domínio público (Public Domain Mark do autor) · **550×381 px**, foto de 2015 · [Commons](https://commons.wikimedia.org/wiki/File:FlavioBolsonaro5_(22913796492).png) |
| 07/10/2018 | Eleito senador pelo RJ | [Senado Notícias, todas as eleições para o Senado no RJ](https://www12.senado.leg.br/noticias/infomaterias/2026/06/todas-as-eleicoes-para-o-senado-no-rio-de-janeiro): 4.380.418 votos e 31,36% | `flavio-2018-senado.jpg` · Consulado dos EUA no Rio · domínio público (PD-USGov-DOS) · [Commons](https://commons.wikimedia.org/wiki/File:Fl%C3%A1vio_Bolsonaro.jpg) |
| 01/02/2019 | Toma posse no Senado | [Perfil no Senado](https://www25.senado.leg.br/web/senadores/senador/-/perfil/5894) | `flavio-2019-posse.jpg` · Edilson Rodrigues/Agência Senado · CC BY 2.0 · [Commons](https://commons.wikimedia.org/wiki/File:Posse_Senadores_2019_(46038615415).jpg) |
| 19/10/2020 | Denunciado no caso das rachadinhas | [Agência Brasil/Radioagência, 04/11/2020](https://agenciabrasil.ebc.com.br/radioagencia-nacional/justica/audio/2020-11/flavio-bolsonaro-e-denunciado-pelo-ministerio-publico-do-rio) | `flavio-2020-denuncia.jpg` · Pedro França/Agência Senado · CC BY 2.0 · **foto de 30/11/2021** · [Commons](https://commons.wikimedia.org/wiki/File:Entrevistas_-_Senador_Fl%C3%A1vio_Bolsonaro_(Republicanos-RJ)_e_advogado_Frederick_Wassef.jpg) |
| 16/05/2022 | TJ-RJ arquiva a denúncia | [Agência Brasil, 16/05/2022](https://agenciabrasil.ebc.com.br/politica/noticia/2022-05/justica-do-rio-arquiva-processo-de-caso-de-supostas-rachadinhas) e [STJ anula decisões, 09/11/2021](https://agenciabrasil.ebc.com.br/justica/noticia/2021-11/stj-anula-decisoes-de-juiz-sobre-rachadinha-na-alerj) | `flavio-2022-arquivamento.jpg` · Edilson Rodrigues/Agência Senado · CC BY 2.0 · [Commons](https://commons.wikimedia.org/wiki/File:Entrevistas_Diversas_(52068540141).jpg) |
| 30/10/2022 | Coordena a campanha do pai | [Agência Brasil, 31/10/2022](https://agenciabrasil.ebc.com.br/politica/noticia/2022-10/flavio-bolsonaro-agradece-pelos-votos-dados-ao-pai-nas-eleicoes): coordenador da campanha; Lula 50,90% e Jair 49,10% | **sem foto** |
| 19/02/2025 | Preside a Comissão de Segurança Pública | [Senado Notícias, 19/02/2025](https://www12.senado.leg.br/noticias/materias/2025/02/19/flavio-bolsonaro-e-eleito-presidente-da-csp) | `flavio-2025-csp.jpg` · Edilson Rodrigues/Agência Senado · CC BY-SA 4.0 · foto de 19/08/2025 · [Commons](https://commons.wikimedia.org/wiki/File:CSP_-_Comiss%C3%A3o_de_Seguran%C3%A7a_P%C3%BAblica_(54730450422).jpg) |
| 05/12/2025 | Lança pré-candidatura à Presidência | [O Globo, 05/12/2025](https://oglobo.globo.com/politica/noticia/2025/12/05/flavio-bolsonaro-confirma-pre-candidatura-a-presidencia-em-2026-bolsonaro-me-conferiu-a-missao.ghtml), fonte primária achada pela Wikipédia usada só como índice (ver divergências) | `flavio-2025-precandidatura.jpg` · Andressa Anholete/Agência Senado · CC BY-SA 4.0 · **foto de 03/09/2025** · [Commons](https://commons.wikimedia.org/wiki/File:Fl%C3%A1vio_Bolsonaro_2025_(cropped).jpg) |
| 04/10/2026 | Candidato à Presidência pelo PL | [TSE, 2º turno 2026](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/flavio-bolsonaro-e-lula-vao-disputar-o-2o-turno-para-a-presidencia-da-republica) e [convenção do PL, Agência Brasil, 25/07/2026](https://agenciabrasil.ebc.com.br/politica/noticia/2026-07/pl-oficializa-candidatura-de-flavio-bolsonaro-presidencia) | `flavio-2026-primeiro-turno.jpg` · Carlos Moura/Agência Senado · CC BY-SA 4.0 · foto de 01/09/2026 · [Commons](https://commons.wikimedia.org/wiki/File:Fl%C3%A1vio_Bolsonaro_01.09.26.jpg) |

## Contagem e licenças

- **Lula:** 7 de 10 marcos têm foto.
  - CC BY-SA 4.0: 4 fotos (Flickr Lula Oficial, de Ricardo Stuckert).
  - Agência Brasil, atribuição: 2 fotos, de 2003 e 2006.
  - CC BY 2.0: 1 foto (Agência Senado).
- **Flávio:** 9 de 10 marcos têm foto.
  - CC BY 2.0: 3 fotos (Agência Senado).
  - CC BY-SA 4.0: 3 fotos (Agência Senado).
  - CC BY 2.0 BR: 1 foto (Governo do RJ).
  - Domínio público: 2 fotos (governo dos EUA e Public Domain Mark do autor).

Os desenhos em traço são obra derivada, e isso tem consequências de licença.

- **CC BY e Agência Brasil:** o crédito tem de acompanhar o desenho, por exemplo "a partir de foto de Edilson Rodrigues/Agência Senado (CC BY 2.0)".
- **CC BY-SA 4.0:** os desenhos feitos a partir dessas 6 fotos de marcos e das 3 de comício de Lula **precisam ser publicados sob CC BY-SA 4.0**, com crédito. Se isso for um problema, troque por foto CC BY ou de domínio público. Dá para fazer isso para Flávio. Para Lula, a única alternativa recente é a Agência Senado.
- **Domínio público:** não exige crédito, mas é boa prática dar.

## Marcos sem foto e por quê

- **Lula, 1975 (sindicato), 1980 (PT) e 1989 (1ª candidatura):** não há foto de licença aberta verificável dessa época.
  - "Lula e sua família… 1978" (Bob Wolfenson, tirada da Veja SP) tem uma marca de domínio público sem base.
  - A ficha do DOPS de 1980 (autor desconhecido, fonte Instituto Lula) não tem licença verificável e mostra a prisão, não a fundação do PT.
  - "Lula e Fidel… 1980" é da Agência F4, uma agência comercial.
  - "Lula, sem data.tif", do Arquivo Nacional, não mostra Lula.
  - "Lula em sua campanha presidencial, 1989.jpg" tem 344 px e alegação de obra própria duvidosa.
  - "Dep. lula.jpg" tem 476 px e é uma foto da ABr de 2003 que reproduz uma foto de arquivo exposta. A original não tem autor nem licença.
  - O acervo CSBH/Fundação Perseu Abramo aparece no Commons como CC BY-SA. A página de origem, porém, diz "Reprodução proibida sem prévia autorização do fotógrafo", por isso não foi usado.
- **Flávio, 2022 (coordenação da campanha):** não há foto livre dele na campanha de 2022.
  - O Commons não tem nenhuma.
  - O Flickr oficial dele (flaviobolsonaro) é "All Rights Reserved", conferido pelo oEmbed.
  - As fotos da Agência Brasil posteriores a 2017 não têm licença aberta (ver abaixo).
  - O Planalto não cobre campanha.

## Fotos com ressalva (época aproximada ou baixa resolução)

- **`flavio-2002-alerj.jpg`:** tem 400×600 px, abaixo dos 800 px pedidos, e é de 2014, 3º mandato na Alerj. Não há foto livre de 2002–2003.
- **`flavio-2016-prefeitura.jpg`:** tem 550×381 px e é um retrato de 2015, de antes da campanha. A outra opção, a foto de candidato do TSE de 2016, tem 161×225 px. "Bolsonaro e seus filhos" (2017) foi descartada porque usa o template PD-Brazil-URAA, que não se aplica a uma foto de 2017.
- **`flavio-2020-denuncia.jpg`:** é de 30/11/2021. Não há foto livre de Flávio em 2020, porque o Senado funcionou em sessões remotas. A cena é do mesmo caso: entrevista com o advogado no dia em que a 2ª Turma do STF manteve o foro do senador.
- **`flavio-2025-precandidatura.jpg`:** é de 03/09/2025, três meses antes do anúncio. Não há foto livre de dezembro de 2025.
- **`flavio-2025-csp.jpg`:** é de 19/08/2025 e mostra a placa "Presidente da CSP". A foto oficial da eleição, de 19/02/2025, é uma reprodução da TV Senado.
- **`lula-2021-anulacao.jpg`:** é de 16/08/2021, cinco meses depois da anulação. Lula está de máscara. As fotos de março de 2021 estão no Flickr do Instituto Lula, que é "All Rights Reserved".
- **`lula-1986-constituinte.jpg`:** é uma foto de arquivo em preto e branco da Constituinte (1987–88), publicada pela Agência Senado em 2008. O fotógrafo não é identificado.
- **`lula-2022-eleicao.jpg`:** o EXIF diz 23/05/2022 (relógio da câmera), mas a legenda oficial é de 30/10/2022.

## Assimetria de imagem (importante para a neutralidade do painel)

Lula tem um Flickr oficial com licença CC BY-SA 4.0, com fotos de atos, multidões e celebrações. O Flickr oficial de Flávio é "Todos os direitos reservados". Por isso, as fotos livres de Flávio são quase todas da Agência Senado: retratos e plenário.

Se os desenhos reproduzirem as cenas como estão, Lula aparecerá mais em cenas de massa. **Sugestão:** padronizar o enquadramento dos desenhos dos marcos (busto ou meio corpo) para os dois, usando as fotos só como referência de fisionomia, roupa e época.

## Comícios ("falando com o povo")

Pedido extra do coordenador. Os registros estão na chave `comicios` do JSON.

- **Lula:** há três fotos reais de 2026, todas do Flickr Lula Oficial (CC BY-SA 4.0, Ricardo Stuckert).
  - `lula-comicio-2026-1.jpg` e `lula-comicio-2026-3.jpg`: lançamento da campanha em 16/08/2026, no Estádio da Vila Euclides, em São Bernardo do Campo. Lula está de costas, no palco, com a arquibancada lotada à frente.
  - `lula-comicio-2026-2.jpg`: ato de 11/10/2026 na Avenida Paulista. Lula está de perfil, ao microfone, no carro de som, com a multidão à frente.
- **Flávio:** não foi achada nenhuma foto livre dele discursando para uma multidão, de 2026 ou de antes.
  - A única foto livre dele num ato com multidão é `flavio-comicio-2021-1.jpg`: ato de 7 de Setembro de 2021 na Avenida Paulista, foto de Isac Nóbrega/PR (Planalto, CC BY 2.0). Ele posa no carro de som com a multidão ao fundo. Não está discursando, e o ato era de Jair Bolsonaro.
  - **Decisão (23/10/2026): usar essa foto**, com legenda honesta ("Ato de 7 de Setembro de 2021, Av. Paulista, São Paulo") e o mesmo enquadramento e peso visual do desenho de Lula, que usa `lula-comicio-2026-2.jpg` (ato de 11/10/2026, também na Av. Paulista). No desenho, o outro participante da foto ficou de fora. Créditos dos desenhos: `desenhos.csv`.
- **Onde mais se procurou para Flávio, sem sucesso:**
  - Categorias do Commons: Flávio em 2018–2026, "with people", atos pró-Bolsonaro, motociatas e a série do Planalto de 7/9/2021 (89 fotos, só uma com ele).
  - Flickr: o oficial dele e perfis que marcaram "flaviobolsonaro" em 2026, como o de uma motocarreata em São Gonçalo em 10/10/2026. Todos são "All Rights Reserved".
  - Agência Senado: só cobre o Senado.
  - Governo argentino (argentina.gob.ar): publicou só a reunião de Milei com Flávio, não a convenção do PL.
  - Agência Brasil 2026: há fotos do lançamento em Copacabana (16/08/2026, Fernando Frazão/ABr) e da convenção do PL (Maura Martins/TV Brasil), mas sem licença aberta (ver abaixo).

## Licença da Agência Brasil: divergência com a regra do pedido

O pedido trata a Agência Brasil como CC BY 3.0 BR. Hoje isso **só vale para conteúdo anterior a 23/02/2017**.

- **Commons:** o [Module:Agência Brasil](https://commons.wikimedia.org/wiki/Module:Ag%C3%AAncia_Brasil) classifica como copyvio as fotos posteriores a essa data.
- **Site:** o rodapé da Agência Brasil diz "© Todos os direitos reservados pela EBC".
- **Termos de uso:** os [termos da EBC](https://www.ebc.com.br/termos-de-uso-e-condicoes-gerais-do-portal-da-ebc) dizem "Reprodução autorizada mediante indicação da fonte", mas limitam o uso do portal a "uso pessoal, sem intuito comercial".

Por isso nenhuma foto da Agência Brasil posterior a 2017 foi usada, nem as de 2026. As duas fotos da ABr usadas são de 2003 e 2006. Se quiserem usar as de 2026, vale pedir autorização à EBC.

## Divergências entre fontes

- **1º turno de 2026:**
  - A Senado Notícias da noite de 04/10, com 99,97% das urnas apuradas, traz Flávio com 47,04%/47,05% e Lula com 45,15%/45,14%.
  - O JSON usa o resultado final passado pelo coordenador: 47,03% e 45,16%.
  - O TSE informa 56.104.268 votos para Flávio.
- **1989:** a página do TSE sobre Collor mostra 42,75% contra 37,86%, que é o percentual sobre o total de votos. O texto usa o percentual dos válidos, 53,03% contra 46,97%: Collor teve 35.089.998 votos e Lula, 31.076.364.
- **2002:** o Senado registra 52.793.364 votos, ou 52,8 milhões. A Agência Brasil diz "quase 53 milhões".
- **2006:** a nota do Senado de 29/10, com apuração parcial, diz 60,56%. A nota final, de 30/10, diz 60,83%, e é a que foi usada.
- **1986:** as fontes oficiais dizem "mais de 650 mil votos". O número exato de 651.763, que circula na imprensa, não foi confirmado em fonte primária e não foi usado.
- **Plenário do STF:** a decisão foi confirmada em 15/04/2021, segundo o STF. Uma citação da defesa na Agência Brasil fala em 15/03, o que parece erro. O plenário fixou a competência da Justiça Federal do DF em 22/04/2021. A suspeição de Moro, decidida na 2ª Turma em março de 2021, não entrou no texto por falta de espaço.
- **Prisão de 2018:** a pena de 12 anos e 1 mês é a do TRF-4. O STJ a reduziu depois, e isso não está no texto.
- **Prisão de 1980:** a data exata não está na fonte oficial (costuma-se citar 19/04/1980), por isso o texto diz "no mesmo ano". O processo na Justiça Militar e o seu resultado também não entraram, porque a fonte não traz o desfecho.
- **Rachadinhas:**
  - O MP-RJ ajuizou a denúncia em 19/10/2020, e ela foi divulgada em 03 e 04/11/2020.
  - A Agência Brasil situa a anulação da quebra de sigilos em fevereiro de 2021. Outro resumo diz março.
  - O STJ anulou as decisões do juiz de 1ª instância em 09/11/2021.
  - Em 30/11/2021, a 2ª Turma do STF manteve o foro do senador, segundo a legenda da Agência Senado.
  - O TJ-RJ arquivou a denúncia em 16/05/2022.
  - Segundo a imprensa, o STF negou em fevereiro de 2025 recursos do MP-RJ para reabrir o caso. Isso não foi confirmado em fonte oficial e não entrou no texto.
- **Mandatos de Flávio na Alerj:** a Agência Brasil diz que ele foi eleito em 2002 e reeleito em 2006, 2010 e 2014, o que dá quatro mandatos (2003–2019). A Senado Notícias de 04/10/2026 tem uma redação ambígua ("reeleito quatro vezes"); foi usada a da Agência Brasil. O partido de 2002 (PPB) não foi confirmado em fonte primária e ficou fora do texto.
- **Mandato de senador:** o perfil do Senado diz 2019–2027, e a Senado Notícias diz "2019 a 2026". O JSON usa 2027.
- **Pré-candidatura de Flávio:**
  - Não foi achada matéria da Agência Brasil nem do Senado sobre o anúncio de 05/12/2025.
  - A data e o fato vêm de O Globo (05/12/2025), localizado pela Wikipédia, que foi usada só como índice. Também estão em Reuters, InfoMoney e Diário do Nordeste.
  - A carta de Jair Bolsonaro formalizando a indicação é datada de 25/12/2025.

## Episódios judiciais avaliados e não incluídos (sem desfecho ou de menor repercussão)

- **Flávio:**
  - Caso "Dark Horse"/Banco Master: em 11/09/2026, o ministro André Mendonça incluiu Flávio como investigado ([Agência Brasil](https://agenciabrasil.ebc.com.br/justica/noticia/2026-09/mendonca-incluiu-flavio-bolsonaro-como-investigado-no-caso-dark-horse)). **Não tem desfecho**, por isso ficou fora, como manda a regra.
  - O TRE-RJ arquivou um inquérito por falsidade ideológica em 23/05/2023.
  - O TSE manteve uma multa por postagem inverídica em 18/04/2023.
  - Esses dois últimos têm desfecho, mas são de menor repercussão e ficaram fora.
- **Lula:**
  - Os demais processos da Lava Jato (sítio de Atibaia e outros) estão cobertos pelo marco da anulação.
  - Não foi achado processo aberto em 2026 contra Lula que fosse marco da trajetória.

## Créditos prontos (para a legenda do painel)

Fotos de marcos:

- lula-1986-constituinte: Senado Federal/Agência Senado (arquivo), CC BY 2.0
- lula-2002-posse e lula-2006-reeleicao: Marcello Casal Jr./Agência Brasil
- lula-2018-prisao, lula-2021-anulacao, lula-2022-eleicao e lula-2026-primeiro-turno: Ricardo Stuckert/Lula Oficial, CC BY-SA 4.0
- flavio-2002-alerj: Governo do Estado do RJ, CC BY 2.0 BR
- flavio-2016-prefeitura: Família Bolsonaro, domínio público
- flavio-2018-senado: Consulado dos EUA no Rio, domínio público
- flavio-2019-posse e flavio-2022-arquivamento: Edilson Rodrigues/Agência Senado, CC BY 2.0
- flavio-2020-denuncia: Pedro França/Agência Senado, CC BY 2.0
- flavio-2025-csp: Edilson Rodrigues/Agência Senado, CC BY-SA 4.0
- flavio-2025-precandidatura: Andressa Anholete/Agência Senado, CC BY-SA 4.0
- flavio-2026-primeiro-turno: Carlos Moura/Agência Senado, CC BY-SA 4.0

Fotos de comício:

- lula-comicio-2026-1 a 3: Ricardo Stuckert/Lula Oficial, CC BY-SA 4.0
- flavio-comicio-2021-1: Isac Nóbrega/PR, CC BY 2.0

## Conteúdo da web tratado como dado

Nenhuma página consultada trazia instruções dirigidas ao agente. Nada foi executado a partir de conteúdo da web.
