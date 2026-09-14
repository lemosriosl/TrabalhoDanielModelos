# Divisão de tarefas — Trabalho de Séries Temporais
## Estratégia recomendada para 6 pessoas

### Base da divisão

Esta divisão foi construída a partir de todas as exigências do enunciado, e não apenas das 20 combinações de modelos.

O trabalho envolve:

- documentação e exploração das cinco bases;
- limpeza e preparação;
- STL e força da sazonalidade;
- Feature Engineering e controle de vazamento;
- validação walk-forward;
- otimização de quatro modelos;
- treinamento e previsão;
- MAE e comparação;
- análise de resíduos, ACF e Ljung-Box;
- importância das features;
- estudo aprofundado do modelo de especialização;
- relatório técnico em HTML e PDF;
- apresentação oral;
- organização dos arquivos da entrega;
- registro diário das demandas.

A divisão também considera que o enunciado diferencia **carga de trabalho** e **complexidade**. Portanto, o objetivo não é dar o mesmo número de tarefas para cada pessoa, e sim aproximar o esforço total e a responsabilidade técnica de cada uma.

---

# 1. Princípio central: dividir por "pacotes de entrega"

A estratégia mais segura para um grupo de seis pessoas é cada integrante possuir um **pacote de entrega completo**, composto por:

1. uma parte técnica relevante;
2. produção da evidência/resultados;
3. uma parte correspondente do relatório;
4. preparação da própria parte da apresentação;
5. revisão cruzada de outra parte.

Isso evita três problemas comuns:

- uma pessoa programar tudo enquanto outra apenas escreve;
- uma pessoa ficar com toda a revisão/integração no final;
- tarefas difíceis ficarem escondidas dentro de uma descrição genérica como "fazer o modelo".

---

# 2. Estrutura dos pacotes

| Pessoa | Pacote principal | Bases/modelos | Parte documental principal |
|---|---|---|---|
| **P1** | Exploração + SARIMAX | SARIMAX nas 5 bases; Bases 1 e 2 | Documentação das Bases 1–2 + SARIMAX |
| **P2** | Exploração + Holt-Winters | Holt-Winters nas 5 bases; Bases 3 e 4 | Documentação das Bases 3–4 + Holt-Winters |
| **P3** | Exploração + Random Forest | RF nas 5 bases; Base 5 | Documentação da Base 5 + RF + importance |
| **P4** | Feature Engineering + preparação | Pipeline comum de features | Feature Engineering + disponibilidade + leakage |
| **P5** | Modelo de especialização | Modelo especial nas 5 bases | Estudo aprofundado do modelo especial |
| **P6** | Validação + integração analítica | Walk-forward + consolidação | MAE + comparação + resíduos + conclusão |

**Observação importante:** a Pessoa 6 é responsável pela infraestrutura de comparação e consolidação, mas não "faz sozinha todos os resultados". As pessoas responsáveis por cada modelo continuam responsáveis por gerar e interpretar os resultados das próprias execuções.

---

# 3. Pacote P1 — Exploração 1 + SARIMAX

## 3.1 Trabalho técnico

### Bases
- Base 1: documentação, exploração e limpeza;
- Base 2: documentação, exploração e limpeza.

Para cada uma:
- fonte;
- período;
- frequência;
- unidade;
- variável-alvo;
- variáveis externas;
- valores ausentes;
- duplicidades;
- irregularidades temporais;
- outliers;
- gráficos;
- decisões de limpeza e transformação.

### STL
- STL da Base 1;
- STL da Base 2;
- interpretação de tendência;
- interpretação de sazonalidade;
- interpretação do residual;
- força da sazonalidade.

### Modelo
Executar SARIMAX para:
- Base 1;
- Base 2;
- Base 3;
- Base 4;
- Base 5.

Para cada execução:
- preparação compatível;
- escolha/otimização das ordens;
- variáveis externas;
- treinamento;
- previsão;
- registro dos parâmetros;
- tempo de execução;
- previsões;
- resíduos;
- MAE;
- interpretação dos coeficientes das variáveis externas.

## 3.2 Relatório

