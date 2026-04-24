import { useEffect, useState } from 'react'
import { Plus, Search, Camera } from 'lucide-react'
import { studentsApi, Student, Belt } from '../../api/client'
import StudentForm from './StudentForm'
import StudentPhotoModal from './StudentPhotoModal'

const BELT_COLORS: Record<Belt, string> = {
  white: 'bg-gray-100 text-gray-800',
  grey: 'bg-gray-300 text-gray-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  orange: 'bg-orange-100 text-orange-800',
  green: 'bg-green-100 text-green-800',
  blue: 'bg-blue-100 text-blue-800',
  purple: 'bg-purple-100 text-purple-800',
  brown: 'bg-amber-100 text-amber-800',
  black: 'bg-gray-800 text-white',
}
const BELT_LABELS: Record<Belt, string> = {
  white: 'Branca', grey: 'Cinza', yellow: 'Amarela', orange: 'Laranja',
  green: 'Verde', blue: 'Azul', purple: 'Roxa', brown: 'Marrom', black: 'Preta',
}

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editStudent, setEditStudent] = useState<Student | null>(null)
  const [photoStudent, setPhotoStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)

  function load() {
    studentsApi.list().then((r) => setStudents(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const filtered = students.filter((s) =>
    s.name.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Alunos</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => { setEditStudent(null); setShowForm(true) }}>
          <Plus size={18} /> Novo aluno
        </button>
      </div>

      <div className="card mb-6">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Buscar aluno..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500">Carregando...</p>
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                {['Aluno', 'Faixa', 'Grau', 'Matrícula', 'Telefone', 'Foto', ''].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{s.name}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${BELT_COLORS[s.belt]}`}>{BELT_LABELS[s.belt]}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{s.degree}ª</td>
                  <td className="px-4 py-3 text-gray-500">{s.enrollment_date}</td>
                  <td className="px-4 py-3 text-gray-500">{s.phone || '—'}</td>
                  <td className="px-4 py-3">
                    {s.photo_path ? (
                      <span className="text-green-600 text-xs font-medium">✓ Cadastrada</span>
                    ) : (
                      <span className="text-orange-500 text-xs">Sem foto</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        className="text-xs text-blue-600 hover:underline"
                        onClick={() => { setEditStudent(s); setShowForm(true) }}
                      >
                        Editar
                      </button>
                      <button
                        className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                        onClick={() => setPhotoStudent(s)}
                      >
                        <Camera size={12} /> Foto
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Nenhum aluno encontrado</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <StudentForm
          student={editStudent}
          onClose={() => setShowForm(false)}
          onSaved={() => { setShowForm(false); load() }}
        />
      )}
      {photoStudent && (
        <StudentPhotoModal
          student={photoStudent}
          onClose={() => setPhotoStudent(null)}
          onSaved={() => { setPhotoStudent(null); load() }}
        />
      )}
    </div>
  )
}
