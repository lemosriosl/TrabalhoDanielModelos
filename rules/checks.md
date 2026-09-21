# Definicao de pronto

Antes de concluir uma demanda:

1. Confirmar que a demanda possui responsavel, evidencia e status em `collaboration/demandas.csv`.
2. Executar `pytest` e corrigir regressões aplicaveis.
3. Confirmar que arquivos brutos nao foram alterados.
4. Verificar ausencia de vazamento temporal nas features, transformacoes e tuning.
5. Confirmar que resultados foram gerados por codigo e incluem configuracao suficiente para reproducao.
6. Atualizar documentacao ou ADR quando houver decisao metodologica.
7. Solicitar revisao de outra pessoa ou agente para mudancas de alta complexidade.
8. Criar um handoff se houver trabalho incompleto.