Responsável principal por:
- documentação das Bases 1 e 2;
- STL das Bases 1 e 2;
- seção do SARIMAX;
- resultados do SARIMAX.

## 3.3 Apresentação

Apresenta:
- características das Bases 1 e 2;
- principais achados da STL;
- SARIMAX e principais resultados.

## 3.4 Carga estimada

**Alta**, com complexidade **média/alta**.

---

# 4. Pacote P2 — Exploração 2 + Holt-Winters

## 4.1 Trabalho técnico

### Bases
- Base 3: documentação, exploração e limpeza;
- Base 4: documentação, exploração e limpeza.

### STL
- STL da Base 3;
- STL da Base 4;
- tendência;
- sazonalidade;
- residual;
- força da sazonalidade.

### Modelo
Executar Holt-Winters para:
- Base 1;
- Base 2;
- Base 3;
- Base 4;
- Base 5.

Investigar:
- tendência;
- sazonalidade;
- tendência amortecida;
- período sazonal;
- parâmetros de suavização.

Também:
- previsão;
- registro de parâmetros;
- tempo de execução;
- resíduos;
- MAE;
- interpretação do comportamento do modelo.

O Holt-Winters deve permanecer como referência **univariada**, conforme o enunciado.

## 4.2 Relatório

Responsável principal por:
- documentação das Bases 3 e 4;
- STL das Bases 3 e 4;
- seção do Holt-Winters;
- resultados do Holt-Winters.

## 4.3 Apresentação

Apresenta:
- características das Bases 3 e 4;
- STL;
- Holt-Winters;
- interpretação do desempenho.

## 4.4 Carga estimada

**Alta**, com complexidade **média**.

---

# 5. Pacote P3 — Exploração 3 + Random Forest

## 5.1 Trabalho técnico

### Base
- Base 5: documentação, exploração e limpeza;
- revisão de consistência da documentação das cinco bases.

### STL
- STL da Base 5;
- interpretação;
- força da sazonalidade.

### Modelo
Executar Random Forest para:
- Base 1;
- Base 2;
- Base 3;
- Base 4;
- Base 5.

Investigar:
- `n_estimators`;
- `max_depth`;
- `min_samples_split`;
- `min_samples_leaf`;
- `max_features`.

Também:
- previsão;
- parâmetros;
- tempo;
- resíduos;
- MAE.

### Feature importance
Fazer:
- importância nativa e/ou Permutation Importance;
- interpretação das features;
- destaque das variáveis externas.

## 5.2 Relatório

Responsável principal por:
- documentação da Base 5;
- STL da Base 5;
- seção do Random Forest;
- importância das features do RF.

## 5.3 Apresentação

Apresenta:
- Base 5;
- Random Forest;
- importância das features;
- principais resultados.

## 5.4 Carga estimada

**Alta**, com complexidade **média/alta**.

---

# 6. Pacote P4 — Feature Engineering e integridade temporal

Esta é uma das responsabilidades mais importantes porque afeta vários modelos simultaneamente.

## 6.1 Trabalho técnico

Construir e documentar o pipeline comum de Feature Engineering:

- lags da variável-alvo;
- lags das variáveis externas quando pertinentes;
- médias móveis;
- desvios móveis;
- features de calendário;
- encoding cíclico;
- novas features justificadas;
- tratamento dos valores ausentes gerados por lags e janelas.

Também verificar:

- quais variáveis externas seriam conhecidas na data real da previsão;
- quais precisam ser defasadas;
- quais podem ser usadas como previsão disponível na origem;
- quais precisam ser excluídas;
- risco de leakage em treinamento;
- risco de leakage na criação de features;
- risco de leakage na otimização.

Garantir que o Random Forest e o modelo de especialização utilizem o mesmo conjunto de features quando houver compatibilidade.

## 6.2 Testes de integridade

Criar uma checklist ou notebook de validação para verificar:

- nenhuma feature usa observações futuras indevidamente;
- os lags respeitam o horizonte;
- as janelas móveis usam apenas dados permitidos;
- os conjuntos de treino/teste respeitam o tempo;
- as cinco bases seguem o mesmo padrão metodológico.

## 6.3 Relatório

