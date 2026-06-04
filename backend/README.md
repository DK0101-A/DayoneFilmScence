# 🎬 Day One Film AI - Backend

> 影视场景参考搜索工具后端服务  
> AI驱动的导演助手，快速找到相似场景的影视参考

---

## 📋 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI主应用入口
│   ├── config.py            # 配置文件（环境变量）
│   ├── api/
│   │   ├── __init__.py
│   │   └── search.py        # 搜索API路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_interface.py  # AI提供商抽象接口
│   │   ├── gemini_provider.py # Gemini实现（开发期）
│   │   └── search_aggregator.py # 多源搜索聚合
│   ├── models/              # 数据模型
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
├── requirements.txt         # Python依赖
├── .env.example             # 环境变量示例
├── start.sh                 # 启动脚本
└── README.md
```

---

## 🚀 快速开始

### 1. 克隆项目并进入目录

```bash
cd /Users/seven/Desktop/v/backend
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 API Keys
```

**必须配置**:
- `GEMINI_API_KEY`: 从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取（免费）

**可选配置**:
- `DOUBAN_API_KEY`: 豆瓣API Key（可选）

### 5. 启动服务

```bash
# 方法1：使用启动脚本
./start.sh

# 方法2：直接启动
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问API

- **API文档**: http://localhost:8000/docs (Swagger UI)
- **API端点**: http://localhost:8000/api/search
- **健康检查**: http://localhost:8000/health

---

## 📡 API使用示例

### 搜索影视场景

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "雨夜追车",
    "limit": 10
  }'
```

**返回示例**:
```json
{
  "query": "雨夜追车",
  "ai_understanding": {
    "scene_elements": ["雨夜", "追车", "紧张"],
    "keywords_zh": ["雨夜追车 电影", ...],
    "keywords_en": ["rainy night car chase", ...],
    "mood": "紧张刺激",
    "similar_movies": ["《盗梦空间》", "《亡命驾驶》"]
  },
  "results": [
    {
      "title": "盗梦空间",
      "year": "2010",
      "rating": 9.3,
      "relevance_score": 95,
      "explanation": "包含雨夜追车的紧张氛围和高速动作场面"
    }
  ],
  "total_found": 15,
  "search_time": 2.5,
  "ai_provider": "gemini",
  "ai_model": "gemini-pro"
}
```

### 简单搜索（GET）

```bash
curl "http://localhost:8000/api/search/simple?query=办公室争吵&limit=5"
```

---

## 🏗️ 架构设计

### 分层架构

```
API层 (FastAPI)
    ↓
服务层 (Services)
    ├── AI提供商接口 (AISceneProvider)
    │   ├── GeminiProvider (开发期)
    │   └── DoubaoProvider (生产环境)
    └── 搜索聚合器 (SearchAggregator)
        ├── 豆瓣搜索
        └── 其他数据源
    ↓
数据源层
    ├── 豆瓣API
    ├── TMDB API
    └── 其他影视数据库
```

### 核心特性

1. **多AI提供商支持**: 通过抽象接口支持Gemini、豆包、通义千问等
2. **分层收费友好**: 不同AI能力对应不同收费层级
3. **多源搜索**: 聚合多个数据源，提高覆盖率
4. **AI智能排序**: 不只是关键词匹配，而是语义理解排序

---

## 🔧 开发计划

### Phase 1: AI Studio快速验证（当前）
- ✅ 项目初始化
- ✅ Gemini集成
- ✅ 基础搜索API
- 🔄 扣子Agent对接

### Phase 2: 功能增强
- [ ] 图片分析（Gemini Vision）
- [ ] 收藏功能
- [ ] 历史记录
- [ ] 更多数据源

### Phase 3: 迁移到国产模型
- [ ] 豆包提供商实现
- [ ] 通义千问提供商实现
- [ ] 智能路由（根据用户等级选择AI）
- [ ] 分层收费实现

---

## 💰 商业模式集成

```
免费版/基础版:
  └── 豆包/通义 (成本低)

专业版:
  └── Gemini (能力强)

旗舰版:
  └── Gemini + 更多数据源 + 高级功能
```

通过 `AI_PROVIDER` 环境变量切换不同层级。

---

## 📝 待办事项

- [ ] 完善错误处理
- [ ] 添加日志记录
- [ ] 实现缓存机制
- [ ] 添加限流保护
- [ ] 编写测试用例
- [ ] 部署脚本

---

## 🤝 贡献

本项目遵循 Superpower 开发模式，所有开发过程沉淀为 Skill。

---

## 📄 许可证

MIT License
