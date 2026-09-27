# Registro de uso de IA — início do SARIMAX

- Data: 2026-09-27
- Integrante responsável: Matheus Bastos Castilho (P1)
- Agente/ferramenta: Codex
- Demanda relacionada: SARIMAX, registro de parâmetros/tempo, métricas, resíduos, ACF e Ljung–Box.
- Arquivos fornecidos como contexto: regras do projeto, ADR-004, divisão temporal, regras de covariáveis e notebooks de Holt-Winters/Random Forest.
- Objetivo do prompt: iniciar uma implementação SARIMAX comparável e sem vazamento temporal.
- Resumo da resposta utilizada: módulo reutilizável que recebe protocolo/configuração externamente, defasa covariáveis observadas, executa walk-forward de um passo causal e gera previsões, métricas e Ljung–Box.
- Validações humanas realizadas: teste automatizado de exógenas defasadas e de corte temporal; `2 passed`.
- Alterações ou correções após revisão: avaliação real das cinco bases continua dependente do horizonte, origens e teste comum aprovados pelo grupo.
- Evidência final: `src/series_temporais/models/sarimax.py` e `tests/unit/test_sarimax.py`.
