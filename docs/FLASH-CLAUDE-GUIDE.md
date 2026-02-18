# 🎬 Day One Film AI - Flash + Claude 使用指南

> **双模型配置**：Gemini 2.0 Flash + Claude 3.5 Sonnet

---

## 📊 模型分工

### Gemini 2.0 Flash（主力 - 80%）

**特点**：
- ⚡ 速度极快
- 💰 成本最低（¥0.003/1K tokens）
- 🇨🇳 中文优秀

**负责模块**：
```
B模块 - 场景搜索
├── 场景理解
├── 关键词生成
├── 结果排序
└── 图片分析（Vision版）

快速任务
├── 简单查询
├── 缓存命中
└── 批量处理
```

**使用场景**：
- 用户输入"雨夜追车"→Flash理解→生成关键词
- 搜索结果快速排序
- 高频查询（可缓存）

---

### Claude 3.5 Sonnet（专业 - 20%）

**特点**：
- 🧠 推理能力最强
- ✍️ 创意写作优秀
- 📚 长文本理解（200K上下文）

**负责模块**：
```
A模块 - 剧本拆解
├── 剧本解析
├── 场景提取
├── 分镜生成
└── 角色分析

复杂任务
├── 创意描述
├── 导演大脑训练
└── 复杂场景分析
```

**使用场景**：
- 上传剧本→Claude深度解析→提取场景
- 生成分镜脚本
- 导演风格学习

---

## 💰 成本对比

### 单任务成本

| 任务 | Flash | Claude | 节省 |
|------|-------|--------|------|
| 场景理解 | ¥0.0015 | ¥0.0075 | 80% |
| 剧本解析 | ¥0.015 | ¥0.075 | 不可比* |
| 分镜生成 | ¥0.003 | ¥0.015 | 80% |

*Claude在剧本解析上不可替代

### 月度成本预估

**开发期**（每天1000次调用）：
```
Flash: 800次 × 500tokens × ¥0.003/1K = ¥1.2/天
Claude: 200次 × 1000tokens × ¥0.015/1K = ¥3/天
日均: ¥4.2
月费: ¥126
```

**优化后**（使用缓存）：
```
Flash: ¥1.2/天 × 0.7(缓存30%) = ¥0.84/天
Claude: ¥3/天 (不缓存)
日均: ¥3.84
月费: ¥115
```

---

## 🔧 配置方法

### 1. API易配置

**获取API Key**：
```
1. 访问 https://api.apiyi.com
2. 注册/登录账号
3. 充值余额（建议¥200）
4. 创建API Key
5. 确保有权限：Gemini 2.0 Flash + Claude 3.5 Sonnet
```

**配置环境变量**：
```bash
# backend/.env

# API易配置
APIYI_BASE_URL=https://api.apiyi.com/v1
APIYI_API_KEY=your_apiyi_key_here

# 模型选择（双模型）
AI_PROVIDER=flash  # 默认用Flash

# 具体模型名称
FLASH_MODEL=gemini-2.0-flash
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 2. 代码中使用

**B模块 - 场景搜索（用Flash）**：
```python
from app.services.ai_interface import AIProviderFactory

# 创建Flash实例
flash = AIProviderFactory.create(
    "flash",
    api_key=settings.APIYI_API_KEY,
    base_url=settings.APIYI_BASE_URL
)

# 场景理解（快速、便宜）
understanding = await flash.understand_scene("雨夜追车")
```

**A模块 - 剧本拆解（用Claude）**：
```python
from app.services.ai_interface import AIProviderFactory

# 创建Claude实例
claude = AIProviderFactory.create(
    "claude",
    api_key=settings.APIYI_API_KEY,
    base_url=settings.APIYI_BASE_URL
)

# 剧本解析（深度、创意）
script_analysis = await claude.parse_script(script_content)

# 生成分镜
shots = await claude.generate_shots("雨夜追车场景")
```

**智能路由（自动选择）**：
```python
async def smart_search(query: str, task_type: str = "simple"):
    """根据任务类型自动选择模型"""
    
    if task_type == "simple":
        # 简单任务 → Flash（快、便宜）
        provider = AIProviderFactory.create("flash", ...)
    elif task_type == "complex":
        # 复杂任务 → Claude（准、创意）
        provider = AIProviderFactory.create("claude", ...)
    
    return await provider.understand_scene(query)
```

---

## 🎯 最佳实践

### 1. 任务分级

**简单任务** → Flash（90%场景）：
- 场景描述理解
- 关键词提取
- 结果排序
- 用户闲聊

**复杂任务** → Claude（10%场景）：
- 剧本解析
- 分镜生成
- 创意写作
- 复杂推理

### 2. 缓存策略

**Flash结果缓存**（1小时）：
```python
# 相同查询缓存
if query in cache:
    return cache[query]

result = await flash.understand_scene(query)
cache[query] = result  # 缓存1小时
```

**Claude结果不缓存**（每次都不同）：
```python
# 剧本解析每次都要新的
result = await claude.parse_script(script)
# 不缓存，每次调用都付费
```

### 3. 降级策略

**成本超过阈值** → 切换到Flash：
```python
if daily_cost > 50:  # ¥50/天
    use_model = "flash"  # 强制用便宜的
```

---

## 📈 性能对比

### 响应时间

| 任务 | Flash | Claude | 差异 |
|------|-------|--------|------|
| 场景理解 | 0.5s | 2.5s | 5倍 |
| 剧本解析 | - | 8s | - |
| 分镜生成 | 1s | 4s | 4倍 |

### 质量对比

| 任务 | Flash | Claude | 推荐 |
|------|-------|--------|------|
| 场景理解 | ⭐⭐⭐ | ⭐⭐⭐⭐ | Flash够用 |
| 剧本解析 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 必须用Claude |
| 分镜生成 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 推荐Claude |
| 创意写作 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 推荐Claude |

---

## 🚨 注意事项

### 1. Claude限制

```
❌ 不支持图片分析（用Gemini Vision）
❌ 不支持Function Calling
✅ 支持200K长文本
✅ 支持Streaming
```

### 2. 成本控制

```python
# 设置每日预算
DAILY_BUDGET = 50  # ¥50/天

# 监控用量
if daily_usage > DAILY_BUDGET * 0.8:
    send_alert("预算即将用完")
```

### 3. 错误处理

```python
try:
    result = await claude.parse_script(script)
except Exception as e:
    # 降级到Flash
    result = await flash.understand_scene(script[:1000])
```

---

## 🎬 立即开始

**Step 1**: 去API易充值（¥200）
```
https://api.apiyi.com
```

**Step 2**: 复制API Key到 `.env`
```bash
APIYI_API_KEY=your_key_here
```

**Step 3**: 测试双模型
```bash
# 测试Flash
curl "http://localhost:8000/api/search?model=flash&query=雨夜追车"

# 测试Claude
curl "http://localhost:8000/api/script/parse?model=claude"
```

**Step 4**: 开始开发！

---

**双模型配置完成！开始高效开发！** 🚀🎬
