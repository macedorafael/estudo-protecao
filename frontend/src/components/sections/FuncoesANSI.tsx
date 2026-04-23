import React from 'react'
import { UseFormRegister } from 'react-hook-form'
import { StudyParameters, CurvaIEC } from '../../types'
import { Field } from '../ui/Field'

const CURVAS: CurvaIEC[] = ['IEC VI', 'IEC EI', 'IEC MI', 'IEC LI']
const CURVA_LABELS: Record<CurvaIEC, string> = {
  'IEC VI': 'IEC VI — Very Inverse',
  'IEC EI': 'IEC EI — Extremely Inverse',
  'IEC MI': 'IEC MI — Moderately Inverse',
  'IEC LI': 'IEC LI — Long-Time Inverse',
}

interface ANSICheckProps {
  label: string
  description: string
  mandatory?: boolean
  name: `funcoes_ansi.${keyof StudyParameters['funcoes_ansi']}`
  register: UseFormRegister<StudyParameters>
}

function ANSICheck({ label, description, mandatory, name, register }: ANSICheckProps) {
  return (
    <label className="flex items-start gap-3 cursor-pointer rounded-lg border border-gray-100 hover:bg-gray-50 p-2 transition-colors">
      <input
        type="checkbox"
        className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600"
        {...register(name)}
        disabled={mandatory}
      />
      <span className="text-sm flex-1">
        <span className="font-semibold text-blue-900">{label}</span>
        {mandatory && <span className="ml-1 text-xs text-red-500 font-medium">(obrigatória)</span>}
        <span className="block text-xs text-gray-500 mt-0.5">{description}</span>
      </span>
    </label>
  )
}

interface Props { register: UseFormRegister<StudyParameters> }

export function FuncoesANSI({ register }: Props) {
  return (
    <div className="section-card">
      <h2 className="section-title">
        <span className="text-lg">⚙️</span> Funções ANSI
      </h2>

      {/* Curva e pickup de neutro */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <Field
          label="Curva do relé consumidor"
          tooltip="Curva de operação temporizada do relé do consumidor. A ENERGISA exige IEC VI (Very Inverse) conforme ATA. Usar IEC EI apenas quando a coordenação não é possível com VI."
          link="https://www.normas.com.br/visualizar/abnt-nbr-nm/14039"
          linkLabel="NBR 14039"
        >
          <select className="field-input" {...register('funcoes_ansi.curva_rele')}>
            {CURVAS.map(c => <option key={c} value={c}>{CURVA_LABELS[c]}</option>)}
          </select>
        </Field>
        <Field
          label="Pickup de neutro 51N (% do pickup de fase)"
          unit="%"
          tooltip="Define o pickup da proteção de neutro como percentual do pickup de fase. Padrão nestes estudos: 20%. Alguns projetos usam 35%."
          hint="Padrão: 20% — alguns estudos usam 35%"
        >
          <input
            className="field-input"
            type="number"
            min={10}
            max={50}
            step={5}
            {...register('funcoes_ansi.pickup_neutro_pct_fase', { valueAsNumber: true })}
          />
        </Field>
      </div>

      {/* Funções obrigatórias */}
      <h3 className="text-sm font-semibold text-gray-700 mb-2">Sobrecorrente (obrigatórias)</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
        <ANSICheck name="funcoes_ansi.f51_fase" label="ANSI 51 — Fase" mandatory
          description="Sobrecorrente de fase temporizada. Pickup calculado em 1,25 × In_demanda." register={register} />
        <ANSICheck name="funcoes_ansi.f50_fase" label="ANSI 50 — Fase" mandatory
          description="Sobrecorrente de fase instantânea. Pickup calculado em 1,1 × Inrush_total." register={register} />
        <ANSICheck name="funcoes_ansi.f51n_neutro" label="ANSI 51N — Neutro" mandatory
          description="Sobrecorrente de neutro temporizada. Pickup = % configurável do pickup de fase." register={register} />
        <ANSICheck name="funcoes_ansi.f50n_neutro" label="ANSI 50N — Neutro"
          description="Sobrecorrente de neutro instantânea. Pickup = 1,1 × Inrush_neutro." register={register} />
      </div>

      {/* Funções opcionais */}
      <h3 className="text-sm font-semibold text-gray-700 mb-2">Falta à terra / Tensão / Frequência</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
        <ANSICheck name="funcoes_ansi.f51gs" label="ANSI 51GS — Terra sensível"
          description="Falta à terra sensível. Habilitar em circuitos com GD ou neutro aterrado." register={register} />
        <ANSICheck name="funcoes_ansi.f27" label="ANSI 27 — Subtensão"
          description="Obrigatória com geração distribuída (NDU 015 Tabela 1)." register={register} />
        <ANSICheck name="funcoes_ansi.f47" label="ANSI 47 — Desequilíbrio de tensão"
          description="Opcional. Detecta desequilíbrio de tensão entre fases." register={register} />
        <ANSICheck name="funcoes_ansi.f59" label="ANSI 59 — Sobretensão"
          description="Obrigatória com geração distribuída (NDU 015 Tabela 1)." register={register} />
        <ANSICheck name="funcoes_ansi.f79v" label="ANSI 79V — Religamento por tensão"
          description="Geralmente desabilitado em consumidores industriais." register={register} />
        <ANSICheck name="funcoes_ansi.f81u" label="ANSI 81U — Subfrequência"
          description="Obrigatória com geração distribuída (NDU 015 Tabela 3)." register={register} />
        <ANSICheck name="funcoes_ansi.f81o" label="ANSI 81O — Sobrefrequência"
          description="Obrigatória com geração distribuída (NDU 015 Tabela 3)." register={register} />
        <ANSICheck name="funcoes_ansi.f86" label="ANSI 86 — Bloqueio"
          description="Relé de bloqueio. Habilitar quando exigido pelo projeto." register={register} />
      </div>
    </div>
  )
}
