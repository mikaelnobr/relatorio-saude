# -*- coding: utf-8 -*-
"""
Processador de dispositivos vinculados.
"""


def processar_dispositivos(dados_csv: list[dict]) -> list[str]:
    """
    Processa o CSV hlth_center_data_source.
    
    Returns:
        lista de strings com nome e modelo dos dispositivos
    """
    dispositivos = []
    for d in dados_csv:
        nome = d.get("Name", "") or d.get("Alias", "")
        modelo = d.get("Model", "")
        if nome:
            dispositivos.append(f"{nome} ({modelo})")
    return dispositivos
