# Revisão da limpeza e preparação das bases

Gerado por `scripts/revisar_bases.py` em modo somente leitura. Os CSVs de origem não foram alterados.

## Conclusão executiva

A documentação identifica corretamente os principais riscos, mas a preparação ainda não está pronta para a modelagem final. As pendências mais importantes são: aprovar a regra de duplicidades das Bases 2 e 4; definir imputação temporal das Bases 3 e 4; impedir covariáveis contemporâneas no alvo futuro; e preencher alvo, horizonte, frequência e protocolo comum no `config/projeto.yaml`.

## Auditoria por base

### Base 1 — Bitcoin

**Decisões e correções necessárias**

- Aprovado como série diária estrutural: sem duplicidades, sem nulos no alvo e com grade diária completa.
- Manter `Adj Close` somente na auditoria; removê-la das features por duplicar `Close`.
- Usar `High`, `Low`, `Close` e `Volume` apenas defasados quando o alvo for o fechamento futuro.
- Ainda falta comprovar a origem direta pela Bitget, unidade do volume e disponibilidade de `Open`.

### Base 2 — tráfego I-94

**Decisões e correções necessárias**

- Há 7629 timestamps repetidos em 5445 grupos; a agregação por média/moda do notebook é uma decisão metodológica ainda não aprovada.
- Conservar `holiday=None` como categoria de não-feriado, sem transformá-lo em nulo.
- A grade horária deve ser regularizada antes da modelagem, mas o alvo ausente não deve ser imputado automaticamente.
- Clima contemporâneo é observado durante/depois da hora: usar somente defasado ou previsão meteorológica disponível na origem.

### Base 3 — PM2.5 em Pequim

**Decisões e correções necessárias**

- A grade horária está completa, mas existem ausências internas nas variáveis; o alvo tem 925 nulos e não pode ser imputado com futuro.
- Excluir `No` e `station` das features; `No` é apenas índice e `station` é constante.
- PM10, gases e meteorologia são simultâneos ao PM2.5: usar lags ou previsões, nunca valores contemporâneos do alvo futuro.
- Imputação de covariáveis deve ser ajustada dentro de cada origem de treino, sem preencher globalmente antes do walk-forward.

### Base 4 — clima de Jena

**Decisões e correções necessárias**

- Existem 327 timestamps duplicados e 38 códigos `-9999`; o notebook identifica ambos, mas a regra de consolidação por média precisa ser aprovada.
- A grade esperada tem 420768 linhas e possui 544 timestamps ausentes; manter lacunas explícitas antes de decidir imputação.
- Converter `-9999` para ausente antes de estatísticas, STL e modelagem; não tratar como velocidade real.
- Se `T (degC)` for o alvo, as demais variáveis simultâneas só podem entrar defasadas nos modelos multivariados.

### Base 5 — ouro


**Decisões e correções necessárias**

- Há 368 preços ausentes; preservar essas linhas na auditoria e removê-las apenas da tabela de modelagem.
- `TARGET_UP` reproduz a comparação com a próxima linha, mas é rótulo futuro e nunca feature; além disso, zero mistura casos com preço ausente.
- `IS_HOLIDAY` não é máscara de ausência: a origem e a disponibilidade do calendário precisam ser confirmadas antes do uso.
- Definir explicitamente se o horizonte é de dia civil ou próxima cotação observada; os intervalos podem variar.


## Critérios para considerar a preparação pronta

1. Cada base tem fonte, checksum, período, frequência, alvo e unidade confirmados.
2. Duplicidades e lacunas têm regra versionada e evidência antes/depois.
3. Nulos do alvo são removidos somente da modelagem; covariáveis são imputadas apenas com o passado de cada origem.
4. Todas as features contemporâneas são deslocadas quando não estão disponíveis na origem.
5. A mesma definição de origem, horizonte e teste é usada nos quatro modelos.
6. O pipeline e os testes reproduzem os artefatos; os CSVs brutos permanecem intactos.

## Status

- Base 1: limpeza estrutural aprovada; documentação de origem/disponibilidade pendente.
- Base 2: parcialmente preparada; regra de duplicidade e disponibilidade meteorológica pendentes.
- Base 3: estruturalmente organizada; imputação e defasagem das covariáveis pendentes.
- Base 4: limpeza inicial correta; duplicidades, lacunas e alvo/frequência final pendentes.
- Base 5: auditoria exploratória consistente; alvo/horizonte e uso das colunas fornecidas pendentes.
