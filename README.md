<p align="center">
  <h1 align="center">念想 NianXiang</h1>
  <p align="center">
    <strong>让 AI 懂你的每一刻情绪，把碎碎念变成有温度的日记</strong>
  </p>
  <p align="center">
    <a href="#产品简介">产品简介</a> · <a href="#核心功能">核心功能</a> · <a href="#技术架构">技术架构</a> · <a href="#快速开始">快速开始</a> · <a href="#项目结构">项目结构</a> · <a href="#api-文档">API 文档</a> · <a href="#数据模型">数据模型</a> · <a href="#ui-设计规范">UI 设计规范</a> · <a href="#团队协作">团队协作</a>
  </p>
</p>

---

## 产品简介

**念想**是一款 AI 驱动的情感记录产品。用户可以随时记录碎碎念，AI 伴侣"阿响"会以朋友的视角给出能量评估、板块标签和温暖回应，并将当天的随笔自动整理成一篇第一人称日记。

> *"大厂用专业让我们对社交媒体和娱乐 APP 成瘾，我们为何不把这种成瘾机制用在有利于自己成长的事情上？"*

### 产品理念

- **低门槛、无教育成本**：参考微信、公众号等用户已广泛认知的交互模式
- **情感化设计**：阿响应像微信朋友一样互动，消解负面情绪、放大正面情绪
- **记录活化**：不是冷冰冰的记录工具，而是将记录变成有温度的产物
- **多维度呈现**：日（日记）、周（文章）、月（播客）、年（书架），不同维度采用不同呈现形式

### 产品命名

产品主打输出内容，各时间维度的"回响"：
- **周的回响** → 公众号文章
- **月的回响** → 播客
- **年的回响** → 微信读书书架

---

## 核心功能

### 1. 随笔记录（Notes）

用户随时记录碎碎念，支持文字输入和语音输入。AI 自动对每条随笔进行评估：

| 评估维度 | 说明 |
|----------|------|
| **能量分数** | 1-5 分，从"极度耗电"到"满电心流" |
| **九宫格板块标签** | 工作/事业、健康/身体、情感/关系、财务、学习/成长、娱乐/休闲、家庭、社交、其他 |
| **AI 评论** | 以"阿响"身份给出温暖、有洞察的回应 |

### 2. AI 日记生成（Diaries）

基于当天所有随笔，AI 自动生成第一人称日记。支持两种模式：

- **非流式生成**：一次性返回完整日记（标题 + 摘要 + 正文）
- **流式生成（SSE）**：分阶段实时输出
  - 第一阶段：日记正文（流式逐字输出）
  - 第二阶段：阿响观察（基于随笔的模式分析与建议）
  - 第三阶段：结尾仪式（今日一问 + 温暖鼓励）

### 3. AI 伴侣"阿响"

一个亲近朋友角色的 AI 伴侣：
- 语气温暖、像朋友聊天、可以轻轻调侃
- 洞察用户情绪模式，指出可能未意识到的心理模式
- 提供小而可做的行动建议
- 根据用户情绪发送对应表情包

### 4. 数据分析（Analysis）

使用 ECharts 进行数据可视化，展示：
- 能量分数趋势
- 九宫格板块分布
- 情绪类型分布

### 5. 周报系统

每周日自动生成周度报告，包含：
- 本周平均能量值
- 每日能量趋势
- 八大板块分布
- 情绪类型分布
- 高频关键词
- 本周最佳时刻
- 阿响的深度洞察与下周建议

### 6. 月度播客

每月 1 日生成月度播客，以音频形式回顾一个月的情感旅程。

### 7. 多端支持

通过 Capacitor 实现 Web + Android + iOS 跨平台支持。

---

## 技术架构

### 系统架构总览

```
┌─────────────────────────────────────────────────────────┐
│  客户端层                                                 │
│  Vue 3 + Vant 4 (Web) / Android / iOS (Capacitor)       │
│  • 语音录制与播放    • 数据可视化（ECharts）               │
├─────────────────────────────────────────────────────────┤
│  后端服务层（Python FastAPI）                             │
│  • 用户服务    • 随笔服务    • 日记服务    • AI 服务       │
├─────────────────────────────────────────────────────────┤
│  AI 引擎层                                                │
│  • LLM（通义千问 qwen-plus via DashScope）                │
│  • LangChain + LangGraph（AI 工作流编排）                  │
│  • SSE 流式输出                                           │
├─────────────────────────────────────────────────────────┤
│  数据存储层                                               │
│  • 主数据库（MySQL）    • JWT 认证                        │
└─────────────────────────────────────────────────────────┘
```

