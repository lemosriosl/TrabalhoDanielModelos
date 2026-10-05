# Decisões do projeto

## 2026-10-04 - Entrega v2 com resultados descritivos e limites de comparação

**Decisão:** publicar no repositório o código gerador e o HTML v2 atualizado do site local, incluindo MAE e número de origens de cada execução disponível. Os valores são apresentados como resultados individuais, sem ranking ou vencedor geral: as Bases 1–4 têm conjuntos de teste diferentes, a Base 4 ainda não tem SARIMAX final, e a igualdade origem a origem dos quatro modelos da Base 5 não foi comprovada. O resultado SARIMAX parcial da Base 4 não recebe MAE na matriz.

**Evidência e limite:** XGBoost vem de `results/metrics.csv`; Random Forest, da extração versionada dos notebooks; SARIMAX final das Bases 1, 2, 3 e 5 e Holt-Winters vêm dos CSVs locais de previsões. Diferenças de preparação, histórico de features e corte de teste são hipóteses plausíveis para a divergência, não causas integralmente comprovadas. O relatório explicita essa incerteza e não mistura MAEs de bases ou amostras distintas.

## 2026-10-04 - Relatório v2 inspirado no Rondo

**Decisão:** preservar o relatório v1 e gerar v2 autocontida com conteúdo acadêmico verificado e referência Rondo como direção visual. Adotar abertura escura, cartões translúcidos, navegação horizontal e seções claras; não incorporar músicas, preços ou mídia comercial do exemplo. Respeitar redução de movimento e impressão completa. Sincronizar main em 906e81a preservando decisões locais e stash de segurança recuperável. Atualizar somente na v2 os resultados XGBoost versionados e sua cadência, sem usar SARIMAX local em andamento.

## 2026-10-04 - Entrega restrita ao XGBoost

**Responsável e status:** Codex, a pedido de Giovanne; entrega separada e revisada. Após a revisão dos 25 arquivos e aprovação dos 103 testes, Giovanne autorizou commit no padrão histórico e push normal da branch `codex/xgboost-base5-price`, sem merge na main.

**Decisão:** integrar `origin/main` até `adb8e6d` por fast-forward e preservar a extração remota de métricas RF. A entrega local contém apenas XGBoost, auxiliares reutilizáveis, testes, documentação e `results/metrics.csv` gerado por código. Notebooks RF, SARIMAX e Holt-Winters permanecem idênticos ao remoto. Alterações e reexecuções RF foram preservadas no stash de segurança `backup antes de separar entrega XGBoost dos RF 2026-10-04` e não fazem parte desta entrega.

**Protocolo:** registrar 7/24/24/144/4 origens de reajuste exclusivamente em `intervalo_retreino_xgboost_por_base`. Não impor essa cadência ao RF nem exigir sua reexecução. Comparações finais devem conferir alvos, origens e horizonte e declarar as diferentes cadências de reajuste. Testes XGBoost não dependem de alterações em notebooks de outra pessoa.

**Artefatos:** preservar os resultados XGBoost existentes, os dados brutos e o `.gitignore`. CSVs completos de resíduos permanecem locais/ignorados; o consolidado versionável é `results/metrics.csv`. A publicação automática está pausada. O processo RF antigo não integra esta entrega; seu verificador de alterações concorrentes impede substituir o notebook restaurado, preservando o resultado em diretório temporário caso termine.

## 2026-10-04 - Informações sincronizadas e resultados parciais

**Decisão:** preencher o relatório somente com evidências rastreadas em origin/main (adb8e6dbfacec244fb2ede2194219a211745cfd7), sem utilizar arquivos locais da execução SARIMAX em andamento. Incorporar a extração RF versionada como resultado parcial, não como ranking homologado; origens das Bases 1–4 não estão preenchidas nessa extração. SARIMAX remoto tem saídas de execução reduzida, não prova de teste final completo. Atualizar indicação do registro de demandas, agora externo ao repositório conforme AGENTS.md. Não editar results/ manualmente nem executar modelos nesta tarefa.

## 2026-10-04 - Reaproveitamento auditável das execuções do remoto

**Decisão:** extrair por código as métricas e evidências já executadas em `origin/main`, identificando commit e notebook de origem. Esses artefatos permanecem separados de `results/metrics.csv` até que os quatro modelos de cada base sejam extraídos sob o mesmo critério.

