# ADR-003 - Consolidação horária da Base 2

**Status:** Proposta

**Data:** 2026-09-23

## Contexto

O CSV da Base 2 possui 48.204 linhas e 40.575 timestamps distintos: há registros repetidos na mesma hora. Os quatro modelos exigem uma observação por instante para manter comparabilidade e para permitir a decomposição STL em frequência horária.

## Decisão

Na preparação exploratória, consolidar cada timestamp repetido pela média das colunas numéricas (`temp`, `rain_1h`, `snow_1h`, `clouds_all` e `traffic_volume`) e pela moda determinística (desempate alfabético) das categóricas (`holiday`, `weather_main` e `weather_description`). Reindexar depois para uma grade de uma hora, preservando lacunas como ausências e sem interpolar o alvo. Separar cronologicamente 80% para treino e 20% para teste apenas entre linhas com alvo observado.

## Alternativas consideradas

- Manter múltiplas linhas por hora: impede uma série univariada regular e dá pesos diferentes a algumas horas.
- Manter a primeira ou a última linha: escolha arbitrária que perde informação.
- Somar `traffic_volume`: as linhas são medições concorrentes para o mesmo horário, não subperíodos.
- Interpolar lacunas: descartada para preparação/modelagem porque pode introduzir informação futura.

## Consequências

Os dados brutos permanecem inalterados e o resultado é reproduzível. A média do alvo em timestamps repetidos deve ser revisada pelo grupo antes de a proposta ser marcada como aceita, pois a documentação de origem não explica a causa das repetições.
