# 智能农业仿真教学管理系统（教务管理平台）

本项目为本人面试求职作品，无商业用途。

## 项目说明

- **前端 `vue-tlias-management`**：本人在实习期间基于开源模板二次开发，使用 Vue 3 + Element Plus + Pinia + Vue Router 构建，涵盖班级管理、学员管理、仿真资源管理、用户管理、数据统计等模块。
- **后端 `tlias-backend-node`**：为配合前端演示，使用 Node.js + Express + SQLite + JWT 搭建的 RESTful API 服务。

## 技术栈

| 前端 | 后端 |
|------|------|
| Vue 3 (Composition API) | Node.js |
| Vite | Express |
| Element Plus | SQLite |
| Pinia | JWT 认证 |
| Vue Router (History 模式) | RESTful API |
| Axios | Middleware 鉴权 |

## 本地运行

```bash
# 前端
cd vue-tlias-management
npm install
npm run dev

# 后端（新开终端）
cd tlias-backend-node
npm install
npm run dev
