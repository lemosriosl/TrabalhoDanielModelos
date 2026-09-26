# Registro de uso de IA

- Data: 2026-09-26
- Integrante responsavel: Auto (agente)
- Agente/ferramenta: Cursor Auto
- Demanda relacionada: feature engineering, disponibilidade temporal,
  prevenção de leakage e revisão dos gráficos exploratórios
- Arquivos fornecidos como contexto: `AGENTS.md`, `config/projeto.yaml`,
  `rules/`, documentação e notebooks das cinco bases
- Objetivo do prompt: implementar features causais, validar a disponibilidade
  das covariáveis, impedir vazamento e verificar a padronização gráfica
- Resumo da resposta utilizada: criação do pipeline comum de features e cortes
  purgados, restauração da preparação semanal da Base 5, testes de invariância
  ao futuro e correção da EDA da Base 5
- Validacoes humanas realizadas: pendente revisão do grupo sobre horizonte,
  origem comum, alvos finais e disponibilidade econômica das taxas da Base 5
- Alteracoes ou correcoes apos revisao: a revisão gráfica anterior foi
  reclassificada como parcial; referências a arquivos inexistentes foram
  removidas do notebook da Base 5
- Evidencia final: `docs/revisoes/revisao_feature_engineering_leakage.md` e
  testes em `tests/unit/`
