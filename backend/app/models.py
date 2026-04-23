from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class RelayUpstream(BaseModel):
    modelo: str = Field("", description="Modelo do religador upstream (ex: NOJA OSM-38 595-07)")
    # Fase 51F/50F
    pickup_fase_a: float = Field(..., gt=0, description="Pickup da proteção de fase 51F (A primário)")
    dial_fase: float = Field(..., gt=0, description="Time Dial da proteção de fase 51F")
    curva_fase: Literal["IEC VI", "IEC EI", "IEC MI", "IEC LI"] = Field("IEC VI")
    inst_fase_a: float = Field(..., gt=0, description="Corrente instantânea 50F (A primário)")
    # Neutro 51N/50N
    pickup_neutro_a: float = Field(..., gt=0, description="Pickup da proteção de neutro 51N (A primário)")
    dial_neutro: float = Field(..., gt=0, description="Time Dial da proteção de neutro 51N")
    curva_neutro: Literal["IEC VI", "IEC EI", "IEC MI", "IEC LI"] = Field("IEC VI")
    inst_neutro_a: Optional[float] = Field(None, description="Corrente instantânea 50N (A). None = bloqueado.")


class DadosConcessionaria(BaseModel):
    tensao_kv: float = Field(..., gt=0, description="Tensão nominal de fornecimento (kV)")
    icc_3f_a: float = Field(..., gt=0, description="Corrente de curto-circuito trifásico simétrico (A)")
    angulo_3f_grau: float = Field(-70.0, description="Ângulo da ICC trifásica (°)")
    icc_ft_a: float = Field(..., gt=0, description="Corrente de curto-circuito fase-terra simétrico (A)")
    angulo_ft_grau: float = Field(-73.0, description="Ângulo da ICC fase-terra (°)")
    r1_pu: float = Field(..., description="Resistência de sequência positiva R1 (pu, base 100 MVA)")
    x1_pu: float = Field(..., description="Reatância de sequência positiva X1 (pu, base 100 MVA)")
    r0_pu: float = Field(..., description="Resistência de sequência zero R0 (pu, base 100 MVA)")
    x0_pu: float = Field(..., description="Reatância de sequência zero X0 (pu, base 100 MVA)")
    potencia_base_mva: float = Field(100.0, gt=0, description="Potência base (MVA)")
    subestacao: str = Field("", description="Nome da subestação (ex: Aparecida do Taboado)")
    circuito: str = Field("", description="Identificação do circuito (ex: ATA52)")
    religador_upstream: RelayUpstream


class DadosCliente(BaseModel):
    razao_social: str = Field(..., min_length=1, description="Razão social do cliente")
    cnpj: str = Field("", description="CNPJ do cliente")
    endereco: str = Field("", description="Endereço completo")
    uc: str = Field("", description="Código da Unidade Consumidora (ex: 1870160)")
    demanda_kva: float = Field(..., gt=0, description="Demanda prevista/contratada (kVA)")
    fator_potencia: float = Field(0.92, gt=0, le=1.0, description="Fator de potência (padrão ENERGISA: 0,92)")


class Transformador(BaseModel):
    potencia_kva: float = Field(..., gt=0, description="Potência nominal (kVA)")
    impedancia_pct: float = Field(..., gt=0, lt=30, description="Impedância percentual Z% (plaqueta do trafo)")
    tipo: Literal["Óleo", "Seco"] = Field("Óleo", description="Tipo de isolamento")
    fator_inrush: float = Field(10.0, ge=5, le=15, description="Fator de inrush (× In). Padrão: 10×")
    tempo_inrush_s: float = Field(0.1, gt=0, description="Duração do inrush (s). Aparece no coordenograma.")
    tempo_ansi_s: float = Field(3.0, gt=0, description="Tempo do ponto ANSI de dano do trafo (s). Tipicamente 2–4 s.")
    fusivel: str = Field("", description="Fusível de MT associado (ex: 10K, 40K, 1H). Conforme NDU 002 Anexo II.")


