export type CurvaIEC = 'IEC VI' | 'IEC EI' | 'IEC MI' | 'IEC LI'
export type CorrenteNominal = 1 | 5

export interface RelayUpstream {
  modelo: string
  pickup_fase_a: number
  dial_fase: number
  curva_fase: CurvaIEC
  inst_fase_a: number
  pickup_neutro_a: number
  dial_neutro: number
  curva_neutro: CurvaIEC
  inst_neutro_a: number | null
}

export interface DadosConcessionaria {
  tensao_kv: number
  icc_3f_a: number
  angulo_3f_grau: number
  icc_ft_a: number
  angulo_ft_grau: number
  r1_pu: number
  x1_pu: number
  r0_pu: number
  x0_pu: number
  potencia_base_mva: number
  subestacao: string
  circuito: string
  religador_upstream: RelayUpstream
}

export interface DadosCliente {
  razao_social: string
  cnpj: string
  endereco: string
  uc: string
  demanda_kva: number
  fator_potencia: number
}

export interface Transformador {
  potencia_kva: number
  impedancia_pct: number
  tipo: 'Óleo' | 'Seco'
  fator_inrush: number
  tempo_inrush_s: number
  tempo_ansi_s: number
  fusivel: string
}

export interface EquipamentosProtecao {
  tc_primario_a: number
  tc_secundario_a: number
  ztc_ohm: number
  cabo_comprimento_m: number
  cabo_secao_mm2: number
  rele_fabricante: string
  rele_modelo: string
  rele_corrente_nominal_a: CorrenteNominal
  rele_impedancia_ohm: number
  possui_geracao_distribuida: boolean
  possui_nobreak: boolean
}

export interface FuncoesANSI {
  f51_fase: boolean
  f50_fase: boolean
  f51n_neutro: boolean
  f50n_neutro: boolean
  f51gs: boolean
  f27: boolean
  f47: boolean
  f59: boolean
  f79v: boolean
  f81u: boolean
  f81o: boolean
  f86: boolean
  curva_rele: CurvaIEC
  pickup_neutro_pct_fase: number
}

export interface EngenheirResponsavel {
  nome: string
  crea: string
}

export interface StudyParameters {
  engenheiro: EngenheirResponsavel
  concessionaria: DadosConcessionaria
  cliente: DadosCliente
  transformadores: Transformador[]
  equipamentos: EquipamentosProtecao
  funcoes_ansi: FuncoesANSI
}

export const DEFAULT_STUDY: StudyParameters = {
  engenheiro: { nome: '', crea: '' },
  concessionaria: {
    tensao_kv: 13.8,
    icc_3f_a: 0,
    angulo_3f_grau: -70,
    icc_ft_a: 0,
    angulo_ft_grau: -73,
    r1_pu: 0,
    x1_pu: 0,
    r0_pu: 0,
    x0_pu: 0,
    potencia_base_mva: 100,
    subestacao: '',
    circuito: '',
    religador_upstream: {
      modelo: '',
      pickup_fase_a: 0,
      dial_fase: 0.2,
      curva_fase: 'IEC VI',
      inst_fase_a: 0,
      pickup_neutro_a: 0,
      dial_neutro: 0.86,
      curva_neutro: 'IEC VI',
      inst_neutro_a: null,
    },
  },
  cliente: {
    razao_social: '',
    cnpj: '',
    endereco: '',
    uc: '',
    demanda_kva: 0,
    fator_potencia: 0.92,
  },
  transformadores: [
    {
      potencia_kva: 0,
      impedancia_pct: 5,
      tipo: 'Óleo',
      fator_inrush: 10,
      tempo_inrush_s: 0.1,
      tempo_ansi_s: 3,
      fusivel: '',
    },
  ],
  equipamentos: {
    tc_primario_a: 0,
    tc_secundario_a: 5,
    ztc_ohm: 0.1,
    cabo_comprimento_m: 4,
    cabo_secao_mm2: 2.5,
    rele_fabricante: '',
    rele_modelo: '',
    rele_corrente_nominal_a: 5,
    rele_impedancia_ohm: 0.028,
    possui_geracao_distribuida: false,
    possui_nobreak: false,
  },
  funcoes_ansi: {
    f51_fase: true,
    f50_fase: true,
    f51n_neutro: true,
    f50n_neutro: true,
    f51gs: false,
    f27: false,
    f47: false,
    f59: false,
    f79v: false,
    f81u: false,
    f81o: false,
    f86: false,
    curva_rele: 'IEC VI',
    pickup_neutro_pct_fase: 20,
  },
}
