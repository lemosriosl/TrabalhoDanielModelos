# Auditoria independente — features, leakage e gráficos

**Data:** 2026-09-26  
**Responsável:** Auto (agente)  
**Escopo:** revisão de feature engineering, disponibilidade temporal, prevenção
de leakage e verificação da padronização dos gráficos exploratórios.

## Veredito

| Tema | Status | Comentário |
| --- | --- | --- |
| Feature engineering (Bases 1–4) | Adequado para 1 passo | API comum causal; sem bloqueador de leakage no quadro atual |
| Feature engineering (Base 5) | Adequado para 1 semana | Preparação semanal causal; `TARGET`/derivações do CSV fora de `X` |
| Disponibilidade temporal | Parcialmente documentada | Classificação operacional ok; confirmação econômica ainda pendente |
| Prevenção de leakage | Adequada no código testado | Lags, janelas, purga e choque futuro cobertos por pytest |
| Gráficos exploratórios | Padronização parcial | Base 5 completa; Bases 1–4 incompletas; scripts citados ausentes |

Protocolo final do trabalho **não** está pronto: horizonte, janela inicial e
identidade das bases em `config/projeto.yaml` continuam nulos; ADR-004 segue
como proposta.

## Feature engineering e leakage

### O que está correto

- `build_one_step_frame` exige grade regular, ordenada e sem duplicatas.
- Cada amostra tem `origin_time` e `target_time`; o alvo previsto não entra em `X`.
- Lags são estritamente positivos; rolling usa `shift(1)` e termina em `t-1`.
- Calendário cíclico usa a data-alvo (conhecida antecipadamente).
- Linhas incompletas saem por `dropna`; não há `bfill` nem interpolação no
  quadro modelável.
- `chronological_train_test` e `purged_time_series_splits` removem alvos que
  cruzam a fronteira seguinte.
- Base 5 reconstrói features só com `DATE`, `GOLD_PRICE`, `TREASURY_10Y` e
  `FED_FUNDS_RATE`; `ffill` semanal é causal; semanas vazias carregam só o
  passado.
- Notebooks de FE por base exportam catálogo e checam invariância ao futuro.

### Disponibilidade por base (estado atual)

| Base | Política atual | Pendência |
| --- | --- | --- |
| 1 | OHLC/Volume de `t` após fechamento para prever `t+1`; `Adj Close` fora | Disponibilidade intradiária de `Open` |
| 2 | Meteorologia observada em `t`; categorias textuais fora; `holiday` ainda não vira feature | Agregação de timestamps repetidos / fuso |
| 3 | Poluentes e meteo em `t`; `No`/`station` fora; sem interpolação global | Imputação por dobra de treino, se necessária |
| 4 | Medições em `t`; vento circular; alvo provisório `T (degC)` | `-9999`, duplicidades, frequência final |
| 5 | Estado semanal em `t`; taxas como `na_origem` provisório | Fonte/unidade/atraso de publicação das taxas |

Nenhum notebook passa `availability=` explícito: todos usam o padrão
`NA_ORIGEM`, coerente com o cenário “estado de `t` → prever `t+1`”.

### Evidência executada

```text
MPLBACKEND=Agg python3 -m pytest \
  tests/unit/test_features_temporais.py \
  tests/unit/test_validacao_temporal.py \
  tests/unit/test_grupo5_preparacao.py \
  tests/unit/test_graficos_exploratorios.py -q
```

Resultado: 17 testes aprovados.

## Gráficos exploratórios — a padronização está correta?

**Resposta curta:** parcialmente. O padrão visual existe e a Base 5 o segue;
as Bases 1–4 ainda não estão padronizadas de ponta a ponta.

### O que o padrão exige

Definido em `src/series_temporais/reporting/graficos_exploratorios.py` e
documentado em `docs/revisoes/revisao_graficos_exploratorios.md`:

- `aplicar_estilo`, `PALETA`, `finalizar_figura`, `plotar_acf`
- títulos/eixos em português com unidade
- ACF sem ausências e com unidade da defasagem
- STL só em grade fixa; interpolação exploratória, se houver, deve ser
  sinalizada e não alimentar treino
- PNGs em `docs/revisoes/graficos/`

### Conformidade observada

| Item | Base 1 | Base 2 | Base 3 | Base 4 | Base 5 |
| --- | --- | --- | --- | --- | --- |
| `aplicar_estilo` | sim | sim | sim | sim | sim |
| `plotar_acf` com unidade | sim | parcial | sim | sim | sim |
| `PALETA` / sem hex solto | não | não | não | não | sim |
| `finalizar_figura` + PNG | não | não | não | não | sim |
| `forca_*` do módulo comum | não | não | não | não | n/a |
| Interpolação bidirecional na STL | não | não | sim* | sim* | não |
| Pasta `docs/revisoes/graficos/` gerada | — | — | — | — | vazia no repo |

\*Bases 3 e 4 interpolam só para STL exploratória e o texto do notebook declara
que isso não alimenta o treino — aceitável para EDA, desde que permaneça
explícito.

### Lacunas que impedem “padronização concluída”

1. Bases 1–4 ainda usam cores literais e funções locais de força sazonal/
   tendência.
2. Bases 1–4 não salvam figuras via `finalizar_figura`; não há PNGs
   consolidados em `docs/revisoes/graficos/`.
3. `collaboration/demandas.csv` cita
   `scripts/revisar_graficos_exploratorios.py` e
   `scripts/gerar_graficos_exploratorios.py`, mas esses scripts **não existem**
   no repositório.
4. `eda_preparacao_base_5_ouro.ipynb` ainda aponta para `grupo5_new.csv`
   (arquivo inexistente); o notebook canônico de gráficos já usa `grupo5.csv`.

Essas lacunas **não criam leakage**; afetam só a padronização visual e a
reprodutibilidade das figuras da entrega.

## Bloqueios remanescentes (não de código)

- Aprovar ADR-004 e preencher horizonte/janela/alvos em `config/projeto.yaml`.
- Confirmar disponibilidade econômica das taxas e de `IS_HOLIDAY`/`TARGET_UP`
  na Base 5.
- Concluir padronização gráfica das Bases 1–4 e restaurar geração consolidada
  de PNGs.

## Conclusão operacional

Pode-se seguir com modelagem de um passo usando a API atual sem evidência de
vazamento temporal no feature store. Não se deve declarar a revisão gráfica
como concluída: falta alinhar Bases 1–4 ao módulo comum e gerar os artefatos
PNG. O protocolo comparativo final dos quatro modelos continua bloqueado pelas
decisões pendentes do grupo.
