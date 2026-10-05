(() => {
  'use strict';
  if(document.body.dataset.auditVersion==='1')return;
  document.body.dataset.auditVersion='1';
  const chapter = number => document.querySelector(`[data-chapter="${number}"] .page-body`);
  const paragraph = text => { const p=document.createElement('p');p.textContent=text;return p; };
  const number = (value,digits=6) => Number(value).toLocaleString('pt-BR',{minimumFractionDigits:digits,maximumFractionDigits:digits});
  const gallery = (title,items,label) => {
    const section=document.createElement('section');section.className='audit-gallery-section';
    const heading=document.createElement('h3');heading.textContent=title;section.append(heading);
    const grid=document.createElement('div');grid.className='audit-gallery';
    items.forEach(item=>{
      const figure=document.createElement('figure');figure.className='figure audit-figure';
      const img=document.createElement('img');img.src=item.data;img.alt=`${label} - Base ${item.base}`;
      const subset=(item.base===5 && (label.startsWith('Resíduos Holt-Winters')||label.startsWith('ACF Holt-Winters')||label.startsWith('Resíduos Random Forest')||label.startsWith('ACF Random Forest'))) ? ' Subconjunto de robustez com 523 cotações novas; não é o conjunto integral de 586 origens.' : '';
      const detail=item.detail ? ` ${item.detail}.` : '';
      const caption=document.createElement('figcaption');caption.textContent=`Base ${item.base}: ${label}.${subset}${detail} Fonte: ${item.source}.`;
      figure.append(img,caption);grid.append(figure);
    });
    section.append(grid);return section;
  };
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
    {base:'01', sarimax:['698,560126','851'], hw:['812,049677','851'], rf:['764,717551','842 no notebook'], xgb:['694,167293','842']},
    {base:'02', sarimax:['574,086284','7.584 de 7.598 · 14 horizontes excluídos'], hw:['250,150540','8.115'], rf:['129,760961','3.372 no notebook'], xgb:['127,891555','3.372']},
    {base:'03', sarimax:['10,369544','6.771 de 6.824 · 53 horizontes excluídos'], hw:['14,196441','6.828'], rf:['10,092369','2.847 no notebook'], xgb:['9,528651','2.847']},
    {base:'04', sarimax:[null,'execução final não concluída'], hw:['0,135438','84.045'], rf:['0,136593','82.830 no notebook'], xgb:['0,136486','82.830']},
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
      el.textContent='Fonte da extração Random Forest: commit 2b06f5b598b1686a820574051dad9ae19628da51. As quantidades de origens foram recuperadas diretamente das tabelas de divisão salvas nos notebooks. Nenhum ranking dos quatro modelos foi calculado.';
  });
  results.append(note('Por que os números não batem',[
    'A auditoria encontrou conjuntos de origens distintos, mesmo quando o alvo e o horizonte nominal de um passo são iguais. Diferentes cortes efetivos de teste, filtragem de linhas e histórico exigido pelas features são explicações possíveis; não foi comprovada a contribuição exata de cada fator em todas as bases. A cadência de reajuste do XGBoost também é própria do modelo e não corrige a diferença de amostra.',
    'A solução metodologicamente correta seria recalcular todos os MAEs nas mesmas observações de cada base. Como essa reavaliação não foi concluída, este relatório registra os resultados individuais, mas não atribui vitórias, posição média ou vencedor geral.'
  ],[
    'Base 1: SARIMAX e Holt-Winters usam 851 origens; RF e XGBoost usam 842. Para RF, considera-se somente a saída executada do notebook remoto.',
    'Base 2: Holt-Winters usa 8.115 origens; SARIMAX tem 7.598 linhas, mas apenas 7.584 de horizonte correto; RF e XGBoost usam 3.372. Para RF, considera-se somente a saída executada do notebook remoto.',
    'Base 3: Holt-Winters usa 6.828 origens; SARIMAX tem 6.824 linhas, mas apenas 6.771 de horizonte correto; RF e XGBoost usam 2.847.',
    'Base 4: Holt-Winters usa 84.045 origens; RF e XGBoost usam 82.830. A execução final SARIMAX está fora do escopo desta atualização.',
    'Base 5: os quatro registros indicam 586 origens. A igualdade exata de instantes e valores foi conferida entre Holt-Winters e SARIMAX; os artefatos por origem de Random Forest e XGBoost não estavam disponíveis nesta auditoria.'
  ]));
  results.append(note('Horizonte efetivo do SARIMAX nas Bases 2 e 3',[
    'A auditoria encontrou 14 previsões da Base 2 e 53 da Base 3 cujo alvo está mais de um passo à frente da origem. Esses desvios estão nos CSVs extensos produzidos depois do smoke test do notebook; não são apenas uma peculiaridade das quatro origens do teste reduzido. Os MAEs originais dos CSVs (574,980677 e 10,439642) misturam horizontes e não são apresentados como teste de um passo. A matriz usa o MAE recalculado apenas nas 7.584 e 6.771 linhas de horizonte correto: 574,086284 e 10,369544. Isso não resolve a diferença de origens entre modelos.',
    'Na Base 3, seis origens compartilhadas com Holt-Winters apontam para alvo/horário diferente no SARIMAX. O diagnóstico de Ljung–Box desta auditoria também filtra as linhas de horizonte inválido. As linhas originais foram preservadas nos CSVs, sem edição manual.'
  ]));
  results.append(note('Proveniência dos valores',[
    'XGBoost: results/metrics.csv versionado no repositório e notebooks com busca completa registrada. Random Forest: exclusivamente results/extraidos_do_remoto/random_forest_metrics.csv, extraído das saídas dos notebooks remotos; CSVs locais divergentes de RF não são usados neste relatório. SARIMAX: CSVs extensos das Bases 1, 2, 3 e 5, gerados após o smoke test com configuração congelada, com auditorias compactas versionadas. Holt-Winters: CSVs de previsões fora da amostra. Os CSVs completos de previsões não estão todos no Git.',
    'Os notebooks SARIMAX das cinco bases registram uma pipe rápida em modo reduzido: busca abreviada e quatro origens no walk-forward salvo. Isso verifica a execução do procedimento, mas não é o teste completo. A execução extensa da Base 4 não foi realizada. Para RF 1–4, as saídas salvas refletem oito blocos de reajuste; a mudança posterior no código para reajuste por origem não atualizou esses resultados.'
  ]));
  results.append(note('Comparação descritiva, com limites explícitos',[
    'É legítimo confrontar os valores observados e explicar quais séries parecem mais ou menos difíceis, desde que cada MAE mantenha seu tamanho de amostra, modo de execução e fonte. Nas Bases 1–4, não se pode atribuir vantagem causal ou vitória ao menor valor, pois as observações de teste não são exatamente as mesmas. Na Base 5, as quatro contagens são 586, mas somente Holt-Winters e SARIMAX tiveram instantes e valores reais pareados integralmente.',
    'No par exato Holt-Winters/SARIMAX, SARIMAX registra MAE menor nas Bases 1 e 3; Holt-Winters, nas Bases 2 e 5. Isso descreve apenas esse par e suas observações comuns. RF e XGBoost possuem as mesmas contagens em cada base, mas faltam exportações por origem para comprovar a identidade exata dos alvos; seus MAEs são apresentados lado a lado, não como ranking homologado.'
  ]));
  results.append(note('O que é comparável sem novo treino',[
    'A interseção exata de origem, instante-alvo e valor real permite apenas uma comparação exploratória entre Holt-Winters e SARIMAX nas Bases 1, 2, 3 e 5. Ela exclui horizontes SARIMAX incorretos e não autoriza ranking dos quatro modelos, vitórias ou posição média. Os dados foram gerados por código em results/comparacao_pareada_hw_sarimax.csv.'
  ]));
  results.append(table('MAE pareado exploratório - somente Holt-Winters e SARIMAX',
    ['Base','Pares exatos','MAE HW no par','MAE SARIMAX no par'],
    window.REPORT_V2_SNAPSHOT.paired.map(row=>[
      row.base_id.slice(-2),Number(row.origens_pareadas).toLocaleString('pt-BR'),
      number(row.mae_hw_pareado),number(row.mae_sarimax_pareado)
    ])));
  results.append(note('Consolidação disponível, sem classificação artificial',[
    'Há 19 avaliações individuais documentadas: cinco Holt-Winters, quatro SARIMAX extensas, cinco Random Forest e cinco XGBoost. A tabela auditada em results/metricas_individuais_auditadas.csv separa fonte e quantidade de origens; o consolidado canônico results/metrics.csv ainda possui apenas as cinco linhas XGBoost. A tabela abaixo amplia a rastreabilidade no corpo do relatório, mas não preenche posições nem vencedores que dependem de teste comum.'
  ]));
  results.append(table('Inventário das 19 métricas individuais documentadas',
    ['Base / modelo','Origens válidas','MAE de um passo','Fonte / modo'],
    window.REPORT_V2_SNAPSHOT.individual.map(row=>{
      const valid=row.origens_horizonte_1||row.origens;
      const mae=row.mae_horizonte_1||row.mae;
      const mode=row.modelo==='Random Forest' ? (row.base_id==='base_05' ? 'notebook remoto · refit por origem' : 'notebook remoto · 8 blocos')
        : row.modelo==='XGBoost' ? 'consolidado · busca completa'
        : row.modelo==='SARIMAX' ? 'CSV extenso pós-smoke'
        : 'CSV fora da amostra';
      return [`${row.base_id.slice(-2)} / ${row.modelo}`,Number(valid).toLocaleString('pt-BR'),number(mae),mode];
    })));
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
    'Bitcoin e ouro em nível apresentam tendência forte, mas não sazonalidade estável nos períodos testados. Tráfego e temperatura apresentam ciclos diário e semanal relevantes. PM2.5 combina tendência forte com sazonalidade moderada. As figuras abaixo foram incorporadas das saídas executadas dos notebooks.'
  ]));
  const oldStlFigure=stl.querySelector('.figure');if(oldStlFigure)oldStlFigure.remove();
  window.REPORT_V2_SNAPSHOT.stl_figures.forEach(item=>{
    const figure=document.createElement('figure');figure.className='figure audit-figure';
    const img=document.createElement('img');img.src=item.data;img.alt=`Decomposição STL registrada para a Base ${item.base}`;
    const caption=document.createElement('figcaption');caption.textContent=`Base ${item.base}: decomposição STL da série de treino. Fonte: ${item.source}.`;
    figure.append(img,caption);stl.append(figure);
  });
  const baseFindings=[
    ['01','Bitcoin: XGBoost e Random Forest usam 842 origens; SARIMAX e Holt-Winters, 851. O menor MAE registrado é 694,167293 do XGBoost, mas a diferença de amostra impede classificá-lo como vencedor.', 'A série tem tendência forte e sazonalidade semanal/anual nula nos testes STL.'],
    ['02','Tráfego: os MAEs de um passo são 574,086284 (SARIMAX, 7.584 origens após filtrar 14 horizontes inválidos), 250,150540 (Holt-Winters, 8.115), 129,760961 (RF, 3.372) e 127,891555 (XGBoost, 3.372).', 'A sazonalidade semanal é alta (0,9717), mas os modelos ainda não compartilham a mesma amostra de teste.'],
    ['03','PM2.5: XGBoost registra MAE 9,528651, SARIMAX 10,369544 em 6.771 origens válidas, RF 10,092369 e Holt-Winters 14,196441; há 53 horizontes SARIMAX inválidos e as amostras divergem.', 'Há tendência forte no ciclo diário e sazonalidade moderada; a falha de horizonte impede homologar o CSV SARIMAX sem filtragem ou correção da execução.'],
    ['04','Temperatura: Holt-Winters, RF e XGBoost registram MAE 0,135438, 0,136593 e 0,136486. SARIMAX ainda não possui MAE final utilizável.', 'Ciclos diário e semanal são fortes, mas os diagnósticos residuais ainda rejeitam ruído branco.'],
    ['05','Ouro: os quatro registros possuem 586 origens: SARIMAX 0,029219, Holt-Winters 0,020078, RF 0,020517 e XGBoost 0,020133. A igualdade exata das origens de RF/XGBoost não foi recuperada nos artefatos locais.', 'O retorno semanal não mostrou sazonalidade estável; a tendência reportada pertence ao preço em nível.']
  ];
  baseFindings.forEach((entry,index)=>{
    const scope=document.querySelector(`#pagina-${index+5} .page-body`);
    fill(scope, 'Referenciar a tabela comparativa de MAE e os gráficos definitivos; registrar unidade e observações de teste comuns', entry[1]);
    fill(scope, 'Preencher a principal interpretação desta base após a validação final', entry[2]);
    fill(scope, 'Indicar tabela, figura ou resultado validado que sustenta a conclusão', 'Notebooks executados, CSVs de previsões e matriz auditada da seção 08.');
  });
  fill(document.querySelector('#pagina-8 .page-body'), 'Explicar o fenômeno, a origem da base, o endereço da fonte e a data de acesso', 'Temperatura em °C na série Jena Climate, da estação do Max Planck Institute for Biogeochemistry. O raw.csv local é tabularmente idêntico às 420.551 linhas e 15 colunas da distribuição TensorFlow/Keras; a data de download original do grupo não foi registrada. Fonte: keras.io/examples/timeseries/timeseries_weather_forecasting/.');
  fill(document.querySelector('#pagina-9 .page-body'), 'Explicar o fenômeno, a origem da base, o endereço da fonte e a data de acesso', 'Ouro semanal derivado do CSV adaptado de repositórios indicados na documentação. As taxas foram identificadas como séries DGS10 e DFF do FRED e a defasagem na origem foi verificada; moeda do ouro, horário histórico de publicação e data de download do grupo ainda não estão comprovados.');
  const residuals=chapter(9);
  residuals.querySelector('.lead').textContent='Diagnósticos de resíduos fora da amostra: CSVs finais de Holt-Winters e SARIMAX; saídas executadas dos notebooks de Random Forest e XGBoost.';
  residuals.querySelector('p').textContent='O teste de Ljung–Box avalia autocorrelação residual. p < 0,05 rejeita a hipótese de resíduos sem autocorrelação até o lag indicado; isso aponta estrutura não capturada, mas não invalida sozinho o MAE. Os lags e p-valores exatos, com fonte de cada resultado, estão no arquivo results/ljung_box_auditado.csv.';
  const byDiagnostic=new Map();
  window.REPORT_V2_SNAPSHOT.diagnostics.forEach(row=>{
    const key=`${row.base_id}/${row.modelo}`;
    if(!byDiagnostic.has(key))byDiagnostic.set(key,[]);
    byDiagnostic.get(key).push(row);
  });
  const individual=new Map(window.REPORT_V2_SNAPSHOT.individual.map(row=>[`${row.base_id}/${row.modelo}`,row]));
  const diagRows=Array.from(byDiagnostic,([key,rows])=>{
    const [base,model]=key.split('/');
    const p=rows.map(row=>`${row.lag}: ${Number(row.p_valor)===0?'<1e-300':Number(row.p_valor).toExponential(2)}`).join(' · ');
    const rejected=rows.filter(row=>Number(row.p_valor)<0.05).map(row=>row.lag);
    const count=base==='base_05' && model==='Random Forest' ? '523 (cotações novas)' : Number(individual.get(key)?.origens_horizonte_1||individual.get(key)?.origens).toLocaleString('pt-BR');
    return [`${base.slice(-2)} / ${model}`,count,p,
      rejected.length ? `Rejeita em ${rejected.join(', ')}` : 'Não rejeita nos lags testados'];
  });
  residuals.querySelector('.table-wrap').replaceWith(table('Ljung–Box dos resíduos fora da amostra (lag: p-valor)',
    ['Base / modelo','Origens','Lag: p-valor','Leitura a 5%'],diagRows));
  residuals.append(note('Ljung–Box já executado',[
    'Holt-Winters e SARIMAX (exceto Base 4) foram recalculados dos CSVs completos de previsões, sem reutilizar a saída reduzida dos notebooks SARIMAX. Nas Bases 2 e 3, o Ljung–Box do SARIMAX usa somente as linhas cujo horizonte é exatamente um passo. Random Forest e XGBoost vêm das tabelas executadas dos notebooks; seus resíduos integrais não estão todos disponíveis localmente.'
  ]));
  residuals.append(note('Diagnóstico final e limite do SARIMAX',[
    'As figuras de ajuste e as quatro origens do teste reduzido nos notebooks não são confundidas com resíduos finais. Os gráficos abaixo foram gerados sem novo treino a partir dos CSVs extensos das Bases 1, 2, 3 e 5, mantendo apenas horizonte de um passo; a Base 4 não possui avaliação final. O manifesto em results/figuras_sarimax/ registra a contagem, as exclusões e o hash de cada CSV de origem. Nas Bases 2 e 3, a ACF e o Ljung-Box percorrem a sequência de previsões válidas após a exclusão, que pode conter saltos de horário; isso limita a interpretação literal de cada lag temporal.'
  ]));
  residuals.append(note('Figuras recuperadas dos notebooks executados',[
    'Os painéis a seguir mostram resíduos ao longo do tempo e ACF de Holt-Winters e Random Forest. Os painéis XGBoost incluem observados versus previstos, ACF residual e Gain. Na Base 5, os gráficos de Holt-Winters e Random Forest são do subconjunto de robustez de 523 cotações novas, diferente do MAE principal de 586 origens. A série temporal residual completa de XGBoost não foi localizada nos artefatos salvos; o painel de ACF disponível não a substitui.'
  ]));
  residuals.append(gallery('SARIMAX: resíduos finais de um passo',window.REPORT_V2_SNAPSHOT.sarimax_residual_figures,'Resíduos SARIMAX fora da amostra'));
  residuals.append(gallery('SARIMAX: ACF residual final',window.REPORT_V2_SNAPSHOT.sarimax_acf_figures,'ACF SARIMAX fora da amostra'));
  residuals.append(gallery('Holt-Winters: resíduos por origem',window.REPORT_V2_SNAPSHOT.hw_residual_figures,'Resíduos Holt-Winters por origem'));
  residuals.append(gallery('Holt-Winters: ACF residual',window.REPORT_V2_SNAPSHOT.hw_acf_figures,'ACF Holt-Winters'));
  residuals.append(gallery('Random Forest: resíduos por origem',window.REPORT_V2_SNAPSHOT.rf_residual_figures,'Resíduos Random Forest por origem'));
  residuals.append(gallery('Random Forest: ACF residual',window.REPORT_V2_SNAPSHOT.rf_acf_figures,'ACF Random Forest'));
  residuals.append(gallery('XGBoost: previsão, ACF e Gain',window.REPORT_V2_SNAPSHOT.xgb_diagnostic_figures,'Painel XGBoost de previsão, ACF e Gain'));
  const importance=chapter(10);
  const oldImportanceFigure=importance.querySelector('.figure');
  if(oldImportanceFigure)oldImportanceFigure.replaceWith(paragraph('As figuras de importância Random Forest e os painéis Gain do XGBoost foram recuperados dos notebooks. Os métodos de importância diferem e não permitem comparação numérica direta nem interpretação causal.'));
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
  importance.append(gallery('Random Forest: importância nativa das features',window.REPORT_V2_SNAPSHOT.rf_importance_figures,'Importância nativa Random Forest'));
  const rfTable=Array.from(results.querySelectorAll('table')).find(element=>element.caption?.textContent.includes('Random Forest —'));
  if(rfTable){
    rfTable.caption.textContent='Random Forest — saídas executadas dos notebooks';
    window.REPORT_V2_SNAPSHOT.individual.filter(row=>row.modelo==='Random Forest').forEach((row,index)=>{
      rfTable.tBodies[0].rows[index].cells[3].textContent=Number(row.origens).toLocaleString('pt-BR');
    });
  }
  const staleResults=Array.from(results.querySelectorAll('p')).find(el=>el.textContent.startsWith('A documentação da Base 5 registra'));
  if(staleResults)staleResults.textContent='Na Base 5, o Random Forest registra MAE 0,020517 nas 586 origens e o baseline de retorno zero, 0,020101. O resultado RF está salvo no notebook executado, mas seu arquivo completo de previsões não está disponível nesta cópia.';
  document.querySelectorAll('.page-body p').forEach(el=>{
    if(el.textContent.includes('results/metrics.csv ainda contém somente o cabeçalho'))el.textContent='Há 19 avaliações individuais registradas; o consolidado canônico results/metrics.csv contém cinco linhas XGBoost. As origens diferentes impedem ranking homologado.';
    if(el.textContent.includes('A referência primária de Jena permanece pendente'))el.textContent=el.textContent.replace('A referência primária de Jena permanece pendente','A equivalência de Jena com a distribuição TensorFlow/Keras foi verificada');
    if(el.textContent.includes('referência de extração da série de Jena pendente'))el.textContent=el.textContent.replace('referência de extração da série de Jena pendente','equivalência tabular da série de Jena verificada, mas data original de download pendente');
    if(el.textContent.includes('fornecedor, moeda e horário de publicação de dados da Base 5 não confirmados'))el.textContent=el.textContent.replace('fornecedor, moeda e horário de publicação de dados da Base 5 não confirmados','moeda do ouro e horários históricos de publicação das taxas da Base 5 ainda não confirmados');
  });
  const resultNotes=Array.from(results.querySelectorAll('.callout'));
  resultNotes.forEach(el=>{if(el.textContent.includes('somente o cabeçalho')||el.textContent.includes('Consolidação pendente'))el.innerHTML='<strong>Consolidação incompleta</strong> Há 19 MAEs individuais, mas somente cinco linhas XGBoost no consolidado canônico e amostras diferentes nas Bases 1–4. Não há ranking homologado.';});
  const appendix=chapter(14);
  appendix.append(note('Achados reproduzíveis da auditoria',[
    'As tabelas results/metricas_individuais_auditadas.csv, results/ljung_box_auditado.csv e results/comparacao_pareada_hw_sarimax.csv são geradas por código. Seus dados distinguem CSV extenso pós-smoke, saída de notebook remoto e consolidado XGBoost. O SARIMAX da Base 4 não teve avaliação extensa.'
  ],window.REPORT_V2_SNAPSHOT.findings.filter(item=>!item.includes('CSV local de RF'))));
  const summary=chapter(1);
  summary.querySelectorAll('.panel').forEach(panel=>{
    const title=panel.querySelector('h3')?.textContent;
    const field=panel.querySelector('.slot');if(!field)return;
    if(title==='Resultado central')field.textContent='Há 19 métricas individuais registradas; a pipe rápida SARIMAX aparece nos cinco notebooks, mas a avaliação extensa da Base 4 não foi rodada e as origens divergem nas Bases 1–4.';
    if(title==='Recomendação principal')field.textContent='Apresentar os MAEs como resultados individuais e declarar explicitamente que não há vencedor geral homologado.';
    field.dataset.pending='false';field.classList.add('filled');
  });
  summary.append(note('Síntese de entrega',[
    'O estudo demonstra pipelines temporais e resultados fora da amostra. A pipe rápida SARIMAX assegurou um fluxo operacional reduzido nas cinco bases, enquanto a avaliação extensa ficou limitada a quatro. A principal limitação é de comparabilidade, não uma autorização para igualar amostras por aproximação. O relatório preserva os resultados existentes e explicita os limites de inferência.'
  ]));
  fill(summary, 'Apontar as bases com maior previsibilidade, os modelos mais consistentes e as limitações principais', 'Tráfego e temperatura têm forte estrutura sazonal e os modelos de árvores registram MAEs baixos em suas próprias amostras. Bitcoin e ouro apresentam ganho pequeno ou negativo do XGBoost contra persistência. Como as origens divergem nas Bases 1–4, essa leitura não constitui ranking entre os quatro modelos.');
  const engineering=chapter(4);
  fill(engineering, 'Confirmar contagens processadas, regras realmente executadas e features finais de cada modelo', 'As Bases 1–4 possuem arquivos prepared, train e test reproduzíveis. A Base 5 reconstrói 2.398 semanas W-FRI a partir do CSV bruto; o quadro comparável contém 1.758 linhas de treino, 586 origens de teste e 49 features. Em todas as bases, lags e janelas usam somente informações disponíveis antes da origem.');
  fill(stl, 'Preencher tendência e força sazonal com saídas verificadas dos notebooks', 'Bitcoin: tendência forte e sazonalidade nula nos períodos 7 e 365. Tráfego: sazonalidade diária e semanal forte. PM2.5: tendência forte com sazonalidade moderada. Temperatura: tendência e ciclos diário/semanal fortes. Ouro: tendência forte no preço em nível e sazonalidade semanal nula.');
  fill(importance, 'Separar contribuição autorregressiva, calendário e variáveis externas; discutir redundância e correlação', 'Em XGBoost, lags, nível/volatilidade e calendário são recorrentes; clima e poluentes aparecem na Base 3, condições de vapor na Base 4 e taxas na Base 5. Gain e permutação medem relevância preditiva, não causalidade, especialmente sob correlação entre features.');
  const models=chapter(7);
  fill(models, 'Registrar melhores parâmetros, espaço de busca, número de candidatos, critério e tempo da execução final', 'XGBoost: busca completa de 150 candidatos por base, três dobras temporais purgadas e parâmetros congelados; configurações e tempos estão em docs/modelo_xgboost.md e results/metrics.csv. Random Forest: oito candidatos e três dobras temporais nas Bases 1–4; suas saídas remotas de teste reajustam em oito blocos, embora o código atual mostre refit por origem. Na Base 5, o notebook registra refit por origem. SARIMAX: pipe rápida de busca/validação salva nos cinco notebooks, seguida por avaliação extensa com configuração congelada nas Bases 1, 2, 3 e 5; a Base 4 permanece sem avaliação extensa. Holt-Winters: parâmetros e diagnósticos nos notebooks, sem resumo único comparável de custo e busca nas 20 combinações.');
  models.querySelectorAll('.callout').forEach(el=>{
    if(el.textContent.includes('SARIMAX remoto: execução reduzida'))
      el.innerHTML='<strong>SARIMAX: pipe rápida e avaliação posterior</strong> Os cinco notebooks salvos exibem busca reduzida e quatro origens. CSVs extensos das Bases 1, 2, 3 e 5 foram produzidos depois com configuração congelada; a Base 4 não foi executada integralmente por custo computacional. Os resultados reduzidos não são tratados como MAE final.';
  });
  const xgb=chapter(11);
  fill(xgb, 'Relacionar parâmetros homologados, desempenho, custo e importâncias por base', 'XGBoost foi executado nas cinco bases com 842, 3.372, 2.847, 82.830 e 586 origens. Superou a persistência nas Bases 2, 3 e 4; perdeu marginalmente nas Bases 1 e 5. Os reajustes periódicos são 7, 24, 24, 144 e 4 origens e foram definidos por custo operacional, não pelo teste.');
  const protocol=chapter(6);
  protocol.append(note('Protocolo planejado versus execução observada',[
    'O projeto define horizonte de um passo, avanço temporal e intenção de origens comuns. A auditoria dos artefatos mostrou que esse último requisito não foi plenamente cumprido. Por isso, a análise quantitativa entre modelos é exploratória e deve ser lida junto com o número de origens de cada célula da matriz.'
  ]));
  protocol.append(note('Por que cada família recebeu tratamento operacional distinto',[
    'As famílias têm custos e requisitos de entrada diferentes. Holt-Winters modela nível, tendência e sazonalidade do alvo; RF e XGBoost exigem a construção causal de lags, janelas e covariáveis, que pode reduzir as primeiras origens válidas; SARIMAX precisa estimar ordens e componentes sazonais a cada ajuste, custo especialmente alto na série de 10 minutos da Base 4. O XGBoost adota cadência de reajuste previamente definida por base; o RF salvo usa oito blocos nas Bases 1–4 e refit por origem na Base 5; a pipe rápida SARIMAX reduz busca e teste no notebook. Essas escolhas tornam o estudo executável, mas alteram o procedimento observado. Não foi medida a contribuição exata de cada regra para todas as diferenças de amostra.',
    'A pipe rápida SARIMAX foi definida e executada nos notebooks das cinco bases para verificar o mesmo fluxo de busca, congelamento e previsão de um passo na frequência própria de cada série. O resultado reduzido usa quatro origens e não deve ser confundido com uma comparação numérica de MAEs entre bases: USD/BTC, veículos/hora, µg/m³, °C e retorno semanal têm escalas distintas. Em quatro bases há CSVs extensos posteriores; na Base 4 só o teste reduzido foi concluído.'
  ]));
  protocol.append(table('Estratégia executada e efeito na comparação',
    ['Modelo','Tratamento observado','Razão operacional','Limite'],[
      ['Holt-Winters','Série univariada e avaliação extensa','Estrutura de nível/tendência/sazonalidade sem engenharia de exógenas','Origens não idênticas às das árvores'],
      ['SARIMAX','Pipe rápida no notebook; CSV extenso em 1, 2, 3 e 5','Ajustes sazonais por origem são custosos; Base 4 de 10 minutos não foi concluída','Smoke não substitui teste final; 2/3 têm horizontes a filtrar'],
      ['Random Forest','Busca temporal; saída remota em 8 blocos nas Bases 1–4 e refit por origem na Base 5','Reajuste de árvores tem custo; lags e janelas exigem histórico','Nas Bases 1–4, código atual e saídas salvas têm cadências diferentes'],
      ['XGBoost','Busca de 150 candidatos; refit 7/24/24/144/4','Cadência congelada para controlar custo por base','Contagens não comprovam mesmas datas das demais famílias']
    ]));
  protocol.append(note('Base 4: limite computacional declarado',[
    'O notebook SARIMAX da Base 4 registra a pipe rápida e quatro origens de teste, mas a avaliação extensa não foi rodada. Na frequência de 10 minutos, o teste comparável teria dezenas de milhares de origens e reajustes SARIMAX repetidos; a equipe estimou que levaria dias. Essa estimativa não é uma medição de tempo final e não autoriza atribuir MAE, gráfico residual final ou posição à Base 4. A decisão de não executar deve ser aceita como limitação explícita pelo professor.'
  ]));
  protocol.append(note('Justificativa e limite de conformidade',[
    'A falta de tempo para reexecutar os notebooks explica por que a equipe apresenta resultados individuais, filtros de horizonte e uma comparação pareada parcial. Essa justificativa não transforma testes diferentes em uma avaliação comum nem substitui as exigências do enunciado: quatro modelos nas cinco bases, mesmas origens e observações, ranking por base, vitórias e posição média. A entrega parcial requer avaliação explícita do professor.'
  ]));
  const conclusion=chapter(12);
  conclusion.append(note('Conclusão que os dados permitem',[
    'Os modelos produziram evidências individuais de previsão fora da amostra, mas a auditoria não sustenta uma classificação única das quatro famílias nas cinco bases. MAEs de séries diferentes têm unidades distintas e não devem ser somados ou promediados; MAEs da mesma base com origens diferentes não devem ser usados para proclamar um vencedor.',
    'A Base 5 é a mais próxima de uma comparação comum pela contagem de 586 origens, porém a igualdade exata de Random Forest e XGBoost com o teste canônico não pôde ser verificada a partir dos artefatos disponíveis. A Base 4 teve apenas a pipe rápida SARIMAX de quatro origens; a avaliação extensa foi omitida por custo estimado elevado. Essas limitações são parte do resultado do trabalho, não resultados corrigidos ou omitidos.'
  ]));
  fill(conclusion, 'Preencher após verificar origens comuns, MAE, resíduos e importância das features', 'As execuções confirmam previsões fora da amostra e diagnósticos residuais. Tráfego e temperatura exibem padrões sazonais fortes; Bitcoin e ouro são mais difíceis de melhorar além da persistência. Não há evidência suficiente para declarar vencedor único entre os quatro modelos nas cinco bases.');
  fill(conclusion, 'Vincular cada recomendação a evidência validada e indicar condições de aplicação', 'Reavaliar os quatro modelos sobre a mesma lista de origens em cada base, exportar resíduos e importância de modo uniforme e só então calcular ranking, vitórias e posição média. A equivalência de Jena com a distribuição TensorFlow/Keras foi comprovada; ainda faltam a data da transferência e a moeda do ouro e os horários históricos de publicação das taxas para homologação operacional.');
  document.querySelector('#pagina-2 .finding .block-slot').textContent='Os quatro modelos possuem evidências individuais fora da amostra, mas as Bases 1–4 não têm origens comuns entre famílias; não existe ranking final defensável. O SARIMAX da Base 4 está excluído desta atualização.';
  document.querySelector('#pagina-2 .finding .block-slot').dataset.pending='false';
  document.querySelector('#pagina-2 .finding-evidence .slot').textContent='Matriz de MAE da seção 08 e auditoria em results/achados_auditoria.json.';
  document.querySelector('#pagina-2 .finding-evidence .slot').dataset.pending='false';
  const overview=document.querySelector('#pagina-4 .finding');
  if(overview){
    overview.querySelector('.block-slot').textContent='As cinco bases variam em unidade, frequência e força sazonal; por isso, a comparação entre elas exige posições e vitórias obtidas após alinhar as origens, nunca média bruta de MAE.';
    overview.querySelector('.block-slot').dataset.pending='false';
    overview.querySelector('.finding-evidence .slot').textContent='Metadados das cinco bases; seções 05 e 08 deste relatório.';
    overview.querySelector('.finding-evidence .slot').dataset.pending='false';
  }
  fill(chapter(13), 'Padronizar referências completas e datas reais de acesso; não inventar datas de download', 'Referências de origem documentadas por base e por DOI quando disponível. Datas de download não comprovadas não foram fabricadas; confirmar antes da submissão final.');
  fill(appendix, 'Anexar logs, parâmetros, contratos de teste, previsões e arquivos reproduzíveis', 'Arquivos de evidência: results/metricas_individuais_auditadas.csv, results/comparacao_pareada_hw_sarimax.csv, results/ljung_box_auditado.csv, results/figuras_sarimax/manifesto.csv, results/metrics.csv e notebooks executados. Os CSVs completos de Holt-Winters/SARIMAX usados na auditoria não estão todos no Git; o pacote contém resultados compactos e figuras geradas, não esses CSVs completos.');
  const dailyTable=Array.from(appendix.querySelectorAll('table')).find(el=>el.caption?.textContent.includes('Registro diário individual'));
  if(dailyTable)dailyTable.replaceWith(paragraph('O acompanhamento de demandas fornecido pelo grupo em 05/10/2026 acompanha a entrega como registro_demandas.pdf. Ele informa responsáveis, datas, esforço, complexidade e status, mas não comprova uma linha de execução para cada dia. O grupo deve revisar essa adequação ao enunciado com o professor; não se inferem dados adicionais a partir dos commits.'));
  appendix.querySelectorAll('p').forEach(el=>{
    if(el.textContent.startsWith('A planilha operacional de demandas é mantida fora do repositório'))
      el.textContent='A planilha operacional original é mantida pelo grupo fora do repositório. Uma cópia em PDF do acompanhamento recebido integra o pacote da entrega; sua adequação ao formato diário exigido ainda requer revisão humana.';
  });
  appendix.querySelectorAll('tr').forEach(row=>{
    if(row.cells?.[0]?.textContent.trim()==='D15' && row.cells.length>1)
      row.cells[1].textContent='projeto.yaml; registro_demandas.pdf (acompanhamento fornecido pelo grupo em 05/10/2026)';
  });
  document.querySelectorAll('td').forEach(cell=>{
    if(cell.textContent.includes('planilha operacional externa do grupo (não disponibilizada nesta atualização)'))
      cell.textContent=cell.textContent.replace('planilha operacional externa do grupo (não disponibilizada nesta atualização)',
        'registro_demandas.pdf (acompanhamento fornecido pelo grupo em 05/10/2026)');
  });
  chapter(14).querySelectorAll('p').forEach(el=>{
    if(el.textContent.startsWith('Relatório v2 gerado após git pull'))
      el.textContent=`Auditoria documental atualizada em 05/10/2026. Revisão Git consultada na geração: ${window.REPORT_V2_SNAPSHOT.commit}; os novos arquivos desta atualização não estão necessariamente incluídos nesse identificador. Foram usados os CSVs locais de previsão disponíveis. O SARIMAX da Base 4 não integra a comparação.`;
  });
  results.querySelectorAll('.subtle').forEach(el=>{
    if(el.textContent.includes('sincronizados em'))el.textContent='Origem documental: results/metrics.csv, projeto.yaml e docs/modelo_xgboost.md. O identificador Git do consolidado e os CSVs locais têm proveniências próprias; a auditoria distingue essas fontes.';
  });
  const notice=document.querySelector('.notice');
  if(notice){notice.querySelector('strong').textContent='Resultados auditados, comparação limitada.';notice.childNodes.forEach(node=>{if(node.nodeType===Node.TEXT_NODE&&node.textContent.includes('Resultados e evidências pendentes'))node.textContent=' Os resultados disponíveis e as limitações de comparabilidade estão descritos no relatório.'})}
  document.querySelectorAll('.page-foot span:first-child').forEach(el=>el.textContent='Séries Temporais · resultados com limitações declaradas');
})();
