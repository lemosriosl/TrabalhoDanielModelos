import csv
from pathlib import Path

from series_temporais.reporting.gerar_relatorio_v2 import achados_compactos


ROOT = Path(__file__).resolve().parents[1]


def _rows(name: str) -> list[dict]:
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_achados_reconstituiveis_sem_json_excluido_do_pacote():
    findings = achados_compactos(
        _rows("metricas_individuais_auditadas.csv"),
        _rows("comparacao_pareada_hw_sarimax.csv"),
    )
    assert any("base_02: SARIMAX possui 14 de 7598" in text for text in findings)
    assert any("base_03: SARIMAX possui 53 de 6824" in text for text in findings)
    assert any("base_04: SARIMAX final não consta" in text for text in findings)
    assert any("base_02: Holt-Winters e SARIMAX têm 7584 origens" in text for text in findings)
    assert not any("discordam em alvo" in text for text in findings)
