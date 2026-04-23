"""
Geração dos coordenogramas (curva tempo × corrente) em PNG para embutir no PDF.
Gera dois gráficos separados: FASE e NEUTRO.

Regra de legenda: só aparece legenda para elementos que estão visíveis
dentro dos limites dos eixos (x_min..x_max , 0.01..100 s).
"""
from __future__ import annotations
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from .calculations import StudyResult, iec_time

_IEC_CURVES = {
    "IEC VI": {"K": 13.5,  "alpha": 1.0},
    "IEC EI": {"K": 80.0,  "alpha": 2.0},
    "IEC MI": {"K":  0.14, "alpha": 0.02},
    "IEC LI": {"K": 120.0, "alpha": 1.0},
}

Y_MIN, Y_MAX = 0.01, 10.0

# ── Cores padronizadas ────────────────────────────────────────────────────────
COR_CONSUMIDOR_FASE   = "#5B2C8D"
COR_CONSUMIDOR_NEUTRO = "#1A7A3A"
COR_UPSTREAM          = "#C0392B"
COR_ICC               = "#555555"
COR_INRUSH            = "#884EA0"

# Uma cor distinta por transformador (até 8 trafos)
CORES_ANSI = [
    "#E74C3C",   # T1 — vermelho
    "#E67E22",   # T2 — laranja
    "#F1C40F",   # T3 — amarelo
    "#27AE60",   # T4 — verde
    "#2980B9",   # T5 — azul
    "#8E44AD",   # T6 — roxo
    "#16A085",   # T7 — turquesa
    "#2C3E50",   # T8 — cinza escuro
]


# ── Helpers de visibilidade ───────────────────────────────────────────────────

def _lbl(label: str, visible: bool) -> str:
    """Retorna o label se visível, senão '_nolegend_' (matplotlib ignora)."""
    return label if visible else "_nolegend_"


def _vline_visible(x: float, x_min: float, x_max: float) -> bool:
    return x_min <= x <= x_max


def _hline_visible(y: float) -> bool:
    return Y_MIN <= y <= Y_MAX


def _point_visible(x: float, y: float, x_min: float, x_max: float) -> bool:
    return x_min <= x <= x_max and Y_MIN <= y <= Y_MAX


def _curve_visible(times: np.ndarray) -> bool:
    """True se a curva tem ao menos um ponto dentro da janela de tempo."""
    valid = times[~np.isnan(times)]
    return len(valid) > 0 and bool(np.any((valid >= Y_MIN) & (valid <= Y_MAX)))


# ── Funções de suporte ────────────────────────────────────────────────────────

def _curve_times(currents: np.ndarray, pickup: float, dial: float, curve: str) -> np.ndarray:
    c = _IEC_CURVES[curve]
    times = np.full_like(currents, np.nan)
    M = currents / pickup
    mask = M > 1.001
    times[mask] = (c["K"] / (M[mask] ** c["alpha"] - 1.0)) * dial
    return times


def _fmt_ax(ax, x_min: float, x_max: float, title: str) -> None:
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_xlabel("Corrente (A) — valor primário", fontsize=10)
    ax.set_ylabel("Tempo (s)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.grid(True, which="major", linestyle="-",  linewidth=0.5, color="#CCCCCC")
    ax.grid(True, which="minor", linestyle=":",  linewidth=0.3, color="#EEEEEE")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.3g}"))
    ax.tick_params(axis="both", labelsize=8)


