# 智能农业仿真教学管理系统（教务管理平台）

本项目为本人面试求职作品，无商业用途。

## 项目说明

- **前端 `vue-tlias-management`**：基于 Vue 3 + Element Plus + Pinia + Vue Router 构建，涵盖班级管理、学员管理、仿真资源管理、用户管理、数据统计等模块。
- **后端 `tlias-backend-python`**：Python + Flask + SQLite + PyJWT 搭建的 RESTful API 服务。

## 技术栈

| 前端 | 后端 |
|------|------|
| Vue 3 (Composition API) | Python 3 |
| Vite | Flask |
| Element Plus | SQLite (WAL 模式) |
| Pinia | PyJWT 认证 |
| Vue Router (Hash 模式) | bcrypt 密码加密 |
| Axios | RESTful API |

## 本地运行

```bash
# 前端
cd vue-tlias-management
npm install
npm run dev          # 启动开发服务器 → http://localhost:5173

# 后端（新开终端）
cd tlias-backend-python
pip install -r requirements.txt
python app.py        # 启动服务 → http://localhost:8080
```

后端首次启动自动创建 SQLite 数据库和默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

前端 Vite 开发服务器将 `/api` 请求代理到后端 8080 端口。

## 演示模式

部署到 GitHub Pages 时无需后端，登录页内置演示模式：输入 `admin` / `admin123` 即可体验前端功能。

