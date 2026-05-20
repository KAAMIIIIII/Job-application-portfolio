# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

双项目架构：前端 `vue-tlias-management`（Vue 3 SPA）+ 后端 `tlias-backend-python`（Python Flask RESTful API）。这是一个智能农业仿真教学管理系统，含班级管理、学员管理、仿真资源管理、用户管理、数据统计等模块。

## 常用命令

```bash
# 前端 (vue-tlias-management/)
npm install                 # 安装依赖
npm run dev                 # Vite 开发服务器 (HMR)，默认 http://localhost:5173
npm run build               # 生产构建 → dist/
npm run preview             # 预览生产构建，端口 4173
npm run lint                # ESLint 检查 .vue/.js/.jsx/.cjs/.mjs，自动修复

# 后端 (tlias-backend-python/)
pip install -r requirements.txt   # 安装依赖
python app.py                      # 启动服务，监听 http://localhost:8080
```

无需测试套件。首次启动自动创建 `data/tlias.db`（SQLite，WAL 模式）和默认管理员 (`admin` / `admin123`，bcrypt 加密)。前端开发时 Vite 将 `/api` 请求代理到 `http://localhost:8080` 并去掉 `/api` 前缀，需前后端同时启动。

## 演示模式

登录页 `views/login/index.vue` 内置演示模式：当 `window.location.hostname !== 'localhost'` 时，跳过真实后端请求，使用硬编码 `admin/admin123` 直接写入 localStorage 的 `loginUser`。此设计用于 GitHub Pages 部署（无后端）。修改认证逻辑时需同时考虑两种模式。

## 前端架构 (`vue-tlias-management/`)

**Vue 3 + Vite + Element Plus** SPA，中文语言包。Pinia 已配置但基本未使用，状态主要通过组件 `ref()` 和 localStorage 管理。

### 路由 (`src/router/index.js`)
- **Hash 模式**（`createWebHashHistory`），适配 GitHub Pages 部署（`base: '/Job-application-portfolio/'`）
- `/login` → 登录页（独立，无 Layout）
- `/` → Layout 布局，重定向到 `/index`，子路由映射菜单项：
  - `/index` 首页仪表盘、`/clazz` 班级管理、`/stu` 学员管理、`/dept` 仿真资源管理、`/emp` 用户管理、`/report/stu` 学员信息统计
- `router.beforeEach` 守卫：非登录页未登录 → `/login`

### API 层 (`src/utils/request.js`)
Axios 实例，`baseURL: '/api'`. 请求拦截器从 localStorage `loginUser` 取 token 放入 `config.headers.token`；响应拦截器解包 `response.data`，401 时跳转 `/login`。

`src/api/` 下各模块（`login.js`, `dept.js`, `emp.js`, `clazz.js`, `stu.js`, `report.js`）导入共享 request 实例，导出 API 函数。

### 登录认证流程
1. 登录页判断 hostname：非 localhost 时走演示模式（硬编码 admin/admin123）
2. 正常模式：POST `/api/login` 发送 `{ username, password }`
3. 成功返回 `{ code: 1, data: { token, name } }`，前端以 `JSON.stringify` 存入 localStorage key `loginUser`
4. 后续请求自动携带 token header
5. 401 响应清除 localStorage 并跳转 `/login`；退出登录同理

### CRUD 页面模式
所有视图使用 `<script setup>` 组合式 API。标准模式（参考 `views/dept/index.vue`、`views/emp/index.vue`）：
- `ref()` 管理表格数据、对话框显示、表单、搜索条件、分页
- `onMounted()` 触发初始加载
- `el-table` + `el-dialog` + `el-form`（含验证规则）+ `ElMessageBox.confirm` 确认删除
- `el-pagination` + `handleSizeChange` / `handleCurrentChange`

### Vite 代理
开发时 `/api` 请求代理到 `http://localhost:8080`，路径去掉 `/api` 前缀。后端需单独在 8080 端口启动。

## 后端架构 (`tlias-backend-python/`)

