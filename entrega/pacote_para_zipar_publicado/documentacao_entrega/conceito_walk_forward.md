# Walk-forward para avaliação de séries temporais

## Conceito

Walk-forward, também chamado de *rolling forecasting origin*, é uma forma de
avaliar previsões respeitando a ordem temporal. Em cada origem `t`, o modelo
pode usar somente dados e alvos que já eram conhecidos em `t`; então produz a
previsão para um horizonte fixo `h`.

Para o protocolo deste projeto, `h = 1` passo da frequência de cada base. Logo,
cada previsão deve usar o passado disponível na origem e prever exatamente a
próxima observação: um dia à frente na Base 1, uma hora nas Bases 2 e 3, dez
minutos na Base 4 e uma semana na Base 5.

## Procedimento correto

1. Fixar a primeira origem de teste e separar o histórico anterior a ela.
2. Ajustar os hiperparâmetros somente no treino, com dobras temporais. Depois
   de escolhidos, os hiperparâmetros ficam congelados no teste final.
3. Na origem `t`, ajustar ou atualizar o modelo apenas com linhas cujo alvo já
   foi observado antes de `t`.
4. Construir as features disponíveis em `t` e prever `y_(t+1)`.
5. Registrar a previsão sem modificá-la.
6. Quando `y_(t+1)` for revelado, avançar a origem e incorporá-lo ao histórico.
7. Repetir até o fim do teste e calcular MAE somente com as previsões registradas
   fora da amostra.

Em uma janela expansiva, todo o histórico observado é mantido. Em uma janela
móvel, apenas os últimos `W` pontos permanecem. Os dois desenhos são válidos,
mas a escolha precisa ser única e declarada antes da comparação entre modelos.

## Regras de comparabilidade

- Todos os modelos de uma base usam as mesmas origens, o mesmo horizonte e os
  mesmos alvos de teste.
- Uma covariável só pode entrar na previsão se for conhecida na origem. Caso
  contrário, usar sua defasagem ou uma previsão externa disponível naquele
  instante.
- Reajustar o modelo a cada passo é o caso estrito. Reajuste periódico também é
  válido, desde que cada previsão ainda use somente informação passada e que a
  cadência seja igual entre os modelos comparados.
- Um único `get_forecast` para todo o conjunto de teste não é walk-forward de
  um passo: mistura horizontes de 1 até o tamanho do teste.

## Fontes

- Hyndman, R. J.; Athanasopoulos, G. *Forecasting: Principles and Practice*,
  3. ed., seção 5.10: [Time series cross-validation](https://otexts.com/fpp3/tscv.html).
- scikit-learn: [Cross-validation of time series data e TimeSeriesSplit](https://scikit-learn.org/stable/modules/cross_validation).
- Hyndman, R. J.; Athanasopoulos, G. *Forecasting: Principles and Practice*,
  2. ed., seção 3.4: [Evaluating forecast accuracy](https://otexts.com/fpp2/accuracy.html).
