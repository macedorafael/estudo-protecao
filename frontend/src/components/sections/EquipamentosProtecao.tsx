import React from 'react'
import { UseFormRegister, useWatch, Control } from 'react-hook-form'
import { StudyParameters } from '../../types'
import { Field } from '../ui/Field'

interface Props {
  register: UseFormRegister<StudyParameters>
  control: Control<StudyParameters>
}

export function EquipamentosProtecao({ register, control }: Props) {
  const gdValue = useWatch({ control, name: 'equipamentos.possui_geracao_distribuida' })

  return (
    <div className="section-card">
      <h2 className="section-title">
        <span className="text-lg">🛡️</span> Equipamentos de Proteção
      </h2>

      {/* TC */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Transformador de Corrente (TC)</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
        <Field
          label="TC — Corrente Primária"
          unit="A"
          tooltip="Corrente primária do TC. Deve ser ≥ In_demanda e satisfazer: RTC × 20 > ICC_3Ø. Ex: 150 A para TC 150/5."
          hint="Deve satisfazer RTC × 20 > ICC"
        >
          <input className="field-input" type="number" min={1} step={5}
            {...register('equipamentos.tc_primario_a', { required: true, valueAsNumber: true })}
            placeholder="Ex: 150"
          />
        </Field>
        <Field
          label="TC — Corrente Secundária"
          unit="A"
          tooltip="Corrente secundária do TC. Padrão no Brasil: 5 A. Deve coincidir com a corrente nominal de entrada do relé."
          hint="Padrão: 5 A"
        >
          <select className="field-input" {...register('equipamentos.tc_secundario_a', { valueAsNumber: true })}>
            <option value={5}>5 A</option>
            <option value={1}>1 A</option>
          </select>
        </Field>
        <Field
          label="Impedância do TC (Ztc)"
          unit="Ω"
          tooltip="Resistência interna do enrolamento secundário do TC. Típica: 0,1 Ω. Fornecida pelo fabricante ou medida. Usada para calcular Ztotal e Vs."
          hint="Típica: 0,1 Ω"
        >
          <input className="field-input" type="number" min={0.001} step={0.001}
            {...register('equipamentos.ztc_ohm', { required: true, valueAsNumber: true })}
          />
        </Field>
        <Field
          label="Comprimento do cabo (TC→relé)"
          unit="m"
          tooltip="Comprimento do cabeamento do secundário do TC até o relé. Usado para calcular Zfiação = ρ × 2L / A. Considere o percurso real (ida + volta)."
          hint="Distância real TC → relé"
        >
          <input className="field-input" type="number" min={0.5} step={0.5}
            {...register('equipamentos.cabo_comprimento_m', { required: true, valueAsNumber: true })}
            placeholder="Ex: 4"
          />
        </Field>
        <Field
          label="Seção do cabo"
          unit="mm²"
          tooltip="Seção transversal do condutor de cobre do circuito secundário. Juntamente com o comprimento, determina Zfiação. Típica: 2,5 mm²."
          hint="Típica: 2,5 mm²"
        >
          <input className="field-input" type="number" min={1} step={0.5}
            {...register('equipamentos.cabo_secao_mm2', { required: true, valueAsNumber: true })}
          />
        </Field>
      </div>

      {/* Relé */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Relé de Proteção</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
        <Field label="Fabricante" tooltip="Fabricante do relé. Ex: Pextron, Noja Power, SEL, ABB, Siemens.">
          <input className="field-input" {...register('equipamentos.rele_fabricante')} placeholder="Ex: Pextron" />
        </Field>
        <Field label="Modelo" tooltip="Modelo do relé de proteção. Ex: URP 1439TU, URP 7104. Aparece na tabela de especificações do relatório.">
          <input className="field-input" {...register('equipamentos.rele_modelo')} placeholder="Ex: URP 1439TU" />
        </Field>
        <Field
          label="Corrente nominal de entrada"
          unit="A"
          tooltip="Corrente nominal do input do relé. Deve coincidir com a corrente secundária do TC escolhido."
        >
          <select className="field-input" {...register('equipamentos.rele_corrente_nominal_a', { valueAsNumber: true })}>
            <option value={5}>5 A</option>
            <option value={1}>1 A</option>
          </select>
        </Field>
        <Field
          label="Impedância do relé (Zr)"
          unit="Ω"
          tooltip="Impedância de entrada do relé por fase. Pextron URP: 0,028 Ω (7 mΩ por entrada). Dado do fabricante. Compõe Ztotal."
          hint="Pextron URP: 0,028 Ω"
        >
          <input className="field-input" type="number" min={0.001} step={0.001}
            {...register('equipamentos.rele_impedancia_ohm', { required: true, valueAsNumber: true })}
          />
        </Field>
      </div>

      {/* Flags */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Condições especiais</h3>
      <div className="flex flex-col gap-3">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600"
            {...register('equipamentos.possui_geracao_distribuida')}
          />
          <span className="text-sm">
            <span className="font-medium">Possui Geração Distribuída (GD)?</span>
            <span className="ml-1 text-gray-500 text-xs">
              Se sim, as funções 27, 59 e 81 devem ser ajustadas conforme Tabelas 1–4 da NDU 015 (ENERGISA).
            </span>
          </span>
        </label>
        {gdValue && (
          <div className="ml-7 rounded-md bg-yellow-50 border border-yellow-200 px-3 py-2 text-xs text-yellow-800">
            ⚠ GD presente: habilitar funções 27 (subtensão), 59 (sobretensão), 81U (subfrequência) e 81O (sobrefrequência) na seção de Funções ANSI.
          </div>
        )}
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600"
            {...register('equipamentos.possui_nobreak')}
          />
          <span className="text-sm">
            <span className="font-medium">Possui No-Break / UPS?</span>
            <span className="ml-1 text-gray-500 text-xs">
              NBR 14039 exige alimentação auxiliar ininterrupta para garantir trip do relé durante curto-circuito (queda de tensão).
            </span>
          </span>
        </label>
      </div>
    </div>
  )
}
