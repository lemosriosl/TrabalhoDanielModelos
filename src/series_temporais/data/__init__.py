"""Preparação reproduzível das bases."""

from .preparacao_base5 import (
    ALVO_CANONICO,
    PROPORCAO_TREINO,
    REGRA_SEMANAL,
    construir_quadro_ouro,
    dividir_quadro_ouro,
    preparar_modelagem_ouro,
    preparar_ouro_semanal,
    selecionar_alvos_observados,
)

__all__ = [
    "ALVO_CANONICO",
    "PROPORCAO_TREINO",
    "REGRA_SEMANAL",
    "construir_quadro_ouro",
    "dividir_quadro_ouro",
    "preparar_modelagem_ouro",
    "preparar_ouro_semanal",
    "selecionar_alvos_observados",
]
