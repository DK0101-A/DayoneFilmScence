# 🎬 Day One Film AI

AI驱动的影视场景参考搜索工具 - 帮助导演快速找到相似场景的影视参考

## ✨ 功能特性

- 🔍 **智能场景搜索**: 输入场景描述，AI自动分析并推荐相似影视作品
- ⏱️ **精确时间戳**: 提供场景出现的具体时间（如 00:32:15）
- 🎯 **AI匹配度评分**: 每部影片都有匹配度百分比和匹配理由
- 🎨 **现代UI界面**: 响应式设计，支持移动端
- 🤖 **扣子Agent集成**: 可在豆包APP中直接使用

## 🚀 快速开始

### 1. 本地运行

```bash
cd backend
pip install -r requirements.txt
python run_full.py
```

访问 http://localhost:8000/static/search.html

### 2. API测试

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "雨夜追车", "limit": 5}'
```

## 🛠️ 技术栈

- **后端**: FastAPI + Python 3.10+
- **AI模型**: Gemini 2.0 Flash (via API易)
- **数据源**: 豆瓣API + 模拟数据
- **前端**: 纯HTML/CSS/JS

## 📁 项目结构

```
.
├── backend/               # FastAPI后端
│   ├── app/              # 应用代码
│   │   ├── api/          # API路由
│   │   ├── services/     # 业务逻辑
│   │   └── main.py       # 应用入口
│   ├── static/           # 静态文件
│   └── requirements.txt  # 依赖
├── docs/                 # 文档
└── PROJECT-OVERVIEW.md   # 项目总览
```

## 🔑 环境变量

创建 `backend/.env` 文件：

```bash
OPENAI_BASE_URL=https://api.apiyi.com/v1
OPENAI_API_KEY=your_api_key
AI_MODEL=gemini-2.0-flash
```

获取 API Key: https://api.apiyi.com

## 🤖 扣子集成

查看详细配置指南: `docs/COZE-SETUP-GUIDE.md`

## 📝 API文档

启动服务后访问: http://localhost:8000/docs

### 主要端点

- `POST /api/search` - 搜索影视场景
- `GET /api/favorites/favorites` - 获取收藏列表
- `GET /health` - 健康检查

## 🌟 示例

**搜索**: 雨夜追车

**返回结果**:
```json
{
  "title": "银翼杀手2049",
  "year": "2017",
  "rating": 8.3,
  "relevance_score": 95,
  "timestamp": "01:12:00",
  "timestamp_note": "K追逐Sapper Morton的雨夜片段",
  "explanation": "洛...