import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

// API接口
export const chatAPI = {
  // 发送消息（非流式）
  sendMessage: (data: { message: string; user_id: number; session_id?: string }) => {
    return api.post('/chat', data)
  },
  // 发送消息（流式）
  sendMessageStream: async (
    data: { message: string; user_id: number; session_id?: string },
    onMessage: (chunk: any) => void,
    onError?: (error: any) => void
  ) => {
    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Stream request failed')
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              onMessage(data)
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error)
      if (onError) {
        onError(error)
      }
    }
  },
  // 获取历史
  getHistory: (userId: number, sessionId?: string) => {
    return api.get(`/chat/history/${userId}`, { params: { session_id: sessionId } })
  },
  // 清除历史
  clearHistory: (userId: number, sessionId?: string) => {
    return api.delete(`/chat/history/${userId}`, { params: { session_id: sessionId } })
  },
  // 获取会话列表
  getSessions: (userId: number) => {
    return api.get(`/chat/sessions/${userId}`)
  }
}

export const healthAPI = {
  // 添加血糖数据
  addBloodGlucose: (data: any) => {
    return api.post('/health/blood-glucose', data)
  },
  // 获取血糖数据
  getBloodGlucose: (userId: number, limit = 10) => {
    return api.get(`/health/blood-glucose/${userId}`, { params: { limit } })
  },
  // 添加血压数据
  addBloodPressure: (data: any) => {
    return api.post('/health/blood-pressure', data)
  },
  // 获取血压数据
  getBloodPressure: (userId: number, limit = 10) => {
    return api.get(`/health/blood-pressure/${userId}`, { params: { limit } })
  },
  // 添加体重数据
  addWeight: (data: any) => {
    return api.post('/health/weight', data)
  }
}

export const userAPI = {
  // 创建用户
  createUser: (data: any) => {
    return api.post('/user', data)
  },
  // 获取用户信息
  getUser: (userId: number) => {
    return api.get(`/user/${userId}`)
  },
  // 获取用户列表
  listUsers: () => {
    return api.get('/user')
  }
}

export default api
