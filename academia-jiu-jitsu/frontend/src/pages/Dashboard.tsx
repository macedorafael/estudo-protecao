import { useEffect, useState } from 'react'
import { Users, Camera, Award, DollarSign } from 'lucide-react'
import { studentsApi, attendanceApi, feesApi } from '../api/client'
import { useAuth } from '../contexts/AuthContext'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface Stats { students: number; sessions: number; overdue: number }

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<Stats>({ students: 0, sessions: 0, overdue: 0 })
  const today = format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })

  useEffect(() => {
    Promise.all([
      studentsApi.list(),
      attendanceApi.listSessions(),
      user?.role === 'admin' ? feesApi.listPayments({ status: 'overdue' }) : Promise.resolve({ data: [] }),
    ]).then(([s, sess, pay]) => {
      setStats({
        students: s.data.length,
        sessions: sess.data.length,
        overdue: (pay as any).data.length,
      })
    }).catch(() => {})
  }, [user])

  const cards = [
    { label: 'Alunos ativos', value: stats.students, icon: Users, color: 'bg-blue-500' },
    { label: 'Sessões de treino', value: stats.sessions, icon: Camera, color: 'bg-green-500' },
    ...(user?.role === 'admin'
      ? [{ label: 'Inadimplentes', value: stats.overdue, icon: DollarSign, color: 'bg-red-500' }]
      : []),
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Olá, {user?.name?.split(' ')[0]} 👋</h1>
        <p className="text-gray-500 capitalize mt-1">{today}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card flex items-center gap-4">
            <div className={`${color} rounded-xl p-3 text-white`}>
              <Icon size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">{label}</p>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-2">Acesso rápido</h2>
        <p className="text-gray-500 text-sm">Use o menu lateral para navegar pelo sistema.</p>
      </div>
    </div>
  )
}
