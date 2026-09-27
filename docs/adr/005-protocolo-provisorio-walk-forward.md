# ADR-005 - Protocolo provisório de avaliação walk-forward

**Status:** Aceita provisoriamente

**Data:** 2026-09-27

## Contexto

O projeto precisava executar os modelos sem postergar as evidências de P1, mas
`config/projeto.yaml` não especificava horizonte ou janela inicial. Em
27/09/2026, Matheus Bastos Castilho autorizou explicitamente um protocolo
provisório para as Bases 1 e 2.

## Decisão

- Prever **um passo à frente**.
- Usar janela de treino **expansiva**.
- Fixar o recorte final cronológico solicitado em cada base: 70%/30% na Base
  1 e 80%/20% na Base 2.
- Escolher ordens somente dentro do trecho de treino, com a cauda cronológica
  de validação; o teste final não participa da escolha.
- Manter a ordem escolhida fixa no walk-forward final.

Na Base 2, o passo é uma hora na grade regular. Horas sem alvo observado são
mantidas no estado do modelo como ausentes e não entram em métricas, resíduos
ou diagnósticos.

## Alternativas consideradas

- Divisão aleatória: rejeitada porque viola a ordem temporal.
- Escolher ordens com o teste final: rejeitada por vazamento de avaliação.
- Imputar `traffic_volume` nas lacunas da Base 2: rejeitada; a série observada
  não deve ser inventada apenas para viabilizar o modelo.

## Consequências

Os resultados ficam reprodutíveis e comparáveis entre as Bases 1 e 2. O grupo
deve substituir este ADR por uma decisão definitiva se adotar outro horizonte,
janela ou intervalo de teste para todos os modelos e bases.
