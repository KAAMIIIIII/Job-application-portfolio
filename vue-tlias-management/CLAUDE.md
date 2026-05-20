# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```sh
npm install          # 安装依赖
npm run dev          # 启动开发服务器 (Vite HMR)
npm run build        # 生产构建到 dist/
npm run preview      # 预览生产构建，端口 4173
npm run lint         # ESLint 检查 .vue/.js/.jsx/.cjs/.mjs，自动修复
```

未配置测试套件。

## 项目架构

Vue 3 + Vite 单页应用，使用 Element Plus 组件库、Pinia 状态管理、Vue Router 路由。后端为独立的 Java 服务，通过 Vite 代理转发请求。

### API 层 (`src/utils/request.js`)

Axios 实例，`baseURL: '/api'`，包含两个拦截器：
- **请求拦截器**：从 localStorage 读取 `loginUser`，将 token 附加到 `config.headers.token`
- **响应拦截器**：成功时解包 `response.data`；遇到 401 时提示错误并跳转到 `/login`

`src/api/` 下各模块导入共享的 `request` 实例，导出调用后端接口的函数。例如 `src/api/dept.js` 导出了 `queryAllApi`、`addDeptApi`、`queryInfoApi`、`updateDeptApi`、`deleteDeptApi`。

### 路由 (`src/router/index.js`)

History 模式路由，包含两个顶级路由：
- `/login` → 登录页（独立页面，无布局）
- `/` → Layout 布局组件，重定向到 `/index`，子路由包括：
  - `/index` — 首页/仪表盘
  - `/clazz` — 班级管理
  - `/stu` — 学员管理
  - `/dept` — 仿真资源管理
  - `/emp` — 用户管理
  - `/report/stu` — 学员信息统计

Layout 中使用 `el-menu` 的 `router` 属性实现导航，菜单项的 `index` 值与路由 path 对应。

### 登录认证流程

1. 登录页将用户名密码 POST 到 `/login`
2. 成功后后端返回 `{ code, data: { token, name } }`，存入 localStorage（键名为 `loginUser`）
3. Axios 请求拦截器从 localStorage 读取 token，作为 `token` 请求头发送
4. 401 响应触发跳转到 `/login`
5. 退出登录清除 localStorage 并跳转到 `/login`

### 页面编写模式

所有视图使用 `<script setup>` 配合组合式 API。标准 CRUD 页面模式（参考 `dept/index.vue`、`emp/index.vue`）：
- 用 `ref()` 管理表格数据、对话框显示状态、表单数据、搜索条件、分页参数
- `onMounted()` 钩子中触发初始数据加载
- Element Plus 的 `el-table` + `el-dialog` + `el-form`（含表单验证规则）+ `ElMessageBox.confirm` 确认删除
- 分页使用 `el-pagination`，配合 `handleSizeChange` / `handleCurrentChange`

### 状态管理

Pinia 已配置但基本未使用 —— store 中仅有一个示例 counter。应用状态主要存放在组件局部的 `ref()` 和 localStorage 中。

### Vite 代理

`/api` 请求代理到 `http://localhost:8080`，并重写路径去掉 `/api` 前缀。后端需要单独在 8080 端口启动。
