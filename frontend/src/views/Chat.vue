<template>
  <div class="chat-container">
    <!-- 会话列表 -->
    <el-card class="sessions-card">
      <template #header>
        <div class="sessions-header">
          <span>历史会话</span>
          <el-button size="small" type="primary" @click="createNewSession">
            新建对话
          </el-button>
        </div>
      </template>
      <div class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.session_id"
          :class="['session-item', { active: session.session_id === sessionId }]"
          @click="switchSession(session.session_id)"
        >
          <div class="session-title">{{ session.title }}</div>
          <div class="session-info">
            <span class="session-time">{{ formatTime(session.last_message_time) }}</span>
            <span class="session-count">{{ session.message_count }}条</span>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="empty-sessions">
          暂无历史会话
        </div>
      </div>
    </el-card>
    
    <!-- 聊天区域 -->
    <el-card class="chat-card">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon :size="64" color="#909399"><ChatDotRound /></el-icon>
          <p>您好！我是您的慢病管理AI助手</p>
          <p class="tips">我可以帮您：</p>
          <ul class="tips-list">
            <li>📊 分析健康数据趋势</li>
            <li>💊 提供用药和饮食建议</li>
            <li>⏰ 设置健康提醒</li>
            <li>📖 解答慢病相关问题</li>
          </ul>
        </div>
        
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'" :size="24"><User /></el-icon>
            <el-icon v-else :size="24"><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            
            <!-- 显示工具调用 -->
            <div v-if="msg.tool_calls && msg.tool_calls.length > 0" class="tool-calls">
              <el-collapse accordion>
                <el-collapse-item title="🔧 工具调用详情" name="1">
                  <div v-for="(tool, idx) in msg.tool_calls" :key="idx" class="tool-call">
                    <el-tag size="small" type="info">{{ tool.tool }}</el-tag>
                    <span class="tool-output">{{ tool.output }}</span>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>
        
        <!-- 加载中 -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <el-icon :size="24"><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入框 -->
      <div class="input-container">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题，例如：我今天测的血糖是8.5，正常吗？"
          @keydown.enter.prevent="handleSend"
          :disabled="loading"
        />
        <div class="input-actions">
          <el-button @click="handleClear" :disabled="loading">清空对话</el-button>
          <el-button type="primary" @click="handleSend" :loading="loading">
            发送 (Enter)
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 快捷操作 -->
    <el-card class="quick-actions">
      <template #header>
        <span>快捷操作</span>
      </template>
      <el-space direction="vertical" :fill="true">
        <el-button @click="quickAsk('查询我最近的血糖数据')" plain>
          📊 查看血糖趋势
        </el-button>
        <el-button @click="quickAsk('分析我最近的血压情况')" plain>
          💓 分析血压情况
        </el-button>
        <el-button @click="quickAsk('给我一些饮食建议')" plain>
          🍎 饮食建议
        </el-button>
        <el-button @click="quickAsk('设置明天早上7点的血糖测量提醒')" plain>
          ⏰ 设置提醒
        </el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, User } from '@element-plus/icons-vue'
import { chatAPI } from '@/api'
import dayjs from 'dayjs'

interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
  tool_calls?: any[]
}

interface Session {
  session_id: string
  title: string
  last_message_time: string
  message_count: number
}

const messages = ref<Message[]>([])
const sessions = ref<Session[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()
const userId = ref(1) // 默认用户ID，实际应该从登录状态获取

// 从localStorage获取或创建session_id
const getSessionId = () => {
  const stored = localStorage.getItem(`chat_session_${userId.value}`)
  if (stored) {
    return stored
  }
  const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  localStorage.setItem(`chat_session_${userId.value}`, newSessionId)
  return newSessionId
}

const sessionId = ref<string>(getSessionId())

// 格式化消息内容
const formatMessage = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/(\d+\.\s)/g, '<br>$1')
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 发送消息（流式）
const handleSend = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  const userMessage = inputMessage.value.trim()
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    time: dayjs().format('HH:mm')
  })
  
  inputMessage.value = ''
  scrollToBottom()
  loading.value = true
  
  // 创建AI消息占位符
  const aiMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    time: dayjs().format('HH:mm'),
    tool_calls: []
  })
  
  try {
    let currentToolCalls: any[] = []
    
    await chatAPI.sendMessageStream(
      {
        message: userMessage,
        user_id: userId.value,
        session_id: sessionId.value
      },
      (chunk) => {
        const aiMessage = messages.value[aiMessageIndex]
        
        switch (chunk.type) {
          case 'start':
            // 保存session_id
            if (chunk.session_id) {
              sessionId.value = chunk.session_id
            }
            break
            
          case 'tool':
            // 工具调用
            currentToolCalls.push(chunk.data)
            aiMessage.tool_calls = [...currentToolCalls]
            break
            
          case 'content':
            // 流式内容
            aiMessage.content += chunk.data
            scrollToBottom()
            break
            
          case 'done':
            // 完成
            loading.value = false
            loadSessions()
            break
            
          case 'error':
            // 错误
            aiMessage.content = chunk.message
            loading.value = false
            ElMessage.error('AI响应出错')
            break
        }
      },
      () => {
        loading.value = false
        ElMessage.error('发送失败，请重试')
      }
    )
  } catch (error) {
    loading.value = false
    ElMessage.error('发送失败，请重试')
  }
}