**Motivo:** os notebooks de Random Forest no remoto foram executados sem erros, mas suas métricas não foram exportadas para o consolidado. Reexecutá-los localmente com reajuste por origem tornou a finalização inviável dentro do prazo.

**Efeito:** não são inventados nem editados valores manualmente. As métricas extraídas preservam seu protocolo original e só entram em ranking após a verificação de compatibilidade de alvo, horizonte e origens com SARIMAX, Holt-Winters e XGBoost.
## 2026-10-04 - Isolamento dos checkpoints XGBoost

**Responsável e status:** Codex, a pedido de Giovanne; implementação concluída e validada nos quadros reais das cinco bases.

**Decisão:** identificar os checkpoints XGBoost pelo quadro efetivamente usado no tuning (features, alvo, origens, instantes dos alvos e tipos), protocolo, sementes, versões das bibliotecas e código metodológico. Alterações em Markdown ou saídas não invalidam a busca; alterações na preparação, no alvo ou na validação invalidam. Não migrar automaticamente checkpoints antigos sem esse contrato e não alterar as previsões XGBoost já executadas.

**Entrega:** manter o `.gitignore` e os CSVs de resíduos ignorados, conforme solicitado. Não fazer commit nem push nesta demanda.

## 2026-10-04 - Documentação final e reconsolidação pós-execução

**Responsável e status:** Codex; atualizar o estudo com as cinco execuções completas realizadas por Giovanne e reconsolidar a tabela da Base 5 após a reexecução das Bases 1–3. Não ajustar novos modelos nem escolher parâmetros pelo teste.

**Evidência:** `results/metrics.csv`, CSVs individuais e saídas salvas dos notebooks. Registrar três vitórias no MAE contra persistência, duas derrotas marginais, resíduos ainda autocorrelacionados e tempos separados de tuning e avaliação. Atualizar apenas a saída da comparação global da Base 5 por código, preservando suas previsões, métricas locais, parâmetros e gráficos.

## 2026-10-04 - Consolidar métricas XGBoost sem novo treinamento

**Responsável e status:** Codex; consolidação das cinco execuções completas solicitada por Giovanne.

**Decisão:** gerar as cinco linhas XGBoost em `results/metrics.csv` pelos CSVs individuais e resumos registrados das execuções. Conferir MAE, hash do dado, quantidade de origens, causalidade e cadência antes de gravar; preservar linhas de outros modelos. Integrar a mesma exportação aos notebooks para execuções futuras.

**Sem extrapolação:** posição e vencedor ficam ausentes até a comparação final dos quatro modelos. MAPE fica ausente para retorno logarítmico e para séries com zeros; nas demais bases é percentual. Tempo registrado é a soma dos tempos de ajuste do tuning e avaliação, não o tempo de parede da chamada que reutilizou checkpoints. Registrar parâmetros do estimador e cadência separadamente no JSON de hiperparâmetros. O campo commit recebe o HEAD mais `+dirty` quando existem mudanças locais.

## 2026-10-04 - Exportação de resíduos da Base 5 em retorno

**Responsável e status:** Codex; exportador adaptado ao contrato remoto, execução final a cargo de Giovanne.

**Decisão:** salvar todas as previsões em `results/residuals/base_05_XGBoost.csv`, com retorno real e previsto, persistência de retorno zero, preços convertidos, resíduos nas duas escalas, cobertura e cortes de treino. Validar causalidade incluindo a origem do reajuste, identidade dos resíduos, conversão `price_t * exp(retorno)`, quantidade de linhas e finitude antes da gravação. O modo reduzido usa arquivo separado. Preservar entrada e não alterar treino, alvo ou métricas.

## 2026-10-04 - Retreinamento periódico do XGBoost

**Responsável e status:** Codex; implementação autorizada por Giovanne, cinco XGBoosts reexecutados e consolidados.

**Decisão:** separar frequência de previsão da frequência de ajuste. XGBoost continua prevendo um passo em todas as origens, com features atualizadas em cada origem e hiperparâmetros congelados. Reajustar a cada 7 origens na Base 1, 24 nas Bases 2–3, 144 na Base 4 e 4 na Base 5. A janela de treino continua expansiva e só recebe alvos revelados até a origem do reajuste.

