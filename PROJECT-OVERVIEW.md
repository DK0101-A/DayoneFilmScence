# 🎬 Day One Film AI - 项目总览

> **项目状态**: Day 1 完成 ✅  
> **当前阶段**: B模块开发 - 项目初始化完成  
> **技术栈**: FastAPI + Gemini (AI Studio) → 后期迁移国产模型  

---

## 📁 项目结构

```
/Users/seven/Desktop/v/
├── 📁 .opencode/              # OpenCode配置（自动备份等）
├── 📁 docs/                   # 文档目录
│   ├── PRD-v2.0.md           # 产品需求文档（A→E全模块）
│   ├── Phase1-Implementation-Plan-v2.md  # 修订版实施计划
│   └── Phase1-AIStudio-Plan.md           # AI Studio快速验证计划
│
├── 📁 backend/                # 后端代码
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   └── search.py     # 搜索API路由
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_interface.py      # AI提供商抽象接口
│   │   │   ├── gemini_provider.py   # Gemini实现（开发期）
│   │   │   └── search_aggregator.py # 多源搜索聚合
│   │   │
│   │   ├── 📁 models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📁 utils/
│   │   │   └── __init__.py
│   │   │
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI主应用入口
│   │   └── config.py         # 配置文件
│   │
│   ├── 📁 tests/
│   │   └── (测试文件待创建)
│   │
│   ├── 📁 venv/              # Python虚拟环境
│   │
│   ├── requirements.txt      # Python依赖
│   ├── .env.example          # 环境变量示例
│   ├── start.sh              # 启动脚本（已添加执行权限）
│   └── README.md             # 后端文档
│
├── 📁 frontend/              # 前端代码（待开发）
│
├── 📁 video/                 # 视频文件（需求参考）
│   ├── A.mp4
│   ├── b.mp4
│   └── c.mp4
│
└── opencode.jsonc            # OpenCode项目配置
```

---

## ✅ Day 1 完成内容

### 1. 需求文档 ✅
- [x] PRD-v2.0.md - 完整产品需求（A→E模块）
- [x] 商业模式设计（工具收费 + 导演大脑IP）
- [x] AI Studio快速验证策略
- [x] 分层收费技术方案（Gemini→国产模型）

### 2. 后端架构 ✅
- [x] 项目目录结构
- [x] Python虚拟环境
- [x] 依赖管理（requirements.txt）
- [x] 环境变量配置（.env.example）

### 3. 核心代码 ✅
- [x] 配置模块（config.py）
- [x] AI抽象接口层（ai_interface.py）
- [x] Gemini提供商实现（gemini_provider.py）
- [x] 搜索聚合服务（search_aggregator.py）
- [x] FastAPI主应用（main.py）
- [x] 搜索API路由（search.py）

### 4. 工具脚本 ✅
- [x] 启动脚本（start.sh）
- [x] 后端README文档

---

## 🚀 下一步（Day 2）

### 任务清单

#### 1. API密钥申请 🔑
**优先级**: P0（阻塞后续开发）

- [ ] **Google AI Studio**
  - 访问: https://aistudio.google.com/app/apikey
  - 创建API Key
  - 复制到 `.env` 文件
  - 免费额度：60次/分钟

- [ ] **豆瓣API**（可选）
  - 访问: https://developers.douban.com
  - 申请开发者权限
  - 获取API Key

#### 2. 本地测试 🧪
```bash
# 1. 进入目录
cd /Users/seven/Desktop/v/backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 添加 GEMINI_API_KEY

# 5. 启动服务
./start.sh
# 或
uvicorn app.main:app --reload

# 6. 测试API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "雨夜追车", "limit": 5}'
```

#### 3. 扣子Agent配置 🤖
- [ ] 注册扣子开发者账号
- [ ] 创建"影视场景搜索"Agent
- [ ] 配置工作流（调用后端API）
- [ ] 测试完整流程

---

## 💡 关键技术决策

### 1. AI分层策略
```
开发期 (现在):
  └── Gemini (AI Studio免费额度)
      └── 最强能力，快速验证

生产期 (未来):
  ├── 基础版: 豆包/通义 (低成本)
  ├── 专业版: Gemini (能力强)
  └── 旗舰版: Gemini+ (更多功能)
```

### 2. 架构优势
- ✅ **抽象接口层**: 便于切换AI提供商
- ✅ **工厂模式**: 运行时动态选择AI
- ✅ **多源搜索**: 聚合多个数据源
- ✅ **分层收费友好**: 不同AI对应不同定价

### 3. 商业模式集成点
```python
# 根据用户等级选择AI
if user.tier == "free":
    ai_provider = DoubaoProvider()  # 免费
elif user.tier == "pro":
    ai_provider = GeminiProvider()  # 付费
```

---

## 📊 进度跟踪

### Week 1 目标
- [x] Day 1: 项目初始化 ✅
- [ ] Day 2: API密钥 + 本地测试
- [ ] Day 3: 扣子对接
- [ ] Day 4-5: 功能完善
- [ ] Day 6-7: 测试优化

### 成功标准
- ✅ 输入"雨夜追车"返回10个相关影视参考
- ✅ 每个结果有AI匹配度评分
- ✅ 能在豆包里直接使用
- ✅ 响应时间 < 5秒

---

## 🔗 重要链接

### 文档
- [产品需求文档](./docs/PRD-v2.0.md)
- [实施计划](./docs/Phase1-AIStudio-Plan.md)
- [后端文档](./backend/README.md)

### API
- AI Studio: https://aistudio.google.com/app/apikey
- 扣子平台: https://www.coze.cn

### 开发
- 后端服务: http://localhost:8000
- API文档: http://localhost:8000/docs

---

## 📝 待办事项

### 高优先级
- [ ] 申请 GEMINI_API_KEY
- [ ] 本地测试通过
- [ ] 扣子Agent配置

### 中优先级
- [ ] 错误处理完善
- [ ] 日志记录
- [ ] 单元测试

### 低优先级
- [ ] 性能优化
- [ ] 缓存机制
- [ ] 监控告警

---

## 🎬 总结

**Day 1 完成**: 项目基础架构搭建完成，代码结构清晰，支持多AI提供商切换，为后期分层收费打下技术基础。

**下一步**: 申请API密钥，本地测试，扣子对接。

**预计**: 2周内完成B模块MVP！

---

**最后更新**: 2024-02-18  
**版本**: v0.1.0-alpha