### 核心业务数据流

```
用户输入随笔 → AI 情感分析 → 能量评估 + 板块标签 + 阿响回应
                                          ↓
                                    存入随笔记录
                                          ↓
                          ┌───────────────┴───────────────┐
                          ↓                               ↓
                    即时回响展示                    触发日记生成
                                                       ↓
                                              整合当日随笔 → AI 生成第一人称日记
                                                       ↓
                                              周度报告（每周日）
                                              月度播客（每月1日）
```

### 技术栈详情

#### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | ^3.5.32 | 核心前端框架（Composition API） |
| **TypeScript** | ~6.0.2 | 类型安全 |
| **Vite** | ^8.0.10 | 构建工具 |
| **Vant 4** | ^4.9.24 | 有赞移动端 UI 组件库 |
| **Pinia** | ^3.0.4 | 状态管理 |
| **Vue Router** | ^5.0.6 | 前端路由 |
| **Axios** | ^1.15.2 | HTTP 请求客户端 |
| **ECharts** | ^6.0.0 | 数据可视化图表 |
| **Marked** | ^18.0.3 | Markdown 解析渲染 |
| **DOMPurify** | ^3.4.2 | HTML 净化（防 XSS） |
| **Capacitor 8** | ^8.3.1 | 跨平台移动端打包（Android + iOS） |

#### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** | Python 异步 Web 框架 |
| **Uvicorn** | ASGI 服务器 |
| **SQLAlchemy** | ORM 数据库工具 |
| **PyMySQL** | MySQL 数据库驱动 |
| **Alembic** | 数据库迁移工具 |
| **Pydantic Settings** | 环境变量/配置管理 |
| **python-jose** | JWT 令牌生成与验证 |
| **Passlib** | 密码哈希处理 |
| **LangChain** | LLM 应用开发框架 |
| **LangGraph** | AI 工作流图编排 |
| **DashScope** | 阿里云通义千问 API SDK |

#### 数据库

| 技术 | 用途 |
|------|------|
| **MySQL** | 主数据库（utf8mb4 字符集） |

---

## 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.10
- **MySQL** >= 8.0
- **阿里云 DashScope API Key**（用于通义千问大模型）

### 1. 克隆仓库

```bash
git clone https://github.com/YBWLawa0/nianxiang.git
cd nianxiang
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入数据库连接串和 DashScope API Key
```

编辑 `backend/.env`：

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/nianxiang?charset=utf8mb4
DASHSCOPE_API_KEY=your-dashscope-api-key
QWEN_MODEL=qwen-plus
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

启动后端服务：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
```

编辑 `frontend/.env`：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

启动开发服务器：

```bash
cd frontend
npm run dev
```

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

### 5. 移动端打包（可选）

```bash
cd frontend

# 构建 Web 产物
npm run build

# 添加 Android 平台
npx cap add android

# 同步 Web 产物到 Android
npx cap sync android