**Motivo:** o reajuste por origem na Base 4 implica 82.830 treinamentos completos. A cadência operacional diária reduz esse total para 576, sem eliminar origens de avaliação. As cadências foram fixadas por custo/frequência dos dados, não por resultados do teste; não são uma otimização comprovada e podem ser estudadas posteriormente apenas dentro do treino.

**Consistência:** RF, SARIMAX e Holt-Winters preservam seus procedimentos remotos. O protocolo comum exige alvo, horizonte, origens e informação disponível equivalentes, não algoritmos de ajuste idênticos. As cadências diferentes devem ser declaradas na comparação final.

**Efeito:** esta decisão substitui a obrigação anterior de refit a cada origem apenas para XGBoost. Busca de 150 candidatos, purga, alvos e divisões não são alterados nesta demanda. Reexecutar RF não é requisito para concluir o pacote XGBoost.

**Atualização remota:** integrado `origin/main` até `2b06f5b`, incluindo preparação, relatório e registros de execução. Alterações locais preservadas em stash antes da integração. O remoto removeu `tarefas.csv`; o acompanhamento desta demanda fica registrado aqui.

## 2026-10-03 - Apresentação científica do relatório

**Decisão:** reduzir títulos internos e usar Poppins seminegrito sem caixa alta; reservar Barlow para a capa. Manter violeta como destaque interno, páginas de altura natural na tela e quebra por seção na impressão. Orientações ficam no modo de edição, mas pendências continuam explícitas em leitura e impressão. Centralizar caminhos de evidência no apêndice com referências curtas no corpo. Não destacar vencedores nem inventar valores na ausência da consolidação.

## 2026-10-03 - Integrantes confirmados e refinamento de leitura

**Decisão:** registrar os seis nomes completos fornecidos pelo usuário em projeto.yaml e no relatório, preservando a associação P1–P6 do planejamento documentado. Refinar tabela da equipe, identificação da capa e espaçamento responsivo sem alterar paleta, responsabilidades ou evidências de execução. A confirmação de nomes não equivale a comprovação de contribuições.

## 2026-10-03 - Preenchimento documental após sincronização

**Decisão:** executar pull fast-forward preservando alterações locais e preencher o relatório com identificação fornecida, configuração vigente e documentação do repositório. O pull informou que main já estava atualizada. Tratar divisão de tarefas como planejamento documentado, não evidência de execução. Usar projeto.yaml e metadata.yaml em preferência a textos antigos que ainda citam horizonte indefinido ou caminhos descontinuados. Não importar métricas/hiperparâmetros finais de documentos antigos: results/metrics.csv ainda não contém linhas de resultados. Documentar separadamente números da Base 5 registrados em sua documentação, sem extrapolar para o ranking das 20 combinações. Preservar gráficos e resultados faltantes como pendentes.

## 2026-10-03 - Retorno à paleta anterior sem decoração figurativa

**Decisão:** a pedido do usuário, restaurar páginas claras, violeta como cor principal e detalhes lima discretos. Remover símbolo da capa, ano decorativo e linha temporal fictícia; preservar títulos Barlow Condensed, pois a mudança solicitada trata de cores e símbolos. Manter somente identificação fornecida, escopo e configurações documentadas; autores, resultados e demais informações desconhecidas continuam como campos pendentes.

## 2026-10-03 - Capa editorial inspirada nas referências

**Decisão:** combinar capa azul-violeta com detalhe lima e ano 2026 na lateral, títulos em Barlow Condensed ExtraBold e caixa alta, preservando páginas internas claras. Incorporar fonte e licença no HTML. A linha da capa é decorativa e não representa resultados. Conferir desktop, celular e impressão sem alterar dados ou metodologia.

## 2026-10-03 - Títulos com maior presença

**Decisão:** substituir Poppins por Archivo Black apenas nos títulos principais (h1 e h2), conforme preferência do usuário por letras mais pesadas e largas. Manter Poppins em subtítulos e Segoe UI no corpo. Incorporar a fonte e sua licença OFL no HTML; verificar quebras de linha no computador e no celular antes da entrega.

## 2026-10-03 - Laboratório editorial

**Decisão:** aplicar o refinamento visual aprovado pelo usuário: Poppins nos títulos, Segoe UI no texto, mais respiro, linha temporal SVG decorativa explicitamente sem dados, fichas uniformes das bases e faixas de principal achado com evidência pendente. Fixar cores e traçados distintos para os quatro modelos nas orientações de gráficos. Não alterar resultados ou metodologia; as demais seções do relatório continuam em construção.

