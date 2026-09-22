# Base 3 - Series financeiras diarias


## 1. Identificacao da base


| Campo | Descricao |
|---|---|
| Nome no projeto | Grupo 3 |
| Arquivos | `grupo3/data.csv` e `grupo3/test.csv` |
| Tipo observado | Series temporais financeiras com OHLCV |
| Frequencia observada | Diaria de mercado, com ausencia de fins de semana e feriados |
| Periodo observado | 2018-07-02 a 2020-06-30 |
| Quantidade em cada arquivo | 503 linhas e 7 colunas, incluindo o cabecalho |
| Coluna temporal | `Date` |
| Colunas numericas | `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume` |


> **Ressalva de proveniencia:** o dicionario de variaveis do projeto descreve o Grupo 3 como qualidade do ar em Pequim, mas os arquivos presentes no repositorio contem series financeiras com colunas OHLCV. A origem, o ativo e a funcao de `data.csv` versus `test.csv` precisam ser confirmados com o grupo antes da versao final do relatorio.


## 2. Estrutura dos arquivos


Os dois arquivos possuem a mesma estrutura e o mesmo periodo:


| Arquivo | Inicio | Fim | Linhas | Interpretacao atual |
|---|---:|---:|---:|---|
| `data.csv` | 2018-07-02 | 2020-06-30 | 503 | Serie financeira 1; ativo nao identificado no arquivo |
| `test.csv` | 2018-07-02 | 2020-06-30 | 503 | Serie financeira 2 ou arquivo de teste com periodo sobreposto |


Os primeiros e ultimos valores indicam que os arquivos nao representam uma divisao cronologica treino/teste convencional: ambos comecam e terminam nas mesmas datas, mas apresentam valores diferentes. Portanto, nao se deve concatenar os arquivos nem tratar `test.csv` como o teste final sem confirmar a especificacao original.


## 3. Dicionario das variaveis


| Variavel | Tipo | Papel | Descricao |
|---|---|---|---|
| `Date` | Data | Indice temporal | Data de negociacao |
| `Open` | Numerica | Atributo financeiro | Preco de abertura |
| `High` | Numerica | Atributo financeiro | Maior preco observado no dia |
| `Low` | Numerica | Atributo financeiro | Menor preco observado no dia |
| `Close` | Numerica | Alvo recomendado | Preco de fechamento |
| `Adj Close` | Numerica | Alternativa de alvo | Fechamento ajustado por eventos corporativos, conforme a fonte |
| `Volume` | Numerica | Atributo financeiro | Volume negociado |


Para o Holt-Winters, recomenda-se definir previamente uma unica serie-alvo. A escolha mais simples e reprodutivel e `Close`. Se o grupo decidir usar `Adj Close`, essa escolha deve ser aplicada de forma consistente em todas as execucoes e registrada no protocolo.


## 4. Qualidade dos dados


As verificacoes realizadas nos arquivos atuais encontraram:


- Nenhum valor ausente nas sete colunas.
- Nenhuma data duplicada em cada arquivo.
- Datas ordenadas de forma crescente.
- Intervalos de 1 dia entre observacoes consecutivas em dias de negociacao.
- Intervalos de 3 e 4 dias associados principalmente a fins de semana prolongados e feriados.
- Nenhuma observacao artificial deve ser criada para fins de semana ou feriados.


Estatisticas observadas:


### `data.csv`


| Coluna | Media | Minimo | Maximo |
|---|---:|---:|---:|
| `Open` | 229.3914 | 143.9800 | 365.0000 |
| `High` | 232.1461 | 145.7200 | 372.3800 |
| `Low` | 227.0625 | 142.0000 | 362.2700 |
| `Close` | 229.7924 | 142.1900 | 366.5300 |
| `Adj Close` | 227.3090 | 139.3763 | 366.5300 |
| `Volume` | 33,545,809.74 | 11,362,000 | 106,721,200 |


### `test.csv`


| Coluna | Media | Minimo | Maximo |
|---|---:|---:|---:|
| `Open` | 33.9698 | 22.1100 | 46.7400 |
| `High` | 34.5601 | 23.4900 | 46.9000 |
| `Low` | 33.3461 | 20.0000 | 44.6100 |
| `Close` | 33.9480 | 22.0000 | 46.6500 |
| `Adj Close` | 33.9480 | 22.0000 | 46.6500 |
| `Volume` | 19,609,709.54 | 4,290,500 | 122,752,800 |


Os valores de preco, isoladamente, nao permitem identificar com seguranca o ativo ou a unidade. A documentacao final deve incluir a fonte original, o ticker e a regra usada para separar os dois arquivos.


## 5. Preparacao recomendada


1. Ler `Date` como data e ordenar crescentemente.
2. Verificar duplicidades, nulos e tipos numericos.
3. Definir `Close` ou `Adj Close` como alvo antes de qualquer modelagem.
4. Manter apenas uma observacao por dia de negociacao.
5. Nao preencher fins de semana ou feriados.
6. Fazer o corte treino/teste por ordem temporal, sem `shuffle`, caso a avaliacao seja feita dentro de uma mesma serie.
7. Se `data.csv` e `test.csv` forem ativos diferentes, analisar cada um como uma serie separada, e nao como treino e teste da mesma serie.
8. Registrar a decisao sobre `Volume` e as demais colunas: elas podem ser usadas por modelos multivariados, mas nao entram no Holt-Winters univariado.


## 6. Implicacoes para Holt-Winters


O Holt-Winters deve receber somente a serie-alvo escolhida. Para esta base, testar:


- Sem tendencia e com tendencia aditiva.
- Tendencia amortecida e nao amortecida.
- Sem sazonalidade e com periodos sazonais justificados pela frequencia diaria de mercado.
- Sazonalidade aditiva quando a escala da variacao for aproximadamente constante.
- Sazonalidade multiplicativa somente se todos os valores forem positivos e a variacao crescer proporcionalmente ao nivel.


Como a base e diaria e possui lacunas normais de calendario, o periodo sazonal deve ser interpretado em dias de negociacao, nao simplesmente em dias corridos. Periodos candidatos comuns, como 5 dias uteis ou aproximadamente 21 dias uteis, devem ser comparados por validacao temporal e nao escolhidos apenas por inspeccao.


## 7. Riscos e limitacoes


- A proveniencia dos arquivos nao esta descrita no proprio CSV.
- O ativo financeiro e a unidade dos precos nao estao identificados.
- `data.csv` e `test.csv` possuem datas sobrepostas e podem representar ativos diferentes.
- Precos financeiros possuem mudancas de regime e podem nao apresentar sazonalidade estavel.
- O desempenho historico nao deve ser interpretado como recomendacao financeira.
- Usar `High`, `Low`, `Close` ou `Volume` do mesmo dia para prever o proprio fechamento pode causar vazamento; esses valores so podem ser usados quando estiverem disponiveis no instante da previsao.


## 8. Checklist antes da entrega


- [ ] Confirmar fonte, ativo e ticker de cada arquivo.
- [ ] Confirmar se `test.csv` e outro ativo ou um teste sobreposto.
- [ ] Definir oficialmente `Close` ou `Adj Close` como alvo.
- [ ] Registrar corte, horizonte e folds walk-forward.
- [ ] Comparar Holt-Winters com o baseline definido pelo grupo.
- [ ] Manter parametros e MAE separados para cada serie analisada.
- [ ] Atualizar esta documentacao depois da confirmacao da proveniencia.

