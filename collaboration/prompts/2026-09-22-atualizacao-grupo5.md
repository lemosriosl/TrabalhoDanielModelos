# Prompt de IA — atualização da base 5

**Responsável:** Codex (agente)  
**Data:** 2026-09-22

## Solicitação do usuário

> Consegue atualizar o MD e o ipynb que anexei, ele se encontra na pasta grupo5, pois o csv mudou, temos o old e o new, o que está feito está feito para o old refaça para o new

## Influência no trabalho

O pedido motivou a troca da leitura do CSV antigo pelo `grupo5_new.csv` no notebook e a revisão da ficha técnica. A inspeção local mostrou as mesmas datas e cotações nos dois arquivos, separador `;` no novo e duas colunas novas. A verificação de `TARGET_UP` confirmou sua dependência do preço da próxima linha; por isso ele foi mantido apenas na auditoria, fora das features. O indicador `IS_HOLIDAY` também ficou fora das features até confirmação de proveniência e disponibilidade.
