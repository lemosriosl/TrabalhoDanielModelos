# Base 4 - Clima de Jena


## 1. Identificacao da base


| Campo | Descricao |
|---|---|
| Nome no projeto | Grupo 4 |
| Arquivo | `trabalho/bases/grupo4/grupo4.csv` |
| Fonte/conjunto reconhecido | Serie meteorologica de Jena, conhecida como Jena Climate |
| Tipo de dado | Serie temporal meteorologica multivariada |
| Frequencia nominal | 10 minutos |
| Periodo observado | 2009-01-01 00:10:00 a 2017-01-01 00:00:00 |
| Quantidade de linhas | 420.551 |
| Quantidade de colunas | 15, incluindo a data |
| Localidade | Estacao meteorologica em Jena, Alemanha; confirmar a referencia original na entrega |


O arquivo contem varias variaveis meteorologicas medidas no mesmo instante. Para o Holt-Winters, deve ser escolhida uma unica coluna-alvo, mantendo o modelo univariado.


## 2. Dicionario das variaveis


| Variavel | Unidade | Descricao |
|---|---|---|
| `Date Time` | Data e hora | Timestamp da medicao, originalmente no formato `dd.mm.yyyy HH:MM:SS` |
| `p (mbar)` | mbar | Pressao atmosferica |
| `T (degC)` | graus Celsius | Temperatura do ar |
| `Tpot (K)` | Kelvin | Temperatura potencial |
| `Tdew (degC)` | graus Celsius | Temperatura do ponto de orvalho |
| `rh (%)` | % | Umidade relativa |
| `VPmax (mbar)` | mbar | Pressao de vapor de saturacao |
| `VPact (mbar)` | mbar | Pressao de vapor atual |
| `VPdef (mbar)` | mbar | Deficit de pressao de vapor |
| `sh (g/kg)` | g/kg | Umidade especifica |
| `H2OC (mmol/mol)` | mmol/mol | Concentracao de agua |
| `rho (g/m**3)` | g/m^3 | Densidade do ar |
| `wv (m/s)` | m/s | Velocidade media do vento |
| `max. wv (m/s)` | m/s | Velocidade maxima do vento |
| `wd (deg)` | graus | Direcao do vento |


Uma escolha recomendada para o trabalho e `T (degC)`, por ser uma variavel continua, de interpretacao direta e com sazonalidade diaria e anual esperada. A coluna escolhida precisa ser confirmada com o grupo antes do treinamento definitivo.


## 3. Qualidade dos dados


As verificacoes do arquivo atual encontraram:


- 420.551 linhas.
- Nenhum valor ausente representado como `NaN` nas colunas lidas.
- 327 timestamps duplicados.
- 420.543 intervalos consecutivos de 10 minutos entre 420.550 intervalos observados.
- Pequeno numero de intervalos irregulares, incluindo uma lacuna de aproximadamente 3 dias e 2 horas e outra de 16 horas.
- 18 valores `-9999` em `wv (m/s)`.
- 20 valores `-9999` em `max. wv (m/s)`.


Os valores `-9999` sao codigos de dado ausente ou invalido, nao velocidades reais. Devem ser convertidos para `NaN` antes da analise. As duplicidades e os intervalos irregulares devem ser tratados explicitamente, principalmente se a serie for reamostrada.


Estatisticas observadas:


| Coluna | Media | Minimo | Maximo |
|---|---:|---:|---:|
| `p (mbar)` | 989.2128 | 913.60 | 1015.35 |
| `T (degC)` | 9.4501 | -23.01 | 37.28 |
| `Tpot (K)` | 283.4927 | 250.60 | 311.34 |
| `Tdew (degC)` | 4.9559 | -25.01 | 23.11 |
| `rh (%)` | 76.0083 | 12.95 | 100.00 |
| `VPmax (mbar)` | 13.5763 | 0.95 | 63.77 |
| `VPact (mbar)` | 9.5338 | 0.79 | 28.32 |
| `VPdef (mbar)` | 4.0424 | 0.00 | 46.01 |
| `sh (g/kg)` | 6.0224 | 0.50 | 18.13 |
| `H2OC (mmol/mol)` | 9.6402 | 0.80 | 28.82 |
| `rho (g/m**3)` | 1216.0627 | 1059.45 | 1393.54 |
| `wv (m/s)` | 1.7022* | -9999.00 | 28.49 |
| `max. wv (m/s)` | 3.0566* | -9999.00 | 23.50 |
| `wd (deg)` | 174.7437 | 0.00 | 360.00 |


