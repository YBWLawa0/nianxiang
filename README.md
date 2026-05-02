# 念想

“念想”是一个让用户随手记录、随心分享的 AI 情感向产品。用户可以记录随笔，AI 会以数字分身 / 朋友的视角给出能量刻度、九宫格标签和亲切回应；用户也可以把当天随笔生成一篇以自己视角写成的日记。

## 目录

- `frontend`：Vue3 + Vite + TypeScript + Vant + Pinia + Capacitor，移动端优先。
- `backend`：FastAPI + SQLAlchemy + MySQL + LangChain + LangGraph + 千问。

## 前端启动

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

生产构建：

```powershell
npm run build
```

Capacitor 同步：

```powershell
npx cap add android
npx cap add ios
npm run build
npx cap sync
```

注意：iOS 最终打包需要 macOS 和 Xcode。

## 后端启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

创建 MySQL 数据库：

```sql
CREATE DATABASE nianxiang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `backend/.env` 中的 `DATABASE_URL`、`SECRET_KEY`、`DASHSCOPE_API_KEY` 后启动：

```powershell
uvicorn app.main:app --reload
```

接口文档在 `http://localhost:8000/docs`。

## 当前 MVP 能力

- 用户注册、登录、JWT 鉴权、退出登录。
- 随笔创建、今日随笔、随笔详情、朋友圈式随笔展示。
- AI 随笔评价：能量刻度 1-5、九宫格 tag、亲切评语。
- AI 日记生成：基于当天随笔，以用户第一人称生成标题、概要和正文。
- MySQL 持久化，并按用户隔离随笔和日记。
- 没有配置千问密钥时，后端会使用本地兜底逻辑，方便先跑通流程。
