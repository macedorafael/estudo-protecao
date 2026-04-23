import React from 'react'
import { UseFormRegister } from 'react-hook-form'
import { StudyParameters } from '../../types'
import { Field } from '../ui/Field'

interface Props { register: UseFormRegister<StudyParameters> }

export function DadosCliente({ register }: Props) {
  return (
    <div className="section-card">
      <h2 className="section-title">
        <span className="text-lg">🏭</span> Dados do Cliente
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Razão Social" tooltip="Nome completo da empresa conforme CNPJ. Aparece no cabeçalho do estudo.">
          <input className="field-input" {...register('cliente.razao_social', { required: true })} placeholder="Ex: ASK Industria e Comercio Mercadorias" />
        </Field>
        <Field label="CNPJ" tooltip="Identificação fiscal do consumidor. Formato: 00.000.000/0000-00.">
          <input className="field-input" {...register('cliente.cnpj')} placeholder="00.000.000/0000-00" />
        </Field>
        <Field label="Endereço" tooltip="Logradouro, número, cidade e estado do ponto de instalação." hint="Ex: Av. das Américas, 1328, Aparecida do Taboado - MS">
          <input className="field-input" {...register('cliente.endereco')} placeholder="Rua, nº, Cidade - Estado" />
        </Field>
        <Field label="UC (Unidade Consumidora)" tooltip="Código da Unidade Consumidora fornecido pela concessionária. Ex: 1870160." energisa>
          <input className="field-input field-input-energisa" {...register('cliente.uc')} placeholder="Ex: 1870160" />
        </Field>
        <Field
          label="Demanda Prevista"
          unit="kVA"
          tooltip="Demanda total contratada ou prevista. Base para o cálculo da corrente de demanda In = S / (√3 × V). NBR 14039:2005 §8."
          link="https://www.normas.com.br/visualizar/abnt-nbr-nm/14039"
          linkLabel="ABNT NBR 14039"
        >
          <input className="field-input" type="number" min={0} step={1} {...register('cliente.demanda_kva', { required: true, valueAsNumber: true })} placeholder="Ex: 1000" />
        </Field>
        <Field
          label="Fator de Potência"
          tooltip="Fator de potência de referência para cálculo de corrente. Padrão ENERGISA NDU 002: 0,92."
          hint="Padrão: 0,92"
        >
          <input className="field-input" type="number" min={0.5} max={1} step={0.01} {...register('cliente.fator_potencia', { required: true, valueAsNumber: true })} />
        </Field>
      </div>
    </div>
  )
}
