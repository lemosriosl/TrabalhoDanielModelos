# Pasta de entrega N2

`pacote_para_zipar_publicado/` é a pasta versionada para compactar. Seu conteúdo
segue somente as sete categorias da seção 13 do enunciado: PDF, HTML, fonte do
relatório, códigos de análise, cinco bases, resultados por MAE e registro de
demandas. Os arquivos internos de triagem, testes, versões antigas e ranking
descritivo não homologado permanecem fora do pacote.

O arquivo `results/metricas_individuais_auditadas.csv` consolida 19 MAEs
documentados. SARIMAX da Base 4 não possui avaliação extensa; o CSV não declara
vencedores nem posição média. O registro fornecido pelo grupo está copiado como
`registro_demandas.pdf`; conferir com o professor sua adequação ao formato diário.
Os CSVs integrais de previsões não estão todos disponíveis e, portanto, não
entram na pasta. As ressalvas metodológicas continuam no relatório.

Para gerar uma nova pasta sem substituir outra, use
`python scripts/montar_pacote_escopo_n2.py --registro-diario CAMINHO_DO_PDF --destino PASTA_NOVA`.
As pastas locais antigas `pacote_para_zipar/` e `pacote_para_zipar_revisado/`
estão ignoradas pelo Git; não são a versão publicada. O ZIP único para a
Plataforma Odete ainda deve ser criado a partir de
`pacote_para_zipar_publicado/` após a revisão humana final.

