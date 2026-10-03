# Regras de dados

- Nunca modificar ou sobrescrever os arquivos congelados em `data/base_NN/raw.csv`.
- Registrar fonte, data de acesso e checksum de cada base.
- Validar ordenacao temporal, frequencia, duplicidades e ausencias antes da modelagem.
- Ajustar transformacoes apenas com o recorte de treino aplicavel.
- Marcar explicitamente a disponibilidade temporal de cada variavel externa.
- Nao usar valores futuros observados como features.
- Gerar dados intermediarios e processados somente por scripts ou funcoes versionadas.
- Materiais em `docs/Bases de exemplo/` sao referencias didaticas e nao se tornam automaticamente as cinco bases finais.

