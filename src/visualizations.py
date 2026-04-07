# -*- coding: utf-8 -*-
"""
Gráficos interativos com Plotly para o dashboard Streamlit.
"""

import plotly.graph_objects as go
import plotly.express as px
from src.helpers import ts_to_date, ts_to_weekday, min_para_hm, seg_para_hm

# ── Paleta de cores ──────────────────────────────────────────────────────────
CORES = {
    "primaria": "#FF6B35",
    "secundaria": "#4ECDC4",
    "terciaria": "#45B7D1",
    "quaternaria": "#96CEB4",
    "destaque": "#FFEAA7",
    "perigo": "#FF6B6B",
    "sucesso": "#6BCB77",
    "fundo": "#0E1117",
    "fundo_card": "#1A1F2E",
    "texto": "#FAFAFA",
    "texto_dim": "#888888",
    "gradiente_1": "#FF6B35",
    "gradiente_2": "#FF8E53",
    "gradiente_3": "#FFA96B",
}

LAYOUT_PADRAO = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=CORES["texto"], family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)", showgrid=True),
    hoverlabel=dict(bgcolor=CORES["fundo_card"], font_size=13),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _aplicar_layout(fig, titulo="", height=400):
    """Aplica layout padrão a um gráfico."""
    fig.update_layout(
        **LAYOUT_PADRAO,
        title=dict(text=titulo, font=dict(size=16)),
        height=height,
    )
    return fig


def grafico_passos_diarios(steps, meta_passos=10000):
    """Gráfico de barras com passos diários e linha de meta."""
    if not steps:
        return None
    
    sorted_steps = sorted(steps, key=lambda x: int(x["data"]))
    datas = [ts_to_date(s["data"]) for s in sorted_steps]
    passos = [s["passos"] for s in sorted_steps]
    cores = [CORES["sucesso"] if p >= meta_passos else CORES["primaria"] for p in passos]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=datas, y=passos,
        marker_color=cores,
        name="Passos",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} passos<extra></extra>",
    ))
    
    fig.add_hline(
        y=meta_passos,
        line_dash="dash",
        line_color=CORES["destaque"],
        annotation_text=f"Meta: {meta_passos:,}".replace(",", "."),
        annotation_position="top right",
        annotation_font_color=CORES["destaque"],
    )
    
    _aplicar_layout(fig, "🚶 Passos Diários", height=380)
    fig.update_layout(showlegend=False)
    return fig


def grafico_distancia_diaria(steps):
    """Gráfico de área com distância diária."""
    if not steps:
        return None
    
    sorted_steps = sorted(steps, key=lambda x: int(x["data"]))
    datas = [ts_to_date(s["data"]) for s in sorted_steps]
    distancias = [s["distancia_m"] / 1000 for s in sorted_steps]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datas, y=distancias,
        fill="tozeroy",
        fillcolor="rgba(78, 205, 196, 0.15)",
        line=dict(color=CORES["secundaria"], width=2),
        name="Distância",
        hovertemplate="<b>%{x}</b><br>%{y:.1f} km<extra></extra>",
    ))
    
    _aplicar_layout(fig, "📏 Distância Diária (km)", height=320)
    fig.update_layout(showlegend=False)
    return fig


def grafico_sono_scores(sleep):
    """Gráfico de linha com scores de sono."""
    if not sleep:
        return None
    
    sorted_sleep = sorted([s for s in sleep if s["score"] > 0], key=lambda x: int(x["data"]))
    datas = [ts_to_date(s["data"]) for s in sorted_sleep]
    scores = [s["score"] for s in sorted_sleep]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datas, y=scores,
        mode="lines+markers",
        line=dict(color=CORES["terciaria"], width=2),
        marker=dict(size=5, color=CORES["terciaria"]),
        name="Score",
        hovertemplate="<b>%{x}</b><br>Score: %{y}<extra></extra>",
    ))
    
    _aplicar_layout(fig, "😴 Score de Sono", height=350)
    fig.update_layout(showlegend=False, yaxis=dict(range=[40, 100], gridcolor="rgba(255,255,255,0.08)"))
    return fig


