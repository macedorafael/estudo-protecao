import React from 'react'
import { UseFormRegister } from 'react-hook-form'
import { StudyParameters, CurvaIEC } from '../../types'
import { Field } from '../ui/Field'

const CURVAS: CurvaIEC[] = ['IEC VI', 'IEC EI', 'IEC MI', 'IEC LI']
const CURVA_LABELS: Record<CurvaIEC, string> = {
  'IEC VI': 'IEC VI — Very Inverse (K=13,5)',
  'IEC EI': 'IEC EI — Extremely Inverse (K=80)',
  'IEC MI': 'IEC MI — Moderately Inverse (K=0,14)',
  'IEC LI': 'IEC LI — Long-Time Inverse (K=120)',
}

interface Props { register: UseFormRegister<StudyParameters> }

export function DadosConcessionaria({ register }: Props) {
  return (
    <div className="section-card border-blue-200">
      <h2 className="section-title text-energisa">
        <span className="text-lg">⚡</span> Dados da Concessionária
        <span className="energisa-badge ml-2">ENERGISA</span>
      </h2>
      <p className="text-xs text-energisa bg-energisa-light border border-blue-200 rounded-md px-3 py-2 mb-4">
        Todos os campos desta seção devem ser preenchidos com os valores do documento <b>ATA / NCC</b> recebido da ENERGISA.
        Os dados são válidos por 1 ano sem alteração de circuito.
      </p>

      {/* Dados gerais */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Field
          label="Tensão de Fornecimento"
          unit="kV"
          energisa
          tooltip="Tensão primária do ponto de entrega (ex: 13,8 kV ou 34,5 kV). Informada no documento ATA/NCC. NBR 14039 §4."
        >
          <select className="field-input field-input-energisa" {...register('concessionaria.tensao_kv', { valueAsNumber: true })}>
            <option value={13.8}>13,8 kV</option>
            <option value={34.5}>34,5 kV</option>
          </select>
        </Field>
        <Field label="Subestação" energisa tooltip="Nome da subestação de origem. Consta no documento ATA. Ex: Aparecida do Taboado.">
          <input className="field-input field-input-energisa" {...register('concessionaria.subestacao')} placeholder="Ex: Aparecida do Taboado" />
        </Field>
        <Field label="Circuito / Alimentador" energisa tooltip="Identificação do circuito de alimentação. Ex: ATA52, PAR04. Consta no ATA.">
          <input className="field-input field-input-energisa" {...register('concessionaria.circuito')} placeholder="Ex: ATA52" />
        </Field>
      </div>

      {/* Curto-circuito */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Correntes de Curto-Circuito</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <Field
          label="ICC Trifásico Simétrico"
          unit="A"
          energisa
          tooltip="Corrente de curto-circuito trifásico no ponto de conexão. Informada no ATA. Usada para verificar saturação do TC e calcular o time-dial."
        >
          <input className="field-input field-input-energisa" type="number" min={0} step={0.01} {...register('concessionaria.icc_3f_a', { required: true, valueAsNumber: true })} placeholder="Ex: 1049" />
        </Field>
        <Field
          label="Ângulo ICC Trifásico"
          unit="°"
          energisa
          tooltip="Ângulo da impedância equivalente para o curto trifásico. Usado para calcular corrente assimétrica. Ex: -70°."
        >
          <input className="field-input field-input-energisa" type="number" step={0.01} {...register('concessionaria.angulo_3f_grau', { valueAsNumber: true })} />
        </Field>
        <Field
          label="ICC Fase-Terra Simétrico"
          unit="A"
          energisa
          tooltip="Corrente de curto-circuito fase-terra. Informada no ATA. Usada para verificar a proteção de neutro 51N."
        >
          <input className="field-input field-input-energisa" type="number" min={0} step={0.01} {...register('concessionaria.icc_ft_a', { required: true, valueAsNumber: true })} placeholder="Ex: 851" />
        </Field>
        <Field
          label="Ângulo ICC Fase-Terra"
          unit="°"
          energisa
          tooltip="Ângulo da impedância para curto fase-terra assimétrico. Informado no ATA."
        >
          <input className="field-input field-input-energisa" type="number" step={0.01} {...register('concessionaria.angulo_ft_grau', { valueAsNumber: true })} />
        </Field>
      </div>

      {/* Impedâncias */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Impedância Equivalente da Rede (base 100 MVA)</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <Field label="R1 (seq. positiva)" unit="pu" energisa tooltip="Resistência de sequência positiva da rede. Base 100 MVA. Informada no ATA.">
          <input className="field-input field-input-energisa" type="number" step={0.0001} {...register('concessionaria.r1_pu', { valueAsNumber: true })} placeholder="Ex: 0.5543" />
        </Field>
        <Field label="X1 (seq. positiva)" unit="pu" energisa tooltip="Reatância de sequência positiva. Base 100 MVA. Informada no ATA.">
          <input className="field-input field-input-energisa" type="number" step={0.0001} {...register('concessionaria.x1_pu', { valueAsNumber: true })} placeholder="Ex: 1.4959" />
        </Field>
        <Field label="R0 (seq. zero)" unit="pu" energisa tooltip="Resistência de sequência zero da rede. Necessária para calcular ICC fase-terra. Informada no ATA.">
          <input className="field-input field-input-energisa" type="number" step={0.0001} {...register('concessionaria.r0_pu', { valueAsNumber: true })} placeholder="Ex: 0.6319" />
        </Field>
        <Field label="X0 (seq. zero)" unit="pu" energisa tooltip="Reatância de sequência zero. Necessária para calcular ICC fase-terra. Informada no ATA.">
          <input className="field-input field-input-energisa" type="number" step={0.0001} {...register('concessionaria.x0_pu', { valueAsNumber: true })} placeholder="Ex: 2.6459" />
        </Field>
      </div>

      {/* Religador upstream */}
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Religador / Relé da Concessionária (a montante)
        <span className="energisa-badge ml-2">ENERGISA</span>
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Estes ajustes vêm do ATA. O relé do consumidor será coordenado com ≥ 0,3 s de margem em relação a estes valores.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Modelo do religador" energisa tooltip="Identificação do relé da concessionária a montante. Ex: NOJA OSM-38 (595-06), Cooper F6 (495-08).">
          <input className="field-input field-input-energisa" {...register('concessionaria.religador_upstream.modelo')} placeholder="Ex: NOJA OSM-38 (595-06)" />
        </Field>
        <div /> {/* spacer */}

        {/* Fase 51F */}
        <div className="sm:col-span-2">
          <p className="text-xs font-semibold text-gray-600 mb-2">Proteção de Fase — 51F / 50F</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Field label="Pickup 51F" unit="A" energisa tooltip="Corrente de pickup do relé de fase da concessionária. Informada no ATA. Ex: 150 A.">
              <input className="field-input field-input-energisa" type="number" min={0} step={0.1} {...register('concessionaria.religador_upstream.pickup_fase_a', { required: true, valueAsNumber: true })} placeholder="Ex: 150" />
            </Field>
            <Field label="Dial 51F" energisa tooltip="Time Dial do relé de fase da concessionária. Ex: 0,20. O relé do consumidor será ajustado 0,3 s abaixo.">
              <input className="field-input field-input-energisa" type="number" min={0} step={0.01} {...register('concessionaria.religador_upstream.dial_fase', { required: true, valueAsNumber: true })} />
            </Field>
            <Field label="Curva 51F" energisa tooltip="Curva de operação temporizada do relé de fase. Padrão ENERGISA: IEC VI (Very Inverse).">
              <select className="field-input field-input-energisa" {...register('concessionaria.religador_upstream.curva_fase')}>
                {CURVAS.map(c => <option key={c} value={c}>{CURVA_LABELS[c]}</option>)}
              </select>
            </Field>
            <Field label="Inst. 50F" unit="A" energisa tooltip="Corrente instantânea de fase do religador da concessionária. Ex: 690 A.">
              <input className="field-input field-input-energisa" type="number" min={0} step={1} {...register('concessionaria.religador_upstream.inst_fase_a', { required: true, valueAsNumber: true })} placeholder="Ex: 690" />
            </Field>
          </div>
        </div>

        {/* Neutro 51N */}
        <div className="sm:col-span-2">
          <p className="text-xs font-semibold text-gray-600 mb-2">Proteção de Neutro — 51N / 50N</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Field label="Pickup 51N" unit="A" energisa tooltip="Corrente de pickup do relé de neutro da concessionária. Informada no ATA. Ex: 35 A.">
              <input className="field-input field-input-energisa" type="number" min={0} step={0.1} {...register('concessionaria.religador_upstream.pickup_neutro_a', { required: true, valueAsNumber: true })} placeholder="Ex: 35" />
            </Field>
            <Field label="Dial 51N" energisa tooltip="Time Dial do relé de neutro da concessionária. Ex: 0,86.">
              <input className="field-input field-input-energisa" type="number" min={0} step={0.01} {...register('concessionaria.religador_upstream.dial_neutro', { required: true, valueAsNumber: true })} />
            </Field>
            <Field label="Curva 51N" energisa tooltip="Curva do relé de neutro da concessionária. Padrão ENERGISA: IEC VI.">
              <select className="field-input field-input-energisa" {...register('concessionaria.religador_upstream.curva_neutro')}>
                {CURVAS.map(c => <option key={c} value={c}>{CURVA_LABELS[c]}</option>)}
              </select>
            </Field>
            <Field label="Inst. 50N" unit="A" energisa tooltip="Corrente instantânea de neutro. Deixe 0 se bloqueado (Bloq.) conforme indicado no ATA.">
              <input className="field-input field-input-energisa" type="number" min={0} step={1} {...register('concessionaria.religador_upstream.inst_neutro_a', { valueAsNumber: true })} placeholder="0 = Bloqueado" />
            </Field>
          </div>
        </div>
      </div>
    </div>
  )
}
