# Melhoria por base — disponibilidade e leakage

**Data:** 2026-09-26  
**Responsável:** Auto (agente)

## O que mudou

A disponibilidade deixou de ser só textual nos notebooks e passou a ser
código versionado por base.

| Base | Melhoria principal |
| --- | --- |
| 1 | `BASE_1` com `Adj Close` proibida; OHLC/Volume com status `em_validacao` |
| 2 | `is_holiday_alvo` conhecido antecipadamente; clima textual proibido |
| 3 | `BASE_3` + proibição explícita de `No`/`station`/`wd` |
| 4 | `BASE_4` + proibição de `wd (deg)` bruto |
| 5 | Catálogo com taxas `provisorio`; `TARGET`/lags diários excluídos |

## Artefatos novos

- `src/series_temporais/features/regras_bases.py`
- `Disponibilidade.CONHECIDO_ANTECIPADAMENTE` em `temporal.py`
- `trabalho/bases/grupoN/disponibilidade_covariaveis_baseN.csv`
- Catálogos com colunas `status` e `nota`

## Testes

`pytest` de features, Base 5, validação temporal e estrutura: aprovados.
