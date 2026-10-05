# Pasta de entrega

`relatorio_v2.html` e `relatorio_v2.pdf` são as versões atualizadas para revisão. O HTML é autocontido; o arquivo-fonte e os scripts de geração ficam em `docs/relatorio/` e `src/series_temporais/reporting/`.

Para reunir os arquivos sem alterar os originais, execute `python scripts/preparar_pacote_entrega.py`. Isso cria `entrega/pacote_para_zipar/`, uma pasta **local, ignorada pelo Git e ainda não aprovada para envio**. Ela contém relatório PDF/HTML, fontes, código, notebooks, cinco `raw.csv`, metadados, resultados auditados, manifesto de hashes e `LEIA_ANTES_DE_ENVIAR.md`. Confira o manifesto e as pendências de `docs/triagem_sem_reexecucao.md` antes de compactar.

O enunciado pede PDF, HTML, fonte, código, bases/fontes, MAE consolidado e registro diário individual. O pacote preserva `results/metrics.csv`, que só contém cinco linhas XGBoost, e adiciona os 19 MAEs individuais auditados; nenhum deles é um ranking homologado. O registro diário real do grupo não está no repositório. Quando recebido, uma nova pasta de pré-entrega poderá ser gerada com `--registro-diario CAMINHO`, sem sobrescrever a atual.

Não crie o ZIP final enquanto o grupo não confirmar o registro diário, a revisão humana do PDF/HTML e como o professor aceitará as limitações metodológicas e o SARIMAX da Base 4 ausente. O nome sugerido no enunciado é `Grupo_XX_Trabalho_Series_Temporais.zip`; `XX` também não deve ser inventado.

