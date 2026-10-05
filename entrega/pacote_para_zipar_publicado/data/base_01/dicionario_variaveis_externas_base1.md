# Dicionário de variáveis externas — Base 1 (Bitcoin)

## Escopo

O alvo é `Close` em frequência diária e o horizonte é `t+1`. O cenário operacional assume que a origem ocorre após o fechamento de `t`. As colunas OHLCV pertencem ao mesmo arquivo da série e são covariáveis internas; calendário é variável derivada. Nenhuma fonte externa adicional foi incorporada.

| ID | Variável | Origem e unidade | Disponibilidade na origem `t` | Uso permitido | Tratamento | Status e risco |
|---|---|---|---|---|---|---|
| G1_OPEN | `Open` | Arquivo bruto; USD/BTC | Conhecida ao longo de `t`; válida no cenário pós-fechamento | `Open_t` para prever `Close_{t+1}` | Escalonar somente no treino quando necessário | Em validação; confirmar o horário de disponibilidade na fonte |
| G1_HIGH | `High` | Arquivo bruto; USD/BTC | Conhecida somente após o fechamento de `t` | `High_t` ou lags positivos | Não usar contemporaneamente para prever `Close_t` | Em validação |
| G1_LOW | `Low` | Arquivo bruto; USD/BTC | Conhecida somente após o fechamento de `t` | `Low_t` ou lags positivos | Não usar contemporaneamente para prever `Close_t` | Em validação |
| G1_VOLUME | `Volume` | Arquivo bruto; unidade conforme o provedor | Acumulada e conhecida no fechamento de `t` | `Volume_t` ou lags positivos | Considerar `log1p`; ajustar transformação apenas no treino | Em validação; unidade/metodologia precisam ser confirmadas |
| G1_CALENDAR | Dia da semana e mês | Derivada de `Date` | Conhecida antecipadamente | Codificação cíclica da data-alvo | Seno/cosseno sem ajuste com o teste | Aprovada como variável derivada |
| G1_ADJ_CLOSE | `Adj Close` | Arquivo bruto; USD/BTC | Idêntica ao alvo em todas as 2.836 linhas | Nenhum | Excluir de `prepared.csv`, features e modelos | Proibida por redundância com o alvo |

## Regras temporais

- A previsão é de `Close_{t+1}` usando somente informações disponíveis até o fechamento de `t`.
- Lags e janelas móveis devem terminar, no máximo, em `t`; janelas do alvo usadas para construir a linha de `t+1` não incluem o valor futuro.
- Transformações aprendidas, como escala, são ajustadas apenas no recorte de treino aplicável.
- O corte final é cronológico: 70% treino e 30% teste, sem embaralhamento.
- A semente comum do projeto é 42.

## Rastreabilidade

- Fonte indicada: https://www.bitget.com/price/bitcoin/historical-data
- Arquivo congelado: `data/base_01/raw.csv`
- SHA-256: `dcb86b9461168a1cc3f122a40d7aa6b53ac773a5703423320a2a90c3823c38f7`
- Frequência: diária, GMT+0 segundo a página indicada.
- Pendente antes da entrega: confirmar a proveniência direta do CSV, a data de download e a definição/unidade de `Volume`.

## Arquivos relacionados

- `documentacao.md`: fonte, qualidade, preparação e sazonalidade.
- `disponibilidade_covariaveis_base1.csv`: contrato legível por código.
- `catalogo_features_base1.csv`: features derivadas e sua disponibilidade.
