<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { queryPageApi , addApi, queryInfoApi, updateApi, deleteApi} from '@/api/clazz'
import { queryAllApi as queryAllEmpApi } from '@/api/emp'
import { ElMessage, ElMessageBox } from 'element-plus'

const toDate = (str) => {
  if (!str) return null
  if (str instanceof Date) return str
  const [y, m, d] = str.split('-')
  return new Date(+y, +m - 1, +d)
}

const toDateString = (date) => {
  if (!date) return ''
  if (typeof date === 'string') return date
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

//学科列表数据
const subjects = ref([{ name: 'Java', value: 1 },{ name: '前端', value: 2 },{ name: '大数据', value: 3 },{ name: 'Python', value: 4 },{ name: 'Go', value: 5 },{ name: '嵌入式', value: 6 }])
//搜索表单对象
let searchClazz = ref({begin: null, end: null, name: '', masterId: ''})
//列表展示数据
let tableData = ref([])

//钩子函数 - 页面加载时触发
onMounted(() => {
  queryPage()
  queryAllEmp()
})

//所有的员工数据
let emps = ref([])
//加载所有的员工数据
const queryAllEmp = async () => {
  let result = await queryAllEmpApi()
  if(result.code) {
    emps.value = result.data
  }
}

//分页组件
const pagination = ref({currentPage: 1, pageSize: 10, total: 0})
//每页展示记录数发生变化时触发
const handleSizeChange = (pageSize) => {
  pagination.value.pageSize = pageSize
  queryPage()
}
//当前页码发生变化时触发
const handleCurrentChange = (page) => {
  pagination.value.currentPage = page
  queryPage()
}

//分页条件查询
const queryPage = async () => {
  const result = await queryPageApi(
      toDateString(searchClazz.value.begin),
      toDateString(searchClazz.value.end),
      searchClazz.value.name,
      searchClazz.value.masterId,
      pagination.value.currentPage,
      pagination.value.pageSize
  );

  if(result.code) {
    tableData.value = result.data.rows
    pagination.value.total = result.data.total
  }
}

//清空搜索栏
const clear = () => {
  searchClazz.value = {begin: null, end: null, name: '', masterId: ''}
  queryPage()
}




//----------- 新增 / 修改 ---------------------------
let dialogFormVisible = ref(false) //控制新增/修改的对话框的显示与隐藏
let labelWidth = ref(80) //form表单label的宽度
let formTitle = ref('') //表单的标题
//员工对象-表单数据绑定
let clazz = ref({
  id: '',
  name: '',
  room: '',
  beginDate: null,
  endDate: null,
  subject: '',
  masterId: ''
})

//清空表单
const clearClazz = () => {
  clazz.value = {
    id: '',
    name: '',
    room: '',
    beginDate: null,
    endDate: null,
    subject: '',
    masterId: ''
  }
}

//新增班级
const addClazz = async () => {
  clearClazz()
  formTitle.value = '新增班级'
  dialogFormVisible.value = true
  await nextTick()
  clazzFormRef.value?.resetFields()
}

//修改班级
const updateClazz = async (id) => {
  let result = await queryInfoApi(id)
  if(result.code){
    clearClazz()
    clazz.value = {
      ...result.data,
      beginDate: toDate(result.data.beginDate),
      endDate: toDate(result.data.endDate)
    }
    formTitle.value = '修改班级'
    dialogFormVisible.value = true
    await nextTick()
    clazzFormRef.value?.resetFields()
  }
}

//表单校验规则
const clazzFormRef = ref()
const rules = ref({
  name: [
    { required: true, message: '班级名称为必填项', trigger: 'blur' },
    { min: 4, max: 30, message: '用户名长度为4-30个字', trigger: 'blur' }
  ],
  room: [
    { min: 1, max: 20, message: '班级教室长度为1-20个字', trigger: 'blur' }
  ],
  beginDate: [{ required: true, message: '开课时间为必填项', trigger: 'change' }],
  endDate: [{ required: true, message: '结课时间为必填项', trigger: 'change' }],
  subject: [{ required: true, message: '学科为必填项', trigger: 'change' }]
})

//重置表单
const resetForm = (clazzForm) => {
  if (!clazzForm) return
  clazzForm.resetFields()
}

//-------------保存班级信息
const save = (clazzForm) => {
  if(!clazzForm) return
  clazzForm.validate(async (valid) => {
    if(valid) {
      const data = {
        ...clazz.value,
        beginDate: toDateString(clazz.value.beginDate),
        endDate: toDateString(clazz.value.endDate)
      }
      let api = data.id ? updateApi(data) : addApi(data)

      let result = await api
      if(result.code) {
        ElMessage.success('操作成功')
        dialogFormVisible.value = false
        queryPage()
      }else {
        ElMessage.error(result.msg)
      }
    }
  })
}


//------- 删除班级
//根据ID删除单个班级
const delById = async (id) => {
  ElMessageBox.confirm('您确认删除此数据吗?' , '删除班级', {confirmButtonText:'确认', cancelButtonText:'取消',type:'warning'})
    .then(async () => {
      let result =  await deleteApi(id)
      if(result.code) {
        ElMessage.success('删除成功')
        queryPage()
      }else {
        ElMessage.error(result.msg)
      }
    }).catch(() => {
      ElMessage.info('取消删除')
    })
}
</script>

<template>

    <!-- 顶部标题 -->
    <div>
      <div id="title">班级管理</div><br>
    </div>

    <!-- 条件搜索表单 -->
    <el-form :inline="true" :model="searchClazz" class="demo-form-inline">
      <el-form-item label="班级名称">
        <el-input v-model="searchClazz.name" placeholder="请输入班级名称"/>
      </el-form-item>
      
      <el-form-item label="开课时间">
        <el-date-picker
          v-model="searchClazz.begin"
          type="date"
          placeholder="选择开课时间"
          format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="结课时间">
        <el-date-picker
          v-model="searchClazz.end"
          type="date"
          placeholder="选择结课时间"
          format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="班主任">
        <el-select v-model="searchClazz.masterId" placeholder="请选择班主任" clearable>
          <el-option v-for="emp in emps" :label="emp.name" :value="emp.id" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="queryPage()">查询</el-button>
        <el-button type="info" @click="clear()">清空</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 功能按钮 -->
    <el-button type="success" @click="addClazz()">+ 新增班级</el-button>
    <br><br>
    
    <!-- 列表展示 -->
    <el-table :data="tableData" border style="width: 100%" fit>
      <el-table-column type="index" label="序号" width="55" align="center"/>
      <el-table-column prop="name" label="班级名称" align="center" width="200px" />
      <el-table-column prop="room" label="班级教室" align="center" width="100px"/>
      <el-table-column prop="masterName" label="班主任" align="center" width="100px"/>
      <el-table-column prop="beginDate" label="开课时间" align="center" width="150px"/>
      <el-table-column prop="endDate" label="结课时间" align="center" width="150px"/>
      <el-table-column prop="status" label="状态" align="center" width="130px" />
      <el-table-column prop="updateTime" label="最后修改时间" align="center" />
      <el-table-column label="操作" align="center">
        <template #default="scope">
          <el-button type="primary" size="small" @click="updateClazz(scope.row.id)">编辑</el-button>
          <el-button type="danger" size="small" @click="delById(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <br>

    <!-- 分页组件Pagination -->
    <el-pagination
      v-model:current-page="pagination.currentPage"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[5, 10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="pagination.total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />



  
  <!-- 新增/修改员工对话框 -->
  <el-dialog v-model="dialogFormVisible" :title="formTitle" width="35%">
    <el-form :model="clazz" ref="clazzFormRef" :rules="rules">
      <el-form-item label="班级名称" :label-width="labelWidth" prop="name">
        <el-input v-model="clazz.name" placeholder="请输入班级名称" />
      </el-form-item>

      <el-form-item label="班级教室" :label-width="labelWidth" prop="room">
        <el-input v-model="clazz.room" placeholder="请输入班级教室"/>
      </el-form-item>
      
      <el-form-item label="开课时间" :label-width="labelWidth" prop="beginDate">
        <el-date-picker v-model="clazz.beginDate" type="date" placeholder="请选择开课时间" format="YYYY-MM-DD" style="width: 100%;"/>
      </el-form-item>

      <el-form-item label="结课时间" :label-width="labelWidth" prop="endDate">
        <el-date-picker v-model="clazz.endDate" type="date" placeholder="请选择结课时间" format="YYYY-MM-DD" style="width: 100%;"/>
      </el-form-item>

      <el-form-item label="班主任" :label-width="labelWidth">
        <el-select v-model="clazz.masterId" placeholder="请选择班主任" style="width: 100%;">
          <el-option v-for="emp in emps" :label="emp.name" :value="emp.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="学科" :label-width="labelWidth" prop="subject">
        <el-select v-model="clazz.subject" placeholder="请选择学科" style="width: 100%;">
          <el-option v-for="sub in subjects" :label="sub.name" :value="sub.value" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogFormVisible = false; resetForm(clazzFormRef)">取消</el-button>
        <el-button type="primary" @click="save(clazzFormRef)">保存</el-button>
      </span>
    </template>
  </el-dialog>

</template>


<style scoped>
#title {
  font-size: 20px;
  font-weight: 600;
}
</style>