def grafico_sono_fases(sleep):
    """Gráfico de barras empilhadas com fases do sono."""
    if not sleep:
        return None
    
    sorted_sleep = sorted([s for s in sleep if s["duracao_total"] > 0], key=lambda x: int(x["data"]))
    datas = [ts_to_date(s["data"]) for s in sorted_sleep]
    profundo = [s["sono_profundo"] / 60 for s in sorted_sleep]
    leve = [s["sono_leve"] / 60 for s in sorted_sleep]
    rem = [s["sono_rem"] / 60 for s in sorted_sleep]
    acordado = [s["acordado"] / 60 for s in sorted_sleep]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=datas, y=profundo, name="Profundo", marker_color="#1B4F72",
                         hovertemplate="%{x}<br>Profundo: %{y:.1f}h<extra></extra>"))
    fig.add_trace(go.Bar(x=datas, y=leve, name="Leve", marker_color="#5DADE2",
                         hovertemplate="%{x}<br>Leve: %{y:.1f}h<extra></extra>"))
    fig.add_trace(go.Bar(x=datas, y=rem, name="REM", marker_color="#A569BD",
                         hovertemplate="%{x}<br>REM: %{y:.1f}h<extra></extra>"))
    fig.add_trace(go.Bar(x=datas, y=acordado, name="Acordado", marker_color="#E74C3C",
                         hovertemplate="%{x}<br>Acordado: %{y:.1f}h<extra></extra>"))
    
    _aplicar_layout(fig, "🛌 Fases do Sono (horas)", height=380)
    fig.update_layout(barmode="stack")
    return fig


def grafico_fc_repouso(hr):
    """Gráfico de linha com FC de repouso ao longo do tempo."""
    if not hr:
        return None
    
    sorted_hr = sorted([h for h in hr if h["fc_repouso"] > 0], key=lambda x: int(x["data"]))
    datas = [ts_to_date(h["data"]) for h in sorted_hr]
    fc_rep = [h["fc_repouso"] for h in sorted_hr]
    fc_max = [h["fc_max"] for h in sorted_hr]
    fc_min = [h["fc_min"] for h in sorted_hr]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=datas, y=fc_max, mode="lines",
        line=dict(width=0), showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=datas, y=fc_min, mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(255, 107, 53, 0.08)",
        showlegend=False, hoverinfo="skip",
    ))
    
    fig.add_trace(go.Scatter(
        x=datas, y=fc_rep,
        mode="lines+markers",
        line=dict(color=CORES["perigo"], width=2.5),
        marker=dict(size=4, color=CORES["perigo"]),
        name="FC Repouso",
        hovertemplate="<b>%{x}</b><br>FC Repouso: %{y} bpm<extra></extra>",
    ))
    
    _aplicar_layout(fig, "❤️ FC de Repouso ao Longo do Tempo", height=380)
    return fig


def grafico_zonas_cardiacas(hr):
    """Gráfico de pizza/donut com tempo em cada zona cardíaca."""
    if not hr:
        return None
    
    total_aquec = sum(h["zona_aquecimento"] for h in hr)
    total_queima = sum(h["zona_queima"] for h in hr)
    total_aerob = sum(h["zona_aerobica"] for h in hr)
    total_anaerob = sum(h["zona_anaerobica"] for h in hr)
    total_extrema = sum(h["zona_extrema"] for h in hr)
    
    zonas = ["Aquecimento", "Queima de Gordura", "Aeróbica", "Anaeróbica", "Extrema"]
    valores = [total_aquec, total_queima, total_aerob, total_anaerob, total_extrema]
    cores_zonas = ["#3498DB", "#2ECC71", "#F39C12", "#E74C3C", "#8E44AD"]
    
    fig = go.Figure(go.Pie(
        labels=zonas, values=valores,
        hole=0.5,
        marker=dict(colors=cores_zonas),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value} min<br>%{percent}<extra></extra>",
    ))
    
    _aplicar_layout(fig, "🫀 Tempo em Zonas Cardíacas", height=400)
    return fig


