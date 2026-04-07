# -*- coding: utf-8 -*-
"""
Módulo para carregamento e detecção automática dos CSVs do MiFitness.
Detecta o prefixo dinâmico dos arquivos (ex: 20260407_6383745807_MiFitness_).
"""

import csv
import os
import re


# Sufixos dos CSVs que o app utiliza
ARQUIVOS_NECESSARIOS = {
    "perfil": "user_fitness_profile.csv",
    "membro": "user_member_profile.csv",
    "dispositivos": "hlth_center_data_source.csv",
    "agregados": "hlth_center_aggregated_fitness_data.csv",
    "treinos": "hlth_center_sport_record.csv",
}

ARQUIVOS_OPCIONAIS = {
    "fitness_data": "hlth_center_fitness_data.csv",
    "sport_track": "hlth_center_sport_track_data.csv",
    "device_setting": "user_device_setting.csv",
    "fitness_records": "user_fitness_data_records.csv",
}


def detectar_prefixo(lista_arquivos: list[str]) -> str:
    """
    Detecta automaticamente o prefixo dos CSVs do MiFitness.
    Procura por padrões como: YYYYMMDD_USERID_MiFitness_
    
    Args:
        lista_arquivos: lista dos nomes de arquivos extraídos do ZIP
    
    Returns:
        string com o prefixo detectado, ou string vazia se não encontrar
    """
    padrao = re.compile(r"(\d{8}_\d+_MiFitness_)")
    
    for arquivo in lista_arquivos:
        # Pegar só o nome do arquivo (sem path)
        nome = os.path.basename(arquivo)
        match = padrao.search(nome)
        if match:
            return match.group(1)
    
    return ""


def carregar_csv(caminho: str) -> list[dict]:
    """
    Carrega um CSV e retorna lista de dicts.
    """
    if not os.path.exists(caminho):
        return []
    
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception:
        return []


def carregar_todos_csvs(temp_dir: str, lista_arquivos: list[str]) -> dict:
    """
    Carrega todos os CSVs necessários a partir do diretório temporário.
    
    Args:
        temp_dir: caminho do diretório temporário
        lista_arquivos: lista de nomes de arquivos extraídos
    
    Returns:
        dict com os dados carregados:
        {
            "perfil": [...],
            "membro": [...],
            "dispositivos": [...],
            "agregados": [...],
            "treinos": [...],
            "prefixo": "...",
            "arquivos_encontrados": [...],
            "arquivos_ausentes": [...]
        }
    """
    prefixo = detectar_prefixo(lista_arquivos)
    
    resultado = {
        "prefixo": prefixo,
        "arquivos_encontrados": [],
        "arquivos_ausentes": [],
    }
    
    for chave, sufixo in ARQUIVOS_NECESSARIOS.items():
        nome_esperado = prefixo + sufixo
        
        # Procurar o arquivo (pode estar em subdiretório)
        caminho = None
        for a in lista_arquivos:
            if os.path.basename(a) == nome_esperado or a.endswith(sufixo):
                caminho = os.path.join(temp_dir, a)
                break
        
        if caminho and os.path.exists(caminho):
            resultado[chave] = carregar_csv(caminho)
            resultado["arquivos_encontrados"].append(sufixo)
        else:
            resultado[chave] = []
            resultado["arquivos_ausentes"].append(sufixo)
    
    return resultado
