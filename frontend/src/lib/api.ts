import axios from 'axios'

//const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const API_BASE_URL = 'https://creative-analysis-backend.onrender.com/api';
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Types
export interface Experiment {
  id: string
  title: string
  description?: string
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed'
  error_message?: string
  video_url?: string
  video_id?: string
  summary?: {
    overall_favorability?: number
    overall_intent?: number
    overall_associations?: number
    recommendation_count: number
    top_segment?: string
    weak_segment?: string
  }
  created_at: string
  updated_at: string
  completed_at?: string
  user_id: string
}

export interface Recommendation {
  id: string
  experiment_id: string
  segment: string
  breakdown?: string
  brand_goal: string
  type: 'add' | 'change' | 'remove'
  priority: 'high' | 'medium' | 'low'
  creative_element: string
  justification: string
  quantitative_support?: {
    metric: string
    delta: number
    ci_95: [number, number]
    baseline_mean?: number
    test_group_mean?: number
    statistical_significance: boolean
  }
  qualitative_support?: Array<{
    comment: string
    theme?: string
    sentiment?: string
  }>
  scene_reference?: {
    scene_id: string
    start_time: number
    end_time: number
    description?: string
  }
  impact_score?: number
  confidence_score?: number
  rank?: number
}

export interface AnalysisStatus {
  status: string
  progress: Record<string, string>
  estimated_completion?: string
  error_message?: string
}

// API Functions
export const experimentApi = {
  list: async (page = 1, limit = 20) => {
    const response = await api.get('/experiments', { params: { page, limit } })
    return response.data
  },

  get: async (id: string) => {
    const response = await api.get(`/experiments/${id}`)
    return response.data
  },

  create: async (formData: FormData) => {
    const response = await api.post('/experiments', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  delete: async (id: string) => {
    await api.delete(`/experiments/${id}`)
  },

  triggerAnalysis: async (id: string) => {
    const response = await api.post(`/analysis/${id}/analyze`)
    return response.data
  },

  getStatus: async (id: string): Promise<AnalysisStatus> => {
    const response = await api.get(`/analysis/${id}/status`)
    return response.data
  },

  getRecommendations: async (
    id: string,
    filters?: {
      segment?: string
      brand_goal?: string
      type?: string
      priority?: string
    }
  ) => {
    const response = await api.get(`/recommendations/${id}`, { params: filters })
    return response.data
  },

  exportJson: async (id: string) => {
    const response = await api.get(`/export/${id}/json`)
    return response.data
  },

  exportPdf: async (id: string) => {
    const response = await api.get(`/export/${id}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },
}