# 用 Android Studio 打开
npx cap open android
```

> iOS 打包需要在 macOS 上使用 Xcode，执行 `npx cap add ios && npx cap sync ios && npx cap open ios`

---

## 项目结构

```
nianxiang/
├── README.md                              # 项目说明文档
├── docs/
│   └── 项目部署方式.md                      # 部署文档
├── backend/                               # 后端项目
│   ├── .env.example                       # 环境变量示例
│   ├── requirements.txt                   # Python 依赖
│   └── app/
│       ├── main.py                        # FastAPI 应用入口
│       ├── api/                           # API 路由
│       │   ├── auth.py                    #   认证（注册/登录/用户信息）
│       │   ├── deps.py                    #   依赖注入
│       │   ├── diaries.py                 #   日记（生成/列表/详情/流式）
│       │   └── notes.py                   #   随笔（创建/列表/详情/删除）
│       ├── core/                          # 核心配置
│       │   ├── config.py                  #   配置管理（pydantic-settings）
│       │   └── security.py                #   JWT/密码哈希
│       ├── db/
│       │   └── session.py                 #   数据库连接与会话管理
│       ├── models/                        # 数据库模型
│       │   ├── user.py                    #   用户模型
│       │   ├── diary.py                   #   日记模型
│       │   └── note.py                    #   随笔模型
│       ├── schemas/                       # Pydantic Schema
│       │   ├── common.py                  #   公共 Schema（GridTag 枚举）
│       │   ├── diary.py                   #   日记 Schema
│       │   ├── note.py                    #   随笔 Schema
│       │   └── user.py                    #   用户 Schema
│       └── services/
│           └── ai.py                      # AI 服务（随笔评估/日记生成/流式输出）
└── frontend/                              # 前端项目
    ├── .env.example                       # 环境变量示例
    ├── package.json                       # Node.js 依赖
    ├── vite.config.ts                     # Vite 构建配置
    ├── capacitor.config.ts                # Capacitor 移动端配置
    ├── android/                           # Android 原生工程
    ├── ios/                               # iOS 原生工程
    └── src/
        ├── main.ts                        # 前端入口
        ├── App.vue                        # 根组件
        ├── style.css                      # 全局样式
        ├── api/                           # API 调用层
        │   ├── client.ts                  #   Axios 实例配置
        │   ├── auth.ts                    #   认证 API
        │   ├── diaries.ts                 #   日记 API
        │   └── notes.ts                   #   随笔 API
        ├── components/                    # 公共组件
        │   ├── NoteCard.vue               #   随笔卡片
        │   └── PageHeader.vue             #   页面头部
        ├── composables/
        │   └── useFitText.ts              # 自适应文字大小
        ├── router/
        │   └── index.ts                   # 路由配置
        ├── stores/                        # Pinia 状态管理
        │   ├── auth.ts                    #   认证状态
        │   ├── notes.ts                   #   随笔状态
        │   ├── diaries.ts                 #   日记状态
        │   └── diaryStream.ts             #   日记流式生成状态（SSE）
        ├── types/
        │   └── domain.ts                  # TypeScript 类型定义
        ├── views/                         # 页面视图
        │   ├── AuthView.vue               #   登录/注册
        │   ├── HomeView.vue               #   首页
        │   ├── RecordView.vue             #   记录随笔
        │   ├── MomentsView.vue            #   时刻/动态流
        │   ├── DiariesView.vue            #   日记列表
        │   ├── DiaryDetailView.vue        #   日记详情（流式生成）
        │   ├── NoteDetailView.vue         #   随笔详情
        │   ├── AnalysisView.vue           #   数据分析
        │   ├── WeeklyReportDetailView.vue #   周报详情
        │   ├── PodcastPlayerView.vue      #   播客播放器
        │   ├── MineView.vue               #   个人中心
        │   └── AppShell.vue               #   应用外壳/导航框架
        └── data/                          # 静态数据
            ├── monthlyPodcasts.ts         #   月度播客数据
            └── weeklyReportDetails.ts     #   周报详情数据
```

---

## API 文档

后端启动后，访问以下地址查看自动生成的 API 文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API 端点总览

#### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/auth/me` | 获取当前用户信息 |

#### 随笔模块 `/api/notes`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/notes/` | 创建随笔（后台异步 AI 评估） |
| GET | `/api/notes/` | 获取随笔列表（可按日期筛选） |
| GET | `/api/notes/{note_id}` | 获取单条随笔详情 |
| DELETE | `/api/notes/{note_id}` | 删除随笔 |

#### 日记模块 `/api/diaries`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/diaries/generate` | 生成今日日记（非流式） |
| POST | `/api/diaries/generate/stream` | 流式生成日记（SSE） |
| GET | `/api/diaries/` | 获取日记列表 |
| GET | `/api/diaries/{diary_id}` | 获取单条日记详情 |

#### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |

---

## 数据模型

### 用户表（users）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 用户 ID |
| username | String | 用户名 |
| hashed_password | String | 密码哈希 |
| created_at | DateTime | 创建时间 |

### 随笔表（notes）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 随笔 ID |
| user_id | Integer (FK) | 用户 ID |
| content | Text | 随笔内容 |
| record_date | Date | 记录日期 |
| energy_score | Integer (1-5) | 能量分数 |
| grid_tag | String | 九宫格板块标签 |
| ai_comment | Text | AI 评论（阿响回应） |
| created_at | DateTime | 创建时间 |