class EquipamentosProtecao(BaseModel):
    tc_primario_a: float = Field(..., gt=0, description="Corrente primária do TC (A). Deve ser ≥ In e RTC×20 > ICC.")
    tc_secundario_a: float = Field(5.0, description="Corrente secundária do TC (A). Padrão: 5 A.")
    ztc_ohm: float = Field(0.1, gt=0, description="Impedância interna do TC (Ω). Típica: 0,1 Ω.")
    cabo_comprimento_m: float = Field(4.0, gt=0, description="Comprimento do cabeamento TC → relé (m). Usado para calcular Zfiação.")
    cabo_secao_mm2: float = Field(2.5, gt=0, description="Seção do cabo secundário (mm²).")
    rele_fabricante: str = Field("", description="Fabricante do relé (ex: Pextron, Noja Power, SEL).")
    rele_modelo: str = Field("", description="Modelo do relé (ex: URP 1439TU).")
    rele_corrente_nominal_a: Literal[1, 5] = Field(5, description="Corrente nominal de entrada do relé (1 A ou 5 A).")
    rele_impedancia_ohm: float = Field(0.028, gt=0, description="Impedância do relé Zr (Ω). Ex: Pextron URP = 0,028 Ω.")
    possui_geracao_distribuida: bool = Field(False, description="Se Sim, exige ajuste de funções 27/59/81 conforme NDU 015.")
    possui_nobreak: bool = Field(False, description="Se Sim, o relé tem alimentação ininterrupta (NBR 14039).")


class FuncoesANSI(BaseModel):
    f51_fase: bool = Field(True, description="51 – Sobrecorrente de fase temporizada. Obrigatória.")
    f50_fase: bool = Field(True, description="50 – Sobrecorrente de fase instantânea. Obrigatória.")
    f51n_neutro: bool = Field(True, description="51N – Sobrecorrente de neutro temporizada. Obrigatória.")
    f50n_neutro: bool = Field(True, description="50N – Sobrecorrente de neutro instantânea.")
    f51gs: bool = Field(False, description="51GS – Falta à terra sensível. Habilitar com GD ou neutro aterrado.")
    f27: bool = Field(False, description="27 – Subtensão. Obrigatória com geração distribuída (NDU 015).")
    f47: bool = Field(False, description="47 – Desequilíbrio de tensão. Opcional.")
    f59: bool = Field(False, description="59 – Sobretensão. Obrigatória com geração distribuída (NDU 015).")
    f79v: bool = Field(False, description="79V – Religamento por tensão. Geralmente desabilitado em consumidores.")
    f81u: bool = Field(False, description="81U – Subfrequência. Obrigatória com geração distribuída (NDU 015).")
    f81o: bool = Field(False, description="81O – Sobrefrequência. Obrigatória com geração distribuída (NDU 015).")
    f86: bool = Field(False, description="86 – Relé de bloqueio. Habilitar quando exigido pelo projeto.")
    # Ajuste da curva do relé consumidor
    curva_rele: Literal["IEC VI", "IEC EI", "IEC MI", "IEC LI"] = Field(
        "IEC VI", description="Curva do relé do consumidor. IEC VI obrigatório conforme ATA da ENERGISA."
    )
    # Percentual do pickup de neutro em relação à fase
    pickup_neutro_pct_fase: float = Field(
        20.0, ge=10, le=50,
        description="Pickup de neutro como % do pickup de fase. Padrão: 20%. Alguns estudos usam 35%."
    )


class EngenheirResponsavel(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome completo do engenheiro responsável.")
    crea: str = Field(..., min_length=1, description="Número do CREA (ex: 5062320435D).")


class StudyParameters(BaseModel):
    engenheiro: EngenheirResponsavel
    concessionaria: DadosConcessionaria
    cliente: DadosCliente
    transformadores: List[Transformador] = Field(..., min_length=1, description="Lista de transformadores do cliente.")
    equipamentos: EquipamentosProtecao
    funcoes_ansi: FuncoesANSI
