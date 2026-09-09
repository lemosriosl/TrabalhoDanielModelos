# Modelagem comparativa de series temporais

Estrutura colaborativa para o trabalho integrador de series temporais. O projeto compara SARIMAX, Holt-Winters, Random Forest e o modelo de especializacao do grupo em cinco bases, usando validacao walk-forward e MAE.

## Inicio rapido

1. Preencha `config/projeto.yaml` com o numero do grupo, integrantes e modelo de especializacao.
2. Registre as cinco bases em `docs/bases/` e coloque as versoes congeladas em `data/raw/base_01/` ate `base_05/`.
3. Crie ou assuma uma demanda em `collaboration/demandas.csv`.
4. Leia `AGENTS.md` e a regra relacionada a sua tarefa antes de alterar arquivos.
5. Execute a analise exploratoria, a preparacao e os experimentos pelas etapas de `docs/plano.md`.
6. Antes de concluir uma demanda, execute `pytest` e os checks descritos em `rules/checks.md`.

## Organizacao

```text
agents/              papeis e prompts dos agentes de IA
collaboration/       demandas, handoffs, revisoes e prompts usados
config/              configuracao comum das bases e experimentos
data/                dados brutos, intermediarios e processados
docs/                enunciado, decisoes, bases e metodologia
notebooks/           exploracao, modelagem e fonte do relatorio
src/series_temporais codigo reutilizavel da analise
tests/               testes unitarios e de integracao
results/             previsoes e resultados consolidados
report/              HTML, PDF e recursos visuais finais
entrega/             somente os arquivos prontos para compactacao
rules/               regras operacionais para pessoas e IAs
scripts/             comandos reproduziveis de automacao
```

Os materiais fornecidos pelo professor permanecem em `docs/Bases de exemplo/`, `docs/Pipes de exemplo/` e `docs/Documento atividade.pdf`. Eles sao referencias, nao resultados finais.

## Principios

- Nunca alterar arquivos em `data/raw/` depois do congelamento.
- Nenhuma feature pode usar informacao indisponivel na origem da previsao.
- Todos os modelos usam as mesmas origens, horizonte e conjunto de teste.
- Hiperparametros sao escolhidos sem consultar o teste final.
- Resultados finais devem ser gerados por codigo, e nao editados manualmente.
- Toda contribuicao deve possuir uma linha objetiva em `collaboration/demandas.csv`.

