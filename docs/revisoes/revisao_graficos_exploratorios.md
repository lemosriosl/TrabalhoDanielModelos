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

- O notebook legado de EDA permanece incompatível com a fonte atual: espera `GOLD_PRICE`, `TREASURY_10Y` e `FED_FUNDS_RATE`.
- A EDA canônica foi criada em `trabalho/bases/grupo5/graficos_exploratorios_base5.ipynb` usando `DATE` e `VALUE`; `TARGET_UP` e `IS_HOLIDAY` ficam fora dos gráficos da série.
- A série semanal é regularizada apenas para ACF/STL; a interpolação da STL é identificada no título e não alimenta o treino.

## Ordem recomendada para a versão final

1. Reexecutar cada notebook a partir da raiz do projeto e salvar apenas PNGs gerados por código.
2. Revisar visualmente títulos, escalas, unidades, legendas, ausência de sobreposição e mensagens de interpolação.

## Estado da padronização

O estilo comum está em `src/series_temporais/reporting/graficos_exploratorios.py` e foi conectado aos notebooks de gráficos das Bases 1 a 4. A função `plotar_acf` rejeita séries com ausências e exige a unidade da defasagem. A Base 5 possui notebook exploratório compatível com o CSV atual. A execução visual completa ainda depende das dependências de notebook e dos artefatos preparados de cada base.
