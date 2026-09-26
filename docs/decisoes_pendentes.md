# Decisoes pendentes

Preencher antes do inicio da modelagem. Nao deixar agentes de IA assumirem estas respostas.

## Informado pelo material do Daniel (ainda nao aplicado no pipeline)

Fonte fornecida pelo usuario como "Bases para o Daniel". Isso **nao** define
qual e o numero do *seu* grupo de trabalho; define as cinco bases do trabalho.

| Base | Fonte | Granularidade declarada | Random state | Treino/teste |
| --- | --- | --- | --- | --- |
| 1 | Bitget Bitcoin historical | Diaria | 42 | 70/30 |
| 2 | UCI Metro Interstate Traffic Volume | Horaria (1h) | **67** | 80/20 |
| 3 | UCI Beijing Multi-Site Air Quality | Horaria (1h) | 42 | 80/20 |
| 4 | Kaggle Weather Archive Jena | **Horaria** (texto do Daniel) | 42 | 80/20 |
| 5 | Adaptada a partir de gold.daily.prices + tratamento TheoMG | Semanal | 42 | 75/25 |

Links oficiais registrados:

- Base 1: https://www.bitget.com/price/bitcoin/historical-data
- Base 2: https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume
- Base 3: https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data
- Base 4: https://www.kaggle.com/datasets/pankrzysiu/weather-archive-jena
- Base 5 adaptada: https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5
- Base 5 oficial diaria: https://github.com/dengyishuo/quantitative-finance/blob/master/gold.daily.prices.csv
- Base 5 tratamento: https://github.com/TheoMGtech/pls-regration-comparation/tree/develop/bases/grupo5-tratamento

### Conflitos ainda abertos (nao alterar o pipeline sem decisao explicita)

- [ ] **Base 4 frequencia:** o texto do Daniel diz horaria; o pipeline atual usa
  passo de **10 minutos**.
- [ ] **Base 2 semente:** Daniel pede `67`; o RF da Base 2 ainda usa `42`.
- [ ] **Semente global vs por base:** o yaml tem uma unica `semente: 42`; o
  material do Daniel define semente **por base**.

### O que ja alinha com o codigo (sem precisar mudar agora)

- Treino/teste: Base 1 = 70/30; Bases 2–4 = 80/20; Base 5 = 75/25.
- Granularidade Bases 1, 2, 3 e 5: diaria / 1h / 1h / semanal.

## Ainda pendente do *seu* grupo

- [ ] Numero do grupo.
- [ ] Nomes dos integrantes.
- [ ] Modelo de especializacao correspondente ao grupo.
- [ ] Horizonte comum de previsao (1 passo? multi-passo?).
- [ ] Origens de previsao e periodo de teste comum entre os quatro modelos.
- [ ] Tamanho da janela inicial e uso de janela expansiva ou deslizante.
- [ ] Formula exata da forca da sazonalidade apresentada em sala.
- [ ] Estrategia e orcamento de busca de hiperparametros.

## Pendencias de disponibilidade / qualidade

- [ ] Base 1: data de download, unidade/metodologia de `Volume` e uso de `Open`.
- [ ] Base 2: agregacao dos timestamps repetidos; fuso e horario de verao.
- [ ] Base 3: imputacao sem futuro por dobra de treino (se necessaria).
- [ ] Base 4: fonte/licenca, `-9999`, duplicidades/lacunas e frequencia final
  (ver conflito 10min vs 1h acima).
- [ ] Base 5: unidade/moeda do ouro; fonte e atraso de publicacao de
  `TREASURY_10Y` e `FED_FUNDS_RATE`.
- [ ] Bases 1 a 5: classificar corretamente covariaveis internas vs externas.
