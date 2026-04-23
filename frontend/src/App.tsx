import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { StudyParameters, DEFAULT_STUDY } from './types'
import { DadosEngenheiro } from './components/sections/DadosEngenheiro'
import { DadosCliente } from './components/sections/DadosCliente'
import { DadosConcessionaria } from './components/sections/DadosConcessionaria'
import { Transformadores } from './components/sections/Transformadores'
import { EquipamentosProtecao } from './components/sections/EquipamentosProtecao'
import { FuncoesANSI } from './components/sections/FuncoesANSI'

type Status = 'idle' | 'loading' | 'error'

export default function App() {
  const [status, setStatus] = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const { register, control, handleSubmit } = useForm<StudyParameters>({
    defaultValues: DEFAULT_STUDY,
  })

  async function onSubmit(data: StudyParameters) {
    setStatus('loading')
    setErrorMsg('')
    try {
      const res = await fetch('/api/gerar-estudo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
        throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))
      }

      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const cliente = data.cliente.razao_social.replace(/\s+/g, '_') || 'cliente'
      a.href = url
      a.download = `Estudo_Protecao_${cliente}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      setStatus('idle')
    } catch (e: unknown) {
      setStatus('error')
      setErrorMsg(e instanceof Error ? e.message : 'Erro ao gerar estudo.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-900 text-white py-4 px-6 shadow-md">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-2xl">⚡</span>
          <div>
            <h1 className="text-lg font-bold leading-tight">
              Gerador de Estudos de Proteção e Seletividade
            </h1>
            <p className="text-xs text-blue-200">
              Média Tensão · ABNT NBR 14039 · NDU 002 ENERGISA
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto py-8 px-4">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <DadosEngenheiro register={register} />
          <DadosCliente register={register} />
          <DadosConcessionaria register={register} />
          <Transformadores register={register} control={control} />
          <EquipamentosProtecao register={register} control={control} />
          <FuncoesANSI register={register} />

          {/* Erro */}
          {status === 'error' && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              <strong>Erro ao gerar o estudo:</strong> {errorMsg}
            </div>
          )}

          {/* Botão */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={status === 'loading'}
              className="btn-primary text-base px-8 py-3"
            >
              {status === 'loading' ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Gerando PDF...
                </>
              ) : (
                <>
                  <span>📄</span> Gerar Estudo em PDF
                </>
              )}
            </button>
          </div>
        </form>
      </main>

      <footer className="text-center text-xs text-gray-400 py-6">
        Gerador de Estudos de Proteção · ABNT NBR 14039:2005 · NDU 002 ENERGISA
      </footer>
    </div>
  )
}
