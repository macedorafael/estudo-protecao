import React from 'react'
import { UseFormRegister, useFieldArray, Control } from 'react-hook-form'
import { StudyParameters } from '../../types'
import { Field } from '../ui/Field'

interface Props {
  register: UseFormRegister<StudyParameters>
  control: Control<StudyParameters>
}

const EMPTY_TRAFO = {
  potencia_kva: 0,
  impedancia_pct: 5,
  tipo: 'Óleo' as const,
  fator_inrush: 10,
  tempo_inrush_s: 0.1,
  tempo_ansi_s: 3,
  fusivel: '',
}

export function Transformadores({ register, control }: Props) {
  const { fields, append, remove } = useFieldArray({ control, name: 'transformadores' })

  return (
    <div className="section-card">
      <h2 className="section-title">
        <span className="text-lg">🔌</span> Transformadores
        <span className="ml-auto text-xs text-gray-400 font-normal">Adicione todos os transformadores da instalação</span>
      </h2>

      <div className="space-y-4">
        {fields.map((field, i) => (
          <div key={field.id} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-gray-700">Transformador T{i + 1}</span>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(i)}
                  className="text-xs text-red-500 hover:text-red-700 font-medium"
                >
                  Remover
                </button>
              )}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <Field
                label="Potência"
                unit="kVA"
                tooltip="Potência nominal do transformador. Usada para calcular In_trafo = kVA / (√3 × V). Consta na plaqueta de identificação."
              >
                <input className="field-input" type="number" min={0} step={1}
                  {...register(`transformadores.${i}.potencia_kva`, { required: true, valueAsNumber: true })}
                  placeholder="Ex: 500"
                />
              </Field>
              <Field
                label="Impedância Z%"
                unit="%"
                tooltip="Impedância percentual de curto-circuito. Consta na plaqueta do trafo. Usada para calcular o ponto ANSI: I_ANSI = In_trafo / (Z%/100)."
                hint="Típico: 4–6%"
              >
                <input className="field-input" type="number" min={0.1} max={20} step={0.01}
                  {...register(`transformadores.${i}.impedancia_pct`, { required: true, valueAsNumber: true })}
                />
              </Field>
              <Field label="Tipo" tooltip="Tipo de isolamento. Óleo (ONAN) ou seco (AN/AF). Ambos usam fator de inrush 10× neste estudo.">
                <select className="field-input" {...register(`transformadores.${i}.tipo`)}>
                  <option value="Óleo">Óleo</option>
                  <option value="Seco">Seco</option>
                </select>
              </Field>
              <Field
                label="Fator de Inrush"
                unit="× In"
                tooltip="Multiplicador da corrente de magnetização. Padrão: 10×. Resulta em I_inrush = 10 × In_trafo para o maior trafo + Σ dos demais."
                hint="Padrão: 10×"
              >
                <input className="field-input" type="number" min={5} max={15} step={0.5}
                  {...register(`transformadores.${i}.fator_inrush`, { valueAsNumber: true })}
                />
              </Field>
              <Field
                label="Duração do Inrush"
                unit="s"
                tooltip="Tempo de duração do inrush. Aparece como ponto no coordenograma. Padrão: 0,1 s."
                hint="Padrão: 0,1 s"
              >
                <input className="field-input" type="number" min={0.01} max={1} step={0.01}
                  {...register(`transformadores.${i}.tempo_inrush_s`, { valueAsNumber: true })}
                />
              </Field>
              <Field
                label="Tempo do Ponto ANSI"
                unit="s"
                tooltip="Tempo do ponto de dano do transformador (ponto ANSI). Geralmente 2 a 4 s conforme tabela do fabricante (C57.109). Aparece no coordenograma."
                hint="Típico: 2–4 s"
              >
                <input className="field-input" type="number" min={0.5} max={10} step={0.5}
                  {...register(`transformadores.${i}.tempo_ansi_s`, { valueAsNumber: true })}
                />
              </Field>
              <Field
                label="Fusível de MT"
                tooltip="Fusível de média tensão associado ao transformador. Conforme NDU 002 Anexo II. Ex: 10K, 40K, 1H, 12K."
                hint="Ex: 10K, 1H, 40K"
              >
                <input className="field-input"
                  {...register(`transformadores.${i}.fusivel`)}
                  placeholder="Ex: 10K"
                />
              </Field>
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        className="add-btn mt-4"
        onClick={() => append(EMPTY_TRAFO)}
      >
        + Adicionar Transformador
      </button>
    </div>
  )
}