## 2026-10-03 - Identidade violeta e lima do relatório

**Decisão:** a pedido do grupo, aplicar violeta como cor principal, verde-lima em pequenos destaques e superfícies claras para leitura. Incorporar Poppins regular e seminegrito no HTML para manter a tipografia disponível offline, sem requisições externas ao abrir o relatório. Preservar conteúdo, dados e funcionalidades. Regerar o artefato de entrega a partir da fonte.

## 2026-10-03 - Modelo do relatório e publicação privada

**Decisão:** criar uma fonte HTML autocontida em `docs/relatorio/modelo.html`, gerar `entrega/relatorio.html` por código e publicar uma cópia privada pelo Sites. A estrutura segue as 14 seções do enunciado, com fichas para as cinco bases, espaço para as 20 combinações e apêndices identificados como material da entrega ao professor.

**Apresentação:** páginas navegáveis, versão completa para leitura e impressão A4, cores claras com detalhes azuis e tipografia local. Não há dependências de fontes, imagens ou bibliotecas externas. Textos e gráficos pendentes permanecem explicitamente marcados; métricas não homologadas não serão preenchidas.

**Preenchimento:** a edição de textos e inclusão de gráficos ocorre no navegador, sem envio dos arquivos a terceiros. As alterações precisam ser baixadas em um HTML atualizado; não há armazenamento automático nem edição colaborativa. O HTML baixado preserva o conteúdo e funciona offline.

**Limite:** a impressão pode criar páginas adicionais quando os campos forem preenchidos. A versão final deve ter paginação, legibilidade e equivalência HTML/PDF novamente verificadas. A nota da estrutura não equivale à nota do trabalho concluído.

**Pendências preservadas:** identificação do grupo, integrantes e resultados finais dependem de confirmação; não alterar `projeto.yaml` nem os resultados durante esta tarefa.

## 2026-09-29 - Estrutura enxuta do repositório

**Decisão:** reduzir o contexto obrigatório a `AGENTS.md` e `projeto.yaml`; organizar cada base em `data/base_NN/`; centralizar notebooks em `notebooks/`; separar referências e entrega.

**Motivo:** o enunciado exige rastreabilidade, prevenção de vazamento e reprodução dos resultados, mas agentes e integrantes não devem precisar navegar por uma hierarquia extensa antes de trabalhar.

**Efeito:** dados brutos passam a se chamar `raw.csv` e permanecem imutáveis. Campos metodológicos ainda não definidos continuam nulos em `projeto.yaml` até confirmação humana.

**Registro de IA:** a proposta de organização e esta decisão foram elaboradas com assistência de IA e devem ser revisadas pelo grupo antes de mudanças metodológicas posteriores.

## 2026-09-29 - Contrato único de caminhos dos notebooks

**Decisão:** todo notebook resolve a base como `data/base_NN/`. Os únicos nomes de dados derivados são `prepared.csv`, `train.csv` e `test.csv`; os dados de origem permanecem em `raw.csv`.

**Motivo:** a migração estrutural revelou referências mistas a `trabalho/bases/grupoN`, `grupoN.csv` e diretórios de execução, que podiam falhar ou criar CSVs fora da base.

**Efeito:** o módulo `series_temporais.paths` é a referência reutilizável para localizar o projeto e as bases. As células de preparação gravam explicitamente na pasta da base.

## 2026-09-29 - XGBoost como modelo de especialização

**Decisão:** usar XGBoost como quarto modelo nas cinco bases, com as mesmas features, origens, horizonte e observações de teste do Random Forest de cada base.

**Validação:** selecionar hiperparâmetros somente no treino por busca aleatória reproduzível em duas etapas (120 candidatos amplos e 30 refinados), usando três dobras temporais expansivas com purga. Congelar a configuração escolhida antes do teste final walk-forward.

**Interpretação:** comparar o modelo com persistência e calcular Gain e Permutation Importance. Essas importâncias são descritivas e não demonstram causalidade. A comparação entre bases usa vitórias e skill relativo ao baseline, não média de MAEs em escalas diferentes.

**Execução:** checkpoints de busca e resumos intermediários ficam no diretório temporário do sistema para permitir retomada sem versionar artefatos transitórios. A análise técnica consolidada está em `docs/modelo_xgboost.md`.

