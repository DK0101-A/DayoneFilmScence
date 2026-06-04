# 🚀 Day One Film AI 部署指南

## 方案1: Render（推荐，完全免费）

### 步骤1: 准备代码

确保代码已推送到GitHub：
```bash
# 1. 创建GitHub仓库（在 https://github.com/new）
# 仓库名: day-one-film-ai

# 2. 推送代码
git remote add origin https://github.com/YOUR_USERNAME/day-one-film-ai.git
git branch -M main
git push -u origin main
```

### 步骤2: 部署到Render

1. 访问 https://dashboard.render.com
2. 点击 **New +** → **Web Service**
3. 连接你的GitHub仓库
4. 配置如下：
   - **Name**: `day-one-film-ai`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python run_full.py`

5. 添加环境变量：
   ```
   OPENAI_API_KEY = sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
   APIYI_API_KEY = sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
   OPENAI_BASE_URL = https://api.apiyi.com/v1
   AI_MODEL = gemini-2.0-flash
   ```

6. 点击 **Create Web Service**

7. 等待部署完成（约3-5分钟）

### 步骤3: 验证部署

```bash
# 替换为你的Render URL
curl https://day-one-film-ai.onrender.com/health
```

访问前端界面：
```
https://day-one-film-ai.onrender.com/static/search.html
```

---

## 方案2: Railway（免费额度）

### 步骤1: 准备代码

同上，确保代码在GitHub

### 步骤2: 部署到Railway

1. 访问 https://railway.app
2. 点击 **New Project** → **Deploy from GitHub repo**
3. 选择你的仓库
4. 点击 **Deploy**

Railway会自动读取 `railway.json` 配置

### 步骤3: 配置环境变量

1. 进入项目 → **Variables**
2. 添加：
   ```
   OPENAI_API_KEY = sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
   APIYI_API_KEY = sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
   ```

3. 重新部署

---

## 方案3: Vercel（Serverless，适合前端）

Vercel适合部署前端，后端API需要额外配置。

建议：只部署前端静态文件，后端使用Render/Railway

---

## 方案4: 自有服务器/VPS

### 使用Docker部署

```bash
# 1. 构建镜像
docker build -t day-one-film-ai .

# 2. 运行容器
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487 \
  -e APIYI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487 \
  --name day-one-film-ai \
  day-one-film-ai
```

### 使用Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
      - APIYI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487
    restart: unless-stopped
```

---

## 🔑 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | API易的API Key | sk-xxx |
| `APIYI_API_KEY` | 同上（兼容性） | sk-xxx |
| `OPENAI_BASE_URL` | API基础URL | https://api.apiyi.com/v1 |
| `AI_MODEL` | 使用的模型 | gemini-2.0-flash |

---

## 🧪 部署后测试

```bash
# 测试健康检查
curl https://your-app-url.com/health

# 测试搜索API
curl -X POST https://your-app-url.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "雨夜追车", "limit": 3}'

# 测试前端
curl https://your-app-url.com/static/search.html
```

---

## 🤖 更新扣子配置

部署完成后：

1. 更新扣子Agent的API地址：
   ```
   旧: http://localhost:8000/api/search
   新: https://your-app-url.com/api/search
   ```

2. 重新发布扣子Agent

3. 在豆包中测试

---

## 📝 域名配置（可选）

### Render自定义域名

1. 在Render控制台 → **Settings** → **Custom Domains**
2. 添加你的域名
3. 按提示配置DNS

### Railway自定义域名

1. 在Railway控制台 → **Settings** → **Domains**
2. 生成railway.app子域名或添加自定义域名

---

## 🔒 安全建议

1. **不要在代码中硬编码API Key** - 使用环境变量
2. **限制API调用频率** - 在Render/Railway设置限流
3. **启用HTTPS** - Render和Railway默认提供
4. **定期轮换API Key** - 在API易控制台重新生成

---

## 💰 成本估算

| 平台 | 费用 | 限制 |
|------|------|------|
| Render | 免费 | 15分钟无活动休眠，首次访问慢 |
| Railway | 免费$5/月额度 | 超出后按量付费 |
| Vercel | 免费 | 适合前端，后端有限制 |
| VPS | $5-10/月 | 无限制 |

---

## 🆘 故障排除

### 部署失败

```bash
# 检查日志
render logs  # 或 railway logs

# 本地测试Docker
docker build -t test .
docker run -p 8000:8000 test
```

### API调用失败

- 检查环境变量是否正确设置
- 确认API Key有效
- 查看API易余额

### 前端404

- 确认静态文件服务配置正确
- 检查 `static/` 目录是否存在

---

## 🎉 完成！

部署成功后：
1. ✅ 公网URL可访问
2. ✅ 扣子Agent可对接
3. ✅ 用户可通过豆包使用
4. ✅ 可在浏览器直接使用

**预计时间**: 10-15分钟