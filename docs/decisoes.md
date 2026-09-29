# Decisões do projeto

## 2026-09-29 - Estrutura enxuta do repositório

**Decisão:** reduzir o contexto obrigatório a `AGENTS.md`, `projeto.yaml` e `tarefas.csv`; organizar cada base em `data/base_NN/`; centralizar notebooks em `notebooks/`; separar referências e entrega.

**Motivo:** o enunciado exige rastreabilidade, prevenção de vazamento e reprodução dos resultados, mas agentes e integrantes não devem precisar navegar por uma hierarquia extensa antes de trabalhar.

**Efeito:** dados brutos passam a se chamar `raw.csv` e permanecem imutáveis. Campos metodológicos ainda não definidos continuam nulos em `projeto.yaml` até confirmação humana.

**Registro de IA:** a proposta de organização e esta decisão foram elaboradas com assistência de IA e devem ser revisadas pelo grupo antes de mudanças metodológicas posteriores.