## 2026-10-01 - Completar contrato de metadados

**Decisão:** registrar em `projeto.yaml` e em cada `data/base_NN/metadata.yaml` os fatos já implementados nos notebooks: previsão de um passo à frente, frequência, coluna temporal, alvo, proporção cronológica de treino e períodos sazonais candidatos. O período sazonal final e o tamanho da janela inicial permanecem pendentes quando ainda não há uma decisão única, pois dependem da validação walk-forward.

**Motivo:** os campos nulos impediam que o projeto fosse auditado sem abrir cada notebook. Preencher somente informações comprovadas centraliza o contrato metodológico, sem transformar candidatos de modelagem em parâmetros definitivos.

**Efeito:** os metadados passam a registrar o contrato reproduzível de cada base. Na Base 5, o alvo canônico é o retorno logarítmico da semana seguinte; o alinhamento dos quatro modelos foi concluído na decisão específica registrada abaixo.

## 2026-10-01 - Protocolo estrito de teste walk-forward

**Decisão:** o teste final passa a produzir uma previsão de um passo por origem. Random Forest e XGBoost são reajustados em cada origem com parâmetros já congelados; Holt-Winters atualiza seu estado depois da observação revelada; SARIMAX é reestimado em cada origem, também com hiperparâmetros congelados. Todo ajuste usa exclusivamente linhas cujo alvo já ocorreu até a origem.

**Motivo:** previsões em bloco ou um único horizonte que cobre todo o teste não têm o mesmo horizonte de um passo e impedem comparação justa entre modelos.

**Efeito:** a cadência de reajuste é comum (`1`), as previsões recebem um esquema comum de origem, alvo, valor real, previsão e corte de treino, e testes automatizados bloqueiam vazamento temporal.

## 2026-10-01 - Janela inicial do walk-forward

**Decisão:** no teste final, a janela inicial é toda a partição cronológica de treino de cada base. No tuning, cada dobra precisa começar com a janela mínima específica da base: 730 dias (Base 1), 336 horas (Bases 2 e 3), 288 observações de dez minutos (Base 4) e 104 semanas (Base 5).

**Motivo:** a janela inicial precisa acomodar simultaneamente lags, janelas móveis e pelo menos dois ciclos da maior sazonalidade candidata. Um único número absoluto não seria coerente entre frequências diária, horária, de dez minutos e semanal.

**Efeito:** as dobras temporais passam a ter um limite inferior explícito; o histórico do teste final permanece expansivo e usa toda a informação disponível no corte de treino.

## 2026-10-02 - Alvo comparável da Base 5

**Decisão:** os quatro modelos finais da Base 5 passam a prever diretamente `target_log_return_t_plus_1`, calculado na grade regular `W-FRI`. Todos recebem o mesmo quadro modelável, o mesmo corte cronológico de 75%/25% e as mesmas 586 origens de teste. Previsões de preço podem ser reconstruídas por `price_t * exp(retorno_previsto)`, mas não substituem o retorno como alvo principal.

**Tratamento das semanas sem nova cotação:** os quatro modelos comparáveis usam a grade semanal completa no tuning, no ajuste e na avaliação principal. Retornos zero decorrentes do último preço conhecido permanecem identificados pelos indicadores de cobertura. O recorte de 523 semanas com nova cotação é apenas uma análise de robustez, nunca o ranking principal.

**Motivo:** SARIMAX e Holt-Winters avaliavam preço em nível, enquanto Random Forest de retorno e XGBoost avaliavam retorno. A divergência impedia comparar MAE, origens e resíduos sob um único protocolo.

**Efeito:** `preparar_modelagem_ouro` centraliza a grade semanal, o alvo, as 49 features e o corte compartilhado. O notebook `RF_preco` permanece somente como análise auxiliar e não participa do ranking final dos quatro modelos.

## 2026-10-03 - Identificação do grupo, semente e controle de demandas

**Decisão:** registrar a turma 3H e os seis integrantes em `projeto.yaml`, adotar a semente 42 em todas as bases e manter a planilha operacional de demandas fora do repositório.

**Motivo:** uma única semente elimina divergências entre modelos estocásticos, enquanto o controle de tarefas não faz parte dos artefatos técnicos versionados.

