# Dicionário de variáveis externas — Base 4 (Clima de Jena)

Responsável: P2 — Pedro Henrique Gomes Frossard. Data da auditoria: 2026-09-22.

**Alvo:** `T (degC)`, a cada 10 minutos, estação meteorológica de Jena, Alemanha (série conhecida como Jena Climate). Confirmar referência original, fonte e licença antes da entrega final. Chave: `Date Time` (formato `dd.mm.yyyy HH:MM:SS`); 327 timestamps duplicados e códigos `-9999` em `wv (m/s)`/`max. wv (m/s)` devem ser tratados antes de qualquer junção.

Uma variável só pode prever `t+h` se estiver disponível na origem `t`; valor observado no futuro é vazamento. Todas as variáveis abaixo são medidas no mesmo instante que `T`, então **nenhuma** pode ser usada contemporânea ao próprio `t` que está sendo previsto — apenas defasadas. Como o Holt-Winters de referência do trabalho é univariado, essas variáveis não entram diretamente nele; ficam registradas como candidatas para os modelos multivariados (SARIMAX, Random Forest, modelo de especialização).

| ID | Variável | Disponibilidade em `t` | Chave/tratamento | Hipótese e risco | Status |
|---|---|---|---|---|---|
| G4_PRESSURE | `p (mbar)` | Simultânea a `T`; só serve como preditora se defasada. | `Date Time`; `lag(1)` ou anterior. | Pressão pode se associar a frentes climáticas; uso contemporâneo é vazamento. | Em validação |
| G4_TPOT | `Tpot (K)` | Simultânea a `T`. | `Date Time`; lag. | Temperatura potencial é quase-duplicata funcional de `T`; alto risco de redundância/vazamento se usada contemporânea. | Em validação |
| G4_TDEW | `Tdew (degC)` | Simultânea a `T`. | `Date Time`; lag. | Ponto de orvalho covaria fortemente com temperatura e umidade; usar apenas defasado. | Em validação |
| G4_HUMIDITY | `rh (%)`, `VPmax (mbar)`, `VPact (mbar)`, `VPdef (mbar)` | Simultâneas a `T`. | `Date Time`; limitar `rh` a 0–100; lag; avaliar multicolinearidade entre elas. | Grupo de variáveis de umidade/pressão de vapor, redundantes entre si; escolher subconjunto justificado. | Em validação |
| G4_SPECHUM | `sh (g/kg)`, `H2OC (mmol/mol)` | Simultâneas a `T`. | `Date Time`; lag. | Umidade específica e concentração de água, fortemente correlacionadas com `VPact`; redundância a controlar. | Em validação |
| G4_RHO | `rho (g/m**3)` | Simultânea a `T`. | `Date Time`; lag. | Densidade do ar é função de `T`, `p` e umidade; variável derivada das demais, redundante. | Em validação |
| G4_WIND_SPEED | `wv (m/s)`, `max. wv (m/s)` | Simultâneas a `T`. | `Date Time`; converter `-9999` para ausente antes de qualquer uso; lag. | Vento pode se associar a advecção térmica; `-9999` é código de ausência, não velocidade real — tratar antes de estatísticas ou modelagem. | Em validação |
| G4_WIND_DIR | `wd (deg)` | Simultânea a `T`. | `Date Time`; tratar como variável circular (seno/cosseno), não como escala linear; lag. | Direção do vento é circular; tratamento linear incorreto distorce a variável. | Proposto |
| G4_CALENDAR | Hora, dia da semana, mês e estação do ano | Conhecidos antecipadamente. | Derivados de `Date Time`; codificação cíclica; recalcular períodos se a série for reamostrada. | Pode capturar o ciclo diário (≈144 observações em 10 min) e a sazonalidade anual; período anual é computacionalmente caro para Holt-Winters. | Proposto |