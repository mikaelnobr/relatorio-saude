# -*- coding: utf-8 -*-
"""
MiFitness Health Report - Aplicação Streamlit
Gera relatórios de saúde a partir dos dados exportados do Xiaomi MiFitness.
"""

import streamlit as st
import tempfile
import shutil
from datetime import datetime

from src.zip_handler import extrair_zip
from src.csv_loader import carregar_todos_csvs
from src.helpers import FUSO, ts_to_date, ts_to_datetime, ts_to_weekday, ts_to_python_date, formatar_numero, min_para_hm, seg_para_hm
from src.processors.profile import processar_perfil, processar_membro
from src.processors.devices import processar_dispositivos
from src.processors.aggregated import processar_agregados
from src.processors.workouts import processar_treinos
from src.processors.trends import (
    analisar_tendencia_passos, analisar_tendencia_fc,
    analisar_tendencia_sono, padroes_por_dia_semana,
    frequencia_semanal_treinos
)
from src.report_builder import gerar_relatorio_markdown
from src.visualizations import (
    grafico_passos_diarios, grafico_distancia_diaria,
    grafico_sono_scores, grafico_sono_fases,
    grafico_fc_repouso, grafico_zonas_cardiacas,
    grafico_calorias, grafico_treinos_timeline,
    grafico_fc_treinos, grafico_padrao_semanal,
)


# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="MiFitness Health Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 50%, #FFA96B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 0.5rem 0;
    }
    
    .sub-header {
        color: #888;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #242B3D 100%);
        border: 1px solid rgba(255, 107, 53, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 107, 53, 0.4);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FF6B35;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.3rem;
    }
    .metric-detail {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.2rem;
    }
    
    .success-badge {
        background: rgba(107, 203, 119, 0.15);
        color: #6BCB77;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    .warning-badge {
        background: rgba(255, 107, 53, 0.15);
        color: #FF6B35;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #151A25 100%);
    }
    
    .upload-zone {
        border: 2px dashed rgba(255, 107, 53, 0.3);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1A1F2E 0%, #242B3D 100%);
        border: 1px solid rgba(255, 107, 53, 0.1);
        border-radius: 10px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)


