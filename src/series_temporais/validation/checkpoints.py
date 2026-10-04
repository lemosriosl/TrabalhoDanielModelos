"""Identificação conservadora das buscas temporais, sem ler o teste final."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pandas as pd


def codigo_metodologico(notebook, *, funcoes, arquivos=()):
    """Hash da lógica relevante; ignora outputs, Markdown e formatação."""
    notebook = json.loads(Path(notebook).read_text(encoding="utf-8"))
    wanted = set(funcoes)
    found = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in wanted:
                if node.name in found:
                    raise ValueError(f"Função metodológica duplicada: {node.name}")
                found[node.name] = ast.dump(node, include_attributes=False)
    if wanted.difference(found):
        raise ValueError(f"Funções não encontradas: {sorted(wanted.difference(found))}")
    payload = {
        "funcoes": found,
        "arquivos": [hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in arquivos],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def assinatura_busca_temporal(quadro, *, features, alvo, origem, instante_alvo,
                              protocolo, codigo):
    """Assina somente o treino/tuning; inclui valores, contrato e implementação."""
    features = list(features)
    if len(features) != len(set(features)) or alvo in features:
        raise ValueError("Features duplicadas ou alvo usado como feature.")
    columns = [origem, instante_alvo, alvo, *features]
    if len(columns) != len(set(columns)):
        raise ValueError("Colunas do contrato devem ser distintas.")
    selected = quadro.loc[:, columns]
    if selected.empty or selected.isna().any().any():
        raise ValueError("Quadro de tuning vazio ou com valores ausentes.")
    origins = pd.to_datetime(selected[origem], errors="raise")
    targets = pd.to_datetime(selected[instante_alvo], errors="raise")
    if origins.duplicated().any() or not origins.is_monotonic_increasing or not targets.gt(origins).all():
        raise ValueError("Contrato temporal inválido.")
    values = pd.util.hash_pandas_object(selected, index=False).to_numpy().tobytes()
    payload = {
        "schema": 2,
        "colunas": columns,
        "tipos": [str(dtype) for dtype in selected.dtypes],
        "linhas": len(selected),
        "dados": hashlib.sha256(values).hexdigest(),
        "protocolo": protocolo,
        "codigo": codigo,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()
