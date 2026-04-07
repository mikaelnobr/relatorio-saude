# -*- coding: utf-8 -*-
"""
Gerador de PDF estilizado para o relatório de saúde.
Usa fpdf2 para criar PDFs sem dependências de sistema.
"""

from fpdf import FPDF
from src.helpers import (
    ts_to_date, ts_to_datetime, ts_to_weekday,
    min_para_hm, seg_para_hm, formatar_numero, FUSO
)
from src.processors.trends import (
    analisar_tendencia_passos, analisar_tendencia_fc,
    analisar_tendencia_sono, padroes_por_dia_semana,
    frequencia_semanal_treinos
)
from datetime import datetime
import os


class RelatorioPDF(FPDF):
    """PDF customizado com header/footer e estilos."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
        # Registrar fonte que suporta Unicode
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.exists(os.path.join(font_dir, "DejaVuSans.ttf")):
            self.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"), uni=True)
            self.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"), uni=True)
            self.unicode_font = "DejaVu"
        else:
            self.unicode_font = None
    
    def _use_font(self, style="", size=10):
        """Usa fonte Unicode se disponível, senão Helvetica."""
        if self.unicode_font:
            self.set_font(self.unicode_font, style, size)
        else:
            self.set_font("Helvetica", style, size)
    
    def header(self):
        self._use_font("B", 10)
        self.set_text_color(255, 107, 53)
        self.cell(0, 8, "MiFitness Health Report", align="L")
        self.set_text_color(150, 150, 150)
        self._use_font("", 8)
        self.cell(0, 8, datetime.now(tz=FUSO).strftime("%d/%m/%Y %H:%M"), align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(255, 107, 53)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
    
    def footer(self):
        self.set_y(-15)
        self._use_font("", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")
    
    def titulo_secao(self, emoji, texto):
        """Título de seção com barra colorida."""
        self.ln(4)
        self.set_fill_color(255, 107, 53)
        self.rect(10, self.get_y(), 3, 8, "F")
        self._use_font("B", 13)
        self.set_text_color(40, 40, 40)
        self.set_x(16)
        self.cell(0, 8, f"{emoji}  {texto}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
    
    def subtitulo(self, texto):
        self._use_font("B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def item(self, label, valor):
        """Item de lista com label em negrito e valor normal."""
        self._use_font("B", 9)
        self.set_text_color(60, 60, 60)
        label_w = self.get_string_width(label + ": ") + 2
        self.cell(label_w, 6, f"{label}: ")
        self._use_font("", 9)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, str(valor), new_x="LMARGIN", new_y="NEXT")
    
    def nota(self, texto):
        """Nota informativa com fundo cinza claro."""
        self.ln(2)
        self.set_fill_color(245, 245, 245)
        self._use_font("", 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, texto, fill=True)
        self.ln(2)
    
    def tabela(self, headers, dados, col_widths=None):
        """Tabela estilizada."""
        if not dados:
            return
        
        n_cols = len(headers)
        if col_widths is None:
            available = 190
            col_widths = [available / n_cols] * n_cols
        
        # Header
        self.set_fill_color(255, 107, 53)
        self.set_text_color(255, 255, 255)
        self._use_font("B", 7)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, fill=True, align="C")
        self.ln()
        
        # Linhas
        self._use_font("", 7)
        self.set_text_color(40, 40, 40)
        for row_idx, row in enumerate(dados):
            if self.get_y() > 265:
                self.add_page()
                # Re-header
                self.set_fill_color(255, 107, 53)
                self.set_text_color(255, 255, 255)
                self._use_font("B", 7)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 6, h, border=1, fill=True, align="C")
                self.ln()
                self._use_font("", 7)
                self.set_text_color(40, 40, 40)
            
            if row_idx % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            for i, val in enumerate(row):
                self.cell(col_widths[i], 5, str(val), border=1, fill=True, align="C")
            self.ln()


def gerar_pdf(perfil, membro, dispositivos, metricas, treinos) -> bytes:
    """
    Gera o relatório em PDF.
    
    Returns:
        bytes do PDF gerado
    """
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    steps = metricas.get("steps", [])
    sleep = metricas.get("sleep", [])
    hr = metricas.get("heart_rate", [])
    cal = metricas.get("calories", [])
    intensity = metricas.get("intensity", [])
    stand = metricas.get("stand", [])
    stress = metricas.get("stress", [])
    spo2 = metricas.get("spo2", [])
    
    all_dates = [int(s["data"]) for s in steps]
    data_inicio = ts_to_date(min(all_dates)) if all_dates else "?"
    data_fim = ts_to_date(max(all_dates)) if all_dates else "?"
    total_dias = len(all_dates)
    
    # ── Cabeçalho principal ──
    pdf._use_font("B", 20)
    pdf.set_text_color(255, 107, 53)
    pdf.cell(0, 12, "Relatorio Completo de Saude e Fitness", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf._use_font("", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Dados extraidos da conta Xiaomi MiFitness", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Periodo: {data_inicio} a {data_fim} ({total_dias} dias)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    
    # ── Perfil ──
    pdf.titulo_secao(">>", "PERFIL DO USUARIO")
    if membro.get("sexo"):
        pdf.item("Sexo", membro["sexo"])
    if membro.get("nascimento"):
        idade_str = f" ({membro['idade']} anos)" if membro.get("idade") else ""
        pdf.item("Nascimento", f"{membro['nascimento']}{idade_str}")
    if membro.get("altura_cm") and membro["altura_cm"] > 0:
        pdf.item("Altura", f"{membro['altura_cm']:.0f} cm")
    if membro.get("peso_atual_kg") and membro["peso_atual_kg"] > 0:
        pdf.item("Peso atual", f"{membro['peso_atual_kg']:.1f} kg")
    pdf.item("Peso inicial (app)", f"{perfil.get('peso', '?')} kg")
    if membro.get("imc"):
        imc = membro["imc"]
        cat = "Abaixo do peso" if imc < 18.5 else "Normal" if imc < 25 else "Sobrepeso" if imc < 30 else "Obesidade"
        pdf.item("IMC", f"{imc:.1f} ({cat})")
    pdf.item("FC maxima registrada", f"{perfil.get('fc_max_registrada', '?')} bpm")
    if membro.get("idade"):
        pdf.item("FC maxima teorica", f"{220 - membro['idade']} bpm")
    pdf.item("Meta passos", formatar_numero(perfil.get("meta_passos", "?")))
    pdf.item("Meta calorias", f"{formatar_numero(perfil.get('meta_calorias', '?'))} kcal")
    pdf.item("Meta intensidade", f"{perfil.get('meta_intensidade', '?')} min")
    if dispositivos:
        pdf.item("Dispositivos", ", ".join(dispositivos))
    
    # ── Passos ──
    if steps:
        pdf.titulo_secao(">>", "ATIVIDADE DIARIA (PASSOS)")
        passos_vals = [s["passos"] for s in steps]
        dist_vals = [s["distancia_m"] for s in steps]
        media_passos = sum(passos_vals) / len(passos_vals)
        meta_p = int(perfil.get("meta_passos", 10000))
        dias_meta = sum(1 for p in passos_vals if p >= meta_p)
        
        pdf.item("Total de passos", formatar_numero(sum(passos_vals)))
        pdf.item("Distancia total", f"{sum(dist_vals)/1000:.1f} km")
        pdf.item("Media diaria", f"{formatar_numero(int(media_passos))} passos")
        pdf.item("Dia mais ativo", f"{formatar_numero(max(passos_vals))} ({ts_to_date([s['data'] for s in steps if s['passos']==max(passos_vals)][0])})")
        pdf.item("Dia menos ativo", f"{formatar_numero(min(passos_vals))} ({ts_to_date([s['data'] for s in steps if s['passos']==min(passos_vals)][0])})")
        pdf.item("Dias na meta", f"{dias_meta}/{total_dias} ({dias_meta/total_dias*100:.0f}%)")
        
        pdf.ln(3)
        pdf.subtitulo("Detalhamento diario")
        
        headers = ["Data", "Dia", "Passos", "Distancia", "Calorias", "Meta"]
        dados_tabela = []
        for s in sorted(steps, key=lambda x: int(x["data"])):
            meta_ok = "Sim" if s["passos"] >= meta_p else "Nao"
            dados_tabela.append([
                ts_to_date(s["data"]),
                ts_to_weekday(s["data"]),
                formatar_numero(s["passos"]),
                f"{s['distancia_m']/1000:.1f} km",
                f"{s['calorias']} kcal",
                meta_ok,
            ])
        pdf.tabela(headers, dados_tabela, [28, 15, 28, 28, 28, 15])
    
    # ── Sono ──
    if sleep:
        pdf.add_page()
        pdf.titulo_secao(">>", "QUALIDADE DO SONO")
        scores = [s["score"] for s in sleep if s["score"] > 0]
        duracoes = [s["duracao_total"] for s in sleep if s["duracao_total"] > 0]
        profundos = [s["sono_profundo"] for s in sleep if s["duracao_total"] > 0]
        
        if scores:
            media_score = sum(scores) / len(scores)
            media_dur = sum(duracoes) / len(duracoes) if duracoes else 0
            media_prof = sum(profundos) / len(profundos) if profundos else 0
            
            pdf.item("Score medio", f"{media_score:.0f}/100")
            pdf.item("Duracao media", min_para_hm(media_dur))
            if media_dur > 0:
                pdf.item("Sono profundo medio", f"{min_para_hm(media_prof)} ({media_prof/media_dur*100:.0f}%)")
            pdf.item("Melhor noite", f"{max(scores)} ({ts_to_date([s['data'] for s in sleep if s['score']==max(scores)][0])})")
            pdf.item("Pior noite", f"{min(scores)} ({ts_to_date([s['data'] for s in sleep if s['score']==min(scores)][0])})")
            pdf.item("Noites registradas", str(len(duracoes)))
        
        fc_sono = [s["fc_media"] for s in sleep if s["fc_media"] > 0]
        fc_sono_min = [s["fc_min"] for s in sleep if s["fc_min"] > 0]
        if fc_sono:
            pdf.item("FC media no sono", f"{sum(fc_sono)/len(fc_sono):.0f} bpm")
        if fc_sono_min:
            pdf.item("FC minima no sono", f"{min(fc_sono_min)} bpm")
        
        pdf.ln(3)
        pdf.subtitulo("Detalhamento noturno")
        headers = ["Data", "Score", "Duracao", "Profundo", "Leve", "REM", "FC"]
        dados_tabela = []
        for s in sorted(sleep, key=lambda x: int(x["data"])):
            if s["duracao_total"] == 0:
                continue
            dados_tabela.append([
                ts_to_date(s["data"]),
                str(s["score"]),
                min_para_hm(s["duracao_total"]),
                min_para_hm(s["sono_profundo"]),
                min_para_hm(s["sono_leve"]),
                min_para_hm(s["sono_rem"]) if s["sono_rem"] else "-",
                f"{s['fc_media']}" if s["fc_media"] > 0 else "-",
            ])
        pdf.tabela(headers, dados_tabela, [25, 18, 27, 27, 27, 22, 18])
    
    # ── FC ──
    if hr:
        pdf.add_page()
        pdf.titulo_secao(">>", "FREQUENCIA CARDIACA")
        fc_medias = [h["fc_media"] for h in hr]
        fc_repousos = [h["fc_repouso"] for h in hr if h["fc_repouso"] > 0]
        fc_maximas = [h["fc_max"] for h in hr]
        fc_minimas = [h["fc_min"] for h in hr]
        
        pdf.item("FC media geral", f"{sum(fc_medias)/len(fc_medias):.0f} bpm")
        if fc_repousos:
            pdf.item("FC repouso media", f"{sum(fc_repousos)/len(fc_repousos):.0f} bpm")
            pdf.item("FC repouso mais baixa", f"{min(fc_repousos)} bpm")
            pdf.item("FC repouso mais alta", f"{max(fc_repousos)} bpm")
        pdf.item("FC maxima absoluta", f"{max(fc_maximas)} bpm")
        pdf.item("FC minima absoluta", f"{min(fc_minimas)} bpm")
        
        total_aquec = sum(h["zona_aquecimento"] for h in hr)
        total_queima = sum(h["zona_queima"] for h in hr)
        total_aerob = sum(h["zona_aerobica"] for h in hr)
        total_anaerob = sum(h["zona_anaerobica"] for h in hr)
        total_extrema = sum(h["zona_extrema"] for h in hr)
        
        pdf.ln(2)
        pdf.subtitulo("Zonas cardiacas (total no periodo)")
        pdf.item("Aquecimento (50-60%)", f"{total_aquec} min")
        pdf.item("Queima gordura (60-70%)", f"{total_queima} min")
        pdf.item("Aerobica (70-80%)", f"{total_aerob} min")
        pdf.item("Anaerobica (80-90%)", f"{total_anaerob} min")
        pdf.item("Extrema (90-100%)", f"{total_extrema} min")
        
        pdf.ln(3)
        pdf.subtitulo("FC diaria")
        headers = ["Data", "FC Media", "Repouso", "FC Max", "FC Min"]
        dados_tabela = []
        for h in sorted(hr, key=lambda x: int(x["data"])):
            dados_tabela.append([
                ts_to_date(h["data"]),
                str(h["fc_media"]),
                str(h["fc_repouso"]),
                str(h["fc_max"]),
                str(h["fc_min"]),
            ])
        pdf.tabela(headers, dados_tabela, [30, 28, 28, 28, 28])
    
    # ── Calorias ──
    if cal:
        pdf.add_page()
        pdf.titulo_secao(">>", "CALORIAS")
        cal_vals = [c["calorias"] for c in cal]
        media_cal = sum(cal_vals) / len(cal_vals)
        meta_cal = int(perfil.get("meta_calorias", 1000))
        dias_meta_c = sum(1 for c in cal_vals if c >= meta_cal)
        
        pdf.item("Total no periodo", f"{formatar_numero(sum(cal_vals))} kcal")
        pdf.item("Media diaria", f"{formatar_numero(int(media_cal))} kcal")
        pdf.item("Dia mais ativo", f"{formatar_numero(max(cal_vals))} kcal")
        pdf.item("Dia menos ativo", f"{formatar_numero(min(cal_vals))} kcal")
        pdf.item("Dias na meta", f"{dias_meta_c}/{len(cal_vals)} ({dias_meta_c/len(cal_vals)*100:.0f}%)")
    
    # ── Intensidade ──
    if intensity:
        pdf.ln(4)
        pdf.subtitulo("Minutos de Atividade Intensa")
        int_vals = [i["duracao_min"] for i in intensity]
        total_int = sum(int_vals)
        media_int = total_int / len(int_vals)
        pdf.item("Total", f"{total_int} min ({min_para_hm(total_int)})")
        pdf.item("Media diaria", f"{media_int:.0f} min")
        pdf.item("Media semanal", f"~{media_int*7:.0f} min (OMS recomenda >=150)")
    
    # ── Treinos ──
    if treinos:
        pdf.add_page()
        pdf.titulo_secao(">>", "TREINOS E EXERCICIOS")
        treinos_musc = [t for t in treinos if "strength" in t["tipo"].lower()]
        
        pdf.item("Total de treinos", str(len(treinos)))
        pdf.item("Musculacao", str(len(treinos_musc)))
        pdf.item("Tempo total", seg_para_hm(sum(t["duracao_seg"] for t in treinos)))
        pdf.item("Calorias totais", f"{formatar_numero(sum(t['calorias_total'] for t in treinos))} kcal")
        
        if treinos_musc:
            dur_musc = [t["duracao_seg"] for t in treinos_musc]
            cal_musc = [t["calorias_total"] for t in treinos_musc]
            fc_m = [t["fc_media"] for t in treinos_musc if t["fc_media"] > 0]
            
            pdf.ln(2)
            pdf.subtitulo("Estatisticas de Musculacao")
            pdf.item("Duracao media/sessao", seg_para_hm(sum(dur_musc)/len(dur_musc)))
            pdf.item("Sessao mais longa", seg_para_hm(max(dur_musc)))
            pdf.item("Sessao mais curta", seg_para_hm(min(dur_musc)))
            pdf.item("Calorias medias/sessao", f"{sum(cal_musc)/len(cal_musc):.0f} kcal")
            if fc_m:
                pdf.item("FC media nos treinos", f"{sum(fc_m)/len(fc_m):.0f} bpm")
        
        pdf.ln(3)
        pdf.subtitulo("Todos os treinos")
        headers = ["Data", "Tipo", "Duracao", "Cal", "FC Med", "FC Max"]
        dados_tabela = []
        for t in treinos:
            dist = f" ({t['distancia']/1000:.1f}km)" if t["distancia"] > 0 else ""
            dados_tabela.append([
                ts_to_date(t["data"]),
                f"{t['tipo']}{dist}"[:20],
                seg_para_hm(t["duracao_seg"]),
                str(t["calorias_total"]),
                str(t["fc_media"]),
                str(t["fc_max"]),
            ])
        pdf.tabela(headers, dados_tabela, [25, 45, 25, 22, 22, 22])
    
    # ── Tendências ──
    pdf.add_page()
    pdf.titulo_secao(">>", "ANALISE DE TENDENCIAS")
    
    tend_p = analisar_tendencia_passos(steps)
    if tend_p:
        pdf.subtitulo("Passos")
        pdf.item("Media 1a metade", formatar_numero(int(tend_p["media_1"])))
        pdf.item("Media 2a metade", formatar_numero(int(tend_p["media_2"])))
        pdf.item("Variacao", f"{tend_p['variacao_pct']:+.1f}%")
        pdf.ln(2)
    
    tend_f = analisar_tendencia_fc(hr)
    if tend_f:
        pdf.subtitulo("FC de Repouso")
        pdf.item("Media 1a metade", f"{tend_f['media_1']:.0f} bpm")
        pdf.item("Media 2a metade", f"{tend_f['media_2']:.0f} bpm")
        pdf.item("Variacao", f"{tend_f['variacao']:+.0f} bpm ({tend_f['status']})")
        pdf.ln(2)
    
    tend_s = analisar_tendencia_sono(sleep)
    if tend_s:
        pdf.subtitulo("Qualidade do Sono")
        pdf.item("Score 1a metade", f"{tend_s['score_1']:.0f}")
        pdf.item("Score 2a metade", f"{tend_s['score_2']:.0f}")
        pdf.item("Variacao", f"{tend_s['variacao']:+.0f} pontos")
        pdf.ln(2)
    
    padroes = padroes_por_dia_semana(steps)
    if padroes:
        pdf.subtitulo("Padrao semanal de passos")
        headers = ["Dia", "Media Passos", "Registros"]
        dados_tabela = [[p["dia"], formatar_numero(int(p["media"])), str(p["registros"])] for p in padroes]
        pdf.tabela(headers, dados_tabela, [30, 80, 30])
    
    return bytes(pdf.output())