def render_metric_card(valor, label, detalhe=""):
    """Renderiza um card de métrica estilizado."""
    detalhe_html = f'<div class="metric-detail">{detalhe}</div>' if detalhe else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{valor}</div>
            <div class="metric-label">{label}</div>
            {detalhe_html}
        </div>
    """, unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📱 Upload dos Dados")
    st.markdown(
        '<p style="color: #888; font-size: 0.85rem;">'
        'Envie o arquivo ZIP exportado do MiFitness com a senha recebida por e-mail.'
        '</p>',
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "Arquivo ZIP do MiFitness",
        type=["zip"],
        help="Exporte seus dados em account.xiaomi.com → Privacidade",
        key="zip_upload",
    )
    
    senha = st.text_input(
        "🔑 Senha do ZIP",
        type="password",
        help="A senha é enviada por e-mail junto com o link de download",
        key="zip_senha",
    )
    
    st.markdown("---")
    
    # Seleção de período (aparece após carregar dados)
    if "dados_carregados" in st.session_state and st.session_state.dados_carregados:
        st.markdown("### 📅 Período do Relatório")
        
        periodo_opcao = st.radio(
            "Selecione o período:",
            ["Período completo", "Personalizado"],
            key="periodo_opcao",
        )
        
        if periodo_opcao == "Personalizado":
            min_date = st.session_state.get("data_min")
            max_date = st.session_state.get("data_max")
            
            if min_date and max_date:
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio = st.date_input(
                        "De:", value=min_date,
                        min_value=min_date, max_value=max_date,
                        key="data_inicio",
                    )
                with col2:
                    data_fim = st.date_input(
                        "Até:", value=max_date,
                        min_value=min_date, max_value=max_date,
                        key="data_fim",
                    )
                
                st.session_state.filtro_inicio = data_inicio
                st.session_state.filtro_fim = data_fim
            else:
                st.session_state.filtro_inicio = None
                st.session_state.filtro_fim = None
        else:
            st.session_state.filtro_inicio = None
            st.session_state.filtro_fim = None
        
        if st.button("🔄 Reprocessar Dados", use_container_width=True, type="primary"):
            st.session_state.reprocessar = True
            st.rerun()
    
    st.markdown("---")
    st.markdown(
        '<p style="color: #555; font-size: 0.75rem; text-align: center;">'
        'MiFitness Health Report<br>'
        'Seus dados são processados localmente.<br>'
        'Nenhum dado é armazenado no servidor.'
        '</p>',
        unsafe_allow_html=True
    )


# ── Página Principal ─────────────────────────────────────────────────────────

st.markdown('<h1 class="main-header">📊 MiFitness Health Report</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">'
    'Analise seus dados de saúde exportados do Xiaomi MiFitness'
    '</p>',
    unsafe_allow_html=True
)


# ── Processamento ────────────────────────────────────────────────────────────

def processar_dados():
    """Processa os dados do ZIP e salva no session_state."""
    if not uploaded_file or not senha:
        return False
    
    try:
        with st.spinner("🔓 Extraindo ZIP..."):
            temp_dir, arquivos = extrair_zip(uploaded_file, senha)
        
        with st.spinner("📄 Carregando CSVs..."):
            csvs = carregar_todos_csvs(temp_dir, arquivos)
        
        # Salvar CSVs no session state
        st.session_state.csvs = csvs
        st.session_state.temp_dir = temp_dir
        st.session_state.dados_carregados = True
        
        # Detectar período dos dados
        metricas_temp = processar_agregados(csvs.get("agregados", []))
        steps_temp = metricas_temp.get("steps", [])
        if steps_temp:
            all_dates = [ts_to_python_date(s["data"]) for s in steps_temp]
            st.session_state.data_min = min(all_dates)
            st.session_state.data_max = max(all_dates)
        
        return True
        
    except ValueError as e:
        st.error(str(e))
        return False
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
        return False


def obter_dados_processados():
    """Retorna os dados processados (com filtros aplicados)."""
    csvs = st.session_state.get("csvs", {})
    if not csvs:
        return None
    
    data_inicio = st.session_state.get("filtro_inicio")
    data_fim = st.session_state.get("filtro_fim")
    
    perfil = processar_perfil(csvs.get("perfil", []))
    membro = processar_membro(csvs.get("membro", []))
    dispositivos = processar_dispositivos(csvs.get("dispositivos", []))
    metricas = processar_agregados(csvs.get("agregados", []), data_inicio, data_fim)
    treinos = processar_treinos(csvs.get("treinos", []), data_inicio, data_fim)
    
    return {
        "perfil": perfil,
        "membro": membro,
        "dispositivos": dispositivos,
        "metricas": metricas,
        "treinos": treinos,
    }


# ── Lógica de carregamento ───────────────────────────────────────────────────

if uploaded_file and senha:
    # Processar na primeira vez ou quando reprocessar
    if not st.session_state.get("dados_carregados") or st.session_state.get("reprocessar"):
        if not st.session_state.get("dados_carregados"):
            processar_dados()
        st.session_state.reprocessar = False

if not st.session_state.get("dados_carregados"):
    # Tela de boas-vindas
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1A1F2E 0%, #242B3D 100%); border-radius: 16px; border: 1px solid rgba(255,107,53,0.15);">
            <h3 style="color: #FF6B35; margin-bottom: 1rem;">🚀 Como usar</h3>
            <div style="text-align: left; color: #ccc; line-height: 2;">
                <p><strong>1️⃣</strong> Exporte seus dados em <a href="https://account.xiaomi.com" target="_blank" style="color: #FF6B35;">account.xiaomi.com</a> → Privacidade</p>
                <p><strong>2️⃣</strong> Baixe o ZIP recebido por e-mail</p>
                <p><strong>3️⃣</strong> Copie a senha do e-mail</p>
                <p><strong>4️⃣</strong> Envie o ZIP e a senha na barra lateral ←</p>
                <p><strong>5️⃣</strong> Visualize e baixe o relatório!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Features
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("🚶", "PASSOS", "Atividade diária")
    with col2:
        render_metric_card("😴", "SONO", "Qualidade noturna")
    with col3:
        render_metric_card("❤️", "FC", "Freq. cardíaca")
    with col4:
        render_metric_card("💪", "TREINOS", "Exercícios")
    
    st.stop()


# ── Dashboard com dados ──────────────────────────────────────────────────────

dados = obter_dados_processados()
if not dados:
    st.error("Erro ao processar dados.")
    st.stop()

perfil = dados["perfil"]
membro = dados["membro"]
dispositivos = dados["dispositivos"]
metricas = dados["metricas"]
treinos_data = dados["treinos"]

steps = metricas.get("steps", [])
sleep = metricas.get("sleep", [])
hr = metricas.get("heart_rate", [])
cal = metricas.get("calories", [])
intensity = metricas.get("intensity", [])
stand = metricas.get("stand", [])
stress = metricas.get("stress", [])
spo2 = metricas.get("spo2", [])

# Período
all_dates = [int(s["data"]) for s in steps] if steps else []
data_inicio_str = ts_to_date(min(all_dates)) if all_dates else "?"
data_fim_str = ts_to_date(max(all_dates)) if all_dates else "?"
total_dias = len(all_dates)

st.markdown(f"""
<div style="text-align: center; padding: 0.5rem; margin-bottom: 1rem; background: rgba(255,107,53,0.05); border-radius: 8px;">
    <span style="color: #888;">📅 Período:</span>
    <strong style="color: #FF6B35;">{data_inicio_str} → {data_fim_str}</strong>
    <span style="color: #888;">({total_dias} dias)</span>