### 日记表（diaries）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 日记 ID |
| user_id | Integer (FK) | 用户 ID |
| diary_date | Date | 日记日期（唯一约束：每人每天最多一篇） |
| title | String | 日记标题 |
| summary | Text | 摘要 |
| content | Text | 日记正文（第一人称） |
| axiang_observation | Text | 阿响观察 |
| daily_ritual | Text | 结尾仪式（今日一问 + 鼓励） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## UI 设计规范

### 设计原则

| 原则 | 说明 |
|------|------|
| **低门槛** | 参考微信、公众号等已广泛认知的交互模式 |
| **情感化** | 阿响应像朋友一样互动，用表情包增强拟人感 |
| **温度感** | 视觉元素有温度，不冰冷 |

### 页面优先级

| 页面 | 优先级 | 说明 |
|------|--------|------|
| 记录页面 | P0 | 核心入口，语音 + 文字输入 |
| 即时回响页面 | P0 | 朋友圈/微博卡片式呈现 |
| 念响日记页面 | P0 | 公众号文章形式 |
| 用户中心页面 | P1 | 登录注册 + 付费入口 |
| 周/月/年分析页面 | P1 | 数据可视化展示 |

### 各页面设计参考

- **记录页面**：参考微信聊天界面，输入框在下方，麦克风按钮大且显眼
- **即时回响页面**：朋友圈/微博卡片式，能量条可视化（1-5 分渐变色），八大板块标签
- **日记页面**：公众号文章形式，图文并茂，封面大图，情绪/能量曲线
- **周报页面**：公众号文章链接形式
- **月度播客**：参考小宇宙 UI，打开即可听
- **年度书架**：参考微信读书书架

---

## 关键技术亮点

### 1. SSE 流式日记生成

使用 Server-Sent Events 实现日记的流式生成，用户可实时看到 AI 的创作过程，分三个阶段输出：

```
客户端 → POST /api/diaries/generate/stream → 服务端
                                                    ↓
                                              Stage 1: 日记正文（逐字流式）
                                              Stage 2: 阿响观察
                                              Stage 3: 结尾仪式
```

### 2. LangGraph 工作流编排

使用 LangGraph 编排日记生成的 AI 工作流，实现复杂的多步骤 AI 推理链。

### 3. 降级兜底机制

AI 服务不可用时，系统自动切换到基于关键词匹配的本地规则引擎，确保基本功能始终可用。

### 4. 异步 AI 评估

随笔创建后，AI 评估通过 FastAPI 的 `BackgroundTasks` 异步执行，不阻塞用户操作。

---

## 版本规划

### 黑客松阶段（2026 年 5 月）

| 时间 | 交付物 |
|------|--------|
| 5 月 2 日 | 后端 API 框架 + 数据库设计完成 |
| 5 月 2 日 | 阿响 Agent v1（对话 + 情感分析） |
| 5 月 2 日 | 移动端 UI 框架 + 核心页面完成 |
| 5 月 2 日 | 日记生成引擎 + 周度报告可视化 |
| 5 月 3 日 | 黑客松路演 + Demo 演示 |

### 产品上线规划

| 里程碑 | 时间 | 目标 |
|--------|------|------|
| Alpha 测试 | 6 月上旬 | 内部测试 + 亲友测试 |
| Beta 测试 | 6 月下旬 | 100 人种子用户测试 |
| v1.0 上线 | 7 月中旬 | App Store + 应用宝双端上线 |
| v1.1 迭代 | 8 月上旬 | 根据用户反馈优化 |
| 1000 用户 | 8 月底 | 达成 1000 注册用户 |

---

## 商业模式

| 版本 | 价格 | 功能 |
|------|------|------|
| 免费版 | 0 元 | 每日最多 5 条记录、基础日记生成、周报告 |
| Pro 版 | 12 元/月 或 128 元/年 | 无限记录、月度播客、年度传记、高级数据分析、导出功能 |
| 团队版 | 待定 | 企业 EAP 服务、团队情绪健康管理 |

---

## 团队协作

### 分支策略

| 分支 | 用途 |
|------|------|
| `master` | 稳定版本 |
| `dev` | 日常开发 |

### 协作流程

1. 从 `dev` 分支创建功能分支：`git checkout -b feature/你的功能名`
2. 开发完成后提交并推送
3. 发起 Pull Request，请团队成员审核
4. 审核通过后合并到 `dev` 分支

---

## 许可证

本项目参加 Flux 南客松 S2 黑客松。

---

<p align="center">
  Made with ❤️ by 念想团队
</p>
