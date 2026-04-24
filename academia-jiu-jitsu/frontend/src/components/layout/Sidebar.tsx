import { NavLink } from 'react-router-dom'
import { Users, Camera, Award, DollarSign, LayoutDashboard, LogOut } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', roles: ['admin', 'professor', 'aluno'] },
  { to: '/students', icon: Users, label: 'Alunos', roles: ['admin', 'professor'] },
  { to: '/attendance', icon: Camera, label: 'Chamada', roles: ['admin', 'professor'] },
  { to: '/belts', icon: Award, label: 'Faixas', roles: ['admin', 'professor'] },
  { to: '/fees', icon: DollarSign, label: 'Mensalidades', roles: ['admin'] },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col min-h-screen">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-lg font-bold text-white">🥋 Academia</h1>
        <p className="text-xs text-gray-400 mt-1">Jiu-Jitsu</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {nav
          .filter((item) => user && item.roles.includes(user.role))
          .map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-500 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
      </nav>

      <div className="p-4 border-t border-gray-700">
        <div className="text-sm text-gray-400 truncate mb-3">{user?.name}</div>
        <button
          onClick={logout}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <LogOut size={16} /> Sair
        </button>
      </div>
    </aside>
  )
}
