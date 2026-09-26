# ADR-004 - Features e disponibilidade temporal

**Status:** Proposta

**Data:** 2026-09-26

## Contexto

Os notebooks de Random Forest das Bases 1 a 4 já orquestram a criação de
features por uma API comum, mas os módulos importados não estavam versionados.
Também é necessário tornar verificável que cada linha de modelagem usa apenas
informação disponível na origem da previsão.

O horizonte final do projeto ainda não foi aprovado em `config/projeto.yaml`.
Esta decisão, portanto, implementa somente o quadro reutilizável de um passo
já declarado nos notebooks, sem declarar esse passo como horizonte final dos
quatro modelos.

## Decisao

- Representar cada amostra por `origin_time` e `target_time`.
- Para a previsão de um passo, aceitar apenas pares separados exatamente pela
  frequência declarada.
- Usar o nível do alvo e covariáveis observadas até a origem, lags positivos,
  janelas históricas deslocadas e calendário da data-alvo.
- Nunca usar alvo, rótulo, data-alvo codificada como número ou covariável
  observada depois da origem como feature.
- Classificar covariáveis como conhecidas na origem, publicadas com atraso,
  conhecidas antecipadamente (calendário/feriado da data-alvo) ou proibidas.
  Variáveis atrasadas recebem deslocamento mínimo explícito. As regras por base
  ficam em `src/series_temporais/features/regras_bases.py`.
- Exigir grade temporal regular, ordenada e sem timestamps duplicados.
- Separar treino, validação e teste cronologicamente, purgando amostras cujo
  alvo cruza a fronteira seguinte.
- Não fazer imputação bidirecional. Valores ausentes permanecem ausentes e a
  linha só entra no quadro modelável quando todas as features requeridas
  estiverem disponíveis.

## Alternativas consideradas

- Criar features diretamente em cada notebook: rejeitada por duplicar lógica e
  dificultar testes de invariância ao futuro.
- Usar `train_test_split` ou validação aleatória: rejeitada por misturar passado
  e futuro.
- Preencher toda a base antes do corte: rejeitada porque interpolação,
  normalização ou imputação global pode consultar o período futuro.
- Fixar agora o horizonte final: rejeitada porque essa decisão continua
  pendente de aprovação do grupo.

## Consequencias

Os notebooks das Bases 1 a 4 passam a ter uma implementação comum e testável.
A Base 5 conserva sua engenharia semanal já existente e recebe apenas revisão.
O grupo ainda precisa aprovar horizonte, origem, período de teste e a
disponibilidade econômica das variáveis marcadas como pendentes antes da
avaliação final.
