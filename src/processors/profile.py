# -*- coding: utf-8 -*-
"""
Processador de perfil do usuário e dados do membro.
"""

from datetime import datetime
from src.helpers import FUSO, parse_json_value


def processar_perfil(dados_csv: list[dict]) -> dict:
    """
    Processa o CSV user_fitness_profile.
    
    Returns:
        dict com: peso, meta_calorias, meta_passos, meta_intensidade, fc_max_registrada
    """
    if not dados_csv:
        return {}
    
    d = dados_csv[0]
    peso_info = parse_json_value(d.get("InitialWeight", "{}"))
    goals = parse_json_value(d.get("RegularGoalList", "[]"))
    
    goal_map = {}
    for g in goals if isinstance(goals, list) else []:
        goal_map[g["field"]] = g["target"]
    
    return {
        "peso": peso_info.get("weight", "?"),
        "meta_calorias": goal_map.get(2, d.get("DailyCalGoal", "?")),
        "meta_passos": goal_map.get(1, d.get("DailyStepGoal", "?")),
        "meta_intensidade": goal_map.get(4, "?"),
        "fc_max_registrada": parse_json_value(d.get("RecordMaxHrm", "{}")).get("hrm", "?"),
    }


def processar_membro(dados_csv: list[dict]) -> dict:
    """
    Processa o CSV user_member_profile.
    
    Returns:
        dict com: nome, sexo, nascimento, idade, altura_cm, peso_atual_kg, imc, regiao
    """
    if not dados_csv:
        return {}
    
    d = dados_csv[0]
    nascimento = d.get("Birth", "")
    idade = None
    if nascimento:
        try:
            dt_nasc = datetime.strptime(nascimento, "%Y-%m-%d")
            hoje = datetime.now(tz=FUSO)
            idade = hoje.year - dt_nasc.year - ((hoje.month, hoje.day) < (dt_nasc.month, dt_nasc.day))
        except Exception:
            pass
    
    altura_cm = float(d.get("Height", 0) or 0)
    peso_kg = float(d.get("Weight", 0) or 0)
    imc = peso_kg / ((altura_cm / 100) ** 2) if altura_cm > 0 and peso_kg > 0 else None
    
    sexo_map = {"male": "Masculino", "female": "Feminino"}
    
    return {
        "nome": d.get("Name", "?"),
        "sexo": sexo_map.get(d.get("Sex", ""), d.get("Sex", "?")),
        "nascimento": nascimento,
        "idade": idade,
        "altura_cm": altura_cm,
        "peso_atual_kg": peso_kg,
        "imc": imc,
        "regiao": d.get("Region", "?"),
    }
