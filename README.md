# 🎬 Day One Film AI — 影视场景搜索

> **一个小实验 · A small experiment**  
> 用 AI 搜影视场景，发现 API 世界的开放与封闭。

---

## 🇨🇳 中文

### 这是什么？

一个用 AI 搜索影视场景的小工具。输入"雨夜追车"，它试图告诉你哪些电影里有类似画面。

**这只是个试验品。** 代码粗糙，功能简陋，但确实能跑。

### 一点心得

做这个小项目的过程中，最大的感触是：

**中国大陆的"大厂"们，API 接口和资源根本不共享，封闭得要命。** 想调个数据比登天还难。

反而是国外的 YouTube、TMDB 这些平台，**更加开放和包容**。文档清晰，API 免费额度大方，开发者体验好太多。

这挺讽刺的——号称开放的互联网，实际上最开放的却是那些被"墙"在外的服务。

### 技术局限

这个项目**做不到精确到秒的时间戳定位**，因为拿不到向量数据库级别的影视数据。要实现那种精度，需要大规模的影视素材库 + 向量化索引，这不是一个小项目能搞定的。

### 未来

如果感兴趣的小伙伴想接着开发，欢迎 fork。可以尝试的方向：
- 接入真正的向量数据库（Milvus / Pinecone）
- 构建影视镜头数据集
- 细化到帧级别的场景匹配

---

## 🇬🇧 English

### What is this?

A small tool that uses AI to search for film scenes. Type "rainy night car chase" and it tries to find which movies have similar visuals.

**This is just an experiment.** The code is rough, the features are basic, but it works.

### A Reflection

The biggest takeaway from building this project:

**Big tech companies in mainland China keep their APIs and resources locked down tight.** Getting access to data feels like pulling teeth.

Meanwhile, platforms like **YouTube and TMDB are far more open and inclusive** — clear documentation, generous free tiers, and a developer experience that actually respects your time.

It's ironic. The so-called "open internet" is most open on the side that's blocked at the firewall.

### Technical Limitations

This project **cannot pinpoint scenes down to the exact second**, because we don't have access to vector-database-grade film data. True scene-level precision would require:
- Large-scale film footage libraries
- Vectorized indexing infrastructure
- Frame-level analysis pipelines

That's beyond what a small experiment can achieve.

### Future

If you're interested in picking this up, feel free to fork. Ideas to explore:
- Integrate real vector databases (Milvus / Pinecone)
- Build a film shot dataset
- Implement frame-level scene matching

---

## 🚀 Quick Start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python run_simple.py
```

Then open `http://localhost:8000/static/search.html`

### API 测试 / API Test

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "雨夜追车", "limit": 5}'
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.10+ |
| AI | Gemini 2.0 Flash (via APIYi) |
| Data Sources | Douban API + mock data |
| Frontend | Vanilla HTML/CSS/JS |

---

## 📁 Project Structure

```
.
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic (AI providers, search aggregation)
│   │   └── main.py       # Entry point
│   ├── static/           # Static frontend files
│   └── requirements.txt
├── docs/                 # Documentation
└── PROJECT-OVERVIEW.md   # Detailed project overview
```

---

## 📝 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/search` | Search film scenes by description |
| GET | `/api/favorites` | Get user favorites |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger API documentation |

---

## 📄 License

MIT

---

*Made with curiosity. Built with frustration. Shared with hope.*
