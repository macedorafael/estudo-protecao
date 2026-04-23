import React from 'react'
import { UseFormRegister } from 'react-hook-form'
import { StudyParameters } from '../../types'
import { Field } from '../ui/Field'

interface Props { register: UseFormRegister<StudyParameters> }

export function DadosEngenheiro({ register }: Props) {
  return (
    <div className="section-card">
      <h2 className="section-title">
        <span className="text-lg">📋</span> Engenheiro Responsável
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Nome completo" tooltip="Nome do engenheiro que assina o estudo. Aparece na capa e na assinatura do relatório PDF.">
          <input className="field-input" {...register('engenheiro.nome', { required: true })} placeholder="Ex: Flávio de Jesus Saletti" />
        </Field>
        <Field label="CREA" tooltip="Número de registro no Conselho Regional de Engenharia e Agronomia. Ex: 5062320435D.">
          <input className="field-input" {...register('engenheiro.crea', { required: true })} placeholder="Ex: 5062320435D" />
        </Field>
      </div>
    </div>
  )
}