def grafico_calorias(cal, meta_cal=1000):
    """Gráfico de barras com calorias diárias."""
    if not cal:
        return None
    
    sorted_cal = sorted(cal, key=lambda x: int(x["data"]))
    datas = [ts_to_date(c["data"]) for c in sorted_cal]
    calorias = [c["calorias"] for c in sorted_cal]
    cores = [CORES["sucesso"] if c >= meta_cal else CORES["primaria"] for c in calorias]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=datas, y=calorias,
        marker_color=cores,
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} kcal<extra></extra>",
    ))
    
    fig.add_hline(
        y=meta_cal,
        line_dash="dash",
        line_color=CORES["destaque"],
        annotation_text=f"Meta: {meta_cal:,}".replace(",", "."),
        annotation_position="top right",
        annotation_font_color=CORES["destaque"],
    )
    
    _aplicar_layout(fig, "🔥 Calorias Diárias", height=380)
    fig.update_layout(showlegend=False)
    return fig


def grafico_treinos_timeline(treinos):
    """Gráfico de timeline dos treinos com duração e calorias."""
    if not treinos:
        return None
    
    datas = [ts_to_date(t["data"]) for t in treinos]
    duracoes = [t["duracao_seg"] / 60 for t in treinos]
    calorias = [t["calorias_total"] for t in treinos]
    tipos = [t["tipo"] for t in treinos]
    cores = [CORES["primaria"] if "strength" in t["tipo"].lower() else CORES["secundaria"] for t in treinos]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=datas, y=duracoes,
        marker_color=cores,
        text=[f"{t}" for t in tipos],
        hovertemplate="<b>%{x}</b><br>%{text}<br>Duração: %{y:.0f} min<extra></extra>",
    ))
    
    _aplicar_layout(fig, "💪 Duração dos Treinos (min)", height=380)
    fig.update_layout(showlegend=False)
    return fig


def grafico_fc_treinos(treinos):
    """Gráfico de scatter com FC média e máxima nos treinos."""
    if not treinos:
        return None
    
    treinos_com_fc = [t for t in treinos if t["fc_media"] > 0]
    if not treinos_com_fc:
        return None
    
    datas = [ts_to_date(t["data"]) for t in treinos_com_fc]
    fc_media = [t["fc_media"] for t in treinos_com_fc]
    fc_max = [t["fc_max"] for t in treinos_com_fc]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datas, y=fc_media,
        mode="lines+markers",
        line=dict(color=CORES["primaria"], width=2),
        marker=dict(size=6),
        name="FC Média",
        hovertemplate="<b>%{x}</b><br>FC Média: %{y} bpm<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=datas, y=fc_max,
        mode="lines+markers",
        line=dict(color=CORES["perigo"], width=1.5, dash="dot"),
        marker=dict(size=4),
        name="FC Máxima",
        hovertemplate="<b>%{x}</b><br>FC Máx: %{y} bpm<extra></extra>",
    ))
    
    _aplicar_layout(fig, "💓 FC nos Treinos", height=350)
    return fig


def grafico_padrao_semanal(padroes):
    """Gráfico de barras com média de passos por dia da semana."""
    if not padroes:
        return None
    
    dias = [p["dia"] for p in padroes]
    medias = [p["media"] for p in padroes]
    
    cores_dias = []
    for m in medias:
        if m >= max(medias) * 0.8:
            cores_dias.append(CORES["sucesso"])
        elif m >= max(medias) * 0.5:
            cores_dias.append(CORES["primaria"])
        else:
            cores_dias.append(CORES["perigo"])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dias, y=medias,
        marker_color=cores_dias,
        hovertemplate="<b>%{x}</b><br>Média: %{y:,.0f} passos<extra></extra>",
    ))
    
    _aplicar_layout(fig, "📅 Padrão Semanal de Passos", height=350)
    fig.update_layout(showlegend=False)
    return fig
