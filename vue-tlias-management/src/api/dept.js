import request from '@/utils/request'

const BASE = '/depts'

// 查询全部
export const queryAllApi = () => request.get(BASE)

// 添加（支持文件上传）
export const addDeptApi = (formData) => request.post(BASE, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 根据ID查询
export const queryInfoApi = (id) => request.get(`${BASE}/${id}`)

// 修改（支持文件上传）
export const updateDeptApi = (formData) => request.put(BASE, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 删除
export const deleteDeptApi = (id) => request.delete(`${BASE}?id=${id}`)

// 文件访问地址
export const getFileUrl = (filePath) => {
  if (!filePath) return ''
  return `/api/depts/file/${filePath}`
}
