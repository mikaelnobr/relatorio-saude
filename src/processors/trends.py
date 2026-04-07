# -*- coding: utf-8 -*-
"""
Análise de tendências e padrões nos dados.
"""

from collections import defaultdict
from datetime import datetime
from src.helpers import FUSO, ts_to_weekday


def analisar_tendencia_passos(steps: list[dict]) -> dict:
    """Compara primeira e segunda metade do período de passos."""
    if len(steps) < 14:
        return {}
    
    sorted_steps = sorted(steps, key=lambda x: int(x["data"]))
    meio = len(sorted_steps) // 2
    media_1 = sum(s["passos"] for s in sorted_steps[:meio]) / meio
    media_2 = sum(s["passos"] for s in sorted_steps[meio:]) / (len(sorted_steps) - meio)
    variacao = ((media_2 - media_1) / media_1) * 100
    
    return {
        "media_1": media_1,
        "media_2": media_2,
        "variacao_pct": variacao,
    }


def analisar_tendencia_fc(hr: list[dict]) -> dict:
    """Compara FC de repouso entre primeira e segunda metade."""
    if len(hr) < 14:
        return {}
    
    sorted_hr = sorted(hr, key=lambda x: int(x["data"]))
    meio = len(sorted_hr) // 2
    rhr1 = [h["fc_repouso"] for h in sorted_hr[:meio] if h["fc_repouso"] > 0]
    rhr2 = [h["fc_repouso"] for h in sorted_hr[meio:] if h["fc_repouso"] > 0]
    
    if not rhr1 or not rhr2:
        return {}
    
    m1 = sum(rhr1) / len(rhr1)
    m2 = sum(rhr2) / len(rhr2)
    
    return {
        "media_1": m1,
        "media_2": m2,
        "variacao": m2 - m1,
        "status": "melhora" if m2 < m1 else "piora",
    }


def analisar_tendencia_sono(sleep: list[dict]) -> dict:
    """Compara scores de sono entre primeira e segunda metade."""
    sorted_sleep = sorted([s for s in sleep if s["score"] > 0], key=lambda x: int(x["data"]))
    
    if len(sorted_sleep) < 14:
        return {}
    
    meio = len(sorted_sleep) // 2
    score1 = sum(s["score"] for s in sorted_sleep[:meio]) / meio
    score2 = sum(s["score"] for s in sorted_sleep[meio:]) / (len(sorted_sleep) - meio)
    
    return {
        "score_1": score1,
        "score_2": score2,
        "variacao": score2 - score1,
    }


def padroes_por_dia_semana(steps: list[dict]) -> list[dict]:
    """Calcula média de passos por dia da semana."""
    if not steps:
        return []
    
    dias_semana = defaultdict(list)
    for s in steps:
        dia = ts_to_weekday(s["data"])
        dias_semana[dia].append(s["passos"])
    
    ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    resultado = []
    for dia in ordem:
        if dia in dias_semana:
            vals = dias_semana[dia]
            resultado.append({
                "dia": dia,
                "media": sum(vals) / len(vals),
                "registros": len(vals),
            })
    
    return resultado


def frequencia_semanal_treinos(treinos: list[dict], tipo_filtro: str = None) -> dict:
    """Calcula frequência semanal de treinos por tipo."""
    semanas = defaultdict(int)
    
    for t in treinos:
        if tipo_filtro and tipo_filtro.lower() not in t["tipo"].lower():
            continue
        dt = datetime.fromtimestamp(int(t["data"]), tz=FUSO)
        semana = dt.isocalendar()[1]
        ano = dt.isocalendar()[0]
        semanas[f"{ano}-S{semana:02d}"] += 1
    
    media = sum(semanas.values()) / len(semanas) if semanas else 0
    
    return {
        "semanas": dict(sorted(semanas.items())),
        "media_semanal": media,
    }
