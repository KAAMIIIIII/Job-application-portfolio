<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryAllApi, addDeptApi, queryInfoApi, updateDeptApi, deleteDeptApi, getFileUrl } from '@/api/dept'

let tableData = ref([])

const queryAll = async () => {
  const result = await queryAllApi()
  tableData.value = result.data
}

onMounted(() => {
  queryAll()
})

const formTitle = ref('')
const fileList = ref([])

const add = () => {
  formTitle.value = '新增仿真资源'
  showDialog.value = true
  deptForm.value = { name: '', url: '' }
  fileList.value = []
}

const handleEdit = async (row) => {
  formTitle.value = '修改仿真资源'
  showDialog.value = true
  deptForm.value = { name: '', url: '' }
  fileList.value = []

  const result = await queryInfoApi(row.id)
  if (result.code) {
    deptForm.value = {
      name: result.data.name || '',
      url: result.data.url || '',
      id: result.data.id,
    }
    if (result.data.filePath && result.data.fileName) {
      deptForm.value.filePath = result.data.filePath
      deptForm.value.fileName = result.data.fileName
      fileList.value = [{ name: result.data.fileName, url: getFileUrl(result.data.filePath) }]
    }
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('此操作将永久删除该仿真资源, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const result = await deleteDeptApi(row.id)
    if (result.code) {
      ElMessage.success('删除仿真资源成功')
      queryAll()
    }
  })
}

const showDialog = ref(false)
const deptForm = ref({ name: '', url: '' })

// 自定义验证：url 和文件至少填一个
const validateUrlOrFile = (rule, value, callback) => {
  const hasUrl = deptForm.value.url && deptForm.value.url.trim()
  const hasFile = fileList.value.length > 0 && fileList.value[0].raw
  const hasExistingFile = fileList.value.length > 0 && !fileList.value[0].raw
  if (!hasUrl && !hasFile && !hasExistingFile) {
    callback(new Error('链接和本地文件至少填写一项'))
  } else {
    callback()
  }
}

const formRules = ref({
  name: [
    { required: true, message: '请输入仿真资源名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  url: [
    { validator: validateUrlOrFile, trigger: 'blur' }
  ]
})

const deptFormRef = ref(null)
const uploadRef = ref(null)

const resetForm = () => {
  deptFormRef.value?.resetFields()
  fileList.value = []
}

const beforeUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = ['zip', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'rar', '7z']
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持的文件格式: .${ext}`)
    return false
  }
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

const handleFileChange = () => {
  // 文件变动后联动验证 url 字段
  deptFormRef.value?.validateField('url')
}

const save = async () => {
  await deptFormRef.value.validate(async valid => {
    if (!valid) return

    const fd = new FormData()
    fd.append('name', deptForm.value.name)
    fd.append('url', deptForm.value.url || '')
    if (deptForm.value.id) fd.append('id', deptForm.value.id)

    // 上传了新文件
    if (fileList.value.length > 0 && fileList.value[0].raw) {
      fd.append('file', fileList.value[0].raw)
    }
    // 删除了已有文件
    else if (fileList.value.length === 0 && deptForm.value.filePath) {
      fd.append('keepFile', '0')
    }

    let result
    if (deptForm.value.id) {
      result = await updateDeptApi(fd)
    } else {
      result = await addDeptApi(fd)
    }
    if (result.code) {
      ElMessage.success('仿真资源操作成功')
      showDialog.value = false
      resetForm()
      queryAll()
    } else {
      ElMessage.error(result.msg)
    }
  })
}
</script>

<template>
  <h1>仿真资源管理</h1>

  <el-button type="primary" @click="add()" style="float: right;"> + 新增仿真资源</el-button> <br><br>

  <el-table :data="tableData" border style="width: 100%;">
    <el-table-column type="index" label="序号" width="80" align="center"/>
    <el-table-column prop="name" label="仿真资源名称" width="180" align="center"/>
    <el-table-column prop="url" label="仿真资源链接" width="220" align="center">
      <template #default="{ row }">
        <span v-if="row.url">{{ row.url }}</span>
        <span v-else style="color: #999;">无</span>
      </template>
    </el-table-column>
    <el-table-column label="仿真资源文件" width="200" align="center">
      <template #default="{ row }">
        <a v-if="row.filePath" :href="getFileUrl(row.filePath)" target="_blank" style="color: #409eff;">
          {{ row.fileName }}
        </a>
        <span v-else style="color: #999;">无</span>
      </template>
    </el-table-column>
    <el-table-column prop="updateTime" label="最后修改时间" width="180" align="center"/>
    <el-table-column fixed="right" label="操作" align="center">
      <template #default="{ row }">
        <el-button size="small" @click="handleEdit(row)">修改</el-button>
        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="showDialog" :title="formTitle" width="35%" @close="resetForm">
    <el-form :model="deptForm" :rules="formRules" ref="deptFormRef">
      <el-form-item label="仿真资源名称" prop="name" label-width="120px">
        <el-input v-model="deptForm.name" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="仿真资源链接" prop="url" label-width="120px">
        <el-input v-model="deptForm.url" autocomplete="off" placeholder="可选：输入URL链接"></el-input>
      </el-form-item>
      <el-form-item label="本地文件" label-width="120px">
        <el-upload
          ref="uploadRef"
          v-model:file-list="fileList"
          :before-upload="beforeUpload"
          :on-change="handleFileChange"
          :auto-upload="false"
          :limit="1"
          drag
          action="#"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处 或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">支持 ZIP/PDF/PNG/JPG/DOC/PPT 等格式，最大50MB</div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="save">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>
</style>
