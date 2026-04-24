import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api

// ── Types ──────────────────────────────────────────────────────────────────

export type Role = 'admin' | 'professor' | 'aluno'
export type Belt = 'white' | 'grey' | 'yellow' | 'orange' | 'green' | 'blue' | 'purple' | 'brown' | 'black'
export type FeeStatus = 'pending' | 'paid' | 'overdue'

export interface User {
  id: number; name: string; email: string; role: Role; active: boolean; created_at: string
}
export interface Student {
  id: number; name: string; belt: Belt; degree: number
  enrollment_date: string; birth_date?: string; phone?: string
  photo_path?: string; active: boolean; created_at: string
  attendance_count?: number; belt_history?: BeltHistory[]
}
export interface BeltHistory {
  id: number; belt: Belt; degree: number; awarded_date: string; notes?: string; professor_id: number
}
export interface AttendanceResult {
  student_id: number; student_name: string; confidence_score?: number
}
export interface UnidentifiedFace {
  id: number; face_image_path: string
}
export interface SessionResult {
  session_id: number; date: string
  recognized: AttendanceResult[]; unidentified: UnidentifiedFace[]
}
export interface Session {
  id: number; professor_id: number; date: string; notes?: string
  created_at: string; attendance_count: number
}
export interface FeePlan {
  id: number; student_id: number; amount: number; due_day: number
  payment_method?: string; active: boolean; created_at: string
}
export interface Payment {
  id: number; fee_plan_id: number; student_id: number
  month_reference: string; amount_paid?: number
  payment_date?: string; status: FeeStatus
}

// ── API helpers ────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.postForm<{ access_token: string }>('/auth/login', { username: email, password }),
  me: () => api.get<User>('/auth/me'),
  register: (data: { name: string; email: string; password: string; role: Role }) =>
    api.post<User>('/auth/register', data),
}

export const studentsApi = {
  list: (active = true) => api.get<Student[]>('/students', { params: { active } }),
  get: (id: number) => api.get<Student>(`/students/${id}`),
  create: (data: Partial<Student>) => api.post<Student>('/students', data),
  update: (id: number, data: Partial<Student>) => api.put<Student>(`/students/${id}`, data),
  deactivate: (id: number) => api.delete(`/students/${id}`),
  uploadPhoto: (id: number, file: File) => {
    const form = new FormData(); form.append('file', file)
    return api.post<Student>(`/students/${id}/photo`, form)
  },
}

export const attendanceApi = {
  createSession: (file: File, notes?: string, date?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (notes) form.append('notes', notes)
    if (date) form.append('session_date', date)
    return api.post<SessionResult>('/sessions', form)
  },
  listSessions: () => api.get<Session[]>('/sessions'),
  getSession: (id: number) => api.get<SessionResult>(`/sessions/${id}`),
  identifyFace: (sessionId: number, faceId: number, studentId: number) =>
    api.post(`/sessions/${sessionId}/identify`, { face_id: faceId, student_id: studentId }),
}

export const beltsApi = {
  history: (studentId: number) => api.get<BeltHistory[]>(`/students/${studentId}/belts`),
  promote: (studentId: number, data: { belt: Belt; degree: number; notes?: string; awarded_date?: string }) =>
    api.post<BeltHistory>(`/students/${studentId}/belts`, data),
}

export const feesApi = {
  getPlans: (studentId: number) => api.get<FeePlan[]>(`/students/${studentId}/fee-plan`),
  createPlan: (studentId: number, data: { amount: number; due_day: number; payment_method?: string }) =>
    api.post<FeePlan>(`/students/${studentId}/fee-plan`, data),
  listPayments: (params?: { month?: string; status?: string }) => api.get<Payment[]>('/payments', { params }),
  studentPayments: (studentId: number) => api.get<Payment[]>(`/students/${studentId}/payments`),
  registerPayment: (data: {
    fee_plan_id: number; student_id: number; month_reference: string
    amount_paid: number; payment_date?: string
  }) => api.post<Payment>('/payments', data),
}
