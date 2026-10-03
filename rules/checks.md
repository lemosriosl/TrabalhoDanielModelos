# Definicao de pronto

Antes de concluir uma demanda:

1. Executar `pytest` e corrigir regressões aplicaveis.
2. Confirmar que `data/base_NN/raw.csv` nao foi alterado.
3. Verificar ausencia de vazamento temporal nas features, transformacoes e tuning.
4. Confirmar que resultados foram gerados por codigo e incluem configuracao suficiente para reproducao.
5. Atualizar `docs/decisoes.md` quando houver decisao metodologica.
6. Solicitar revisao de outra pessoa ou agente para mudancas de alta complexidade.
7. Criar um handoff em `docs/handoffs/` se houver trabalho incompleto.
