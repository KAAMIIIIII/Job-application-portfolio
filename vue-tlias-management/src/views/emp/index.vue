<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryPageApi, addEmpApi, queryInfoApi, updateEmpApi, deleteEmpApi} from '@/api/emp'

//性别列表数据
const genders = ref([{ name: '男', value: 1 }, { name: '女', value: 2 }])

const searchEmp = ref({
  name: '',
  gender: ''
})

onMounted(async () => {
  handleSearch()
})

//查询员工
const handleSearch = async () => {
  console.log('Search:', searchEmp.value)
  const result = await queryPageApi(searchEmp.value.name, searchEmp.value.gender, '', '', currentPage.value, pageSize.value);
  if(result.code){
    empList.value = result.data.rows
    total.value = result.data.total
  }
}

const handleReset = () => {
  // 清空表单
  searchEmp.value = {
    name: '',
    gender: ''
  }
  handleSearch()
}

// 示例数据
const empList = ref([])

// 分页配置
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 职位转换函数
const getJobTitle = (job) => {
  switch (job) {
    case 1:
      return '班主任'
    case 2:
      return '讲师'
    case 3:
      return '学工主管'
    case 4:
      return '教研主管'
    case 5:
      return '咨询师'
    default:
      return '其他'
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}
const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}

// 操作处理
const handleEdit = async (id) => {
  console.log('Edit:', id)
  const result = await queryInfoApi(id);
  if(result.code){
    dialogVisible.value = true
    dialogTitle.value = '修改员工'
    employee.value = result.data
  }
}

// 删除单个员工
const handleDelete = async (id) => {
  //弹出一个确认框, 如果确认, 就删除;
  ElMessageBox.confirm('确定删除该员工吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    // 删除员工
    const result = await deleteEmpApi(id);
    if(result.code){
      ElMessage.success('删除员工成功')
      handleSearch()
    }else{
      ElMessage.error(result.msg)
    }
  })
}

//新增员工
const addEmp = () => {
  dialogVisible.value = true
  dialogTitle.value = '新增员工'
  employee.value = {
    username: '',
    name: '',
    gender: '',
    phone: ''
  }
  employeeFormRef.value.resetFields()
}


//新增/修改表单
const employeeFormRef = ref(null)
const employee = ref({
  username: '',
  name: '',
  gender: '',
  phone: ''
})

//表单校验规则
// 验证规则
const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度应在2到20个字符之间', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度应在2到10个字符之间', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ]
});

// 控制弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增员工')


//保存员工信息
const save = async () => {
  employeeFormRef.value.validate(async valid => {
    if(valid){ // 校验通过
      let result ;
      if(employee.value.id){ //存在ID, 修改
        result = await updateEmpApi(employee.value);
      }else { //不存在ID, 新增
        result = await addEmpApi(employee.value);
      }
      if(result.code){
        ElMessage.success('新增员工成功')
        dialogVisible.value = false
        handleSearch()
      }else {
        ElMessage.error(result.msg)
      }
    }
  })
}

// 存储选中的 ID
const selectedIds = ref([]);

// 处理复选框选择变化的函数
function handleSelectionChange(selection) {
  const ids = selection.map(item => item.id);
  selectedIds.value = ids;
}

//批量删除
const deleteByIds = async () => {
  //弹出一个确认框, 如果确认, 就删除;
  ElMessageBox.confirm('确定删除选中员工吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    // 删除员工
    const result = await deleteEmpApi(selectedIds.value);
    if(result.code){
      ElMessage.success('删除员工成功')
      handleSearch()
    }else{
      ElMessage.error(result.msg)
    }
  })
}

</script>

<template>
  <h1>用户管理</h1> <br>
  <el-form :inline="true" :model="searchEmp">
    <el-form-item label="姓名">
      <el-input v-model="searchEmp.name" placeholder="请输入员工姓名"></el-input>
    </el-form-item>

    <el-form-item label="性别">
      <el-select v-model="searchEmp.gender" placeholder="请选择">
        <el-option label="男" value="1"></el-option>
        <el-option label="女" value="2"></el-option>
      </el-select>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSearch">查询</el-button>
      <el-button @click="handleReset">清空</el-button>
    </el-form-item>
  </el-form>


  <el-button type="primary" @click="addEmp"> + 新增员工</el-button>
  <el-button type="danger" @click="deleteByIds"> - 批量删除</el-button>
  <br><br>

  <!-- 表格 -->
  <el-table :data="empList" border style="width: 100%" @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" align="center"></el-table-column>
    <el-table-column prop="name" label="姓名" width="100" align="center"></el-table-column>
    <el-table-column label="性别" width="60" align="center">
      <template #default="scope" >
        {{ scope.row.gender == 1 ? '男' : '女' }}
      </template>
    </el-table-column>
    <el-table-column label="所在班级" width="200" align="center">
      <template #default="scope">
        <span v-if="scope.row.clazzNames">{{ scope.row.clazzNames }}</span>
        <span v-else style="color: #999;">无</span>
      </template>
    </el-table-column>
    <el-table-column label="管理总人数" width="110" align="center">
      <template #default="scope">
        <span v-if="scope.row.totalStudents">{{ scope.row.totalStudents }}</span>
        <span v-else style="color: #999;">无</span>
      </template>
    </el-table-column>
    <el-table-column prop="updateTime" label="最后操作时间" width="210" align="center"></el-table-column>
    <el-table-column label="操作" fixed="right" align="center">
      <template #default="scope">
        <el-button size="small" type="primary" @click="handleEdit(scope.row.id)">编辑</el-button>
        <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  <br>

  <!-- 分页 -->
  <el-pagination
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
    :current-page="currentPage"
    :page-sizes="[10, 20, 30, 40]"
    :page-size="pageSize"
    layout="total, sizes, prev, pager, next, jumper"
    :total="total"
  >
  </el-pagination>

  <!-- 新增/修改员工的对话框 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle">
      <el-form ref="employeeFormRef" :model="employee" :rules="rules" label-width="80px">
        <!-- 基本信息 -->
        <!-- 第一行 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="employee.username" placeholder="请输入员工用户名，2-20个字"></el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="employee.name" placeholder="请输入员工姓名，2-10个字"></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二行 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="employee.gender" placeholder="请选择性别" style="width: 100%;">
                <el-option v-for="gender in genders" :key="gender.name" :label="gender.name" :value="gender.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="employee.phone" placeholder="请输入员工手机号"></el-input>
            </el-form-item>
          </el-col>
        </el-row>


      </el-form>

      <!-- 底部按钮 -->
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="save">保存</el-button>
        </span>
      </template>
    </el-dialog>

</template>

<style scoped>

</style>