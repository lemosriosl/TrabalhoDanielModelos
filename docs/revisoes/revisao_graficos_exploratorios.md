# Revisão e padronização dos gráficos exploratórios

Auditoria estática dos cinco notebooks existentes. Os dados brutos e os notebooks não foram sobrescritos nesta etapa.

## Padrão obrigatório

- Uma figura por pergunta: série completa, janela representativa, perfil intraperíodo, distribuição, ausências e autocorrelação.
- Títulos e eixos em português, sempre com unidade; datas em ordem cronológica e sem embaralhamento.
- Paleta única e legível: azul para série principal, laranja para ausência/alerta, verde para sazonalidade, rosa para tendência e amarelo para resíduo.
- Mesmas dimensões, DPI, grade discreta, fonte e posição de título; salvar PNGs em `docs/revisoes/graficos/`.
- Não usar `target`, `TARGET_UP` ou qualquer variável futura nos gráficos de features; gráficos de qualidade podem mostrar esses campos apenas como auditoria.
- ACF deve indicar claramente a unidade da defasagem: dias, horas, semanas ou intervalos de 10 minutos.
- STL só deve usar série com grade fixa. Se houver interpolação para fins exploratórios, informar no título/caption que ela não alimenta o treino.

## Resultado por base

### Base 1

- Reaproveitar série, retorno, volume, ACF e STL; uniformizar títulos, unidades e salvar figuras.

### Base 2

- Manter perfis por hora/dia e mapa de ausências; declarar que a série foi regularizada e que duplicidades foram consolidadas.

### Base 3

- Corrigir a ACF para uma série horária regularizada; não usar `autocorrelation_plot` diretamente sobre dados com nulos removidos.
- Usar a interpolação apenas na etapa visual/STL e sinalizar isso no gráfico.

### Base 4


- Manter período diário de 144 e semanal de 1008 para 10 minutos; indicar unidades nos eixos e preservar marcação das lacunas.
- O gráfico deve deixar explícito que `-9999` virou ausência antes da análise.

### Base 5

- O notebook canônico usa o arquivo atual `grupo5.csv` e somente as colunas
  primitivas para reconstruir a série semanal.
- A ACF usa retorno em grade semanal regular. Semanas vazias recebem apenas o
  último estado conhecido, pela mesma função causal revisada da modelagem.
- A STL explicita no título o carregamento causal e não usa interpolação
  bidirecional.

## Ordem recomendada para a versão final

1. Reexecutar cada notebook a partir da raiz do projeto e salvar apenas PNGs gerados por código.
2. Revisar visualmente títulos, escalas, unidades, legendas, ausência de sobreposição e mensagens de interpolação.

## Estado da padronização

O estilo comum está em
`src/series_temporais/reporting/graficos_exploratorios.py`. A função
`plotar_acf` rejeita séries com ausências e exige a unidade da defasagem.

A implementação anterior não estava integralmente correta: a Base 5 apontava
para `grupo5_new.csv`, que não existe no repositório, removia semanas ausentes
antes da ACF e interpolava nos dois sentidos para a STL. Esses pontos foram
corrigidos e possuem teste estático.

Nas Bases 1 a 4 a padronização é parcial: os notebooks aplicam o estilo comum e
usam a função de ACF, mas ainda possuem cores literais, funções locais de força
e não salvam todas as figuras com `finalizar_figura`. Isso não cria leakage,
mas impede considerar a padronização visual totalmente concluída. Os scripts
citados no registro de demanda anterior também não estão presentes no
repositório atual; portanto, a geração consolidada precisa ser restaurada em
uma demanda específica antes da entrega.

### Auditoria independente (2026-09-26)

Confirmação: **a padronização gráfica não está implementada por completo**.

- Base 5: conforme (`PALETA`, `finalizar_figura`, ACF sem nulos, STL causal,
  `grupo5.csv`).
- Bases 1–4: só parcial (`aplicar_estilo` + `plotar_acf`; sem PNGs
  consolidados; cores/forças locais).
- Pasta `docs/revisoes/graficos/` ainda sem artefatos versionados.
- Detalhamento em `docs/revisoes/auditoria_features_leakage_e_graficos.md`.