def _save_fig(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── API pública ───────────────────────────────────────────────────────────────

def generate_coordenograma(result: StudyResult) -> tuple[bytes, bytes]:
    """Retorna (png_fase, png_neutro) — dois coordenogramas separados."""
    return _chart_fase(result), _chart_neutro(result)


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO DE FASE
# ─────────────────────────────────────────────────────────────────────────────

def _chart_fase(result: StudyResult) -> bytes:
    icc = result.params.concessionaria.icc_3f_a
    up  = result.params.concessionaria.religador_upstream

    x_min = max(1.0, result.pickup_fase_51f_a * 0.3)
    x_max = icc * 2.5
    currents = np.logspace(np.log10(x_min), np.log10(x_max), 1000)

    fig, ax = plt.subplots(figsize=(14, 7))
    _fmt_ax(ax, x_min, x_max, "Coordenograma — FASE (51F / 50F)")

    # ── Curva upstream 51F (clipada na inst. 50F upstream) ───────────────
    t_up = _curve_times(currents, up.pickup_fase_a, up.dial_fase, up.curva_fase)
    t_up[currents > up.inst_fase_a] = np.nan      # para onde entra a inst. 50F
    ax.plot(currents, t_up, color=COR_UPSTREAM, linewidth=2.2,
            label=_lbl(
                f"ENERGISA 51F — {up.curva_fase}  Ip={up.pickup_fase_a:.0f} A  TD={up.dial_fase:.2f}",
                _curve_visible(t_up)
            ))

    # ── Instantânea upstream 50F ──────────────────────────────────────────
    ax.axvline(x=up.inst_fase_a, color=COR_UPSTREAM, linewidth=1.4, linestyle="--",
               label=_lbl(
                   f"ENERGISA 50F inst. = {up.inst_fase_a:.0f} A",
                   _vline_visible(up.inst_fase_a, x_min, x_max)
               ))

    # ── Curva consumidor 51F (clipada na inst. 50F consumidor) ───────────
    t_cons = _curve_times(currents, result.pickup_fase_51f_a,
                          result.dial_fase, result.curva_consumidor)
    t_cons[currents > result.inst_50f_a] = np.nan  # para onde entra a inst. 50F
    ax.plot(currents, t_cons, color=COR_CONSUMIDOR_FASE, linewidth=2.2,
            label=_lbl(
                f"Consumidor 51F — {result.curva_consumidor}  "
                f"Ip={result.pickup_fase_51f_a:.2f} A  TD={result.dial_fase:.3f}",
                _curve_visible(t_cons)
            ))

    # ── Instantânea consumidor 50F ────────────────────────────────────────
    ax.axvline(x=result.inst_50f_a, color=COR_CONSUMIDOR_FASE, linewidth=1.6, linestyle=":",
               label=_lbl(
                   f"Consumidor 50F inst. = {result.inst_50f_a:.1f} A",
                   _vline_visible(result.inst_50f_a, x_min, x_max)
               ))

    # Anotação do tempo no ponto 50F
    t_at_inst = iec_time(result.inst_50f_a, result.pickup_fase_51f_a,
                         result.dial_fase, result.curva_consumidor)
    if (t_at_inst is not None
            and _point_visible(result.inst_50f_a, t_at_inst, x_min, x_max)):
        ax.annotate(
            f"{t_at_inst:.3f} s",
            xy=(result.inst_50f_a, t_at_inst),
            xytext=(result.inst_50f_a * 0.55, t_at_inst * 2.2),
            fontsize=7.5, color=COR_CONSUMIDOR_FASE,
            arrowprops=dict(arrowstyle="->", color=COR_CONSUMIDOR_FASE, lw=0.8),
        )

    # ── Pontos ANSI dos transformadores (fase) ────────────────────────────
    for tr in result.trafos:
        cor = CORES_ANSI[(tr.idx - 1) % len(CORES_ANSI)]
        vis = _point_visible(tr.ansi_fase_a, tr.tempo_ansi_s, x_min, x_max)
        ax.plot(tr.ansi_fase_a, tr.tempo_ansi_s,
                marker="o", markersize=9, markeredgewidth=1.5,
                color=cor, markerfacecolor=cor, markeredgecolor="white",
                linestyle="None",
                label=_lbl(
                    f"ANSI T{tr.idx} {tr.potencia_kva:.0f} kVA  "
                    f"{tr.ansi_fase_a:.0f} A / {tr.tempo_ansi_s:.1f} s",
                    vis
                ))

    # ── Ponto de inrush (fase) ────────────────────────────────────────────
    t_inrush = max(t.tempo_inrush_s for t in result.params.transformadores)
    ax.plot(result.inrush_real_fase_a, t_inrush,
            marker="D", markersize=9, markeredgewidth=1.8,
            color=COR_INRUSH, markerfacecolor="#E8DAEF", linestyle="None",
            label=_lbl(
                f"Inrush fase  {result.inrush_real_fase_a:.1f} A / {t_inrush:.2f} s",
                _point_visible(result.inrush_real_fase_a, t_inrush, x_min, x_max)
            ))

    # ── ICC 3Ø ────────────────────────────────────────────────────────────
    ax.axvline(x=icc, color=COR_ICC, linewidth=1.4, linestyle="--",
               label=_lbl(
                   f"ICC 3Ø = {icc:.0f} A",
                   _vline_visible(icc, x_min, x_max)
               ))

    # ── Texto de coordenação ──────────────────────────────────────────────
    if result.margem_coordenacao_s is not None:
        ok_txt = "✓ COORDENAÇÃO OK" if result.coordenacao_ok else "✗ VERIFICAR"
        ok_col = "#2E7D32" if result.coordenacao_ok else "#B71C1C"
        ax.text(0.02, 0.03,
                f"Margem = {result.margem_coordenacao_s:.3f} s  {ok_txt}",
                transform=ax.transAxes, fontsize=8, color=ok_col,
                fontweight="bold", verticalalignment="bottom")

    ax.legend(fontsize=7, loc="upper right", framealpha=0.92,
              handlelength=2.5, borderpad=0.8)
    fig.tight_layout()
    return _save_fig(fig)


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO DE NEUTRO
# ─────────────────────────────────────────────────────────────────────────────

def _chart_neutro(result: StudyResult) -> bytes:
    icc_3f = result.params.concessionaria.icc_3f_a
    icc_ft = result.params.concessionaria.icc_ft_a
    up     = result.params.concessionaria.religador_upstream

    x_min = max(1.0, result.pickup_neutro_51n_a * 0.3)
    x_max = icc_3f * 2.0
    currents = np.logspace(np.log10(x_min), np.log10(x_max), 1000)

    fig, ax = plt.subplots(figsize=(14, 7))
    _fmt_ax(ax, x_min, x_max, "Coordenograma — NEUTRO (51N / 50N)")

    # ── Curva upstream 51N (clipada na inst. 50N upstream) ───────────────
    t_up_n = _curve_times(currents, up.pickup_neutro_a, up.dial_neutro, up.curva_neutro)
    if up.inst_neutro_a:
        t_up_n[currents > up.inst_neutro_a] = np.nan   # para onde entra a inst. 50N
    ax.plot(currents, t_up_n, color=COR_UPSTREAM, linewidth=2.2,
            label=_lbl(
                f"ENERGISA 51N — {up.curva_neutro}  Ip={up.pickup_neutro_a:.0f} A  TD={up.dial_neutro:.2f}",
                _curve_visible(t_up_n)
            ))

    # ── Instantânea upstream 50N ──────────────────────────────────────────
    if up.inst_neutro_a:
        ax.axvline(x=up.inst_neutro_a, color=COR_UPSTREAM, linewidth=1.4, linestyle="--",
                   label=_lbl(
                       f"ENERGISA 50N inst. = {up.inst_neutro_a:.0f} A",
                       _vline_visible(up.inst_neutro_a, x_min, x_max)
                   ))

    # ── Curva consumidor 51N (clipada na inst. 50N consumidor) ───────────
    t_cons_n = _curve_times(currents, result.pickup_neutro_51n_a,
                             result.dial_neutro, result.curva_consumidor)
    t_cons_n[currents > result.inst_50n_a] = np.nan    # para onde entra a inst. 50N
    ax.plot(currents, t_cons_n, color=COR_CONSUMIDOR_NEUTRO, linewidth=2.2,
            label=_lbl(
                f"Consumidor 51N — {result.curva_consumidor}  "
                f"Ip={result.pickup_neutro_51n_a:.2f} A  TD={result.dial_neutro:.3f}",
                _curve_visible(t_cons_n)
            ))

    # ── Instantânea consumidor 50N ────────────────────────────────────────
    ax.axvline(x=result.inst_50n_a, color=COR_CONSUMIDOR_NEUTRO, linewidth=1.6, linestyle=":",
               label=_lbl(
                   f"Consumidor 50N inst. = {result.inst_50n_a:.1f} A",
                   _vline_visible(result.inst_50n_a, x_min, x_max)
               ))

    # Anotação do tempo no ponto 50N
    t_at_inst_n = iec_time(result.inst_50n_a, result.pickup_neutro_51n_a,
                            result.dial_neutro, result.curva_consumidor)
    if (t_at_inst_n is not None
            and _point_visible(result.inst_50n_a, t_at_inst_n, x_min, x_max)):
        ax.annotate(
            f"{t_at_inst_n:.3f} s",
            xy=(result.inst_50n_a, t_at_inst_n),
            xytext=(result.inst_50n_a * 0.45, t_at_inst_n * 2.4),
            fontsize=7.5, color=COR_CONSUMIDOR_NEUTRO,
            arrowprops=dict(arrowstyle="->", color=COR_CONSUMIDOR_NEUTRO, lw=0.8),
        )

    # ── Pontos ANSI dos transformadores (neutro) ──────────────────────────
    for tr in result.trafos:
        cor = CORES_ANSI[(tr.idx - 1) % len(CORES_ANSI)]
        vis = _point_visible(tr.ansi_neutro_a, tr.tempo_ansi_s, x_min, x_max)
        ax.plot(tr.ansi_neutro_a, tr.tempo_ansi_s,
                marker="o", markersize=9, markeredgewidth=1.5,
                color=cor, markerfacecolor=cor, markeredgecolor="white",
                linestyle="None",
                label=_lbl(
                    f"ANSI T{tr.idx} {tr.potencia_kva:.0f} kVA  "
                    f"{tr.ansi_neutro_a:.0f} A / {tr.tempo_ansi_s:.1f} s",
                    vis
                ))

    # ── Ponto de inrush (neutro) ──────────────────────────────────────────
    t_inrush = max(t.tempo_inrush_s for t in result.params.transformadores)
    ax.plot(result.inrush_real_neutro_a, t_inrush,
            marker="^", markersize=9, markeredgewidth=1.8,
            color=COR_INRUSH, markerfacecolor="#E8DAEF", linestyle="None",
            label=_lbl(
                f"Inrush neutro  {result.inrush_real_neutro_a:.1f} A / {t_inrush:.2f} s",
                _point_visible(result.inrush_real_neutro_a, t_inrush, x_min, x_max)
            ))

    # ── ICC fase-terra ────────────────────────────────────────────────────
    ax.axvline(x=icc_ft, color=COR_ICC, linewidth=1.4, linestyle="--",
               label=_lbl(
                   f"ICC fase-terra = {icc_ft:.0f} A",
                   _vline_visible(icc_ft, x_min, x_max)
               ))

    ax.legend(fontsize=7, loc="upper right", framealpha=0.92,
              handlelength=2.5, borderpad=0.8)
    fig.tight_layout()
    return _save_fig(fig)
