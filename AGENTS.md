# Trabalho de series temporais

O enunciado oficial esta em `docs/Documento atividade.pdf`. O plano executavel esta em `docs/plano.md`.

## Processo obrigatorio

- Antes de trabalhar, leia este arquivo, `config/projeto.yaml` e a regra aplicavel em `rules/`.
- Consulte `collaboration/demandas.csv`; trabalhe em uma demanda por vez e identifique o responsavel.
- Nao invente numero do grupo, integrantes, modelo de especializacao, bases, horizonte ou frequencia. Se estiverem pendentes, registre em `docs/decisoes_pendentes.md`.
- Decisoes metodologicas estruturais devem ser registradas em `docs/adr/` antes de alterar o pipeline.
- Use `collaboration/handoffs/` para transferir trabalho incompleto entre pessoas ou agentes.
- Registre prompts de IA que influenciem codigo, metodologia ou interpretacao em `collaboration/prompts/`.

## Dados e prevencao de vazamento

- `data/raw/` e imutavel depois do congelamento. Nunca sobrescreva, limpe ou complete dados nessa pasta.
- Transformacoes devem gerar artefatos em `data/interim/` ou `data/processed/`.
- Ajuste de imputacao, escala, encoding, selecao de features e hiperparametros usa somente o passado disponivel em cada origem.
- Variaveis externas futuras so podem ser usadas se forem conhecidas antecipadamente ou se representarem uma previsao disponivel na origem.
- Lags e janelas moveis devem ser deslocados de forma a excluir o valor-alvo previsto.

## Comparabilidade

- SARIMAX, Holt-Winters, Random Forest e o modelo de especializacao usam as mesmas origens, horizonte e teste por base.
- Random Forest e o modelo de especializacao usam o mesmo conjunto de features quando compativeis.
- MAE e calculado apenas sobre previsoes fora da amostra do walk-forward.
- Nao calcular media direta de MAE entre bases de escalas diferentes; usar vitorias e posicao media.
- Hiperparametros permanecem fixos durante o teste final.

## Codigo e resultados

- Logica reutilizavel pertence a `src/series_temporais/`; notebooks devem orquestrar e explicar, nao duplicar funcoes extensas.
- Use caminhos relativos a raiz e configuracao central em `config/projeto.yaml`.
- Fixe sementes aleatorias e registre versoes, parametros, tempo, previsoes e residuos.
- Todo codigo metodologico novo deve possuir teste adequado em `tests/`.
- Nao editar manualmente arquivos consolidados em `results/` nem os relatorios finais.

## Onde olhar

- `agents/README.md`: divisao sugerida entre agentes de IA.
- `rules/data.md`: congelamento, qualidade e disponibilidade temporal.
- `rules/experiments.md`: protocolo experimental.
- `rules/checks.md`: definicao de pronto.
- `rules/handoff.md`: formato de transferencia de contexto.
- `docs/adr/README.md`: como registrar decisoes.