// 快捷提问
const quickAsk = (question: string) => {
  inputMessage.value = question
  handleSend()
}

// 清空对话
const handleClear = async () => {
  try {
    await chatAPI.clearHistory(userId.value, sessionId.value)
    messages.value = []
    // 清除localStorage中的session_id
    localStorage.removeItem(`chat_session_${userId.value}`)
    // 创建新的session_id
    sessionId.value = getSessionId()
    ElMessage.success('对话已清空')
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const response: any = await chatAPI.getSessions(userId.value)
    sessions.value = response.sessions || []
  } catch (error) {
    console.error('加载会话列表失败', error)
  }
}

// 加载历史对话
const loadHistory = async () => {
  try {
    const response: any = await chatAPI.getHistory(userId.value, sessionId.value)
    if (response.history && response.history.length > 0) {
      messages.value = response.history.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        time: dayjs(msg.created_at || new Date()).format('HH:mm'),
        tool_calls: msg.tool_calls
      }))
      scrollToBottom()
    } else {
      messages.value = []
    }
  } catch (error) {
    console.error('加载历史失败', error)
  }
}

// 切换会话
const switchSession = async (newSessionId: string) => {
  sessionId.value = newSessionId
  localStorage.setItem(`chat_session_${userId.value}`, newSessionId)
  await loadHistory()
}

// 创建新会话
const createNewSession = () => {
  localStorage.removeItem(`chat_session_${userId.value}`)
  sessionId.value = getSessionId()
  messages.value = []
  loadSessions()
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

onMounted(() => {
  loadSessions()
  loadHistory()
})
</script>

<style scoped>
.chat-container {
  display: grid;
  grid-template-columns: 260px 1fr 280px;
  gap: 20px;
  height: calc(100vh - 120px);
}

/* 会话列表样式 */
.sessions-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.sessions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.session-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.session-item:hover {
  background: #f5f7fa;
}

.session-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.session-time {
  flex: 1;
}

.session-count {
  margin-left: 8px;
}

.empty-sessions {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  font-size: 14px;
}

.chat-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* 防止整个卡片滚动 */
}

.chat-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: scroll !important; /* 强制显示滚动条 */
  overflow-x: hidden;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 0; /* 重要：确保flex子元素可以滚动 */
  max-height: 100%; /* 限制最大高度 */
}

/* 自定义滚动条样式 - WebKit浏览器 */
.messages-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 5px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 5px;
  border: 2px solid #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Firefox滚动条样式 */
.messages-container {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-state p {
  margin: 10px 0;
  font-size: 16px;
}

.tips {
  margin-top: 20px;
  font-weight: bold;
}

.tips-list {
  list-style: none;
  margin-top: 10px;
}

.tips-list li {
  margin: 8px 0;
  font-size: 14px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #67c23a;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  word-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
  max-width: 100%;
}

.message.user .message-text {
  background: #409eff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  padding: 0 8px;
}

.tool-calls {
  margin-top: 8px;
  font-size: 12px;
}

.tool-call {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
}

.tool-output {
  color: #606266;
  font-size: 12px;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-container {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

.quick-actions {
  height: fit-content;
}

.quick-actions :deep(.el-card__body) {
  padding: 16px;
}

.quick-actions .el-button {
  width: 100%;
  justify-content: flex-start;
}
</style>