Responsável principal por:
- limpeza/preparação;
- Feature Engineering;
- disponibilidade temporal das variáveis;
- prevenção de leakage;
- decisões metodológicas sobre as features.

## 6.4 Apresentação

Apresenta:
- construção das features;
- exemplo de feature;
- prevenção de vazamento;
- decisões sobre variáveis externas.

## 6.5 Carga estimada

**Alta**, com complexidade **alta**.

O pacote não possui cinco modelos próprios porque seu resultado é compartilhado pelos modelos baseados em tabela e influencia a comparabilidade geral.

---

# 7. Pacote P5 — Modelo de especialização

A especialização depende do grupo:

- XGBoost;
- SVR;
- Elastic Net;
- MLP Regressor;
- PLS Regression.

## 7.1 Trabalho técnico

Executar o modelo escolhido nas cinco bases:

- Base 1;
- Base 2;
- Base 3;
- Base 4;
- Base 5.

Para cada base:
- treinamento;
- previsão;
- parâmetros;
- tempo;
- resíduos;
- MAE.

Também fazer a otimização dos principais hiperparâmetros.

## 7.2 Estudo aprofundado

Produzir domínio conceitual sobre:

- funcionamento e intuição;
- hipóteses;
- vantagens;
- limitações;
- requisitos de preparação;
- principais hiperparâmetros;
- efeitos dos hiperparâmetros;
- método de otimização;
- método de importância das features;
- desempenho nas cinco bases;
- possíveis explicações para diferenças de desempenho.

## 7.3 Importância das features

Aplicar o método compatível com o modelo:

- XGBoost → Gain, Permutation Importance ou SHAP;
- SVR → Permutation Importance ou equivalente;
- Elastic Net → coeficientes após padronização;
- MLP → Permutation Importance ou equivalente;
- PLS → coeficientes, Permutation Importance ou VIP Scores.

## 7.4 Relatório

Responsável principal por:
- seção do modelo especial;
- hiperparâmetros;
- otimização;
- importância das features;
- comparação do modelo especial nas cinco bases.

## 7.5 Apresentação

Apresenta:
- como o modelo funciona;
- por que foi escolhido;
- hiperparâmetros;
- resultados;
- importância das features.

## 7.6 Carga estimada

**Muito alta**, com complexidade **alta**.

Por isso, P5 recebe menos responsabilidades administrativas e de edição final.

---

# 8. Pacote P6 — Walk-forward + consolidação analítica

## 8.1 Protocolo de validação

Implementar ou padronizar o walk-forward para todo o grupo.

Garantir:

- mesma janela inicial;
- mesmas datas de origem;
- mesmo horizonte;
- mesmo período de teste;
- incorporação correta das observações reais após cada previsão;
- hiperparâmetros congelados no teste final;
- ausência de informação futura.

## 8.2 Consolidação

Definir um formato único para salvar os resultados de cada combinação:

- base;
- modelo;
- data de origem;
- data prevista;
- valor real;
- previsão;
- erro/resíduo;
- parâmetros;
- MAE.

## 8.3 Comparação por MAE

Consolidar:

- MAE dos quatro modelos em cada base;
- ranking por base;
- melhor modelo por base;
- quantidade de vitórias;
- posição média;
- discussão das características das bases associadas ao desempenho.

## 8.4 Resíduos

Consolidar:

- resíduos ao longo do tempo;
- ACF;
- Ljung-Box;
- p-valores;
- interpretação de viés;
- padrões remanescentes;
- variabilidade;
- autocorrelação.

Os responsáveis por cada modelo devem fornecer os gráficos e resultados; P6 consolida, padroniza e compara.

## 8.5 Relatório

Responsável principal por:

- protocolo walk-forward;
- resultados comparativos;
- MAE;
- ranking;
- análise consolidada dos resíduos;
- Ljung-Box;
- conclusões;
- limitações;
- recomendações.

## 8.6 Apresentação

Apresenta:
- protocolo de validação;
- comparação por MAE;
- vencedores por base;
- principais achados de resíduos;
- conclusão.

## 8.7 Carga estimada

**Alta**, com complexidade **alta**.

---

# 9. Distribuição de todas as tarefas do enunciado

