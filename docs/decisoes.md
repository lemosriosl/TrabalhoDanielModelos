# Decisões do projeto

## 2026-09-29 - Estrutura enxuta do repositório

**Decisão:** reduzir o contexto obrigatório a `AGENTS.md`, `projeto.yaml` e `tarefas.csv`; organizar cada base em `data/base_NN/`; centralizar notebooks em `notebooks/`; separar referências e entrega.

**Motivo:** o enunciado exige rastreabilidade, prevenção de vazamento e reprodução dos resultados, mas agentes e integrantes não devem precisar navegar por uma hierarquia extensa antes de trabalhar.

**Efeito:** dados brutos passam a se chamar `raw.csv` e permanecem imutáveis. Campos metodológicos ainda não definidos continuam nulos em `projeto.yaml` até confirmação humana.

**Registro de IA:** a proposta de organização e esta decisão foram elaboradas com assistência de IA e devem ser revisadas pelo grupo antes de mudanças metodológicas posteriores.

## 2026-09-29 - Contrato único de caminhos dos notebooks

**Decisão:** todo notebook resolve a base como `data/base_NN/`. Os únicos nomes de dados derivados são `prepared.csv`, `train.csv` e `test.csv`; os dados de origem permanecem em `raw.csv`.

**Motivo:** a migração estrutural revelou referências mistas a `trabalho/bases/grupoN`, `grupoN.csv` e diretórios de execução, que podiam falhar ou criar CSVs fora da base.

**Efeito:** o módulo `series_temporais.paths` é a referência reutilizável para localizar o projeto e as bases. As células de preparação gravam explicitamente na pasta da base.
