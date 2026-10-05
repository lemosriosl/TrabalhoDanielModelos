(() => {
  'use strict';
  if(document.body.dataset.auditVersion==='1')return;
  document.body.dataset.auditVersion='1';
  const chapter = number => document.querySelector(`[data-chapter="${number}"] .page-body`);
  const paragraph = text => { const p=document.createElement('p');p.textContent=text;return p; };
  const table = (caption, headings, rows) => {
    const wrap=document.createElement('div');wrap.className='table-wrap audit-table';
    const element=document.createElement('table');
    const title=document.createElement('caption');title.textContent=caption;element.append(title);
    const head=document.createElement('thead'), headRow=document.createElement('tr');
    headings.forEach(value=>{const cell=document.createElement('th');cell.scope='col';cell.textContent=value;headRow.append(cell)});
    head.append(headRow);element.append(head);
    const body=document.createElement('tbody');
    rows.forEach(row=>{const tr=document.createElement('tr');row.forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td)});body.append(tr)});
    element.append(body);wrap.append(element);return wrap;
  };
  const fill = (scope, label, value) => {
    scope.querySelectorAll('.slot').forEach(field=>{
      if(field.getAttribute('aria-label')===label){field.textContent=value;field.dataset.pending='false';field.classList.add('filled');}
    });
  };
  const note = (title, paragraphs, bullets=[]) => {
    const box=document.createElement('section');box.className='audit-note';
    const heading=document.createElement('h3');heading.textContent=title;box.append(heading);
    paragraphs.forEach(text=>box.append(paragraph(text)));
    if(bullets.length){const list=document.createElement('ul');bullets.forEach(text=>{const item=document.createElement('li');item.textContent=text;list.append(item)});box.append(list)}
    return box;
  };
  const data=[
    {base:'01', sarimax:['698,560126','851'], hw:['812,049677','851'], rf:['764,717551','não informado'], xgb:['694,167293','842']},
    {base:'02', sarimax:['574,980677','7.598'], hw:['250,150540','8.115'], rf:['129,760961','não informado'], xgb:['127,891555','3.372']},
    {base:'03', sarimax:['10,439642','6.824'], hw:['14,196441','6.828'], rf:['10,092369','não informado'], xgb:['9,528651','2.847']},
    {base:'04', sarimax:[null,'33.177 previstas; execução parcial'], hw:['0,135438','84.045'], rf:['0,136593','não informado'], xgb:['0,136486','82.830']},
    {base:'05', sarimax:['0,029219','586'], hw:['0,020078','586'], rf:['0,020517','586 registradas'], xgb:['0,020133','586']}
  ];
  const results=chapter(8);
  results.querySelector('.lead').textContent='Resultados existentes, apresentados com suas amostras e sem ranking não sustentado.';
  results.querySelector('.callout').innerHTML='<strong>Leitura correta</strong> Os MAEs abaixo são descritivos. Nas Bases 1–4, as avaliações não compartilham exatamente as mesmas origens; portanto, o menor número não comprova superioridade de um modelo.';
  const matrix=results.querySelector('table');matrix.classList.add('audit-matrix');
  data.forEach((entry,index)=>{
    const cells=matrix.tBodies[0].rows[index].cells;
    [entry.sarimax,entry.hw,entry.rf,entry.xgb].forEach((value,column)=>{
      cells[column+1].replaceChildren();
      const number=document.createElement('strong');number.textContent=value[0]??'Não concluído';
      const count=document.createElement('small');count.className='audit-small';count.textContent=`Origens: ${value[1]}`;
      cells[column+1].append(number,count);
    });
  });
  matrix.caption.textContent='MAE fora da amostra por execução — valores não comparáveis como ranking final';
  const mobileHint=paragraph('No celular, deslize a matriz horizontalmente para ver os quatro modelos.');
  mobileHint.className='audit-mobile-hint';matrix.closest('.table-wrap').before(mobileHint);
  results.querySelectorAll('p').forEach(el=>{
    if(el.textContent.startsWith('Fonte da extração:')&&el.textContent.includes('não foram importados'))
      el.textContent='Fonte da extração Random Forest: commit 2b06f5b598b1686a820574051dad9ae19628da51. A matriz acima apresenta esses MAEs apenas como registros descritivos; nas Bases 1–4, a extração não informa quantas origens foram avaliadas, e nenhum ranking foi calculado.';
  });
  results.append(note('Por que os números não batem',[
    'A auditoria encontrou conjuntos de origens distintos, mesmo quando o alvo e o horizonte nominal de um passo são iguais. Diferentes cortes efetivos de teste, filtragem de linhas e histórico exigido pelas features são explicações possíveis; não foi comprovada a contribuição exata de cada fator em todas as bases. A cadência de reajuste do XGBoost também é própria do modelo e não corrige a diferença de amostra.',
    'A solução metodologicamente correta seria recalcular todos os MAEs nas mesmas observações de cada base. Como essa reavaliação não foi concluída, este relatório registra os resultados individuais, mas não atribui vitórias, posição média ou vencedor geral.'
  ],[
    'Base 1: SARIMAX e Holt-Winters usam as mesmas 851 origens; XGBoost usa 842. A extração remota do Random Forest não informa a contagem.',
    'Base 2: os conjuntos registrados têm 8.115, 7.598 e 3.372 origens para Holt-Winters, SARIMAX e XGBoost; a contagem do Random Forest remoto não consta.',
    'Base 3: Holt-Winters usa 6.828 origens, SARIMAX 6.824 e XGBoost 2.847; falta a contagem remota do Random Forest.',
    'Base 4: Holt-Winters usa 84.045 origens e XGBoost 82.830. O SARIMAX continua em execução para 33.177 origens previstas; seu MAE parcial foi excluído.',
    'Base 5: os quatro registros indicam 586 origens. A igualdade exata de instantes e valores foi conferida entre Holt-Winters e SARIMAX; os artefatos por origem de Random Forest e XGBoost não estavam disponíveis nesta auditoria.'
  ]));
  results.append(note('Proveniência dos valores',[
    'XGBoost: results/metrics.csv versionado no repositório. Random Forest: results/extraidos_do_remoto/random_forest_metrics.csv, extraído das saídas dos notebooks remotos. SARIMAX: CSVs finais locais das Bases 1, 2, 3 e 5, com auditorias compactas versionadas. Holt-Winters: CSVs locais de previsões. Os CSVs completos locais são ignorados pelo Git; clonar o repositório não os recupera.',
    'Os cinco notebooks SARIMAX do remoto possuem saídas de teste reduzido, não a avaliação final completa. Os 35 notebooks permaneceram idênticos ao remoto; células executadas e ausência de erro salvo não demonstram, por si só, igualdade de protocolo entre modelos.'
  ]));
  const stl=chapter(5);
  stl.append(note('STL executada nas cinco bases',[
    'As decomposições e as medidas abaixo foram extraídas das saídas salvas dos notebooks exploratórios. Elas descrevem a série no treino e orientam a interpretação; não escolhem sozinhas o melhor modelo.'
  ]));
  stl.append(table('Força sazonal e de tendência registradas', ['Base', 'Período', 'Força sazonal', 'Força de tendência'], [
    ['01 · Bitcoin', '7 dias', '0,0000', '0,9942'],
    ['01 · Bitcoin', '365 dias', '0,0000', '0,7414'],
    ['02 · Tráfego', '24 horas', '0,8080', '0,1037'],
    ['02 · Tráfego', '168 horas', '0,9717', '0,0386'],
    ['03 · PM2.5', '24 horas', '0,3970', '0,8739'],
    ['03 · PM2.5', '168 horas', '0,3314', '0,3801'],
    ['04 · Temperatura', '144 passos', '0,8605', '0,9816'],
    ['04 · Temperatura', '1.008 passos', '0,6250', '0,9165'],
    ['05 · Ouro', '52 semanas', '0,0000', '0,9275']
  ]));
  stl.append(note('Leitura das decomposições',[
    'Bitcoin e ouro em nível apresentam tendência forte, mas não sazonalidade estável nos períodos testados. Tráfego e temperatura apresentam ciclos diário e semanal relevantes. PM2.5 combina tendência forte com sazonalidade moderada. As figuras completas permanecem nos notebooks exploratórios, que são a fonte visual destas tabelas.'
  ]));
  const baseFindings=[
    ['01','Bitcoin: XGBoost e Random Forest usam 842 origens; SARIMAX e Holt-Winters, 851. O menor MAE registrado é 694,167293 do XGBoost, mas a diferença de amostra impede classificá-lo como vencedor.', 'A série tem tendência forte e sazonalidade semanal/anual nula nos testes STL.'],
    ['02','Tráfego: os MAEs executados são 574,980677 (SARIMAX), 250,150540 (Holt-Winters), 129,760961 (RF) e 127,891555 (XGBoost), com 7.598, 8.115 e 3.372 origens registradas.', 'A sazonalidade semanal é alta (0,9717), compatível com a vantagem dos modelos que usam lags e calendário.'],
    ['03','PM2.5: XGBoost registra MAE 9,528651, SARIMAX 10,439642, RF 10,092369 e Holt-Winters 14,196441; as amostras têm tamanhos distintos.', 'Há tendência forte no ciclo diário e sazonalidade moderada.'],
    ['04','Temperatura: Holt-Winters, RF e XGBoost registram MAE 0,135438, 0,136593 e 0,136486. SARIMAX ainda não possui MAE final utilizável.', 'Ciclos diário e semanal são fortes, mas os diagnósticos residuais ainda rejeitam ruído branco.'],
    ['05','Ouro: os quatro registros possuem 586 origens: SARIMAX 0,029219, Holt-Winters 0,020078, RF 0,020517 e XGBoost 0,020133. A igualdade exata das origens de RF/XGBoost não foi recuperada nos artefatos locais.', 'O retorno semanal não mostrou sazonalidade estável; a tendência reportada pertence ao preço em nível.']
  ];
  baseFindings.forEach((entry,index)=>{
    const scope=document.querySelector(`#pagina-${index+5} .page-body`);
    fill(scope, 'Referenciar a tabela comparativa de MAE e os gráficos definitivos; registrar unidade e observações de teste comuns', entry[0]);
    fill(scope, 'Preencher a principal interpretação desta base após a validação final', entry[1]);
    fill(scope, 'Indicar tabela, figura ou resultado validado que sustenta a conclusão', 'Notebooks executados, CSVs de previsões e matriz auditada da seção 08.');
  });
  const residuals=chapter(9);
  residuals.querySelector('.lead').textContent='Diagnósticos executados, identificados por modelo e sem transformar saídas reduzidas em resultado final.';
  residuals.append(note('Ljung–Box já executado',[
    'Holt-Winters, Random Forest e XGBoost possuem diagnósticos fora da amostra registrados nos notebooks. Os notebooks SARIMAX exibem Ljung–Box do modo reduzido; por isso, esses valores não foram misturados à tabela final.'
  ]));
  residuals.append(table('Ljung–Box registrado nos notebooks', ['Base / modelo', 'Lags', 'Leitura'], [
    ['01 / Holt-Winters', '1, 7, 14, 30', 'Rejeita ruído branco em todos os lags apresentados.'],
    ['01 / Random Forest', '1, 7, 14, 30', 'Não rejeita no lag 1; rejeita nos lags 7, 14 e 30.'],
    ['01 / XGBoost', '1, 7, 14, 30', 'Rejeita em 1, 14 e 30; não rejeita no lag 7.'],
    ['02 / Holt-Winters, RF e XGBoost', '1, 24, 48, 168', 'Rejeitam ruído branco nos lags exibidos.'],
    ['03 / Holt-Winters, RF e XGBoost', '1, 24, 48, 168', 'Rejeitam ruído branco nos lags exibidos.'],
    ['04 / Holt-Winters, RF e XGBoost', '1, 6, 144, 288', 'Rejeitam ruído branco nos lags exibidos.'],
    ['05 / Holt-Winters', '1, 4, 13, 26', 'Não rejeita no lag 1; rejeita a partir do lag 4.'],
    ['05 / Random Forest', '1, 4, 13, 26', 'Não rejeita no lag 1; rejeita a partir do lag 4.'],
    ['05 / XGBoost', '1, 4, 13, 26, 52', 'Não rejeita no lag 1; rejeita a partir do lag 4.']
  ]));
  residuals.append(note('Limite do SARIMAX',[
    'As células executadas de SARIMAX mostram diagnósticos do teste reduzido de quatro origens. Os CSVs finais locais das Bases 1, 2, 3 e 5 existem, mas a tabela consolidada de Ljung–Box dessas execuções ainda não foi gerada por código. A Base 4 continua sem execução final SARIMAX.'
  ]));
  const importance=chapter(10);
  importance.append(table('Principais sinais do XGBoost nas execuções finais', ['Base', 'Features com maior Gain registrado', 'Leitura'], [
    ['01', 'target_std_7; target_lag_30; target_mean_30', 'Dependência de volatilidade e histórico; ganho marginal sobre persistência é fraco.'],
    ['02', 'target_lag_3; hora; target_lag_1', 'Rotina intradiária e dependência recente são dominantes.'],
    ['03', 'target_lag_1; WSPM_t; target_lag_2; RAIN_t', 'Persistência recente e variáveis ambientais contribuem.'],
    ['04', 'hora; target_std_6; VPdef (mbar)_t', 'Ciclo diário e condições de vapor dominam.'],
    ['05', 'price_mean_4; price_lag_13; fed_funds_lag_4', 'Gain não prova contribuição causal; permutação das taxas é próxima de zero.']
  ]));
  importance.append(note('Importância do Random Forest',[
    'Os cinco notebooks Random Forest executados calculam importância nativa. A documentação da Base 5 registra retorno corrente, volatilidade, dispersão histórica, lags de retorno e defasagens da Fed Funds entre as primeiras posições. Os valores completos por base precisam ser exportados de modo uniforme antes de uma tabela única; relevância preditiva não demonstra causalidade.'
  ]));
  const summary=chapter(1);
  summary.querySelectorAll('.panel').forEach(panel=>{
    const title=panel.querySelector('h3')?.textContent;
    const field=panel.querySelector('.slot');if(!field)return;
    if(title==='Resultado central')field.textContent='Há métricas registradas para os quatro modelos nas cinco bases, mas as origens avaliadas divergem nas Bases 1–4; o SARIMAX da Base 4 segue incompleto.';
    if(title==='Recomendação principal')field.textContent='Apresentar os MAEs como resultados individuais e declarar explicitamente que não há vencedor geral homologado.';
    field.dataset.pending='false';field.classList.add('filled');
  });
  summary.append(note('Síntese de entrega',[
    'O estudo demonstra pipelines temporais e resultados fora da amostra. A principal limitação é de comparabilidade, não uma autorização para igualar amostras por aproximação. O relatório preserva os resultados existentes e explicita os limites de inferência.'
  ]));
  fill(summary, 'Apontar as bases com maior previsibilidade, os modelos mais consistentes e as limitações principais', 'Tráfego e temperatura têm forte estrutura sazonal e os modelos de árvores registram MAEs baixos em suas próprias amostras. Bitcoin e ouro apresentam ganho pequeno ou negativo do XGBoost contra persistência. Como as origens divergem nas Bases 1–4, essa leitura não constitui ranking entre os quatro modelos.');
  const engineering=chapter(4);
  fill(engineering, 'Confirmar contagens processadas, regras realmente executadas e features finais de cada modelo', 'As Bases 1–4 possuem arquivos prepared, train e test reproduzíveis. A Base 5 reconstrói 2.398 semanas W-FRI a partir do CSV bruto; o quadro comparável contém 1.758 linhas de treino, 586 origens de teste e 49 features. Em todas as bases, lags e janelas usam somente informações disponíveis antes da origem.');
  fill(stl, 'Preencher tendência e força sazonal com saídas verificadas dos notebooks', 'Bitcoin: tendência forte e sazonalidade nula nos períodos 7 e 365. Tráfego: sazonalidade diária e semanal forte. PM2.5: tendência forte com sazonalidade moderada. Temperatura: tendência e ciclos diário/semanal fortes. Ouro: tendência forte no preço em nível e sazonalidade semanal nula.');
  fill(importance, 'Separar contribuição autorregressiva, calendário e variáveis externas; discutir redundância e correlação', 'Em XGBoost, lags, nível/volatilidade e calendário são recorrentes; clima e poluentes aparecem na Base 3, condições de vapor na Base 4 e taxas na Base 5. Gain e permutação medem relevância preditiva, não causalidade, especialmente sob correlação entre features.');
  const models=chapter(7);
  fill(models, 'Registrar melhores parâmetros, espaço de busca, número de candidatos, critério e tempo da execução final', 'XGBoost: 150 candidatos por base, três dobras temporais purgadas e parâmetros congelados; configurações e tempos das cinco bases estão em docs/modelo_xgboost.md e results/metrics.csv. Random Forest registra busca temporal; na Base 5, a configuração final é 250 árvores, profundidade 6, min_samples_leaf 3 e max_features=sqrt. SARIMAX e Holt-Winters mantêm parâmetros nos notebooks, mas não há resumo único, comparável e final para as 20 combinações.');
  const xgb=chapter(11);
  fill(xgb, 'Relacionar parâmetros homologados, desempenho, custo e importâncias por base', 'XGBoost foi executado nas cinco bases com 842, 3.372, 2.847, 82.830 e 586 origens. Superou a persistência nas Bases 2, 3 e 4; perdeu marginalmente nas Bases 1 e 5. Os reajustes periódicos são 7, 24, 24, 144 e 4 origens e foram definidos por custo operacional, não pelo teste.');
  const protocol=chapter(6);
  protocol.append(note('Protocolo planejado versus execução observada',[
    'O projeto define horizonte de um passo, avanço temporal e intenção de origens comuns. A auditoria dos artefatos mostrou que esse último requisito não foi plenamente cumprido. Por isso, a análise quantitativa entre modelos é exploratória e deve ser lida junto com o número de origens de cada célula da matriz.'
  ]));
  const conclusion=chapter(12);
  conclusion.append(note('Conclusão que os dados permitem',[
    'Os modelos produziram evidências individuais de previsão fora da amostra, mas a auditoria não sustenta uma classificação única das quatro famílias nas cinco bases. MAEs de séries diferentes têm unidades distintas e não devem ser somados ou promediados; MAEs da mesma base com origens diferentes não devem ser usados para proclamar um vencedor.',
    'A Base 5 é a mais próxima de uma comparação comum pela contagem de 586 origens, porém a igualdade exata de Random Forest e XGBoost com o teste canônico não pôde ser verificada a partir dos artefatos disponíveis. A Base 4 permanece sem avaliação SARIMAX final. Essas limitações são parte do resultado do trabalho, não resultados corrigidos ou omitidos.'
  ]));
  fill(conclusion, 'Preencher após verificar origens comuns, MAE, resíduos e importância das features', 'As execuções confirmam previsões fora da amostra e diagnósticos residuais. Tráfego e temperatura exibem padrões sazonais fortes; Bitcoin e ouro são mais difíceis de melhorar além da persistência. Não há evidência suficiente para declarar vencedor único entre os quatro modelos nas cinco bases.');
  fill(conclusion, 'Vincular cada recomendação a evidência validada e indicar condições de aplicação', 'Reavaliar os quatro modelos sobre a mesma lista de origens em cada base, exportar resíduos e importância de modo uniforme e só então calcular ranking, vitórias e posição média. Confirmar também a fonte da série de Jena e a proveniência, moeda e horário das taxas do ouro antes da entrega definitiva.');
  chapter(14).querySelectorAll('p').forEach(el=>{
    if(el.textContent.startsWith('Relatório v2 gerado após git pull'))
      el.textContent='Auditoria documental atualizada em 04/10/2026 com base no commit b483b781e226822f6b9477f1e303c7d0b2e43feb e nos CSVs locais de previsão disponíveis nesta data. Os resultados SARIMAX da Base 4 permanecem parciais e não integram a comparação final.';
  });
  const notice=document.querySelector('.notice');
  if(notice){notice.querySelector('strong').textContent='Resultados auditados, comparação limitada.';notice.childNodes.forEach(node=>{if(node.nodeType===Node.TEXT_NODE&&node.textContent.includes('Resultados e evidências pendentes'))node.textContent=' Os resultados disponíveis e as limitações de comparabilidade estão descritos no relatório.'})}
  document.querySelectorAll('.page-foot span:first-child').forEach(el=>el.textContent='Séries Temporais · resultados com limitações declaradas');
})();
