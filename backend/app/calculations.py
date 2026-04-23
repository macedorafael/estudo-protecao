"""
Cálculos de coordenação de proteção e seletividade de média tensão.
Método conforme estudos do Eng. Flávio Saletti / João Mamede Filho 8ª ed.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Optional

from .models import StudyParameters

# ── Constantes das curvas IEC ────────────────────────────────────────────────
_IEC_CURVES = {
    "IEC VI": {"K": 13.5,  "alpha": 1.0},   # Very Inverse   (Muito Inversa)
    "IEC EI": {"K": 80.0,  "alpha": 2.0},   # Extremely Inverse
    "IEC MI": {"K":  0.14, "alpha": 0.02},  # Moderately Inverse
    "IEC LI": {"K": 120.0, "alpha": 1.0},   # Long-Time Inverse
}

RHO_CU = 0.0172  # Ω·mm²/m (cobre a 20 °C)


def iec_time(current_a: float, pickup_a: float, dial: float, curve: str) -> Optional[float]:
    """Tempo de operação (s) pela curva IEC. Retorna None se M ≤ 1."""
    c = _IEC_CURVES[curve]
    M = current_a / pickup_a
    if M <= 1.0:
        return None
    return (c["K"] / (M ** c["alpha"] - 1.0)) * dial


def _in_trafo(kva: float, tensao_kv: float) -> float:
    return kva / (math.sqrt(3) * tensao_kv)


def _z_fiacao(comprimento_m: float, secao_mm2: float) -> float:
    return RHO_CU * comprimento_m * 2.0 / secao_mm2


def _calc_dial_from_inst(pickup: float, inst: float, curve: str, t_max: float = 0.2) -> float:
    """
    Método do estudo (João Mamede filho 8ª ed.):
    Ajusta o dial para que a curva temporizada atinja t_max exatamente
    na corrente da instantânea (50F ou 50N).

    Equação:  t = K / (M - 1) × DT  →  DT = t × (M - 1) / K
    """
    c = _IEC_CURVES[curve]
    M = inst / pickup
    if M <= 1.0:
        return 0.05
    dial = t_max * (M - 1.0) / c["K"]
    # Arredonda para baixo na resolução de 0,001 (3 casas decimais)
    dial = math.floor(dial * 1000) / 1000
    return max(0.050, dial)


# ── Resultado por transformador ──────────────────────────────────────────────
@dataclass
class TransformerResult:
    idx: int
    potencia_kva: float
    tipo: str
    in_trafo_a: float
    inrush_parcial_a: float   # contribuição para o inrush parcial
    z_pct: float
    ansi_fase_a: float
    ansi_neutro_a: float
    tempo_ansi_s: float
    fusivel: str


# ── Resultado completo do estudo ─────────────────────────────────────────────
@dataclass
class StudyResult:
    params: StudyParameters

    # Correntes de carga
    in_demanda_a: float
    in_total_trafo_a: float

    # Inrush
    inrush_parcial_a: float      # 10 × maior + Σ demais (sem fonte)
    inrush_real_fase_a: float    # corrigido pela impedância da fonte
    inrush_real_neutro_a: float  # = inrush_real_fase × pct_neutro/100

    # Impedâncias do inrush
    Zs_ohm: float                # impedância da fonte = Vfn / ICC
    Zitm_ohm: float              # impedância de inrush = Vfn / I_parcial
    Ztotal_inrush_ohm: float     # Zs + Zitm

    # TC
    rtc: float
    z_fiacao_ohm: float
    z_total_sec_ohm: float
    i_sat_primario_a: float
    v_saturacao_v: float
    tc_ok: bool

    # Transformadores
    trafos: List[TransformerResult]

    # Proteção consumidor — FASE
    pickup_fase_51f_a: float
    pickup_fase_51f_sec_a: float
    inst_50f_a: float
    inst_50f_sec_a: float
    dial_fase: float
    curva_consumidor: str

    # Proteção consumidor — NEUTRO
    pickup_neutro_51n_a: float
    pickup_neutro_51n_sec_a: float
    inst_50n_a: float
    inst_50n_sec_a: float
    dial_neutro: float

    # Verificação de coordenação
    t_consumidor_icc_s: Optional[float]   # t do consumidor na ICC_3f
    t_upstream_icc_s: Optional[float]     # t do upstream na ICC_3f
    margem_coordenacao_s: Optional[float]
    coordenacao_ok: bool

    # Tensão de fase (para coordenograma)
    vfn_v: float


def run(params: StudyParameters) -> StudyResult:
    V = params.concessionaria.tensao_kv
    icc_3f = params.concessionaria.icc_3f_a
    eq = params.equipamentos
    fn = params.funcoes_ansi

    # ── Corrente de demanda ──────────────────────────────────────────────
    in_demanda = params.cliente.demanda_kva / (math.sqrt(3) * V)

    # ── Correntes dos transformadores ────────────────────────────────────
    in_list = [_in_trafo(t.potencia_kva, V) for t in params.transformadores]
    in_total = sum(in_list)

    pairs = sorted(zip(params.transformadores, in_list), key=lambda x: x[1], reverse=True)
    maior_trafo, maior_in = pairs[0]
    outros_in = sum(x[1] for x in pairs[1:])

    # ── Inrush PARCIAL (fórmula do estudo: 10×maior + Σdemais) ──────────
    I_parcial = maior_trafo.fator_inrush * maior_in + outros_in

    # ── Inrush REAL (corrigido pela impedância da fonte) ─────────────────
    # Conforme João Mamede Filho 8ª ed. / método do estudo:
    #   Zs   = Vfn / ICC_3f      (impedância da fonte)
    #   Zitm = Vfn / I_parcial   (impedância de inrush)
    #   I_real = Vfn / (Zs + Zitm)
    Vfn = (V * 1000.0) / math.sqrt(3)          # tensão fase-neutro [V]
    Zs  = Vfn / icc_3f                          # [Ω]
    Zitm = Vfn / I_parcial                      # [Ω]
    Ztotal_inrush = Zs + Zitm
    inrush_real_fase = Vfn / Ztotal_inrush
    inrush_real_neutro = inrush_real_fase * (fn.pickup_neutro_pct_fase / 100.0)

    # ── Resultados por transformador ─────────────────────────────────────
    trafos_result: List[TransformerResult] = []
    for i, (t, in_t) in enumerate(zip(params.transformadores, in_list)):
        ansi_fase   = in_t / (t.impedancia_pct / 100.0)
        ansi_neutro = ansi_fase * 0.578   # ≈ (√3/3) × ANSI_fase
        if i == 0:
            inrush_parc = t.fator_inrush * in_t
        else:
            inrush_parc = in_t
        trafos_result.append(TransformerResult(
            idx=i + 1,
            potencia_kva=t.potencia_kva,
            tipo=t.tipo,
            in_trafo_a=in_t,
            inrush_parcial_a=inrush_parc,
            z_pct=t.impedancia_pct,
            ansi_fase_a=ansi_fase,
            ansi_neutro_a=ansi_neutro,
            tempo_ansi_s=t.tempo_ansi_s,
            fusivel=t.fusivel,
        ))

    # ── TC ───────────────────────────────────────────────────────────────
    rtc = eq.tc_primario_a / eq.tc_secundario_a
    z_fio = _z_fiacao(eq.cabo_comprimento_m, eq.cabo_secao_mm2)
    z_sec = z_fio + eq.rele_impedancia_ohm + eq.ztc_ohm
    i_sat = rtc * 20.0
    v_sat = z_sec * (icc_3f / rtc)
    tc_ok = i_sat > icc_3f

    # ── Pickup 51F ───────────────────────────────────────────────────────
    pickup_fase   = 1.25 * in_demanda
    pickup_neutro = pickup_fase * (fn.pickup_neutro_pct_fase / 100.0)

    pickup_fase_sec   = pickup_fase   / rtc
    pickup_neutro_sec = pickup_neutro / rtc

    # ── Instantâneas 50F / 50N ───────────────────────────────────────────
    # Baseado no INRUSH REAL (não no parcial)
    inst_50f = 1.1 * inrush_real_fase
    inst_50n = 1.1 * inrush_real_neutro

    inst_50f_sec = inst_50f / rtc
    inst_50n_sec = inst_50n / rtc

    # ── Dials ─────────────────────────────────────────────────────────────
    # Método: DT escolhido para que a curva atinja 0,2 s no ponto da instantânea
    # (método João Mamede / prática do estudo)
    dial_fase   = _calc_dial_from_inst(pickup_fase,   inst_50f, fn.curva_rele)
    dial_neutro = _calc_dial_from_inst(pickup_neutro, inst_50n, fn.curva_rele)

    # ── Verificação de coordenação ────────────────────────────────────────
    up = params.concessionaria.religador_upstream
    t_upstream = iec_time(icc_3f, up.pickup_fase_a, up.dial_fase, up.curva_fase)
    t_consumidor = iec_time(icc_3f, pickup_fase, dial_fase, fn.curva_rele)

    margem = None
    if t_consumidor is not None and t_upstream is not None:
        margem = t_upstream - t_consumidor
    coordenacao_ok = (margem is not None and margem >= 0.28)

    return StudyResult(
        params=params,
        in_demanda_a=in_demanda,
        in_total_trafo_a=in_total,
        inrush_parcial_a=I_parcial,
        inrush_real_fase_a=inrush_real_fase,
        inrush_real_neutro_a=inrush_real_neutro,
        Zs_ohm=Zs,
        Zitm_ohm=Zitm,
        Ztotal_inrush_ohm=Ztotal_inrush,
        rtc=rtc,
        z_fiacao_ohm=z_fio,
        z_total_sec_ohm=z_sec,
        i_sat_primario_a=i_sat,
        v_saturacao_v=v_sat,
        tc_ok=tc_ok,
        trafos=trafos_result,
        pickup_fase_51f_a=pickup_fase,
        pickup_fase_51f_sec_a=pickup_fase_sec,
        inst_50f_a=inst_50f,
        inst_50f_sec_a=inst_50f_sec,
        dial_fase=dial_fase,
        curva_consumidor=fn.curva_rele,
        pickup_neutro_51n_a=pickup_neutro,
        pickup_neutro_51n_sec_a=pickup_neutro_sec,
        inst_50n_a=inst_50n,
        inst_50n_sec_a=inst_50n_sec,
        dial_neutro=dial_neutro,
        t_consumidor_icc_s=t_consumidor,
        t_upstream_icc_s=t_upstream,
        margem_coordenacao_s=margem,
        coordenacao_ok=coordenacao_ok,
        vfn_v=Vfn,
    )
