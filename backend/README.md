# 念想 Backend

## 本地启动

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

修改 `.env` 中的 `DATABASE_URL`、`SECRET_KEY`、`DASHSCOPE_API_KEY` 后启动：

```powershell
uvicorn app.main:app --reload
```

接口文档：`http://localhost:8000/docs`
