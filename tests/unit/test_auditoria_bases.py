from pathlib import Path

from series_temporais.data.auditoria_bases import auditar_todas


ROOT = Path(__file__).resolve().parents[2]
PATHS = {
    "base_01": ROOT / "trabalho/bases/grupo1/grupo1.csv",
    "base_02": ROOT / "trabalho/bases/grupo2/grupo2.csv",
    "base_03": ROOT / "trabalho/bases/grupo3/PRSA_Data_Aotizhongxin_20130301-20170228.csv",
    "base_04": ROOT / "trabalho/bases/grupo4/grupo4.csv",
    "base_05": ROOT / "trabalho/bases/grupo5/grupo5.csv",
}


def test_auditoria_cobre_as_cinco_bases_sem_alterar_origem():
    audit = auditar_todas(PATHS)
    assert set(audit) == set(PATHS)
    assert all(len(row["sha256"]) == 64 for row in audit.values())
    assert audit["base_01"]["lacunas_diarias"] == 0
    assert audit["base_02"]["timestamps_duplicados"] > 0
    assert audit["base_03"]["lacunas_horarias"] == 0
    assert audit["base_04"]["total_codigos_menos_9999"] > 0
    assert audit["base_05"]["esquema"] == "ouro_com_taxas"
    assert audit["base_05"]["target_entregue_igual_proxima_linha_fracao"] < 1


def test_auditoria_registra_riscos_de_disponibilidade():
    audit = auditar_todas(PATHS)
    assert audit["base_02"]["nulos_alvo"] == 0
    assert audit["base_03"]["nulos_numericos"]["PM2.5"] > 0
    assert audit["base_04"]["timestamps_ausentes_na_grade"] > 0
    assert audit["base_05"]["nulos_preco"] == 0
    assert audit["base_05"]["lag_1_entregue_igual_shift_fracao"] < 1
