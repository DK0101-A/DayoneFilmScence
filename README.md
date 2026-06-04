# 🎬 Day One Film AI — 影视场景搜索

> **一个小实验 · A small experiment**  
> 用 AI 搜影视场景，发现 API 世界的开放与封闭。

---

## 🇨🇳 中文

### 这是什么？

一个用 AI 搜索影视场景的小工具。输入"雨夜追车"，它试图告诉你哪些电影里有类似画面。

**这只是个试验品。** 代码粗糙，功能简陋，但确实能跑。

### 开发初衷

我是个喜欢电影的小导演，有时候脑海里有一个画面，想找某部电影或电视剧里的类似场景做参考——但翻遍全网也搜不到。

Google 搜"雨夜追车"，出来的全是影评，没有一帧画面是对得上的。

于是就想着，能不能用 AI 来搜？

### 关于这个项目

这是我的第一个 **vibe coding** 试验项目。虽然没达到预期效果，但**至少走完了一遍完整的流程**：从需求梳理 → 搭后端 → 接 AI → 出结果，实现了小闭环。

代码不完美，但能跑。经验有了，下次就知道怎么做了。

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

**Contact:** xdnsun@gmail.com

> **Note:** The `.env` file with real API keys has been removed from git tracking.  
> Your keys stay local — they'll never be committed.

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

### 🔑 Getting API Keys

This project uses AI APIs for scene search. Here's how to get your own keys for free:

#### Google Gemini API (Recommended)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy the key and add it to your `.env` file:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```
5. Free tier: **60 requests per minute** — plenty for development

#### Alternative: APIYi (OpenAI-compatible, Chinese-friendly)
1. Visit [apiyi.com](https://api.apiyi.com)
2. Register an account
3. Top up a small amount (¥1-10 is enough for testing)
4. Get your API key and configure:
   ```bash
   OPENAI_BASE_URL=https://api.apiyi.com/v1
   OPENAI_API_KEY=your_apiyi_key_here
   AI_MODEL=gemini-2.0-flash
   ```

#### Optional: TMDB API (for movie metadata)
1. Go to [TMDB](https://www.themoviedb.org/settings/api)
2. Register an account
3. Request an API key (free for non-commercial use)
4. Add to `.env`:
   ```bash
   TMDB_API_KEY=your_tmdb_key_here
   ```

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
