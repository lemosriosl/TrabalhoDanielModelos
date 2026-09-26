# Registro de uso de IA

- Data: 2026-09-26
- Integrante responsavel: Auto (agente)
- Agente/ferramenta: Cursor Auto
- Demanda relacionada: melhorar feature engineering, disponibilidade temporal
  e prevenção de leakage por grupo
- Arquivos fornecidos como contexto: auditoria anterior, dicionário de
  variáveis externas, notebooks FE/RF e `features/temporal.py`
- Objetivo do prompt: tornar a disponibilidade explícita e auditável em cada
  base, sem inventar decisões pendentes
- Resumo da resposta utilizada: criado `regras_bases.py`, suporte a
  `CONHECIDO_ANTECIPADAMENTE`, inclusão de `is_holiday_alvo` na Base 2,
  catálogos com status e CSVs de disponibilidade por grupo
- Validacoes humanas realizadas: pendente confirmação de Open (Base 1) e
  taxas (Base 5)
- Alteracoes ou correcoes apos revisao: notebooks FE/RF alinhados às regras
- Evidencia final: `docs/revisoes/melhoria_disponibilidade_por_base.md` e
  testes unitários aprovados
