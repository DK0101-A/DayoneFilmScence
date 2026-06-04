# 🎬 Day One Film AI - 推荐模型集合

> 针对影视场景搜索工具的优化模型配置策略

---

## 📊 核心模型组合（推荐）

### 🥇 主力模型：Gemini 2.0 Flash
```yaml
用途: 场景搜索、简单分析、快速响应
价格: ¥0.003/1K tokens（最便宜）
占比: 80%调用量
优势: 速度快、成本低、中文好
适用: B模块场景理解、基础搜索
```

### 🥈 增强模型：Gemini 1.5 Pro
```yaml
用途: 剧本解析、复杂场景、长文本
价格: ¥0.007/1K tokens（2.3倍）
占比: 15%调用量
优势: 长上下文、结构化输出稳定
适用: A模块剧本拆解、复杂场景分析
```

### 🥉 专业模型：Claude 3.5 Sonnet
```yaml
用途: 创意生成、剧本分析、高级功能
价格: ¥0.015/1K tokens（5倍）
占比: 5%调用量
优势: 创意写作最强、推理能力好
适用: 分镜生成、提示词优化、导演大脑训练
```

---

## 🎯 分模块模型策略

### B模块：场景搜索（当前开发中）

| 功能 | 主模型 | 备用模型 | 说明 |
|------|--------|----------|------|
| 场景理解 | Gemini 2.0 Flash | Gemini 1.5 Pro | 简单理解用Flash，复杂用Pro |
| 关键词生成 | Gemini 2.0 Flash | - | 简单任务 |
| 结果排序 | Gemini 2.0 Flash | - | 快速排序 |
| 图片分析 | Gemini 1.5 Pro Vision | - | 多模态分析剧照 |

**预估成本**: ¥30-50/月（开发期）

### A模块：剧本拆解（下一步开发）

| 功能 | 主模型 | 备用模型 | 说明 |
|------|--------|----------|------|
| 剧本解析 | Gemini 1.5 Pro | Claude 3.5 Sonnet | 长文本处理 |
| 场景提取 | Gemini 1.5 Pro | - | 结构化输出 |
| 分镜生成 | Gemini 2.0 Flash | Claude 3.5 Sonnet | 创意描述 |
| 角色分析 | Claude 3.5 Sonnet | - | 人物理解 |

**预估成本**: ¥50-100/月（含B模块）

### C/D/E模块：高级功能（后期）

| 功能 | 推荐模型 | 说明 |
|------|----------|------|
| 风格分析 | Gemini 1.5 Pro Vision | 视觉风格理解 |
| 提示词生成 | Claude 3.5 Sonnet | AI绘画/视频提示词 |
| 导演大脑训练 | Claude 3.5 Sonnet | 模式学习 |
| 视频生成对接 | 官方API | Sora/可灵/Runway |

**预估成本**: ¥100-300/月（全功能）

---

## 💰 成本优化策略

### 策略1：智能降级
```python
if cost_today > 50:  # 超过¥50
    use_model = "gemini-2.0-flash"  # 自动切到便宜模型
```

### 策略2：缓存复用
- 相同查询缓存1小时
- 预估节省30%调用量

### 策略3：批量处理
- 合并多个小请求
- 减少API调用次数

### 策略4：分层收费对应
```
免费版/基础版: 只用 Gemini 2.0 Flash
专业版:         Gemini 2.0 Flash + Gemini 1.5 Pro
旗舰版:         全模型 + Claude 3.5 Sonnet
```

---

## 📈 用量预估与成本

### 开发期（1-2个月）
```
日调用量: 1,000次
平均tokens: 500/次
月用量: 15M tokens
费用: ¥45-60/月
```

### 内测期（50用户）
```
日调用量: 5,000次
月用量: 75M tokens
费用: ¥200-300/月
```

### 生产期（1000用户）
```
日调用量: 50,000次
月用量: 750M tokens
费用: ¥1,500-2,000/月
优化后: ¥800-1,000/月（用缓存+降级）
```

---

## 🔧 配置方法

### 方法1：API易（国内，推荐开发期）
```bash
# 配置文件: .env.apiyi
APIYI_BASE_URL=https://api.apiyi.com/v1
APIYI_API_KEY=your_key_here

# 模型选择
SCENE_MODEL=gemini-2.0-flash
SCRIPT_MODEL=gemini-1.5-pro
VISION_MODEL=gemini-1.5-pro-vision
```

### 方法2：官方Google（最便宜，长期用）
```bash
# 配置文件: .env.google
GEMINI_API_KEY=your_key_here

# 模型选择
SCENE_MODEL=gemini-2.0-flash
SCRIPT_MODEL=gemini-1.5-pro
VISION_MODEL=gemini-1.5-pro-vision
```

### 方法3：混合策略（最佳性价比）
```bash
# 简单任务用官方（便宜）
# 复杂任务用API易（稳定）
# 创意任务用Claude（能力强）
```

---

## 🚀 立即实施方案

### 第一阶段（本周）：基础版
```yaml
模型: Gemini 2.0 Flash (100%)
成本: ¥30-50/月
功能: B模块场景搜索
```

### 第二阶段（下周）：标准版
```yaml
模型: 
  - Gemini 2.0 Flash (70%)
  - Gemini 1.5 Pro (30%)
成本: ¥100-150/月
功能: B模块 + A模块剧本拆解
```

### 第三阶段（下月）：专业版
```yaml
模型:
  - Gemini 2.0 Flash (60%)
  - Gemini 1.5 Pro (25%)
  - Claude 3.5 Sonnet (15%)
成本: ¥200-300/月
功能: 全模块A+B+C+D+E
```

---

## 📝 配置文件位置

```
backend/.env.models  # 模型集合配置
```

**使用时**:
```bash
# 复制对应配置
cp .env.models .env

# 或
source .env.models
```

---

## ✅ 选择建议

**立即开始（今天）**:
- ✅ Gemini 2.0 Flash（API易或官方）
- ✅ 成本：¥30-50/月
- ✅ 足够B模块开发

**下周升级**:
- ➕ 添加 Gemini 1.5 Pro
- ➕ 用于A模块剧本拆解

**后期优化**:
- ➕ 添加 Claude 3.5 Sonnet
- ➕ 用于高级创意功能

---

**推荐配置：先上 Gemini 2.0 Flash，便宜够用！** 🎬🚀
