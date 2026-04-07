# -*- coding: utf-8 -*-
"""
Processador de dados agregados diários:
passos, sono, frequência cardíaca, calorias, intensidade, estresse, SpO2, horas em pé.
"""

from collections import defaultdict
from src.helpers import parse_json_value, ts_to_python_date


def processar_agregados(dados_csv: list[dict], data_inicio=None, data_fim=None) -> dict:
    """
    Processa o CSV hlth_center_aggregated_fitness_data.
    Filtra por período se data_inicio e/ou data_fim forem fornecidos.
    
    Args:
        dados_csv: dados do CSV
        data_inicio: date object (opcional)
        data_fim: date object (opcional)
    
    Returns:
        dict com listas de métricas diárias: steps, sleep, heart_rate, calories,
        intensity, stress, spo2, stand
    """
    metricas = defaultdict(list)
    
    for row in dados_csv:
        tag = row.get("Tag", "")
        key = row.get("Key", "")
        time = row.get("Time", "")
        value = row.get("Value", "")
        
        if tag != "daily_report":
            continue
        
        # Filtrar por período
        if time and (data_inicio or data_fim):
            try:
                data = ts_to_python_date(time)
                if data_inicio and data < data_inicio:
                    continue
                if data_fim and data > data_fim:
                    continue
            except (ValueError, OSError):
                continue
        
        val = parse_json_value(value)
        
        if key == "steps" and isinstance(val, dict):
            metricas["steps"].append({
                "data": time,
                "passos": val.get("steps", 0),
                "distancia_m": val.get("distance", 0),
                "calorias": val.get("calories", 0),
            })
        elif key == "sleep" and isinstance(val, dict):
            metricas["sleep"].append({
                "data": time,
                "duracao_total": val.get("total_duration", 0),
                "sono_profundo": val.get("sleep_deep_duration", 0),
                "sono_leve": val.get("sleep_light_duration", 0),
                "sono_rem": val.get("sleep_rem_duration", 0),
                "acordado": val.get("sleep_awake_duration", 0),
                "score": val.get("sleep_score", 0),
                "fc_media": val.get("avg_hr", 0),
                "fc_min": val.get("min_hr", 0),
                "fc_max": val.get("max_hr", 0),
            })
        elif key == "heart_rate" and isinstance(val, dict):
            metricas["heart_rate"].append({
                "data": time,
                "fc_media": val.get("avg_hr", 0),
                "fc_repouso": val.get("avg_rhr", 0),
                "fc_max": val.get("max_hr", 0),
                "fc_min": val.get("min_hr", 0),
                "zona_aquecimento": val.get("warm_up_hr_zone_duration", 0),
                "zona_queima": val.get("fat_burning_hr_zone_duration", 0),
                "zona_aerobica": val.get("aerobic_hr_zone_duration", 0),
                "zona_anaerobica": val.get("anaerobic_hr_zone_duration", 0),
                "zona_extrema": val.get("extreme_hr_zone_duration", 0),
            })
        elif key == "calories" and isinstance(val, dict):
            metricas["calories"].append({
                "data": time,
                "calorias": val.get("calories", 0),
            })
        elif key == "intensity" and isinstance(val, dict):
            metricas["intensity"].append({
                "data": time,
                "duracao_min": val.get("duration", 0),
            })
        elif key == "stress" and isinstance(val, dict):
            metricas["stress"].append({
                "data": time,
                "media": val.get("avg_stress", 0),
                "max": val.get("max_stress", 0),
                "min": val.get("min_stress", 0),
            })
        elif key == "spo2" and isinstance(val, dict):
            metricas["spo2"].append({
                "data": time,
                "media": val.get("avg_spo2", 0),
                "max": val.get("max_spo2", 0),
                "min": val.get("min_spo2", 0),
            })
        elif key == "valid_stand" and isinstance(val, dict):
            metricas["stand"].append({
                "data": time,
                "contagem": val.get("count", 0),
            })
    
    return dict(metricas)
