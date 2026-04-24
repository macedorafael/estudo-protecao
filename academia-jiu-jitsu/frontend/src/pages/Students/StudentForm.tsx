import { useForm } from 'react-hook-form'
import { studentsApi, Student, Belt } from '../../api/client'
import { X } from 'lucide-react'

const BELTS: Belt[] = ['white', 'grey', 'yellow', 'orange', 'green', 'blue', 'purple', 'brown', 'black']
const BELT_LABELS: Record<Belt, string> = {
  white: 'Branca', grey: 'Cinza', yellow: 'Amarela', orange: 'Laranja',
  green: 'Verde', blue: 'Azul', purple: 'Roxa', brown: 'Marrom', black: 'Preta',
}

interface FormData {
  name: string; belt: Belt; degree: number
  birth_date: string; phone: string; enrollment_date: string
}

export default function StudentForm({
  student, onClose, onSaved,
}: { student: Student | null; onClose: () => void; onSaved: () => void }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    defaultValues: {
      name: student?.name ?? '',
      belt: student?.belt ?? 'white',
      degree: student?.degree ?? 0,
      birth_date: student?.birth_date ?? '',
      phone: student?.phone ?? '',
      enrollment_date: student?.enrollment_date ?? new Date().toISOString().split('T')[0],
    },
  })

  async function onSubmit(data: FormData) {
    try {
      if (student) {
        await studentsApi.update(student.id, data)
      } else {
        await studentsApi.create(data)
      }
      onSaved()
    } catch (err: any) {
      alert(err.response?.data?.detail ?? 'Erro ao salvar')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-xl">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold">{student ? 'Editar aluno' : 'Novo aluno'}</h2>
          <button onClick={onClose}><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nome completo *</label>
            <input className="input" {...register('name', { required: true })} />
            {errors.name && <p className="text-red-500 text-xs mt-1">Obrigatório</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Faixa</label>
              <select className="input" {...register('belt')}>
                {BELTS.map((b) => <option key={b} value={b}>{BELT_LABELS[b]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Grau (0-4)</label>
              <input type="number" min={0} max={4} className="input" {...register('degree', { min: 0, max: 4 })} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Data de nascimento</label>
              <input type="date" className="input" {...register('birth_date')} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Data de matrícula</label>
              <input type="date" className="input" {...register('enrollment_date')} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Telefone / WhatsApp</label>
            <input className="input" placeholder="(11) 99999-9999" {...register('phone')} />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" className="btn-secondary flex-1" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary flex-1" disabled={isSubmitting}>
              {isSubmitting ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