**Efeito:** `tarefas.csv` deixa de ser requisito estrutural. O repositório preserva decisões metodológicas em `docs/decisoes.md`, resultados reproduzíveis em `results/` e handoffs excepcionais em `docs/handoffs/`.

**Integrantes:** Matheus Bastos Castilho, Mayumi Shimizu, Levy, Pedro Gomes Frossard, Ruan Lourenço e Giovane Torquato.

## 2026-10-03 - Execução e rastreabilidade das buscas SARIMAX

**Decisão:** os cinco notebooks SARIMAX mantêm como padrão a busca completa de `s=0` a `s=100`, com checkpoints temporários versionados. O benchmark SARIMA versus SARIMAX usa somente uma validação interna extraída do treino; o teste final permanece intocado até o walk-forward. Um modo reduzido, ativado apenas por variável de ambiente, testa a pipeline com 730 observações e quatro origens sem representar o resultado final.

**Motivo:** a grade completa contém 57.632 candidatos SARIMA e 691.584 candidatos SARIMAX por base e precisa ser retomável. Checkpoints antigos não podem ser misturados após mudanças na preparação ou no contrato causal. O modo reduzido permite verificar código, rankings, resíduos e reajuste por origem sem alegar que a busca integral foi executada.

## 2026-10-04 - Reuso auditável de configuração SARIMAX e teste final

**Decisão:** as configurações vencedoras registradas nos notebooks executados de `origin/main` serão lidas dos próprios outputs e tratadas como hiperparâmetros congelados. Um executor separado fará somente o walk-forward final completo, com uma previsão de um passo por origem e sem rodar novamente a busca de candidatos. Os notebooks remotos permanecem inalterados; previsões e métricas serão geradas por código e validadas antes de qualquer consolidação.

**Motivo:** a execução salva no remoto está explicitamente marcada como teste reduzido (730 linhas e quatro origens), mas registra a configuração selecionada. Repetir a grade inteira não é necessário para aplicar a avaliação final com a configuração já congelada.

**Retomada da Base 4:** o benchmark de três origens finais consumiu 52,72 segundos com 132.707 linhas iniciais de treino. A execução integral tem 33.177 origens e pode durar vários dias. Para não perder previsões já computadas em uma interrupção, o executor gravará checkpoints atômicos em blocos contíguos. Ao retomar, validará cada previsão existente contra o prefixo do teste canônico; o histórico de cada bloco incluirá somente observações já reveladas. O modelo e seus parâmetros permanecem os mesmos e são reajustados em cada origem.

**Efeito:** todas as cinco pipelines foram verificadas de ponta a ponta no modo reduzido. A execução completa continua explícita, reproduzível e separada dos resultados de validação técnica.

## 2026-10-03 - Contrato do consolidado de métricas

**Decisão:** `results/metrics.csv` passa a usar um esquema único com identificação da base, modelo, alvo, frequência, horizonte, origens, métricas, ranking, parâmetros, exógenas, notebook, commit e instante de geração.

**Motivo:** MAEs só são comparáveis dentro da mesma base e do mesmo alvo. O consolidado precisa carregar contexto suficiente para impedir comparações ambíguas e permitir rastreabilidade.

**Efeito:** o arquivo começa apenas com o cabeçalho e será preenchido por `series_temporais.results.write_metrics` quando as execuções finais forem concluídas; valores não serão digitados manualmente.

## 2026-10-04 - Aproveitamento documental de saídas executadas

**Decisão:** incorporar no relatório v2 as saídas verificáveis já salvas nos notebooks — força de sazonalidade e tendência por STL, métricas individuais, diagnósticos de Ljung-Box e sinais de importância — identificando a origem e a limitação de cada evidência. Não preencher ranking, vitórias, posição média ou vencedor geral quando as quatro famílias não compartilham as mesmas origens de teste.

**Motivo:** resultados executados não devem ficar ocultos apenas por ainda não integrarem o consolidado canônico. Ao mesmo tempo, transcrever MAEs de amostras temporais diferentes como um ranking violaria o protocolo do projeto.

**Efeito:** o relatório passa a diferenciar resultados individuais auditados, diagnósticos disponíveis e comparações ainda não homologadas. A ausência da execução SARIMAX final da Base 4, a falta de contagens de origem do RF nas Bases 1–4 e o registro diário externo permanecem explícitos.