| Atividade | P1 | P2 | P3 | P4 | P5 | P6 |
|---|---:|---:|---:|---:|---:|---:|
| Documentação Base 1 | ● |  |  | revisão |  |  |
| Documentação Base 2 | ● |  |  | revisão |  |  |
| Documentação Base 3 |  | ● |  | revisão |  |  |
| Documentação Base 4 |  | ● |  | revisão |  |  |
| Documentação Base 5 |  |  | ● | revisão |  |  |
| Dicionário de variáveis externas | ● | ● | ● | consolidação |  | revisão |
| Limpeza/preparação | ● | ● | ● | padronização |  | revisão |
| Gráficos exploratórios | ● | ● | ● | padronização |  | revisão |
| STL | B1–B2 | B3–B4 | B5 | revisão |  | consolidação |
| Força da sazonalidade | ● | ● | ● |  |  | consolidação |
| Feature Engineering |  |  |  | ● | apoio | revisão |
| Disponibilidade temporal |  |  |  | ● | apoio | revisão |
| Prevenção de leakage |  |  |  | ● | apoio | revisão |
| Walk-forward |  |  |  | apoio | apoio | ● |
| SARIMAX — 5 bases | ● |  |  | apoio |  | revisão |
| Holt-Winters — 5 bases |  | ● |  |  |  | revisão |
| Random Forest — 5 bases |  |  | ● | apoio |  | revisão |
| Modelo especial — 5 bases |  |  |  | apoio | ● | revisão |
| Otimização SARIMAX | ● |  |  |  |  | revisão |
| Otimização Holt-Winters |  | ● |  |  |  | revisão |
| Otimização Random Forest |  |  | ● |  |  | revisão |
| Otimização modelo especial |  |  |  |  | ● | revisão |
| Registro de parâmetros/tempo | ● | ● | ● | ● | ● | padronização |
| MAE individual | ● | ● | ● |  | ● | consolidação |
| Ranking e vitórias |  |  |  |  |  | ● |
| Resíduos individuais | ● | ● | ● |  | ● | consolidação |
| ACF | ● | ● | ● |  | ● | consolidação |
| Ljung-Box | ● | ● | ● |  | ● | consolidação |
| Feature importance RF |  |  | ● |  |  | revisão |
| Feature importance especial |  |  |  |  | ● | revisão |
| Estudo aprofundado especial |  |  |  |  | ● | revisão |
| Conclusões | contribui | contribui | contribui | contribui | contribui | redação |
| Referências | próprias | próprias | próprias | próprias | próprias | consolidação |
| HTML/PDF | conteúdo | conteúdo | conteúdo | revisão técnica | conteúdo | integração |
| Apresentação | ● | ● | ● | ● | ● | ● |
| Revisão cruzada | P4 | P5 | P6 | P1 | P2 | P3 |
| Organização dos arquivos | apoio | apoio | apoio | apoio | apoio | liderança |

**Legenda:**  
`●` = responsável principal  
`apoio` = contribui quando necessário  
`revisão` = verifica a entrega de outra pessoa

---

# 10. Relatório: divisão recomendada

O relatório deve ser **escrito de forma distribuída**, mas com uma pessoa fazendo a integração estrutural.

## 10.1 Responsabilidade por seção

| Seção mínima | Responsável |
|---|---|
| 1. Resumo executivo | P6 |
| 2. Integrantes/divisão de responsabilidades | P6 |
| 3. Documentação das cinco bases | P1, P2, P3 |
| 4. Limpeza, preparação e Feature Engineering | P4 + P1/P2/P3 |
| 5. STL, tendência e força da sazonalidade | P1, P2, P3 |
| 6. Protocolo walk-forward | P6 |
| 7. Modelos, hiperparâmetros e otimização | P1, P2, P3, P5 |
| 8. Resultados comparativos por MAE | P6 |
| 9. Resíduos e Ljung-Box | P6 + responsáveis dos modelos |
| 10. Importância das features | P3 + P5 + P1 |
| 11. Explicação do modelo escolhido | P5 |
| 12. Conclusões, limitações e recomendações | P6 + revisão de todos |
| 13. Referências | cada integrante registra suas fontes |
| 14. Apêndices técnicos/registro | cada integrante fornece seus materiais; P6 integra |

