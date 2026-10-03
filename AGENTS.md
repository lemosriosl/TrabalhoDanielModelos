# Projeto de séries temporais

## Leitura obrigatória antes de qualquer demanda

1. `AGENTS.md` (este arquivo);
2. `projeto.yaml`.

Leia também `data/base_NN/metadata.yaml` ao trabalhar em uma base específica. Consulte `docs/atividade/n2_series_temporais.pdf` apenas para requisitos de entrega ou interpretação metodológica.

## Regras essenciais

- Trabalhe em uma demanda por vez e registre as decisões metodológicas relevantes em `docs/decisoes.md`.
- `data/base_NN/raw.csv` é congelado e imutável. Todo dado preparado deve ser reproduzível a partir dele.
- Nunca use valores futuros observados como feature. Transformações, seleção de features e tuning usam somente o passado disponível em cada origem.
- Os quatro modelos usam as mesmas origens, horizonte e observações de teste. O teste final é walk-forward, com hiperparâmetros já congelados.
- Calcule MAE somente em previsões fora da amostra. Entre bases, compare vitórias e posição média; não faça média bruta de MAE.
- Funções reutilizáveis ficam em `src/series_temporais/`; notebooks orquestram, documentam e interpretam.
- Resultados em `results/` são gerados por código e não devem ser editados manualmente.
- Toda nova lógica metodológica deve ter teste em `tests/`. Registre decisões estruturais em `docs/decisoes.md` antes da mudança.

## Estrutura rápida

- `data/`: uma pasta autocontida por base.
- `notebooks/`: exploração, preparação e modelos existentes.
- `references/`: materiais de aula; não fazem parte do pipeline.
- `docs/`: enunciado, decisões e referências.
- `entrega/`: apenas artefatos finais gerados.

Campos ainda indefinidos em `projeto.yaml` não devem ser inventados: registre a pendência em `docs/decisoes.md`. A planilha operacional de demandas é mantida fora do repositório pelo grupo.

