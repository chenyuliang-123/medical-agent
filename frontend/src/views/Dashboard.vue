<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#409eff"><DataLine /></el-icon>
            <div class="stat-info">
              <div class="stat-value">7.2</div>
              <div class="stat-label">平均血糖 (mmol/L)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#67c23a"><TrendCharts /></el-icon>
            <div class="stat-info">
              <div class="stat-value">128/82</div>
              <div class="stat-label">平均血压 (mmHg)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#e6a23c"><Calendar /></el-icon>
            <div class="stat-info">
              <div class="stat-value">7</div>
              <div class="stat-label">连续监测天数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#f56c6c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">2</div>
              <div class="stat-label">异常次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 血糖趋势图 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>血糖趋势（最近7天）</span>
          </template>
          <div ref="glucoseChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <!-- 血压趋势图 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>血压趋势（最近7天）</span>
          </template>
          <div ref="pressureChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 健康建议 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日健康建议</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="08:00" color="#67c23a">
              空腹血糖测量完成，数值正常
            </el-timeline-item>
            <el-timeline-item timestamp="12:30" color="#409eff">
              午餐后建议散步30分钟
            </el-timeline-item>
            <el-timeline-item timestamp="18:00" color="#e6a23c">
              晚餐注意控制主食摄入
            </el-timeline-item>
            <el-timeline-item timestamp="21:00" color="#909399">
              睡前血糖测量提醒
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      
      <!-- 待办提醒 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待办提醒</span>
          </template>
          <el-empty v-if="reminders.length === 0" description="暂无提醒" />
          <div v-else class="reminders">
            <div v-for="reminder in reminders" :key="reminder.id" class="reminder-item">
              <el-checkbox v-model="reminder.completed">
                {{ reminder.title }}
              </el-checkbox>
              <span class="reminder-time">{{ reminder.time }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { DataLine, TrendCharts, Calendar, Warning } from '@element-plus/icons-vue'

const glucoseChart = ref<HTMLElement>()
const pressureChart = ref<HTMLElement>()

const reminders = ref([
  { id: 1, title: '早餐后血糖测量', time: '09:00', completed: true },
  { id: 2, title: '午餐后散步', time: '13:00', completed: false },
  { id: 3, title: '晚餐后血糖测量', time: '19:30', completed: false },
])

// 初始化血糖图表
const initGlucoseChart = () => {
  if (!glucoseChart.value) return
  
  const chart = echarts.init(glucoseChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['空腹', '餐后']
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value',
      name: 'mmol/L',
      min: 0,
      max: 12
    },
    series: [
      {
        name: '空腹',
        type: 'line',
        data: [6.2, 6.5, 6.1, 6.8, 6.3, 6.4, 6.6],
        smooth: true,
        itemStyle: { color: '#409eff' }
      },
      {
        name: '餐后',
        type: 'line',
        data: [8.1, 8.5, 7.8, 8.9, 8.2, 8.0, 8.3],
        smooth: true,
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
  chart.setOption(option)
}

// 初始化血压图表
const initPressureChart = () => {
  if (!pressureChart.value) return
  
  const chart = echarts.init(pressureChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['收缩压', '舒张压']
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value',
      name: 'mmHg',
      min: 60,
      max: 160
    },
    series: [
      {
        name: '收缩压',
        type: 'line',
        data: [125, 128, 132, 126, 130, 127, 129],
        smooth: true,
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '舒张压',
        type: 'line',
        data: [78, 82, 85, 80, 83, 79, 81],
        smooth: true,
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  initGlucoseChart()
  initPressureChart()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 100%;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.reminders {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.reminder-time {
  font-size: 12px;
  color: #909399;
}
</style>
