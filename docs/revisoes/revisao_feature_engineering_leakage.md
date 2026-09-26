# Revisão de feature engineering, disponibilidade e leakage

## Escopo

Revisão das cinco bases e implementação da infraestrutura comum usada pelos
notebooks de Random Forest. O horizonte final do trabalho continua pendente;
os quadros atuais são de um passo e não alteram essa decisão do grupo.

## Implementação comum

- `features/temporal.py` valida ordem, unicidade e regularidade da grade.
- Cada amostra registra separadamente origem e data-alvo.
- Lags são estritamente positivos; janelas são deslocadas e terminam em
  `t-1`; o nível em `t` aparece uma única vez em `level_t`.
- Covariáveis podem ser classificadas como disponíveis na origem, publicadas
  com atraso explícito ou proibidas.
- Linhas incompletas são removidas do quadro modelável; não há `bfill`,
  interpolação bidirecional, escala ou imputação ajustada com o futuro.
- O corte treino/teste e as dobras expansivas purgam qualquer alvo que alcance
  a primeira origem do período seguinte.
- Testes de invariância alteram observações futuras e comprovam que features
  de origens anteriores permanecem idênticas.

## Disponibilidade por base

### Base 1 — Bitcoin

- Alvo: `Close`; calendário da data-alvo é conhecido antecipadamente.
- `Open`, `High`, `Low` e `Volume` entram no estado completo de `t` para prever
  `t+1`. Não entram valores de `t+1`.
- `Adj Close` permanece excluída por duplicar o alvo.
- A disponibilidade intradiária de `Open` continua pendente, mas não afeta o
  cenário atual após o fechamento de `t`.

### Base 2 — tráfego

- Alvo: `traffic_volume`; feriado e calendário são conhecidos antecipadamente.
- Temperatura, chuva, neve e nuvens observadas entram apenas em `t` para prever
  `t+1`; previsão meteorológica futura não foi simulada.
- Categorias meteorológicas contemporâneas foram conservadoramente excluídas
  do quadro atual.

### Base 3 — PM2.5

- Poluentes e meteorologia entram somente no estado observado em `t`.
- `No` e `station` permanecem excluídos.
- Ausências não são interpoladas globalmente; a linha só é modelável quando o
  histórico requerido está disponível.

### Base 4 — clima de Jena

- Alvo provisório dos notebooks: `T (degC)`.
- Demais medições entram em `t` para prever `t+1`; direção do vento usa
  representação circular já preparada.
- `-9999`, duplicidades e lacunas devem continuar tratados antes das features.

### Base 5 — ouro

- A engenharia semanal existente foi preservada e movida para
  `data/preparacao_base5.py`, pois o notebook importava esse módulo, mas ele não
  estava no repositório.
- A grade `W-FRI` usa a última observação disponível; semanas vazias carregam
  somente o último estado passado. São mantidos cobertura e idade da cotação.
- As 49 features são reconstruídas a partir das quatro colunas primitivas. As
  derivações entregues no CSV e o `TARGET` original ficam fora de `X`.
- O quadro contém 2.344 origens modeláveis; o corte de 75% resulta em 1.757
  linhas de treino, uma fronteira purgada e 586 linhas de teste.
- Fonte, unidade, revisão e horário de publicação das taxas continuam
  pendentes; por isso a classificação econômica delas ainda não está aprovada.

## Evidência reproduzível

Os quadros das Bases 1 a 4 reproduzem os números exibidos nos notebooks:

- Base 1: 2.805 origens, 23 features; 1.962 treino e 842 teste após purga.
- Base 2: 16.859 origens, 21 features; 13.486 treino e 3.372 teste.
- Base 3: 14.231 origens, 29 features; 11.383 treino e 2.847 teste.
- Base 4: 414.150 origens, 33 features; 331.319 treino e 82.830 teste.

Os testes automatizados cobrem lags, janelas, classificação de disponibilidade,
grade irregular, invariância ao futuro, cortes purgados e a revisão da Base 5.

## Bloqueios para a avaliação final

Ainda não se deve declarar o protocolo final pronto: `config/projeto.yaml` não
define horizonte, janela inicial, alvo/frequência das bases nem período de
teste comum. O ADR-004 permanece como proposta até aprovação do grupo.

## Auditoria independente (2026-09-26)

Revisão cruzada do código, notebooks, catálogos e testes unitários:

- **Leakage no quadro de um passo:** sem bloqueadores. Lags positivos, janelas
  em `t-1`, calendário da data-alvo, purga na fronteira e choque futuro
  preservando features anteriores.
- **Disponibilidade:** coerente com o cenário pós-fechamento / estado em `t`
  para prever `t+1`; confirmações econômicas (taxas da Base 5, `Open`
  intradiário, etc.) seguem em `docs/decisoes_pendentes.md`.
- **Pytest:** 17 testes em features, validação temporal, Base 5 e gráficos
  aprovados com `MPLBACKEND=Agg`.
- Relatório completo: `docs/revisoes/auditoria_features_leakage_e_graficos.md`.

## Melhoria por base (2026-09-26)

A disponibilidade passou a ser código compartilhado em
`src/series_temporais/features/regras_bases.py`:

- `CONHECIDO_ANTECIPADAMENTE` para calendário/feriado da data-alvo.
- Base 2 inclui `is_holiday_alvo` (aprovado no dicionário).
- Cada grupo gera `disponibilidade_covariaveis_baseN.csv` além do catálogo.
- Detalhe: `docs/revisoes/melhoria_disponibilidade_por_base.md`.
