# Decisões do projeto

## 2026-09-29 - Estrutura enxuta do repositório

**Decisão:** reduzir o contexto obrigatório a `AGENTS.md`, `projeto.yaml` e `tarefas.csv`; organizar cada base em `data/base_NN/`; centralizar notebooks em `notebooks/`; separar referências e entrega.

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

## 2026-10-01 - Completar contrato de metadados e rastreio de tarefas

**Decisão:** registrar em `projeto.yaml` e em cada `data/base_NN/metadata.yaml` os fatos já implementados nos notebooks: previsão de um passo à frente, frequência, coluna temporal, alvo, proporção cronológica de treino e períodos sazonais candidatos. O período sazonal final e o tamanho da janela inicial permanecem pendentes quando ainda não há uma decisão única, pois dependem da validação walk-forward.

**Motivo:** os campos nulos impediam que o projeto fosse auditado sem abrir cada notebook. Preencher somente informações comprovadas centraliza o contrato metodológico, sem transformar candidatos de modelagem em parâmetros definitivos.

**Efeito:** `tarefas.csv` passa a registrar demandas e evidências. Na Base 5, o alvo canônico é o retorno logarítmico da semana seguinte; o alinhamento dos quatro modelos foi concluído na decisão específica registrada abaixo.

## 2026-10-01 - Protocolo estrito de teste walk-forward

**Decisão:** o teste final passa a produzir uma previsão de um passo por origem. Random Forest e XGBoost são reajustados em cada origem com parâmetros já congelados; Holt-Winters atualiza seu estado depois da observação revelada; SARIMAX é reestimado ou atualizado somente depois de cada previsão de um passo. Todo ajuste usa exclusivamente linhas cujo alvo já ocorreu até a origem.

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
