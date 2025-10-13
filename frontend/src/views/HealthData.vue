<template>
  <div class="health-data">
    <el-tabs v-model="activeTab">
      <!-- 血糖数据 -->
      <el-tab-pane label="血糖数据" name="glucose">
        <div class="tab-content">
          <div class="actions">
            <el-button type="primary" @click="showAddDialog('glucose')">
              <el-icon><Plus /></el-icon>
              添加血糖数据
            </el-button>
          </div>
          
          <el-table :data="glucoseData" stripe style="margin-top: 16px;">
            <el-table-column prop="measured_at" label="测量时间" width="180" />
            <el-table-column prop="value" label="血糖值 (mmol/L)" width="150" />
            <el-table-column prop="measurement_type" label="测量类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getTypeColor(row.measurement_type)">
                  {{ getTypeName(row.measurement_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getGlucoseStatus(row.value, row.measurement_type).type">
                  {{ getGlucoseStatus(row.value, row.measurement_type).text }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <!-- 血压数据 -->
      <el-tab-pane label="血压数据" name="pressure">
        <div class="tab-content">
          <div class="actions">
            <el-button type="primary" @click="showAddDialog('pressure')">
              <el-icon><Plus /></el-icon>
              添加血压数据
            </el-button>
          </div>
          
          <el-table :data="pressureData" stripe style="margin-top: 16px;">
            <el-table-column prop="measured_at" label="测量时间" width="180" />
            <el-table-column label="血压值 (mmHg)" width="150">
              <template #default="{ row }">
                {{ row.systolic }}/{{ row.diastolic }}
              </template>
            </el-table-column>
            <el-table-column prop="heart_rate" label="心率 (次/分)" width="120" />
            <el-table-column prop="notes" label="备注" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getPressureStatus(row.systolic, row.diastolic).type">
                  {{ getPressureStatus(row.systolic, row.diastolic).text }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <!-- 体重数据 -->
      <el-tab-pane label="体重数据" name="weight">
        <div class="tab-content">
          <div class="actions">
            <el-button type="primary" @click="showAddDialog('weight')">
              <el-icon><Plus /></el-icon>
              添加体重数据
            </el-button>
          </div>
          
          <el-table :data="weightData" stripe style="margin-top: 16px;">
            <el-table-column prop="measured_at" label="测量时间" width="180" />
            <el-table-column prop="value" label="体重 (kg)" width="120" />
            <el-table-column prop="bmi" label="BMI" width="100" />
            <el-table-column prop="notes" label="备注" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加数据对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="测量时间">
          <el-date-picker
            v-model="formData.measured_at"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%;"
          />
        </el-form-item>
        
        <!-- 血糖表单 -->
        <template v-if="dataType === 'glucose'">
          <el-form-item label="血糖值">
            <el-input-number
              v-model="formData.value"
              :min="0"
              :max="30"
              :precision="1"
              :step="0.1"
            />
            <span style="margin-left: 8px;">mmol/L</span>
          </el-form-item>
          <el-form-item label="测量类型">
            <el-select v-model="formData.measurement_type" style="width: 100%;">
              <el-option label="空腹" value="fasting" />
              <el-option label="餐前" value="before_meal" />
              <el-option label="餐后" value="after_meal" />
              <el-option label="睡前" value="before_sleep" />
              <el-option label="随机" value="random" />
            </el-select>
          </el-form-item>
        </template>
        
        <!-- 血压表单 -->
        <template v-if="dataType === 'pressure'">
          <el-form-item label="收缩压">
            <el-input-number
              v-model="formData.systolic"
              :min="60"
              :max="200"
            />
            <span style="margin-left: 8px;">mmHg</span>
          </el-form-item>
          <el-form-item label="舒张压">
            <el-input-number
              v-model="formData.diastolic"
              :min="40"
              :max="150"
            />
            <span style="margin-left: 8px;">mmHg</span>
          </el-form-item>
          <el-form-item label="心率">
            <el-input-number
              v-model="formData.heart_rate"
              :min="40"
              :max="200"
            />
            <span style="margin-left: 8px;">次/分</span>
          </el-form-item>
        </template>
        
        <!-- 体重表单 -->
        <template v-if="dataType === 'weight'">
          <el-form-item label="体重">
            <el-input-number
              v-model="formData.value"
              :min="20"
              :max="200"
              :precision="1"
              :step="0.1"
            />
            <span style="margin-left: 8px;">kg</span>
          </el-form-item>
          <el-form-item label="身高">
            <el-input-number
              v-model="formData.height"
              :min="100"
              :max="250"
              :precision="0"
            />
            <span style="margin-left: 8px;">cm（用于计算BMI）</span>
          </el-form-item>
        </template>
        
        <el-form-item label="备注">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { healthAPI } from '@/api'

const activeTab = ref('glucose')
const dialogVisible = ref(false)
const dataType = ref('')
const userId = ref(1)

const glucoseData = ref<any[]>([])
const pressureData = ref<any[]>([])
const weightData = ref<any[]>([])

const formData = ref({
  measured_at: new Date(),
  value: 0,
  measurement_type: 'fasting',
  systolic: 120,
  diastolic: 80,
  heart_rate: 75,
  height: 170,
  notes: ''
})

const dialogTitle = computed(() => {
  const titles: Record<string, string> = {
    glucose: '添加血糖数据',
    pressure: '添加血压数据',
    weight: '添加体重数据'
  }
  return titles[dataType.value] || ''
})

// 显示添加对话框
const showAddDialog = (type: string) => {
  dataType.value = type
  formData.value = {
    measured_at: new Date(),
    value: type === 'glucose' ? 6.0 : 65.0,
    measurement_type: 'fasting',
    systolic: 120,
    diastolic: 80,
    heart_rate: 75,
    height: 170,
    notes: ''
  }
  dialogVisible.value = true
}

// 添加数据
const handleAdd = async () => {
  try {
    const data = {
      user_id: userId.value,
      measured_at: formData.value.measured_at,
      notes: formData.value.notes
    }
    
    if (dataType.value === 'glucose') {
      await healthAPI.addBloodGlucose({
        ...data,
        value: formData.value.value,
        measurement_type: formData.value.measurement_type
      })
      loadGlucoseData()
    } else if (dataType.value === 'pressure') {
      await healthAPI.addBloodPressure({
        ...data,
        systolic: formData.value.systolic,
        diastolic: formData.value.diastolic,
        heart_rate: formData.value.heart_rate
      })
      loadPressureData()
    } else if (dataType.value === 'weight') {
      await healthAPI.addWeight({
        ...data,
        value: formData.value.value,
        height: formData.value.height
      })
      loadWeightData()
    }
    
    ElMessage.success('添加成功')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 加载数据
const loadGlucoseData = async () => {
  try {
    const response: any = await healthAPI.getBloodGlucose(userId.value, 20)
    glucoseData.value = response.data
  } catch (error) {
    console.error('加载血糖数据失败', error)
  }
}

const loadPressureData = async () => {
  try {
    const response: any = await healthAPI.getBloodPressure(userId.value, 20)
    pressureData.value = response.data
  } catch (error) {
    console.error('加载血压数据失败', error)
  }
}

const loadWeightData = async () => {
  try {
    const response: any = await healthAPI.getWeight(userId.value, 20)
    weightData.value = response.data
  } catch (error) {
    console.error('加载体重数据失败', error)
  }
}

// 工具函数
const getTypeName = (type: string) => {
  const names: Record<string, string> = {
    fasting: '空腹',
    before_meal: '餐前',
    after_meal: '餐后',
    before_sleep: '睡前',
    random: '随机'
  }
  return names[type] || type
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    fasting: '',
    before_meal: 'info',
    after_meal: 'success',
    before_sleep: 'warning',
    random: 'danger'
  }
  return colors[type] || ''
}

const getGlucoseStatus = (value: number, type: string) => {
  if (type === 'fasting') {
    if (value < 3.9) return { type: 'danger', text: '偏低' }
    if (value <= 6.1) return { type: 'success', text: '正常' }
    return { type: 'warning', text: '偏高' }
  } else if (type === 'after_meal') {
    if (value <= 7.8) return { type: 'success', text: '正常' }
    return { type: 'warning', text: '偏高' }
  }
  return { type: 'info', text: '-' }
}

const getPressureStatus = (systolic: number, diastolic: number) => {
  if (systolic >= 140 || diastolic >= 90) {
    return { type: 'danger', text: '偏高' }
  } else if (systolic < 90 || diastolic < 60) {
    return { type: 'warning', text: '偏低' }
  }
  return { type: 'success', text: '正常' }
}

onMounted(() => {
  loadGlucoseData()
  loadPressureData()
  loadWeightData()
})
</script>

<style scoped>
.health-data {
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.tab-content {
  padding: 16px 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
}
</style>