`*` As medias brutas incluem o codigo `-9999` e, portanto, nao devem ser usadas no relatorio sem limpeza previa.


## 4. Preparacao recomendada


1. Ler `Date Time` com o formato `%d.%m.%Y %H:%M:%S`.
2. Converter `-9999` para `NaN` nas colunas meteorologicas.
3. Ordenar por timestamp.
4. Verificar e documentar os 327 timestamps duplicados.
5. Definir uma regra para duplicidades: preservar a primeira observacao, agregar por media/mediana ou investigar a origem. A regra deve ser aplicada antes da reamostragem.
6. Reindexar ou reamostrar para 10 minutos apenas depois de tratar duplicidades e lacunas.
7. Preencher valores ausentes somente se a estrategia for justificada e ajustada sem utilizar informacao futura. Para Holt-Winters, pode ser preferivel remover ou tratar os intervalos problematicos de forma documentada.
8. Escolher uma coluna-alvo continua, preferencialmente `T (degC)`.
9. Separar treino e teste cronologicamente, sem embaralhar.
10. Usar validacao walk-forward no treino para escolher os parametros.


## 5. Analise exploratoria esperada


Para a coluna-alvo escolhida, produzir:


- Serie temporal completa.
- Trechos ampliados para visualizar o padrao intradiario.
- Medias por hora, dia da semana, mes e estacao do ano.
- Distribuicao dos valores.
- Grafico de ausencias e lacunas.
- Analise de valores extremos.
- ACF para identificar ciclos curtos e dependencia temporal.
- STL com periodos coerentes com a frequencia usada na modelagem.


Em uma serie de 10 minutos, um ciclo diario equivale a 144 observacoes. Um ciclo semanal equivale a 1008 observacoes. Um ciclo anual exige cuidado, porque possui muitos pontos e pode tornar o ajuste computacionalmente pesado. Se a serie for agregada para hora ou dia, os periodos sazonais precisam ser recalculados para a nova frequencia.


## 6. Implicacoes para Holt-Winters


O modelo deve usar apenas a coluna-alvo. Para temperatura, testar principalmente:


- Tendencia sem amortecimento e tendencia amortecida.
- Sazonalidade aditiva.
- Periodo diario, caso a frequencia de 10 minutos seja mantida.
- Periodo semanal, se houver memoria suficiente e custo computacional aceitavel.
- Dados agregados por hora ou dia como analise de sensibilidade, desde que o grupo mantenha um protocolo de comparacao unico.


A sazonalidade multiplicativa exige valores positivos e uma variacao proporcional ao nivel. Para temperatura em graus Celsius, a sazonalidade aditiva e mais apropriada como ponto de partida, pois a escala possui valores negativos e o zero em Celsius nao representa ausencia fisica da grandeza.


O periodo escolhido nao deve ser definido somente pelo maior valor de forca da sazonalidade na STL. Ele deve ser coerente com a frequencia final, com os graficos e com o MAE obtido na validacao walk-forward.


## 7. Riscos e limitacoes


- Duplicidades de timestamp podem alterar a frequencia efetiva e causar vazamento ou ponderacao indevida.
- Os codigos `-9999` precisam ser tratados antes de calcular estatisticas, STL ou previsoes.
- A serie e muito grande; testar todas as combinacoes de tendencia, sazonalidade e periodos pode ser caro.
- Uma sazonalidade anual em dados de 10 minutos gera um periodo muito extenso para Holt-Winters.
- A direcao do vento e uma variavel circular; nao deve ser tratada como uma temperatura ou uma escala linear comum.
- As variaveis meteorologicas sao relacionadas, mas o Holt-Winters permanece univariado; utilizar as demais colunas mudaria o modelo e o protocolo.
- A fonte e a unidade devem ser confirmadas na documentacao final do projeto.


## 8. Checklist antes da entrega


- [ ] Confirmar a coluna-alvo com o grupo.
- [ ] Converter `-9999` para ausente.
- [ ] Resolver e documentar os timestamps duplicados.
- [ ] Medir as lacunas depois da ordenacao e limpeza.
- [ ] Confirmar a frequencia usada no modelo: 10 minutos, hora ou dia.
- [ ] Recalcular os periodos sazonais conforme a frequencia final.
- [ ] Produzir STL e graficos da Base 4.
- [ ] Avaliar Holt-Winters por walk-forward, sem usar o teste para tuning.
- [ ] Registrar parametros, previsoes, residuos, MAE e tempo de execucao.

