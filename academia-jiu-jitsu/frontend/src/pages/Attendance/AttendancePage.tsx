import { useState, useRef } from 'react'
import { Upload, CheckCircle, AlertCircle, Calendar } from 'lucide-react'
import { attendanceApi, studentsApi, SessionResult, Student } from '../../api/client'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default function AttendancePage() {
  const [result, setResult] = useState<SessionResult | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [identifyingFace, setIdentifyingFace] = useState<number | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFile(f: File) {
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError('')
  }

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setError('')
    try {
      const { data } = await attendanceApi.createSession(file, notes)
      setResult(data)
      if (data.unidentified.length > 0) {
        const { data: list } = await studentsApi.list()
        setStudents(list)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Erro ao processar foto')
    } finally {
      setLoading(false)
    }
  }

  async function handleIdentify(faceId: number, studentId: number) {
    if (!result) return
    await attendanceApi.identifyFace(result.session_id, faceId, studentId)
    setResult((prev) => prev ? {
      ...prev,
      unidentified: prev.unidentified.filter((f) => f.id !== faceId),
      recognized: [...prev.recognized, {
        student_id: studentId,
        student_name: students.find((s) => s.id === studentId)?.name ?? 'Aluno',
        confidence_score: undefined,
      }],
    } : prev)
    setIdentifyingFace(null)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Chamada por Foto</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload */}
        <div className="card space-y-4">
          <h2 className="font-semibold text-lg flex items-center gap-2"><Calendar size={18} /> Nova sessão</h2>

          <div
            className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-primary-500 transition-colors"
            onClick={() => inputRef.current?.click()}
          >
            {preview ? (
              <img src={preview} alt="treino" className="mx-auto max-h-64 object-cover rounded-lg" />
            ) : (
              <div className="text-gray-400 py-8">
                <Upload size={40} className="mx-auto mb-3" />
                <p className="font-medium">Clique para enviar a foto do treino</p>
                <p className="text-sm mt-1">JPG, PNG ou WEBP</p>
              </div>
            )}
          </div>
          <input ref={inputRef} type="file" accept="image/*" className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />

          <textarea
            className="input resize-none"
            placeholder="Observações (opcional)"
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          {error && <p className="text-red-600 text-sm">{error}</p>}

          <button className="btn-primary w-full" onClick={handleUpload} disabled={!file || loading}>
            {loading ? 'Processando reconhecimento facial...' : 'Registrar chamada'}
          </button>
        </div>

        {/* Resultado */}
        <div className="space-y-4">
          {result ? (
            <>
              <div className="card">
                <h2 className="font-semibold text-lg flex items-center gap-2 mb-4">
                  <CheckCircle size={18} className="text-green-500" />
                  Reconhecidos ({result.recognized.length})
                </h2>
                <ul className="space-y-2">
                  {result.recognized.map((r) => (
                    <li key={r.student_id} className="flex items-center justify-between text-sm">
                      <span className="font-medium">{r.student_name}</span>
                      {r.confidence_score && (
                        <span className="text-gray-400 text-xs">
                          {Math.round(r.confidence_score * 100)}% confiança
                        </span>
                      )}
                    </li>
                  ))}
                  {result.recognized.length === 0 && (
                    <p className="text-gray-400 text-sm">Nenhum aluno reconhecido</p>
                  )}
                </ul>
              </div>

              {result.unidentified.length > 0 && (
                <div className="card border-orange-200 bg-orange-50">
                  <h2 className="font-semibold text-lg flex items-center gap-2 mb-4 text-orange-700">
                    <AlertCircle size={18} />
                    Não identificados ({result.unidentified.length})
                  </h2>
                  <div className="grid grid-cols-2 gap-3">
                    {result.unidentified.map((face) => (
                      <div key={face.id} className="bg-white rounded-lg p-3 border">
                        <img
                          src={`/uploads/${face.face_image_path.split('/uploads/').pop()}`}
                          alt="face"
                          className="w-full h-24 object-cover rounded mb-2"
                        />
                        {identifyingFace === face.id ? (
                          <div>
                            <select
                              className="input text-xs mb-2"
                              onChange={(e) => e.target.value && handleIdentify(face.id, Number(e.target.value))}
                              defaultValue=""
                            >
                              <option value="" disabled>Selecione o aluno</option>
                              {students.map((s) => (
                                <option key={s.id} value={s.id}>{s.name}</option>
                              ))}
                            </select>
                            <button
                              className="text-xs text-gray-500 hover:text-gray-700"
                              onClick={() => setIdentifyingFace(null)}
                            >
                              Cancelar
                            </button>
                          </div>
                        ) : (
                          <button
                            className="text-xs text-primary-500 hover:underline"
                            onClick={() => setIdentifyingFace(face.id)}
                          >
                            Identificar aluno
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="card text-center text-gray-400 py-12">
              <Upload size={32} className="mx-auto mb-2 opacity-30" />
              <p>Os resultados aparecerão aqui após o upload</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
