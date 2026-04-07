# -*- coding: utf-8 -*-
"""
Gerador do relatório Markdown completo.
Mesma lógica do script original, refatorado para receber dados como parâmetro.
"""

from datetime import datetime
from src.helpers import (
    FUSO, ts_to_date, ts_to_datetime, ts_to_weekday,
    min_para_hm, seg_para_hm, formatar_numero
)
from src.processors.trends import (
    analisar_tendencia_passos, analisar_tendencia_fc,
    analisar_tendencia_sono, padroes_por_dia_semana,
    frequencia_semanal_treinos
)


def gerar_relatorio_markdown(perfil, membro, dispositivos, metricas, treinos) -> str:
    """
    Gera o relatório completo em formato Markdown.
    
    Returns:
        string com o relatório Markdown
    """
    steps = metricas.get("steps", [])
    sleep = metricas.get("sleep", [])
    hr = metricas.get("heart_rate", [])
    cal = metricas.get("calories", [])
    intensity = metricas.get("intensity", [])
    stand = metricas.get("stand", [])
    stress = metricas.get("stress", [])
    spo2 = metricas.get("spo2", [])
    
    # Período dos dados
    all_dates = [int(s["data"]) for s in steps]
    data_inicio = ts_to_date(min(all_dates)) if all_dates else "?"
    data_fim = ts_to_date(max(all_dates)) if all_dates else "?"
    total_dias = len(all_dates)
    
    r = []
    
    # ── Cabeçalho ──
    r.append("# 📊 RELATÓRIO COMPLETO DE SAÚDE E FITNESS")
    r.append("**Dados extraídos da conta Xiaomi MiFitness**")
    r.append(f"**Período:** {data_inicio} a {data_fim} ({total_dias} dias)")
    r.append(f"**Gerado em:** {datetime.now(tz=FUSO).strftime('%d/%m/%Y às %H:%M')}")
    r.append("")
    
    # ── Perfil ──
    r.append("---")
    r.append("## 👤 PERFIL DO USUÁRIO")
    r.append("")
    if membro.get("sexo"):
        r.append(f"- **Sexo:** {membro['sexo']}")
    if membro.get("nascimento"):
        idade_str = f" ({membro['idade']} anos)" if membro.get('idade') else ""
        r.append(f"- **Data de nascimento:** {membro['nascimento']}{idade_str}")
    if membro.get("altura_cm") and membro["altura_cm"] > 0:
        r.append(f"- **Altura:** {membro['altura_cm']:.0f} cm")
    if membro.get("peso_atual_kg") and membro["peso_atual_kg"] > 0:
        r.append(f"- **Peso atual:** {membro['peso_atual_kg']:.1f} kg")
    r.append(f"- **Peso inicial (no app):** {perfil.get('peso', '?')} kg")
    if membro.get("imc"):
        imc = membro['imc']
        if imc < 18.5:
            cat = "Abaixo do peso"
        elif imc < 25:
            cat = "Peso normal"
        elif imc < 30:
            cat = "Sobrepeso"
        else:
            cat = "Obesidade"
        r.append(f"- **IMC:** {imc:.1f} ({cat})")
    r.append(f"- **FC máxima registrada:** {perfil.get('fc_max_registrada', '?')} bpm")
    if membro.get("idade"):
        fc_max_teorica = 220 - membro['idade']
        r.append(f"- **FC máxima teórica (220 - idade):** {fc_max_teorica} bpm")
    r.append(f"- **Meta diária de passos:** {formatar_numero(perfil.get('meta_passos', '?'))}")
    r.append(f"- **Meta diária de calorias ativas:** {formatar_numero(perfil.get('meta_calorias', '?'))}")
    r.append(f"- **Meta diária de intensidade:** {perfil.get('meta_intensidade', '?')} min")
    r.append(f"- **Dispositivos:** {', '.join(dispositivos) if dispositivos else '?'}")
    r.append("")
    
    # ── Passos ──
    r.append("---")
    r.append("## 🚶 ATIVIDADE DIÁRIA (PASSOS)")
    r.append("")
    if steps:
        passos_vals = [s["passos"] for s in steps]
        dist_vals = [s["distancia_m"] for s in steps]
        media_passos = sum(passos_vals) / len(passos_vals)
        total_passos = sum(passos_vals)
        total_dist = sum(dist_vals)
        max_passos = max(passos_vals)
        min_passos = min(passos_vals)
        meta_passos = int(perfil.get("meta_passos", 10000))
        dias_meta = sum(1 for p in passos_vals if p >= meta_passos)
        
        r.append(f"- **Total de passos no período:** {formatar_numero(total_passos)}")
        r.append(f"- **Distância total:** {total_dist/1000:.1f} km")
        r.append(f"- **Média diária:** {formatar_numero(int(media_passos))} passos")
        r.append(f"- **Dia com mais passos:** {formatar_numero(max_passos)} ({ts_to_date([s['data'] for s in steps if s['passos']==max_passos][0])})")
        r.append(f"- **Dia com menos passos:** {formatar_numero(min_passos)} ({ts_to_date([s['data'] for s in steps if s['passos']==min_passos][0])})")
        r.append(f"- **Dias que atingiu a meta ({formatar_numero(meta_passos)}):** {dias_meta}/{total_dias} ({dias_meta/total_dias*100:.0f}%)")
        r.append("")
        
        r.append("### Detalhamento diário")
        r.append("")
        r.append("| Data | Dia | Passos | Distância | Calorias Ativas |")
        r.append("|------|-----|--------|-----------|-----------------|")
        for s in sorted(steps, key=lambda x: int(x["data"])):
            meta_ok = "✅" if s["passos"] >= meta_passos else "❌"
            r.append(f"| {ts_to_date(s['data'])} | {ts_to_weekday(s['data'])} | {formatar_numero(s['passos'])} {meta_ok} | {s['distancia_m']/1000:.1f} km | {s['calorias']} kcal |")
        r.append("")
    
    # ── Sono ──
    r.append("---")
    r.append("## 😴 QUALIDADE DO SONO")
    r.append("")
    if sleep:
        scores = [s["score"] for s in sleep if s["score"] > 0]
        duracoes = [s["duracao_total"] for s in sleep if s["duracao_total"] > 0]
        profundos = [s["sono_profundo"] for s in sleep if s["duracao_total"] > 0]
        
        media_score = sum(scores) / len(scores) if scores else 0
        media_dur = sum(duracoes) / len(duracoes) if duracoes else 0
        media_prof = sum(profundos) / len(profundos) if profundos else 0
        
        r.append(f"- **Score médio de sono:** {media_score:.0f}/100")
        r.append(f"- **Duração média total:** {min_para_hm(media_dur)}")
        if media_dur > 0:
            r.append(f"- **Sono profundo médio:** {min_para_hm(media_prof)} ({media_prof/media_dur*100:.0f}% do total)")
        if scores:
            r.append(f"- **Melhor noite (score):** {max(scores)} ({ts_to_date([s['data'] for s in sleep if s['score']==max(scores)][0])})")
            r.append(f"- **Pior noite (score):** {min(scores)} ({ts_to_date([s['data'] for s in sleep if s['score']==min(scores)][0])})")
        r.append(f"- **Noites registradas:** {len(duracoes)}")
        r.append("")
        
        fc_sono_media = [s["fc_media"] for s in sleep if s["fc_media"] > 0]
        fc_sono_min = [s["fc_min"] for s in sleep if s["fc_min"] > 0]
        if fc_sono_media:
            r.append(f"- **FC média durante o sono:** {sum(fc_sono_media)/len(fc_sono_media):.0f} bpm")
            if fc_sono_min:
                r.append(f"- **FC mínima durante o sono (menor registrada):** {min(fc_sono_min)} bpm")
            r.append("")
        
        r.append("### Detalhamento noturno")
        r.append("")
        r.append("| Data | Score | Duração Total | Profundo | Leve | REM | Acordado | FC Média |")
        r.append("|------|-------|---------------|----------|------|-----|----------|----------|")
        for s in sorted(sleep, key=lambda x: int(x["data"])):
            if s["duracao_total"] == 0:
                continue
            rem = min_para_hm(s['sono_rem']) if s['sono_rem'] else '-'
            acordado = min_para_hm(s['acordado']) if s['acordado'] else '-'
            r.append(f"| {ts_to_date(s['data'])} | {s['score']} | {min_para_hm(s['duracao_total'])} | {min_para_hm(s['sono_profundo'])} | {min_para_hm(s['sono_leve'])} | {rem} | {acordado} | {s['fc_media']} bpm |")
        r.append("")
    
    # ── FC ──
    r.append("---")
    r.append("## ❤️ FREQUÊNCIA CARDÍACA")
    r.append("")
    if hr:
        fc_medias = [h["fc_media"] for h in hr]
        fc_repousos = [h["fc_repouso"] for h in hr if h["fc_repouso"] > 0]
        fc_maximas = [h["fc_max"] for h in hr]
        fc_minimas = [h["fc_min"] for h in hr]
        
        r.append(f"- **FC média geral:** {sum(fc_medias)/len(fc_medias):.0f} bpm")
        if fc_repousos:
            r.append(f"- **FC de repouso média:** {sum(fc_repousos)/len(fc_repousos):.0f} bpm")
            r.append(f"- **FC de repouso mais baixa:** {min(fc_repousos)} bpm ({ts_to_date([h['data'] for h in hr if h['fc_repouso']==min(fc_repousos)][0])})")
            r.append(f"- **FC de repouso mais alta:** {max(fc_repousos)} bpm ({ts_to_date([h['data'] for h in hr if h['fc_repouso']==max(fc_repousos)][0])})")
        r.append(f"- **FC máxima absoluta registrada:** {max(fc_maximas)} bpm ({ts_to_date([h['data'] for h in hr if h['fc_max']==max(fc_maximas)][0])})")
        r.append(f"- **FC mínima absoluta registrada:** {min(fc_minimas)} bpm")
        r.append("")
        
        r.append("### FC de repouso ao longo do tempo")
        r.append("")
        r.append("| Data | FC Média | FC Repouso | FC Máx | FC Mín |")
        r.append("|------|----------|------------|--------|--------|")
        for h in sorted(hr, key=lambda x: int(x["data"])):
            r.append(f"| {ts_to_date(h['data'])} | {h['fc_media']} | {h['fc_repouso']} | {h['fc_max']} | {h['fc_min']} |")
        r.append("")
        
        total_aquec = sum(h["zona_aquecimento"] for h in hr)
        total_queima = sum(h["zona_queima"] for h in hr)
        total_aerob = sum(h["zona_aerobica"] for h in hr)
        total_anaerob = sum(h["zona_anaerobica"] for h in hr)
        total_extrema = sum(h["zona_extrema"] for h in hr)
        
        r.append("### Tempo total em zonas cardíacas (período completo)")
        r.append("")
        r.append(f"- **Aquecimento (50-60% FC máx):** {total_aquec} min")
        r.append(f"- **Queima de gordura (60-70% FC máx):** {total_queima} min")
        r.append(f"- **Aeróbica (70-80% FC máx):** {total_aerob} min")
        r.append(f"- **Anaeróbica (80-90% FC máx):** {total_anaerob} min")
        r.append(f"- **Extrema (90-100% FC máx):** {total_extrema} min")
        r.append("")
    
    # ── Calorias ──
    r.append("---")
    r.append("## 🔥 CALORIAS")
    r.append("")
    if cal:
        cal_vals = [c["calorias"] for c in cal]
        media_cal = sum(cal_vals) / len(cal_vals)
        meta_cal = int(perfil.get("meta_calorias", 1000))
        dias_meta_cal = sum(1 for c in cal_vals if c >= meta_cal)
        r.append(f"- **Gasto calórico total no período:** {formatar_numero(sum(cal_vals))} kcal")
        r.append(f"- **Média diária:** {formatar_numero(int(media_cal))} kcal")
        r.append(f"- **Dia mais ativo:** {formatar_numero(max(cal_vals))} kcal ({ts_to_date([c['data'] for c in cal if c['calorias']==max(cal_vals)][0])})")
        r.append(f"- **Dia menos ativo:** {formatar_numero(min(cal_vals))} kcal ({ts_to_date([c['data'] for c in cal if c['calorias']==min(cal_vals)][0])})")
        r.append(f"- **Dias atingindo meta ({formatar_numero(meta_cal)} kcal):** {dias_meta_cal}/{len(cal_vals)} ({dias_meta_cal/len(cal_vals)*100:.0f}%)")
        r.append("")
    
    # ── Intensidade ──
    r.append("---")
    r.append("## ⚡ MINUTOS DE ATIVIDADE INTENSA (PAI/Intensidade)")
    r.append("")
    if intensity:
        int_vals = [i["duracao_min"] for i in intensity]
        total_int = sum(int_vals)
        media_int = total_int / len(int_vals)
        meta_int = int(perfil.get("meta_intensidade", 30))
        dias_meta_int = sum(1 for i in int_vals if i >= meta_int)
        
        r.append(f"- **Total de minutos no período:** {total_int} min ({min_para_hm(total_int)})")
        r.append(f"- **Média diária:** {media_int:.0f} min")
        r.append(f"- **Dia mais intenso:** {max(int_vals)} min ({ts_to_date([i['data'] for i in intensity if i['duracao_min']==max(int_vals)][0])})")
        r.append(f"- **Dias atingindo meta ({meta_int} min):** {dias_meta_int}/{len(int_vals)} ({dias_meta_int/len(int_vals)*100:.0f}%)")
        r.append(f"- **OMS recomenda:** ≥150 min/semana de atividade moderada ou ≥75 min/semana vigorosa")
        r.append(f"- **Sua média semanal:** ~{media_int*7:.0f} min")
        r.append("")
    
    # ── Horas em pé ──
    r.append("---")
    r.append("## 🧍 HORAS EM PÉ (Valid Stand)")
    r.append("")
    if stand:
        stand_vals = [s["contagem"] for s in stand]
        media_stand = sum(stand_vals) / len(stand_vals)
        r.append(f"- **Média diária de horas ativas:** {media_stand:.0f}")
        r.append(f"- **Máximo em um dia:** {max(stand_vals)}")
        r.append(f"- **Mínimo em um dia:** {min(stand_vals)}")
        r.append("")
    
    # ── Estresse ──
    r.append("---")
    r.append("## 🧠 ESTRESSE")
    r.append("")
    if stress:
        r.append(f"- **Registros disponíveis:** {len(stress)} dias")
        for s in stress:
            r.append(f"- {ts_to_date(s['data'])}: Média {s['media']}, Máx {s['max']}, Mín {s['min']}")
        r.append("")
        r.append("> ⚠️ Poucos dados de estresse disponíveis. Considere manter o monitoramento contínuo ativado.")
        r.append("")
    else:
        r.append("Sem dados de estresse disponíveis.")
        r.append("")
    
    # ── SpO2 ──
    r.append("---")
    r.append("## 🫁 SATURAÇÃO DE OXIGÊNIO (SpO2)")
    r.append("")
    if spo2:
        r.append(f"- **Registros disponíveis:** {len(spo2)} dias")
        for s in spo2:
            r.append(f"- {ts_to_date(s['data'])}: Média {s['media']}%, Máx {s['max']}%, Mín {s['min']}%")
        r.append("")
        r.append("> ℹ️ Valores normais de SpO2 são ≥95%. Valores abaixo de 90% requerem atenção médica.")
        r.append("")
    else:
        r.append("Sem dados de SpO2 disponíveis.")
        r.append("")
    
    # ── Treinos ──
    r.append("---")
    r.append("## 💪 TREINOS E EXERCÍCIOS")
    r.append("")
    if treinos:
        total_treinos = len(treinos)
        treinos_musculacao = [t for t in treinos if "strength" in t["tipo"].lower()]
        treinos_caminhada = [t for t in treinos if "walking" in t["tipo"].lower()]
        
        duracao_total = sum(t["duracao_seg"] for t in treinos)
        calorias_total = sum(t["calorias_total"] for t in treinos)
        
        r.append(f"- **Total de treinos registrados:** {total_treinos}")
        r.append(f"- **Treinos de musculação:** {len(treinos_musculacao)}")
        r.append(f"- **Caminhadas ao ar livre:** {len(treinos_caminhada)}")
        r.append(f"- **Tempo total de treino:** {seg_para_hm(duracao_total)}")
        r.append(f"- **Calorias totais queimadas em treinos:** {formatar_numero(calorias_total)} kcal")
        r.append("")
        
        if treinos_musculacao:
            dur_musc = [t["duracao_seg"] for t in treinos_musculacao]
            cal_musc = [t["calorias_total"] for t in treinos_musculacao]
            fc_media_musc = [t["fc_media"] for t in treinos_musculacao if t["fc_media"] > 0]
            
            r.append("### Estatísticas de Musculação")
            r.append("")
            r.append(f"- **Duração média por sessão:** {seg_para_hm(sum(dur_musc)/len(dur_musc))}")
            r.append(f"- **Sessão mais longa:** {seg_para_hm(max(dur_musc))}")
            r.append(f"- **Sessão mais curta:** {seg_para_hm(min(dur_musc))}")
            r.append(f"- **Calorias médias por sessão:** {sum(cal_musc)/len(cal_musc):.0f} kcal")
            if fc_media_musc:
                r.append(f"- **FC média durante treinos:** {sum(fc_media_musc)/len(fc_media_musc):.0f} bpm")
            r.append("")
            
            freq = frequencia_semanal_treinos(treinos, "strength")
            if freq["semanas"]:
                r.append("### Frequência semanal de musculação")
                r.append("")
                r.append("| Semana | Treinos |")
                r.append("|--------|---------|")
                for sem, count in freq["semanas"].items():
                    r.append(f"| {sem} | {count} |")
                r.append(f"\n**Média:** {freq['media_semanal']:.1f} treinos/semana")
                r.append("")
        
        r.append("### Detalhamento de todos os treinos")
        r.append("")
        r.append("| Data | Tipo | Duração | Calorias | FC Média | FC Máx | Vitalidade |")
        r.append("|------|------|---------|----------|----------|--------|------------|")
        for t in treinos:
            dist_info = f" ({t['distancia']/1000:.1f}km)" if t["distancia"] > 0 else ""
            r.append(f"| {ts_to_datetime(t['data'])} | {t['tipo']}{dist_info} | {seg_para_hm(t['duracao_seg'])} | {t['calorias_total']} kcal | {t['fc_media']} bpm | {t['fc_max']} bpm | {t['vitalidade']} |")
        r.append("")
    
    # ── Tendências ──
    r.append("---")
    r.append("## 📈 ANÁLISE DE TENDÊNCIAS E PADRÕES")
    r.append("")
    
    tend_passos = analisar_tendencia_passos(steps)
    if tend_passos:
        r.append("### Passos")
        r.append(f"- Média 1ª metade do período: {formatar_numero(int(tend_passos['media_1']))}")
        r.append(f"- Média 2ª metade do período: {formatar_numero(int(tend_passos['media_2']))}")
        r.append(f"- Variação: {tend_passos['variacao_pct']:+.1f}%")
        r.append("")
    
    tend_fc = analisar_tendencia_fc(hr)
    if tend_fc:
        r.append("### Frequência Cardíaca de Repouso")
        r.append(f"- Média 1ª metade: {tend_fc['media_1']:.0f} bpm")
        r.append(f"- Média 2ª metade: {tend_fc['media_2']:.0f} bpm")
        r.append(f"- Variação: {tend_fc['variacao']:+.0f} bpm ({tend_fc['status']})")
        r.append("")
    
    tend_sono = analisar_tendencia_sono(sleep)
    if tend_sono:
        r.append("### Qualidade do Sono")
        r.append(f"- Score médio 1ª metade: {tend_sono['score_1']:.0f}")
        r.append(f"- Score médio 2ª metade: {tend_sono['score_2']:.0f}")
        r.append(f"- Variação: {tend_sono['variacao']:+.0f} pontos")
        r.append("")
    
    padroes = padroes_por_dia_semana(steps)
    if padroes:
        r.append("### Padrões por dia da semana")
        r.append("")
        r.append("| Dia | Média de Passos | Nº Registros |")
        r.append("|-----|-----------------|--------------|")
        for p in padroes:
            r.append(f"| {p['dia']} | {formatar_numero(int(p['media']))} | {p['registros']} |")
        r.append("")
    
    return "\n".join(r)