---

# 11. HTML e PDF

Não colocar a geração do documento inteiro como tarefa exclusiva de uma pessoa.

### Cada integrante entrega:
- texto da própria seção;
- tabelas;
- gráficos;
- legendas;
- referências;
- arquivos ou evidências necessários.

### Pessoa 6 coordena:
- montagem final;
- ordem das seções;
- consistência visual;
- links internos;
- numeração;
- verificação do HTML;
- exportação/validação do PDF.

### Todos fazem revisão final

Cada integrante deve revisar:

1. sua própria parte;
2. a parte atribuída no rodízio de revisão;
3. erros críticos visíveis no documento inteiro.

---

# 12. Rodízio de revisão

Para reduzir erro e distribuir a carga de revisão:

| Autor | Revisor |
|---|---|
| P1 | P4 |
| P2 | P5 |
| P3 | P6 |
| P4 | P1 |
| P5 | P2 |
| P6 | P3 |

A revisão deve verificar:

- resultado coerente com o código;
- números corretos;
- gráficos com títulos/eixos;
- interpretação sustentada pelos resultados;
- ausência de leakage;
- metodologia compatível com o enunciado;
- referências;
- clareza do texto.

---

# 13. Apresentação oral

Todos os seis integrantes participam.

A divisão recomendada é:

| Pessoa | Conteúdo principal |
|---|---|
| **P1** | Bases 1–2 + SARIMAX |
| **P2** | Bases 3–4 + Holt-Winters |
| **P3** | Base 5 + Random Forest + importance |
| **P4** | Feature Engineering + disponibilidade + leakage |
| **P5** | Modelo de especialização |
| **P6** | Walk-forward + MAE + resíduos + conclusão |

### Regra importante

Cada pessoa deve entender:

- sua parte;
- as demais partes em nível suficiente para responder perguntas;
- as cinco bases;
- por que o protocolo de validação é comparável;
- por que os resultados de MAE podem ou não ser comparados entre bases.

O grupo não deve dividir o conhecimento de forma que cada um conheça somente "o seu pedaço".

---

# 14. Entrega final

A pessoa 6 coordena o checklist final, mas **todos são responsáveis por verificar suas próprias evidências**.

Checklist:

- [ ] PDF final
- [ ] HTML paginado e autocontido
- [ ] arquivo-fonte do relatório
- [ ] códigos organizados
- [ ] cinco bases ou fontes claramente indicadas
- [ ] arquivo consolidado de MAE
- [ ] registro diário das demandas
- [ ] referências
- [ ] gráficos
- [ ] resultados de resíduos/Ljung-Box
- [ ] resultados de feature importance
- [ ] arquivos reproduzíveis

---

# 15. Registro diário de demandas

Cada integrante deve registrar as tarefas de forma objetiva.

Exemplo:

| Data | Integrante | Demanda | Evidência | Carga | Complexidade | Status |
|---|---|---|---|---|---|---|
| 14/09 | P1 | Otimizei as ordens do SARIMAX da Base 1 e comparei os candidatos | notebook + tabela | Alta | Alta | Concluída |
| 14/09 | P4 | Implementei lags de 1, 7 e 14 períodos e validei ausência de leakage | código + teste | Alta | Alta | Concluída |
| 14/09 | P6 | Consolidei previsões das quatro classes de modelos para o cálculo final do MAE | tabela consolidada | Alta | Alta | Concluída |

Evitar:

- "ajudei no trabalho";
- "fiz o modelo";
- "corrigi algumas coisas";
- "trabalhei no relatório".

A demanda precisa indicar **o que foi feito e qual evidência foi produzida**.

---

# 16. Como verificar se a divisão continua equilibrada

A distribuição não deve ser considerada "justa" apenas porque todos têm seis ou sete itens.

O grupo deve acompanhar três dimensões:

### Volume
Quanto código, análise, gráficos, tabelas e texto precisam ser produzidos?

### Complexidade
Quanto de pesquisa, tomada de decisão metodológica e resolução de problemas a tarefa exige?

