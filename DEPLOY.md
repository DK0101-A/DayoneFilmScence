# 服务器部署指南

## 1. 上传项目到服务器

### 方法A：使用宝塔文件管理器
1. 登录宝塔面板
2. 打开**文件**管理器
3. 进入 `/www/wwwroot/` 目录
4. 上传项目文件夹（或创建新目录）

### 方法B：使用Git克隆
```bash
cd /www/wwwroot/
git clone 你的项目仓库URL
```

## 2. 安装依赖

```bash
cd /www/wwwroot/你的项目目录
pip3 install -r requirements.txt
pip3 install tencentcloud-sdk-python
```

## 3. 配置环境变量

复制并编辑 .env 文件：
```bash
cp .env.example .env
# 编辑 .env 填入你的API密钥
```

## 4. 启动服务

```bash
# 后台运行
nohup python3 run_simple.py > app.log 2>&1 &

# 检查是否启动成功
lsof -i :8000
```

## 5. 配置宝塔网站

1. 打开宝塔面板 → **网站**
2. 添加站点 → 填写域名
3. 设置**反向代理**到 `http://127.0.0.1:8000`

## 6. 访问测试

- API: http://你的域名/api/search
- 前端: http://你的域名/static/search.html
- 后台: http://你的域名/admin
