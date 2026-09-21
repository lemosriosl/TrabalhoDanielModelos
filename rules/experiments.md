# Regras dos experimentos

- Usar exatamente as mesmas origens, horizonte e observacoes de teste nos quatro modelos de cada base.
- Usar walk-forward; divisao aleatoria de treino e teste e proibida.
- Otimizar hiperparametros antes da avaliacao final e sem consultar o teste final.
- Manter hiperparametros fixos durante o walk-forward final.
- Fixar a semente aleatoria definida em `config/projeto.yaml`.
- Registrar base, modelo, features, hiperparametros, versao do codigo, tempo, previsoes e residuos.
- Calcular MAE sobre previsoes fora da amostra.
- Comparar bases por vitorias e posicao media, nunca pela media bruta de MAEs de escalas diferentes.
- Random Forest e modelo de especializacao devem compartilhar features quando houver compatibilidade.

