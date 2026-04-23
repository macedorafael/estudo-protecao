"""
Geração do relatório PDF de coordenação de proteção e seletividade.
Usa ReportLab para layout e incorpora os dois coordenogramas PNG do Matplotlib.
"""
from __future__ import annotations
import io
from datetime import date
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether,
    NextPageTemplate, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

from .calculations import StudyResult

W, H = A4                       # portrait: 595 × 842 pt
LW, LH = landscape(A4)         # landscape: 842 × 595 pt
MARGIN = 2.0 * cm

# ── Paleta ───────────────────────────────────────────────────────────────────
BLUE_DARK    = colors.HexColor("#1A237E")
BLUE_MED     = colors.HexColor("#1565C0")
BLUE_LIGHT   = colors.HexColor("#E3F2FD")
GREY_LIGHT   = colors.HexColor("#F5F5F5")
ENERGISA_COLOR = colors.HexColor("#0077C8")

styles = getSampleStyleSheet()


def _style(name: str, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, parent=styles["Normal"], **kw)


TITLE_STYLE   = _style("TitleS",  fontSize=14, textColor=BLUE_DARK,
                        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
H1_STYLE      = _style("H1S",     fontSize=11, textColor=BLUE_DARK,
                        fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)
BODY_STYLE    = _style("BodyS",   fontSize=9,  leading=13)
SMALL_STYLE   = _style("SmallS",  fontSize=8,  textColor=colors.grey)
CENTER_STYLE  = _style("CenterS", fontSize=9,  alignment=TA_CENTER)
RIGHT_STYLE   = _style("RightS",  fontSize=9,  alignment=TA_RIGHT)
WARN_STYLE    = _style("WarnS",   fontSize=8,  textColor=colors.HexColor("#B71C1C"))


def _section(title: str) -> List:
    return [
        Spacer(1, 0.3 * cm),
        Paragraph(title, H1_STYLE),
        HRFlowable(width="100%", thickness=1.5, color=BLUE_MED, spaceAfter=4),
    ]


def _tbl(data: list, col_widths=None, header: bool = True) -> Table:
    tbl = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style_cmds = [
        ("FONTNAME",     (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1),(-1, -1), [colors.white, GREY_LIGHT]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#BDBDBD")),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]
    if header:
        style_cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE_MED),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def _bool_ansi(enabled: bool) -> str:
    return "HABILITADO" if enabled else "DESABILITADO"


def generate_pdf(result: StudyResult,
                 png_fase: bytes,
                 png_neutro: bytes) -> bytes:
    buf = io.BytesIO()

    # ── Frames e templates (retrato + paisagem para os coordenogramas) ────────
    portrait_frame = Frame(MARGIN, MARGIN,
                           W - 2 * MARGIN, H - 2 * MARGIN,
                           id="portrait_frame")
    landscape_frame = Frame(MARGIN, MARGIN,
                            LW - 2 * MARGIN, LH - 2 * MARGIN,
                            id="landscape_frame")

    portrait_tmpl  = PageTemplate(id="portrait",  frames=[portrait_frame],  pagesize=A4)
    landscape_tmpl = PageTemplate(id="landscape", frames=[landscape_frame], pagesize=landscape(A4))

    doc = BaseDocTemplate(
        buf,
        pageTemplates=[portrait_tmpl, landscape_tmpl],
        title="Estudo de Coordenação de Proteção e Seletividade",
    )

    story: List = []
    p  = result.params
    c  = p.concessionaria
    cl = p.cliente
    eq = p.equipamentos
    fn = p.funcoes_ansi
    up = c.religador_upstream

    # ═══════════════════════════════════════════════════════════════════════
    # CAPA
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        "ESTUDO DE COORDENAÇÃO DA PROTEÇÃO E SELETIVIDADE",
        _style("Cover", fontSize=16, textColor=BLUE_DARK, fontName="Helvetica-Bold",
               alignment=TA_CENTER, spaceAfter=8)
    ))
    story.append(Paragraph(
        "Média Tensão — Instalações acima de 1,0 kV até 36,2 kV",
        CENTER_STYLE
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE_MED))
    story.append(Spacer(1, 0.5 * cm))

    cover_data = [
        ["Cliente:",                 cl.razao_social],
        ["CNPJ:",                    cl.cnpj or "—"],
        ["Endereço:",                cl.endereco or "—"],
        ["UC (Unidade Consumidora):", cl.uc or "—"],
        ["Tensão de fornecimento:",  f"{c.tensao_kv:.1f} kV"],
        ["Subestação / Circuito:",   f"{c.subestacao} / {c.circuito}"],
        ["Data do estudo:",          date.today().strftime("%d/%m/%Y")],
        ["Engenheiro responsável:",  p.engenheiro.nome],
        ["CREA:",                    p.engenheiro.crea],
    ]
    cov_tbl = Table(cover_data, colWidths=[6 * cm, 10 * cm])
    cov_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [colors.white, GREY_LIGHT]),
    ]))
    story.append(cov_tbl)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Elaborado conforme ABNT NBR 14039:2005, NDU 002 e procedimentos ENERGISA.",
        SMALL_STYLE
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════
    # 1. OBJETIVO
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("1. OBJETIVO")
    story.append(Paragraph(
        "O presente estudo tem por objetivo dimensionar e ajustar o sistema de proteção de sobrecorrente "
        "da instalação de média tensão do cliente, garantindo a coordenação e seletividade com o sistema "
        "de proteção da concessionária ENERGISA, em conformidade com a ABNT NBR 14039:2005 e a NDU 002.",
        BODY_STYLE
    ))

    # ═══════════════════════════════════════════════════════════════════════
    # 2. IDENTIFICAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("2. IDENTIFICAÇÃO")

    story.append(Paragraph("2.1 Dados do Cliente",
                            _style("H2a", fontSize=9, fontName="Helvetica-Bold")))
    id_cli = [
        ["Razão Social",   cl.razao_social],
        ["CNPJ",           cl.cnpj or "—"],
        ["Endereço",       cl.endereco or "—"],
        ["UC",             cl.uc or "—"],
        ["Demanda Prevista", f"{cl.demanda_kva:.0f} kVA"],
        ["Fator de Potência", f"{cl.fator_potencia:.2f}"],
    ]
    story.append(_tbl([["Campo", "Valor"]] + id_cli, col_widths=[5 * cm, 11 * cm]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("2.2 Dados da Concessionária (ENERGISA)",
                            _style("H2b", fontSize=9, fontName="Helvetica-Bold")))
    story.append(Paragraph(
        "<font color='#0077C8'><b>⚡ Campos abaixo informados pela concessionária no documento ATA/NCC.</b></font>",
        _style("EnergisaNote", fontSize=8, textColor=ENERGISA_COLOR)
    ))
    story.append(Spacer(1, 0.15 * cm))
    id_con = [
        ["Tensão de Fornecimento",        f"{c.tensao_kv:.1f} kV"],
        ["Subestação / Circuito",         f"{c.subestacao} / {c.circuito}"],
        ["ICC Trifásico Simétrico",       f"{c.icc_3f_a:.2f} A  (∠ {c.angulo_3f_grau:.2f}°)"],
        ["ICC Fase-Terra Simétrico",      f"{c.icc_ft_a:.2f} A  (∠ {c.angulo_ft_grau:.2f}°)"],
        ["Impedância Positiva (R1+jX1)",  f"{c.r1_pu:.4f} + j{c.x1_pu:.4f} pu"],
        ["Impedância Zero (R0+jX0)",      f"{c.r0_pu:.4f} + j{c.x0_pu:.4f} pu"],
        ["Potência Base",                 f"{c.potencia_base_mva:.0f} MVA"],
        ["Religador Upstream",            up.modelo or "—"],
        ["51F: Pickup / Dial / Curva / Inst.",
         f"{up.pickup_fase_a:.0f} A / {up.dial_fase:.2f} / {up.curva_fase} / {up.inst_fase_a:.0f} A"],
        ["51N: Pickup / Dial / Curva / Inst.",
         f"{up.pickup_neutro_a:.0f} A / {up.dial_neutro:.2f} / {up.curva_neutro} / "
         + (f"{up.inst_neutro_a:.0f} A" if up.inst_neutro_a else "Bloq.")],
    ]
    con_tbl = Table([["Parâmetro", "Valor (ENERGISA)"]] + id_con,
                    colWidths=[7 * cm, 9 * cm])
    con_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ENERGISA_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, BLUE_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#90CAF9")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(con_tbl)

    # ═══════════════════════════════════════════════════════════════════════
    # 3. CÁLCULO DE CORRENTES
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("3. CÁLCULO DE CORRENTES")

    # Correntes gerais
    story.append(Paragraph(
        f"Corrente de demanda: <b>In = {cl.demanda_kva:.0f} / (√3 × {c.tensao_kv:.1f}) = "
        f"<font color='#1565C0'>{result.in_demanda_a:.4f} A</font></b>",
        BODY_STYLE
    ))
    story.append(Paragraph(
        f"Inrush parcial (10 × maior trafo + Σ demais): "
        f"<b><font color='#1565C0'>{result.inrush_parcial_a:.4f} A</font></b>",
        BODY_STYLE
    ))
    story.append(Paragraph(
        f"Impedância da fonte: Zs = Vfn / ICC = "
        f"{result.vfn_v:.2f} / {c.icc_3f_a:.2f} = "
        f"<b><font color='#1565C0'>{result.Zs_ohm:.4f} Ω</font></b>",
        BODY_STYLE
    ))
    story.append(Paragraph(
        f"Impedância de inrush: Zitm = Vfn / I_parcial = "
        f"{result.vfn_v:.2f} / {result.inrush_parcial_a:.4f} = "
        f"<b><font color='#1565C0'>{result.Zitm_ohm:.4f} Ω</font></b>",
        BODY_STYLE
    ))
    story.append(Paragraph(
        f"Inrush REAL (corrigido): I_real = Vfn / (Zs + Zitm) = "
        f"<b><font color='#1565C0'>{result.inrush_real_fase_a:.4f} A (fase) "
        f"| {result.inrush_real_neutro_a:.4f} A (neutro)</font></b>",
        BODY_STYLE
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Tabela de transformadores
    tr_header = ["Trafo", "kVA", "Z%", "In (A)", "Inrush parc. (A)",
                 "ANSI Fase (A)", "ANSI Neutro (A)", "t_ANSI (s)", "Fusível"]
    tr_rows = []
    for tr in result.trafos:
        tr_rows.append([
            f"T{tr.idx}",
            f"{tr.potencia_kva:.0f}",
            f"{p.transformadores[tr.idx-1].impedancia_pct:.2f}%",
            f"{tr.in_trafo_a:.4f}",
            f"{tr.inrush_parcial_a:.4f}",
            f"{tr.ansi_fase_a:.2f}",
            f"{tr.ansi_neutro_a:.2f}",
            f"{tr.tempo_ansi_s:.1f}",
            tr.fusivel or "—",
        ])
    tr_rows.append([
        "TOTAL",
        f"{sum(t.potencia_kva for t in p.transformadores):.0f}",
        "—",
        f"{result.in_total_trafo_a:.4f}",
        f"{result.inrush_parcial_a:.4f}",
        "—", "—", "—", "—"
    ])
    story.append(_tbl([tr_header] + tr_rows,
                      col_widths=[1.2*cm, 1.5*cm, 1.5*cm, 2.2*cm, 2.5*cm,
                                  2.5*cm, 2.5*cm, 1.8*cm, 1.3*cm]))

    # ═══════════════════════════════════════════════════════════════════════
    # 4. DIMENSIONAMENTO DO TC
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("4. DIMENSIONAMENTO DO TRANSFORMADOR DE CORRENTE (TC)")
    tc_ok_str  = f"> ICC_3Ø = {c.icc_3f_a:.0f} A  ✓" if result.tc_ok else f"< ICC_3Ø  ✗ REVISAR"
    tc_data = [
        ["Parâmetro", "Valor", "Critério"],
        ["Relação do TC (RTC)",
         f"{eq.tc_primario_a:.0f}/{eq.tc_secundario_a:.0f} A  →  RTC = {result.rtc:.0f}",
         "Primário ≥ In_demanda"],
        ["Corrente de Saturação (RTC × 20)",
         f"{result.i_sat_primario_a:.0f} A", tc_ok_str],
        ["Zfiação (cabo L×2/A)",
         f"{result.z_fiacao_ohm:.4f} Ω",
         f"{eq.cabo_comprimento_m:.0f} m × {eq.cabo_secao_mm2:.1f} mm²"],
        ["Zrelé",   f"{eq.rele_impedancia_ohm:.4f} Ω", "Dado do fabricante do relé"],
        ["Ztc",     f"{eq.ztc_ohm:.4f} Ω",            "Resistência interna do TC"],
        ["Ztotal = Zfio+Zr+Ztc", f"{result.z_total_sec_ohm:.4f} Ω", ""],
        ["Tensão de Saturação Vs = Ztot × (ICC/RTC)",
         f"{result.v_saturacao_v:.2f} V",
         "Verificar limite da classe do TC"],
    ]
    story.append(_tbl(tc_data, col_widths=[6.5*cm, 5.5*cm, 5*cm]))
    story.append(Paragraph(
        f"Relé: {eq.rele_fabricante} {eq.rele_modelo} — corrente nominal {eq.rele_corrente_nominal_a} A",
        BODY_STYLE
    ))

    # ═══════════════════════════════════════════════════════════════════════
    # 5. AJUSTES DE PROTEÇÃO DO CONSUMIDOR
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("5. AJUSTES DE PROTEÇÃO DO CONSUMIDOR")

    adj_data = [
        ["Função", "Parâmetro", "Valor Primário (A)", "Valor Secundário (A)", "Observação"],
        ["ANSI 51F", "Pickup",
         f"{result.pickup_fase_51f_a:.5f}",
         f"{result.pickup_fase_51f_sec_a:.5f}",
         "1,25 × In_demanda"],
        ["ANSI 51F", "Curva / Time Dial",
         result.curva_consumidor, f"{result.dial_fase:.3f}", ""],
        ["ANSI 50F", "Instantânea",
         f"{result.inst_50f_a:.2f}",
         f"{result.inst_50f_sec_a:.5f}",
         "1,1 × Inrush_real_fase"],
        ["ANSI 51N", "Pickup",
         f"{result.pickup_neutro_51n_a:.5f}",
         f"{result.pickup_neutro_51n_sec_a:.5f}",
         f"{fn.pickup_neutro_pct_fase:.0f}% do pickup de fase"],
        ["ANSI 51N", "Curva / Time Dial",
         result.curva_consumidor, f"{result.dial_neutro:.3f}", ""],
        ["ANSI 50N", "Instantânea",
         f"{result.inst_50n_a:.2f}",
         f"{result.inst_50n_sec_a:.5f}",
         "1,1 × Inrush_real_neutro"],
    ]
    story.append(_tbl(adj_data, col_widths=[2.5*cm, 2.8*cm, 4*cm, 4*cm, 3.7*cm]))

    # Funções ANSI extras
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Demais funções ANSI:",
                            _style("H2c", fontSize=9, fontName="Helvetica-Bold")))
    fn_data = [
        ["Função", "Descrição", "Status"],
        ["51GS", "Falta à terra sensível",  _bool_ansi(fn.f51gs)],
        ["27",   "Subtensão",               _bool_ansi(fn.f27)],
        ["47",   "Desequilíbrio de tensão", _bool_ansi(fn.f47)],
        ["59",   "Sobretensão",             _bool_ansi(fn.f59)],
        ["79V",  "Religamento por tensão",  _bool_ansi(fn.f79v)],
        ["81U",  "Subfrequência",           _bool_ansi(fn.f81u)],
        ["81O",  "Sobrefrequência",         _bool_ansi(fn.f81o)],
        ["86",   "Relé de bloqueio",        _bool_ansi(fn.f86)],
    ]
    fn_tbl = Table(fn_data, colWidths=[2.5*cm, 7*cm, 6.5*cm])
    fn_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_MED),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.HexColor("#BDBDBD")),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0),(-1,-1), 3),
    ])
    for row_idx in range(1, len(fn_data)):
        val = fn_data[row_idx][2]
        bg = colors.HexColor("#E8F5E9") if val == "HABILITADO" else GREY_LIGHT
        fn_style.add("BACKGROUND", (2, row_idx), (2, row_idx), bg)
    fn_tbl.setStyle(fn_style)
    story.append(fn_tbl)

    if eq.possui_geracao_distribuida:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            "⚠ Geração Distribuída presente: ajustar funções 27, 59 e 81 conforme "
            "Tabelas 1–4 da NDU 015 (ENERGISA).",
            WARN_STYLE
        ))

    # ═══════════════════════════════════════════════════════════════════════
    # 6. TABELA RESUMO DOS AJUSTES
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("6. TABELA RESUMO DOS AJUSTES")
    res_data = [
        ["Parâmetro",                    "FASE",                                  "NEUTRO"],
        ["Função",                       "51/50",                                 "51N/50N"],
        ["Curva",                        result.curva_consumidor,                 result.curva_consumidor],
        ["Pickup Primário (A)",          f"{result.pickup_fase_51f_a:.5f}",       f"{result.pickup_neutro_51n_a:.5f}"],
        ["Pickup Secundário (A)",        f"{result.pickup_fase_51f_sec_a:.5f}",   f"{result.pickup_neutro_51n_sec_a:.5f}"],
        ["Time Dial (TD)",               f"{result.dial_fase:.3f}",               f"{result.dial_neutro:.3f}"],
        ["Instantânea 50 Primário (A)",  f"{result.inst_50f_a:.2f}",              f"{result.inst_50n_a:.2f}"],
        ["Instantânea 50 Secundário (A)",f"{result.inst_50f_sec_a:.5f}",          f"{result.inst_50n_sec_a:.5f}"],
    ]
    story.append(_tbl(res_data, col_widths=[8*cm, 5*cm, 5*cm]))

    # Verificação de coordenação
    story.append(Spacer(1, 0.3 * cm))
    if result.margem_coordenacao_s is not None:
        coord_ok_str = "✓ COORDENAÇÃO OK" if result.coordenacao_ok else "✗ VERIFICAR COORDENAÇÃO"
        coord_color  = "#2E7D32" if result.coordenacao_ok else "#B71C1C"
        story.append(Paragraph(
            f"Verificação de coordenação: "
            f"t_upstream(ICC) = {result.t_upstream_icc_s:.3f} s — "
            f"t_consumidor(ICC) = {result.t_consumidor_icc_s:.3f} s → "
            f"Margem = {result.margem_coordenacao_s:.3f} s  "
            f"<font color='{coord_color}'><b>{coord_ok_str}</b></font>",
            BODY_STYLE
        ))

    # ═══════════════════════════════════════════════════════════════════════
    # 7. COORDENOGRAMA — FASE  (página paisagem)
    # ═══════════════════════════════════════════════════════════════════════
    story.append(NextPageTemplate("landscape"))
    story.append(PageBreak())
    story += _section("7. COORDENOGRAMA — FASE (51F / 50F)")
    story.append(Paragraph(
        "Diagrama tempo × corrente: curva do consumidor (roxo) vs. religador ENERGISA (vermelho). "
        "Eixos em escala logarítmica. Curva IEC Very Inverse.",
        BODY_STYLE
    ))
    story.append(Spacer(1, 0.2 * cm))
    # Em paisagem: área útil ≈ 25,3 × 16,9 cm
    img_fase = Image(io.BytesIO(png_fase),
                     width=LW - 2 * MARGIN, height=LH - 2 * MARGIN,
                     kind="proportional")
    story.append(img_fase)

    # ═══════════════════════════════════════════════════════════════════════
    # 8. COORDENOGRAMA — NEUTRO  (página paisagem)
    # ═══════════════════════════════════════════════════════════════════════
    story.append(NextPageTemplate("landscape"))
    story.append(PageBreak())
    story += _section("8. COORDENOGRAMA — NEUTRO (51N / 50N)")
    story.append(Paragraph(
        "Diagrama tempo × corrente para proteção de neutro: curva do consumidor (verde) "
        "vs. religador ENERGISA (vermelho).",
        BODY_STYLE
    ))
    story.append(Spacer(1, 0.2 * cm))
    img_neutro = Image(io.BytesIO(png_neutro),
                       width=LW - 2 * MARGIN, height=LH - 2 * MARGIN,
                       kind="proportional")
    story.append(img_neutro)

    # Volta ao retrato para a seção seguinte
    story.append(NextPageTemplate("portrait"))

    # ═══════════════════════════════════════════════════════════════════════
    # 9. DADOS DO RELIGADOR UPSTREAM (ENERGISA)
    # ═══════════════════════════════════════════════════════════════════════
    story += _section("9. DADOS DO RELIGADOR UPSTREAM (ENERGISA)")
    story.append(Paragraph(
        "<font color='#0077C8'><b>⚡ Dados fornecidos pela ENERGISA no documento ATA/NCC. "
        "Válidos por 1 ano sem restrição ou alteração de circuito.</b></font>",
        _style("EnergisaNote2", fontSize=8, textColor=ENERGISA_COLOR)
    ))
    story.append(Spacer(1, 0.2 * cm))
    ata_data = [
        ["Parâmetro",       "FASE",                    "NEUTRO"],
        ["Função",          "51F / 50F",               "51N / 50N"],
        ["Pickup (A)",      f"{up.pickup_fase_a:.0f}",  f"{up.pickup_neutro_a:.0f}"],
        ["Time Dial",       f"{up.dial_fase:.2f}",      f"{up.dial_neutro:.2f}"],
        ["Curva",           up.curva_fase,              up.curva_neutro],
        ["Instantânea (A)", f"{up.inst_fase_a:.0f}",
         f"{up.inst_neutro_a:.0f}" if up.inst_neutro_a else "Bloqueado"],
    ]
    ata_tbl = Table(ata_data, colWidths=[8*cm, 4*cm, 4*cm])
    ata_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ENERGISA_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, BLUE_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#90CAF9")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(ata_tbl)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Filosofia de proteção (ENERGISA): abertura de 51F e 51N com tempo máximo de 0,2 s, "
        "mantendo margem de 0,3 s de coordenação (consumidor/concessionária), curva IEC VI.",
        BODY_STYLE
    ))

    # ═══════════════════════════════════════════════════════════════════════
    # ASSINATURA
    # ═══════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5 * cm))
    story.append(HRFlowable(width="50%", thickness=0.8, color=colors.black,
                             hAlign="CENTER"))
    story.append(Paragraph(p.engenheiro.nome, CENTER_STYLE))
    story.append(Paragraph(f"CREA: {p.engenheiro.crea}", CENTER_STYLE))
    story.append(Paragraph(f"Data: {date.today().strftime('%d/%m/%Y')}", CENTER_STYLE))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Documento elaborado em conformidade com ABNT NBR 14039:2005 e NDU 002 ENERGISA.",
        SMALL_STYLE
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()