**Python + Flask + SQLite + PyJWT**，RESTful 风格。

### 入口 `app.py`
- Flask + CORS，Blueprint 方式注册路由
- 启动时自动调用 `init_db()` 建表并创建默认管理员
- 全局错误处理返回 `{ code: 0, msg, data: null }`

### 路由分组（`/login` 无需鉴权，其余均需 `@auth_required`）

| Blueprint | 路径前缀 | 说明 |
|---|---|---|
| login_bp | `/login` | 登录认证 |
| dept_bp | `/depts` | 仿真资源管理 — 简单 CRUD，全量查询无分页 |
| emp_bp | `/emps` | 用户管理 — 分页+搜索，密码 bcrypt 处理，批量删除 |
| clazz_bp | `/clazzs` | 班级管理 — 分页+搜索，JOIN emp 取班主任名，计算在读状态 |
| student_bp | `/students` | 学员管理 — 分页+搜索，JOIN clazz 取班级名，违纪记录 |
| report_bp | `/report` | 数据统计 — 4 个图表数据接口，返回 ECharts 就绪格式 |

### 非标准路由模式

仅有 `dept` 使用"全量查询"模式，其他模块均为**分页查询**（`page`/`pageSize` query 参数 + 多条件搜索）。删除接口不统一：

| 模块 | 删除方式 |
|---|---|
| dept | `DELETE /depts?id=xxx`（query 参数，单条） |
| emp | `DELETE /emps?ids=1,2,3`（query 参数，逗号分隔批量） |
| clazz | `DELETE /clazzs/<int:id>`（URL 路径参数，单条） |
| student | `DELETE /students/1,2,3`（URL 路径参数，逗号分隔批量） |

额外端点：
- `GET /emps/list` — 全量 emp 列表（不含分页，用于下拉选择）
- `GET /clazzs/list` — 全量 clazz 列表（仅 id+name，用于下拉选择）
- `PUT /students/violation/<id>/<score>` — 违纪扣分，`violation_count + 1`，`violation_score + score`

**emp 密码处理**：查询不返回 password 字段；新增默认密码 `123456`（bcrypt）；更新时仅当 body 含 `password` 字段才更新密码。

### 数据库 (`database.py`)
SQLite 文件位于 `data/tlias.db`，WAL 模式，外键开启。四张表，两个外键均为 `ON DELETE SET NULL`：
- `clazz.master_id` → `emp.id`（班主任）
- `student.clazz_id` → `clazz.id`（所属班级）

### JWT 鉴权 (`utils/jwt_util.py` + `middleware/auth.py`)
- `generate_token(userId, name)` → HS256 签名，24h 过期
- `verify_token(token)` → 解码，失败抛异常
- `@auth_required` 装饰器：从 `request.headers.token` 取 token，验证后注入 `request.user_id` / `request.user_name`；OPTIONS 请求直接放行

### 响应格式
所有接口统一返回 `{ code: 1|0, msg: string, data: any }`。`code: 1` 成功，`code: 0` 失败。

分页接口 data 结构：`{ rows: [...], total: N }`。

### camelize (`utils/camelize.py`)
Python 版递归 key 转换器。SQLite 返回 snake_case 列名（如 `update_time`），`camelize()` 将 dict 的 key 转为 camelCase（`updateTime`）以匹配前端。report 接口不使用 camelize，因其手动构造返回值时已用 camelCase key。

## CI/CD

GitHub Actions (`.github/workflows/deploy.yml`)：推送到 `main` 分支时自动构建前端（Node 18，`npm run build`）并部署到 GitHub Pages（`peaceiris/actions-gh-pages@v4`），publish 目录为 `vue-tlias-management/dist`。Vite `base` 设为 `'/Job-application-portfolio/'` 匹配 GitHub Pages 路径。部署后无后端，依赖前端演示模式登录。

## 子项目 CLAUDE.md

`vue-tlias-management/CLAUDE.md` 覆盖前端专属细节（页面编写模式、状态管理、API 模块命名等），与本文档互补。修改前端架构时两处均需更新。