### Dependência
Quanto o trabalho daquela pessoa bloqueia ou afeta o trabalho dos demais?

P4 e P6 possuem tarefas muito dependentes do restante do projeto. Por isso, elas devem começar cedo, mesmo que algumas tarefas de P1/P2/P3/P5 ainda estejam em andamento.

---

# 17. Ordem de execução recomendada

## Fase 1 — Preparação
Todos:
- congelam as bases;
- alinham estrutura;
- distribuem fontes;
- definem horizonte;
- definem convenções de nomes;
- definem formato das saídas.

P4:
- começa o Feature Engineering.

P6:
- define o protocolo do walk-forward e o formato de saída.

P1/P2/P3:
- começam exploração, documentação e STL.

P5:
- pesquisa o modelo de especialização e seus hiperparâmetros.

## Fase 2 — Modelagem
P1:
- SARIMAX.

P2:
- Holt-Winters.

P3:
- Random Forest.

P5:
- modelo especial.

P4:
- valida o pipeline comum e acompanha leakage/consistência.

P6:
- valida a execução walk-forward e recebe os primeiros resultados.

## Fase 3 — Avaliação
P1/P2/P3/P5:
- MAE individual;
- resíduos;
- ACF;
- Ljung-Box;
- interpretação.

P3/P5:
- importância das features.

P6:
- consolidação e comparação.

## Fase 4 — Relatório
Cada pessoa finaliza suas seções.

P6:
- integra o documento.

Todos:
- revisão cruzada.

## Fase 5 — Apresentação e entrega
Todos:
- preparação da apresentação;
- ensaio;
- revisão final.

P6:
- checklist final e organização do pacote.

---

# 18. Ponto crítico: não criar seis "ilhas"

A divisão funciona somente se houver padrões compartilhados.

Antes de cada pessoa desenvolver sua implementação, o grupo deve fechar:

- versão das cinco bases;
- nomes das colunas;
- tratamento dos dados;
- horizonte;
- datas de origem;
- conjunto de teste;
- estrutura de features;
- formato das previsões;
- formato dos resíduos;
- formato do MAE;
- convenção de arquivos.

Sem isso, o projeto corre o risco de possuir seis soluções tecnicamente corretas, mas impossíveis de comparar.

---

# 19. Avaliação da estratégia

### Por que esta estratégia é preferível?

**Equilíbrio:** cada pessoa possui uma responsabilidade técnica real e uma responsabilidade documental/apresentacional.

**Especialização sem isolamento:** cada integrante se aprofunda em uma área, mas continua integrado ao resultado final.

**Redução de gargalos:** o walk-forward e o Feature Engineering começam cedo e não são deixados para a última hora.

**Rastreabilidade:** as contribuições são fáceis de registrar no controle diário.

**Revisão independente:** cada entrega importante é revisada por outra pessoa.

**Coerência final:** uma única pessoa coordena a integração do relatório e da consolidação dos resultados, mas não monopoliza a produção do conteúdo.

---

# 20. Regra de ouro para o grupo

A unidade mínima de trabalho não deve ser:

> "fazer uma parte do trabalho."

Deve ser:

> **problema → implementação → resultado → interpretação → evidência → relatório → apresentação.**

Dessa forma, cada integrante consegue demonstrar sua contribuição de ponta a ponta, enquanto o grupo mantém uma metodologia única e resultados comparáveis.

---

## Referência ao enunciado

A divisão foi construída a partir das exigências do documento "TRABALHO - SÉRIES TEMPORAIS", especialmente as seções de organização dos modelos, etapas obrigatórias, validação, otimização, avaliação, resíduos, importância das features, modelo de especialização, relatório, apresentação, gestão por demandas, entrega e critérios de avaliação.

Entre os pontos estruturais mais importantes do enunciado estão:

- 5 bases × 4 modelos = 20 combinações principais;
- mesmas origens, horizonte e conjunto de teste no walk-forward;
- otimização antes da avaliação final;
- MAE como métrica principal;
- resíduos fora da amostra;
- análise de importância das features;
- participação de todos na apresentação;
- registro diário individual;
- possibilidade de ajuste da nota individual conforme a contribuição registrada.
