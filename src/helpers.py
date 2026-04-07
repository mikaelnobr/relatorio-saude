# -*- coding: utf-8 -*-
"""
Funções utilitárias para conversão de timestamps, parse de JSON e formatação.
"""

import json
from datetime import datetime, timezone, timedelta

# Fuso horário padrão (BRT)
FUSO = timezone(timedelta(hours=-3))


def ts_to_date(ts):
    """Converte timestamp Unix para data legível (BRT)."""
    return datetime.fromtimestamp(int(ts), tz=FUSO).strftime("%d/%m/%Y")


def ts_to_datetime(ts):
    """Converte timestamp Unix para data+hora legível (BRT)."""
    return datetime.fromtimestamp(int(ts), tz=FUSO).strftime("%d/%m/%Y %H:%M")


def ts_to_weekday(ts):
    """Converte timestamp Unix para dia da semana abreviado."""
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    return dias[datetime.fromtimestamp(int(ts), tz=FUSO).weekday()]


def ts_to_python_date(ts):
    """Converte timestamp Unix para objeto date do Python."""
    return datetime.fromtimestamp(int(ts), tz=FUSO).date()


def parse_json_value(val_str):
    """Faz parse do campo Value que vem como JSON com aspas duplas escapadas."""
    try:
        return json.loads(val_str.replace('""', '"').strip('"'))
    except Exception:
        try:
            return json.loads(val_str)
        except Exception:
            return val_str


def min_para_hm(minutos):
    """Converte minutos para formato legível (ex: 2h30min)."""
    h = int(minutos) // 60
    m = int(minutos) % 60
    if h > 0:
        return f"{h}h{m:02d}min"
    return f"{m}min"


def seg_para_hm(segundos):
    """Converte segundos para formato legível (ex: 1h05min)."""
    h = int(segundos) // 3600
    m = (int(segundos) % 3600) // 60
    if h > 0:
        return f"{h}h{m:02d}min"
    return f"{m}min"


def formatar_numero(n):
    """Formata número com separador de milhares (ponto)."""
    return f"{n:,}".replace(",", ".")


def filtrar_por_periodo(registros, campo_data, data_inicio, data_fim):
    """
    Filtra lista de registros por período.
    
    Args:
        registros: lista de dicts
        campo_data: nome do campo que contém o timestamp
        data_inicio: date object (início do período)
        data_fim: date object (fim do período)
    
    Returns:
        lista filtrada
    """
    if data_inicio is None and data_fim is None:
        return registros
    
    filtrados = []
    for r in registros:
        ts = int(r[campo_data])
        data = ts_to_python_date(ts)
        if data_inicio and data < data_inicio:
            continue
        if data_fim and data > data_fim:
            continue
        filtrados.append(r)
    return filtrados
