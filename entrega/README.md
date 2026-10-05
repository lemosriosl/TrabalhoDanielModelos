# Pasta de entrega

`relatorio_v2.html` e `relatorio_v2.pdf` são as versões atualizadas para revisão. O HTML é autocontido; o arquivo-fonte e os scripts de geração ficam em `docs/relatorio/` e `src/series_temporais/reporting/`.

`relatorio.html` é a versão anterior. `relatorio_modelos_por_base.md`, acrescentado por outro integrante no remoto, é um texto teórico suplementar: não substitui o relatório v2 e contém afirmações gerais que não foram usadas para homologar métricas ou ranking. Esses dois arquivos não entram na pasta preparada para ZIP.

Para reunir os arquivos sem alterar os originais, execute `python scripts/preparar_pacote_entrega.py --destino entrega/pacote_para_zipar_NOME`. Isso cria uma pasta nova. A pasta **versionada no Git para revisão e futura compactação** é `entrega/pacote_para_zipar_publicado/`; as montagens locais anteriores `pacote_para_zipar/` e `pacote_para_zipar_revisado/` estão ignoradas e não devem ser usadas. A pasta publicada contém relatório PDF/HTML, fontes, código, notebooks, cinco `raw.csv`, metadados, resultados auditados, manifesto de hashes e `LEIA_ANTES_DE_ENVIAR.md`. Confira o manifesto e as pendências de `docs/triagem_sem_reexecucao.md` antes de compactar. Estar no Git não significa que a entrega integral esteja aprovada.

Para sincronizar **somente** uma pasta gerada cujo manifesto ainda esteja íntegro, execute `python scripts/preparar_pacote_entrega.py --destino entrega/pacote_para_zipar_publicado --atualizar`. A atualização recusa alterações manuais ou arquivos inesperados. As figuras SARIMAX do pacote são produzidas por código a partir das previsões já existentes, sem novo treinamento.

O enunciado pede PDF, HTML, fonte, código, bases/fontes, MAE consolidado e registro diário individual. O pacote preserva `results/metrics.csv`, que só contém cinco linhas XGBoost, e adiciona os 19 MAEs individuais auditados; nenhum deles é um ranking homologado. O registro diário real do grupo não está no repositório. Quando recebido, uma nova pasta de pré-entrega poderá ser gerada com `--registro-diario CAMINHO`, sem sobrescrever a atual.

Não crie o ZIP final enquanto o grupo não confirmar o registro diário, a revisão humana do PDF/HTML e como o professor aceitará as limitações metodológicas e o SARIMAX da Base 4 ausente. O nome sugerido no enunciado é `Grupo_XX_Trabalho_Series_Temporais.zip`; `XX` também não deve ser inventado.

