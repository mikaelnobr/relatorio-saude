# -*- coding: utf-8 -*-
"""
Processador de registros de treinos/exercícios.
"""

from src.helpers import parse_json_value, ts_to_python_date


def processar_treinos(dados_csv: list[dict], data_inicio=None, data_fim=None) -> list[dict]:
    """
    Processa o CSV hlth_center_sport_record.
    
    Args:
        dados_csv: dados do CSV
        data_inicio: date object (opcional)
        data_fim: date object (opcional)
    
    Returns:
        lista de dicts com dados de cada treino, ordenada por data
    """
    treinos = []
    
    for row in dados_csv:
        val = parse_json_value(row.get("Value", "{}"))
        if not isinstance(val, dict):
            continue
        
        tipo = row.get("Key", "desconhecido")
        start_time = val.get("start_time", row.get("Time", 0))
        
        # Filtrar por período
        if start_time and (data_inicio or data_fim):
            try:
                data = ts_to_python_date(start_time)
                if data_inicio and data < data_inicio:
                    continue
                if data_fim and data > data_fim:
                    continue
            except (ValueError, OSError):
                continue
        
        treinos.append({
            "tipo": tipo.replace("_", " ").title(),
            "data": start_time,
            "duracao_seg": val.get("duration", 0),
            "calorias": val.get("calories", 0),
            "calorias_total": val.get("total_cal", 0),
            "fc_media": val.get("avg_hrm", 0),
            "fc_max": val.get("max_hrm", 0),
            "fc_min": val.get("min_hrm", 0),
            "distancia": val.get("distance", 0),
            "passos": val.get("steps", 0),
            "vitalidade": val.get("vitality", 0),
            "zona_aquecimento": val.get("hrm_warm_up_duration", 0),
            "zona_queima": val.get("hrm_fat_burning_duration", 0),
            "zona_aerobica": val.get("hrm_aerobic_duration", 0),
            "zona_anaerobica": val.get("hrm_anaerobic_duration", 0),
            "zona_extrema": val.get("hrm_extreme_duration", 0),
        })
    
    return sorted(treinos, key=lambda x: x["data"])
