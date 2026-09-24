# Registro de uso de IA — Bases 1 e 2

- Data: 2026-09-23
- Integrante responsável: Matheus Bastos Castilho (P1)
- Agente/ferramenta: Codex
- Demanda relacionada: limpeza/preparação, gráficos exploratórios e STL das Bases 1 e 2.
- Arquivos fornecidos como contexto: `AGENTS.md`, regras de dados/experimentos, notebooks e artefatos das Bases 3 e 4, CSVs das Bases 1 e 2.
- Objetivo do prompt: preparar as bases sem alterar dados brutos, reproduzir o padrão das Bases 3 e 4 e produzir exploração/STL.
- Resumo da resposta utilizada: foi criado módulo reutilizável, quatro notebooks executados e artefatos derivados. A Base 2 consolida horários repetidos com média numérica e moda categórica, conforme ADR-003 em status de proposta.
- Validações humanas realizadas: conferência dos CSVs brutos, verificação de ordenação/divisão cronológica, execução dos notebooks e `pytest`.
- Alterações ou correções após revisão: pendente de revisão do grupo para aceitar ou alterar a regra de consolidação da Base 2.
- Evidência final: `src/series_temporais/data/preparacao_bases_1_2.py`, `trabalho/bases/grupo1/`, `trabalho/bases/grupo2/` e ADR-003.