</div>
""", unsafe_allow_html=True)


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_resumo, tab_passos, tab_sono, tab_fc, tab_calorias, tab_treinos, tab_tendencias, tab_relatorio = st.tabs([
    "📊 Resumo", "🚶 Passos", "😴 Sono", "❤️ FC", "🔥 Calorias", "💪 Treinos", "📈 Tendências", "📄 Relatório"
])


# ── TAB: Resumo ──────────────────────────────────────────────────────────────
with tab_resumo:
    # Perfil
    st.markdown("### 👤 Perfil do Usuário")
    cols = st.columns(5)
    with cols[0]:
        if membro.get("sexo"):
            render_metric_card(membro["sexo"], "SEXO")
    with cols[1]:
        if membro.get("idade"):
            render_metric_card(f"{membro['idade']} anos", "IDADE")
    with cols[2]:
        if membro.get("altura_cm") and membro["altura_cm"] > 0:
            render_metric_card(f"{membro['altura_cm']:.0f} cm", "ALTURA")
    with cols[3]:
        if membro.get("peso_atual_kg") and membro["peso_atual_kg"] > 0:
            render_metric_card(f"{membro['peso_atual_kg']:.1f} kg", "PESO")
    with cols[4]:
        if membro.get("imc"):
            imc = membro['imc']
            cat = "Abaixo" if imc < 18.5 else "Normal" if imc < 25 else "Sobrepeso" if imc < 30 else "Obesidade"
            render_metric_card(f"{imc:.1f}", "IMC", cat)
    
    st.markdown("")
    
    # KPIs principais
    st.markdown("### 📊 Resumo do Período")
    cols = st.columns(4)
    
    with cols[0]:
        if steps:
            media_passos = sum(s["passos"] for s in steps) / len(steps)
            render_metric_card(
                formatar_numero(int(media_passos)),
                "PASSOS / DIA",
                f"Total: {formatar_numero(sum(s['passos'] for s in steps))}"
            )
    with cols[1]:
        if sleep:
            scores = [s["score"] for s in sleep if s["score"] > 0]
            if scores:
                render_metric_card(
                    f"{sum(scores)/len(scores):.0f}/100",
                    "SCORE SONO",
                    f"{len(scores)} noites"
                )
    with cols[2]:
        if hr:
            fc_rep = [h["fc_repouso"] for h in hr if h["fc_repouso"] > 0]
            if fc_rep:
                render_metric_card(
                    f"{sum(fc_rep)/len(fc_rep):.0f} bpm",
                    "FC REPOUSO",
                    f"Mín: {min(fc_rep)} bpm"
                )
    with cols[3]:
        if treinos_data:
            render_metric_card(
                str(len(treinos_data)),
                "TREINOS",
                f"{seg_para_hm(sum(t['duracao_seg'] for t in treinos_data))} total"
            )
    
    st.markdown("")
    
    cols2 = st.columns(4)
    with cols2[0]:
        if cal:
            media_cal = sum(c["calorias"] for c in cal) / len(cal)
            render_metric_card(
                f"{int(media_cal)}",
                "CALORIAS / DIA",
                f"Total: {formatar_numero(sum(c['calorias'] for c in cal))} kcal"
            )
    with cols2[1]:
        if intensity:
            media_int = sum(i["duracao_min"] for i in intensity) / len(intensity)
            render_metric_card(
                f"{media_int:.0f} min",
                "ATIVIDADE / DIA",
                f"~{media_int*7:.0f} min/semana"
            )
    with cols2[2]:
        if steps:
            meta = int(perfil.get("meta_passos", 10000))
            dias_meta = sum(1 for s in steps if s["passos"] >= meta)
            pct = dias_meta / len(steps) * 100
            render_metric_card(
                f"{pct:.0f}%",
                "META PASSOS",
                f"{dias_meta}/{len(steps)} dias"
            )
    with cols2[3]:
        if dispositivos:
            render_metric_card(
                str(len(dispositivos)),
                "DISPOSITIVOS",
                dispositivos[0].split("(")[0].strip() if dispositivos else ""
            )
    
    st.markdown("")
    if dispositivos:
        with st.expander("📱 Dispositivos conectados"):
            for d in dispositivos:
                st.markdown(f"- {d}")


# ── TAB: Passos ──────────────────────────────────────────────────────────────
with tab_passos:
    if steps:
        passos_vals = [s["passos"] for s in steps]
        meta_p = int(perfil.get("meta_passos", 10000))
        
        cols = st.columns(4)
        with cols[0]:
            render_metric_card(formatar_numero(sum(passos_vals)), "TOTAL PASSOS")
        with cols[1]:
            render_metric_card(f"{sum(s['distancia_m'] for s in steps)/1000:.1f} km", "DISTÂNCIA TOTAL")
        with cols[2]:
            render_metric_card(formatar_numero(int(sum(passos_vals)/len(passos_vals))), "MÉDIA DIÁRIA")
        with cols[3]:
            dias_meta = sum(1 for p in passos_vals if p >= meta_p)
            render_metric_card(f"{dias_meta}/{total_dias}", "DIAS NA META", f"{dias_meta/total_dias*100:.0f}%")
        
        st.markdown("")
        
        fig = grafico_passos_diarios(steps, meta_p)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        fig2 = grafico_distancia_diaria(steps)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("📋 Tabela detalhada"):
            import pandas as pd
            df = pd.DataFrame([{
                "Data": ts_to_date(s["data"]),
                "Dia": ts_to_weekday(s["data"]),
                "Passos": s["passos"],
                "Distância (km)": round(s["distancia_m"] / 1000, 1),
                "Calorias": s["calorias"],
                "Meta": "✅" if s["passos"] >= meta_p else "❌",
            } for s in sorted(steps, key=lambda x: int(x["data"]))])
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de passos disponíveis.")


# ── TAB: Sono ────────────────────────────────────────────────────────────────
with tab_sono:
    if sleep:
        scores = [s["score"] for s in sleep if s["score"] > 0]
        duracoes = [s["duracao_total"] for s in sleep if s["duracao_total"] > 0]
        
        if scores:
            cols = st.columns(4)
            with cols[0]:
                render_metric_card(f"{sum(scores)/len(scores):.0f}", "SCORE MÉDIO", "/100")
            with cols[1]:
                media_dur = sum(duracoes) / len(duracoes) if duracoes else 0
                render_metric_card(min_para_hm(media_dur), "DURAÇÃO MÉDIA")
            with cols[2]:
                render_metric_card(str(max(scores)), "MELHOR NOITE")
            with cols[3]:
                render_metric_card(str(len(duracoes)), "NOITES")
        
        st.markdown("")
        
        fig = grafico_sono_scores(sleep)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        fig2 = grafico_sono_fases(sleep)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("📋 Tabela detalhada do sono"):
            import pandas as pd
            df = pd.DataFrame([{
                "Data": ts_to_date(s["data"]),
                "Score": s["score"],
                "Duração": min_para_hm(s["duracao_total"]),
                "Profundo": min_para_hm(s["sono_profundo"]),
                "Leve": min_para_hm(s["sono_leve"]),
                "REM": min_para_hm(s["sono_rem"]) if s["sono_rem"] else "-",
                "FC Média": f"{s['fc_media']} bpm" if s["fc_media"] > 0 else "-",
            } for s in sorted(sleep, key=lambda x: int(x["data"])) if s["duracao_total"] > 0])
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de sono disponíveis.")


# ── TAB: Frequência Cardíaca ─────────────────────────────────────────────────
with tab_fc:
    if hr:
        fc_medias = [h["fc_media"] for h in hr]
        fc_repousos = [h["fc_repouso"] for h in hr if h["fc_repouso"] > 0]
        fc_maximas = [h["fc_max"] for h in hr]
        
        cols = st.columns(4)
        with cols[0]:
            render_metric_card(f"{sum(fc_medias)/len(fc_medias):.0f}", "FC MÉDIA", "bpm")
        with cols[1]:
            if fc_repousos:
                render_metric_card(f"{sum(fc_repousos)/len(fc_repousos):.0f}", "FC REPOUSO", "bpm")
        with cols[2]:
            render_metric_card(str(max(fc_maximas)), "FC MÁXIMA", "bpm")
        with cols[3]:
            if membro.get("idade"):
                render_metric_card(str(220 - membro["idade"]), "FC MÁX TEÓRICA", "220 - idade")
        
        st.markdown("")
        
        fig = grafico_fc_repouso(hr)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        fig2 = grafico_zonas_cardiacas(hr)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # SpO2 e Estresse
        col1, col2 = st.columns(2)
        with col1:
            if spo2:
                st.markdown("#### 🫁 Saturação de Oxigênio (SpO2)")
                for s in spo2:
                    st.markdown(f"- **{ts_to_date(s['data'])}:** Média {s['media']}%, Mín {s['min']}%")
                st.info("Valores normais ≥95%. Abaixo de 90% requer atenção médica.")
        with col2:
            if stress:
                st.markdown("#### 🧠 Estresse")
                for s in stress:
                    st.markdown(f"- **{ts_to_date(s['data'])}:** Média {s['media']}, Máx {s['max']}")
                st.warning("Poucos dados disponíveis. Mantenha o monitoramento ativado.")
    else:
        st.info("Sem dados de frequência cardíaca disponíveis.")


# ── TAB: Calorias ────────────────────────────────────────────────────────────
with tab_calorias:
    if cal:
        cal_vals = [c["calorias"] for c in cal]
        meta_cal = int(perfil.get("meta_calorias", 1000))
        
        cols = st.columns(4)
        with cols[0]:
            render_metric_card(formatar_numero(sum(cal_vals)), "TOTAL", "kcal")
        with cols[1]:
            render_metric_card(formatar_numero(int(sum(cal_vals)/len(cal_vals))), "MÉDIA / DIA", "kcal")
        with cols[2]:
            render_metric_card(formatar_numero(max(cal_vals)), "DIA MAIS ATIVO", "kcal")
        with cols[3]:
            dias_meta_c = sum(1 for c in cal_vals if c >= meta_cal)
            render_metric_card(f"{dias_meta_c}/{len(cal_vals)}", "DIAS NA META", f"{dias_meta_c/len(cal_vals)*100:.0f}%")
        
        st.markdown("")
        
        fig = grafico_calorias(cal, meta_cal)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Intensidade
        if intensity:
            st.markdown("### ⚡ Minutos de Atividade Intensa")
            int_vals = [i["duracao_min"] for i in intensity]
            total_int = sum(int_vals)
            media_int = total_int / len(int_vals)
            
            cols = st.columns(3)
            with cols[0]:
                render_metric_card(f"{total_int}", "TOTAL MINUTOS", min_para_hm(total_int))
            with cols[1]:
                render_metric_card(f"{media_int:.0f}", "MÉDIA / DIA", "min")
            with cols[2]:
                render_metric_card(f"~{media_int*7:.0f}", "MÉDIA / SEMANA", "min (OMS: ≥150)")
    else:
        st.info("Sem dados de calorias disponíveis.")


# ── TAB: Treinos ─────────────────────────────────────────────────────────────
with tab_treinos:
    if treinos_data:
        treinos_musculacao = [t for t in treinos_data if "strength" in t["tipo"].lower()]
        treinos_caminhada = [t for t in treinos_data if "walking" in t["tipo"].lower()]
        duracao_total = sum(t["duracao_seg"] for t in treinos_data)
        cal_total = sum(t["calorias_total"] for t in treinos_data)
        
        cols = st.columns(4)
        with cols[0]:
            render_metric_card(str(len(treinos_data)), "TOTAL TREINOS")
        with cols[1]:
            render_metric_card(str(len(treinos_musculacao)), "MUSCULAÇÃO")
        with cols[2]:
            render_metric_card(seg_para_hm(duracao_total), "TEMPO TOTAL")
        with cols[3]:
            render_metric_card(formatar_numero(cal_total), "CALORIAS", "kcal")
        
        st.markdown("")
        
        fig = grafico_treinos_timeline(treinos_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        fig2 = grafico_fc_treinos(treinos_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # Frequência semanal
        if treinos_musculacao:
            st.markdown("### 📅 Frequência Semanal de Musculação")
            freq = frequencia_semanal_treinos(treinos_data, "strength")
            if freq["semanas"]:
                import pandas as pd
                df_freq = pd.DataFrame([
                    {"Semana": sem, "Treinos": count}
                    for sem, count in freq["semanas"].items()
                ])
                st.dataframe(df_freq, use_container_width=True, hide_index=True)
                st.markdown(f"**Média:** {freq['media_semanal']:.1f} treinos/semana")
        
        with st.expander("📋 Detalhamento de todos os treinos"):
            import pandas as pd
            df = pd.DataFrame([{
                "Data": ts_to_date(t["data"]),
                "Tipo": t["tipo"],
                "Duração": seg_para_hm(t["duracao_seg"]),
                "Calorias": f"{t['calorias_total']} kcal",
                "FC Média": f"{t['fc_media']} bpm",
                "FC Máx": f"{t['fc_max']} bpm",
                "Distância": f"{t['distancia']/1000:.1f} km" if t["distancia"] > 0 else "-",
                "Vitalidade": t["vitalidade"],
            } for t in treinos_data])
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de treinos disponíveis.")


# ── TAB: Tendências ──────────────────────────────────────────────────────────
with tab_tendencias:
    st.markdown("### 📈 Análise de Tendências")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tend_passos = analisar_tendencia_passos(steps)
        if tend_passos:
            st.markdown("#### 🚶 Passos")
            variacao = tend_passos["variacao_pct"]
            emoji = "📈" if variacao > 0 else "📉"
            cor = "green" if variacao > 0 else "red"
            st.metric(
                "Média 1ª metade → 2ª metade",
                f"{formatar_numero(int(tend_passos['media_2']))} passos",
                f"{variacao:+.1f}%",
            )
        
        tend_sono = analisar_tendencia_sono(sleep)
        if tend_sono:
            st.markdown("#### 😴 Sono")
            st.metric(
                "Score 1ª metade → 2ª metade",
                f"{tend_sono['score_2']:.0f}/100",
                f"{tend_sono['variacao']:+.0f} pontos",
            )
    
    with col2:
        tend_fc = analisar_tendencia_fc(hr)
        if tend_fc:
            st.markdown("#### ❤️ FC Repouso")
            st.metric(
                "Média 1ª metade → 2ª metade",
                f"{tend_fc['media_2']:.0f} bpm",
                f"{tend_fc['variacao']:+.0f} bpm",
                delta_color="inverse",
            )
    
    st.markdown("---")
    
    # Padrão semanal
    padroes = padroes_por_dia_semana(steps)
    if padroes:
        st.markdown("### 📅 Padrão Semanal")
        fig = grafico_padrao_semanal(padroes)
        if fig:
            st.plotly_chart(fig, use_container_width=True)


# ── TAB: Relatório ───────────────────────────────────────────────────────────
with tab_relatorio:
    st.markdown("### 📄 Relatório Completo")
    st.markdown(
        '<p style="color: #888;">Gere o relatório para copiar e enviar para uma IA analisar (ChatGPT, Gemini, Claude, etc.).</p>',
        unsafe_allow_html=True
    )
    
    col_md, col_pdf = st.columns(2)
    
    with col_md:
        if st.button("📝 Gerar Markdown", type="primary", use_container_width=True):
            with st.spinner("Gerando relatório..."):
                relatorio = gerar_relatorio_markdown(
                    perfil, membro, dispositivos, metricas, treinos_data
                )
                st.session_state.relatorio_md = relatorio
    
    with col_pdf:
        if st.button("📑 Gerar PDF", type="secondary", use_container_width=True):
            with st.spinner("Gerando PDF..."):
                from src.pdf_generator import gerar_pdf
                pdf_bytes = gerar_pdf(
                    perfil, membro, dispositivos, metricas, treinos_data
                )
                st.session_state.relatorio_pdf = pdf_bytes
    
    st.markdown("")
    
    if "relatorio_md" in st.session_state:
        st.download_button(
            label="⬇️ Baixar Relatório (.md)",
            data=st.session_state.relatorio_md,
            file_name="relatorio_saude.md",
            mime="text/markdown",
            use_container_width=True,
        )
    
    if "relatorio_pdf" in st.session_state:
        st.download_button(
            label="⬇️ Baixar Relatório (.pdf)",
            data=st.session_state.relatorio_pdf,
            file_name="relatorio_saude.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    
    if "relatorio_md" in st.session_state:
        with st.expander("👁️ Visualizar relatório", expanded=False):
            st.markdown(st.session_state.relatorio_md)
