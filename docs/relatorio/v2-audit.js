(() => {
  'use strict';
  if(document.body.dataset.auditVersion==='1')return;
  document.body.dataset.auditVersion='1';
  const chapter = number => document.querySelector(`[data-chapter="${number}"] .page-body`);
  const paragraph = text => { const p=document.createElement('p');p.textContent=text;return p; };
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
  const protocol=chapter(6);
  protocol.append(note('Protocolo planejado versus execução observada',[
    'O projeto define horizonte de um passo, avanço temporal e intenção de origens comuns. A auditoria dos artefatos mostrou que esse último requisito não foi plenamente cumprido. Por isso, a análise quantitativa entre modelos é exploratória e deve ser lida junto com o número de origens de cada célula da matriz.'
  ]));
  const conclusion=chapter(12);
  conclusion.append(note('Conclusão que os dados permitem',[
    'Os modelos produziram evidências individuais de previsão fora da amostra, mas a auditoria não sustenta uma classificação única das quatro famílias nas cinco bases. MAEs de séries diferentes têm unidades distintas e não devem ser somados ou promediados; MAEs da mesma base com origens diferentes não devem ser usados para proclamar um vencedor.',
    'A Base 5 é a mais próxima de uma comparação comum pela contagem de 586 origens, porém a igualdade exata de Random Forest e XGBoost com o teste canônico não pôde ser verificada a partir dos artefatos disponíveis. A Base 4 permanece sem avaliação SARIMAX final. Essas limitações são parte do resultado do trabalho, não resultados corrigidos ou omitidos.'
  ]));
  chapter(14).querySelectorAll('p').forEach(el=>{
    if(el.textContent.startsWith('Relatório v2 gerado após git pull'))
      el.textContent='Auditoria documental atualizada em 04/10/2026 com base no commit b483b781e226822f6b9477f1e303c7d0b2e43feb e nos CSVs locais de previsão disponíveis nesta data. Os resultados SARIMAX da Base 4 permanecem parciais e não integram a comparação final.';
  });
  const notice=document.querySelector('.notice');
  if(notice){notice.querySelector('strong').textContent='Resultados auditados, comparação limitada.';notice.childNodes.forEach(node=>{if(node.nodeType===Node.TEXT_NODE&&node.textContent.includes('Resultados e evidências pendentes'))node.textContent=' Os resultados disponíveis e as limitações de comparabilidade estão descritos no relatório.'})}
  document.querySelectorAll('.page-foot span:first-child').forEach(el=>el.textContent='Séries Temporais · resultados com limitações declaradas');
})();
