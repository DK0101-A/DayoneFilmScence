# 🎬 Day One Film AI - 第一阶段实施计划

> **阶段目标**: B模块优先 → A模块 → A+B合并  
> **时间周期**: 3周  
> **交付成果**: 可演示的影视场景搜索工具（B）+ 剧本拆解（A）

---

## 📊 开发顺序调整

```
Week 1-2: B模块（场景搜索）- 高优先级 ⭐
    ↓
Week 2-3: A模块（剧本拆解）
    ↓
Week 3-4: A+B合并（数据流打通）
```

**为什么B优先？**
- B模块是**核心价值**（场景搜索是导演最痛的需求）
- B模块可以**独立演示**和验证市场
- B模块的数据可以被A模块**复用**
- 先跑通搜索流程，再补剧本输入

---

## 🎯 Week 1-2: B模块开发（场景搜索）

### Week 1: B模块核心开发

#### Day 1 (周一): 项目初始化 ⚙️
**任务清单**:
- [ ] 创建项目目录结构
- [ ] 初始化Python虚拟环境
- [ ] 安装核心依赖（FastAPI, uvicorn, pydantic）
- [ ] 配置Git仓库和.gitignore
- [ ] 创建Docker开发环境

**交付物**:
```
/backend
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   └── api/
  ├── tests/
  ├── requirements.txt
  ├── Dockerfile
  └── docker-compose.yml
```

**验收标准**: `docker-compose up` 能启动基础服务

---

#### Day 2 (周二): 数据库设计 📦
**任务清单**:
- [ ] 设计PostgreSQL表结构
- [ ] 配置SQLAlchemy模型
- [ ] 设计Milvus向量库集合
- [ ] 创建数据库迁移脚本

**核心表结构**:
```sql
-- 场景表
CREATE TABLE scenes (
    id UUID PRIMARY KEY,
    source_type VARCHAR(20), -- movie/tv
    title VARCHAR(255),
    scene_description TEXT,
    genre VARCHAR(50),
    year INTEGER,
    region VARCHAR(50),
    created_at TIMESTAMP
);

-- 搜索记录表
CREATE TABLE search_logs (
    id UUID PRIMARY KEY,
    query TEXT,
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP
);

-- 收藏表
CREATE TABLE favorites (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    scene_id UUID,
    created_at TIMESTAMP
);
```

**Milvus集合设计**:
```python
# 场景向量集合
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="scene_id", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]
```

**验收标准**: 数据库能正常连接，模型能创建表

---

#### Day 3 (周三): AI模型接入 🤖
**任务清单**:
- [ ] 接入豆包大模型API
- [ ] 实现场景描述向量化
- [ ] 实现搜索结果重排序
- [ ] 配置API密钥管理

**核心接口**:
```python
class SceneEmbedder:
    """场景描述向量化服务"""
    
    async def embed_query(self, query: str) -> List[float]:
        """将用户查询转为向量"""
        pass
    
    async def rank_results(
        self, 
        query: str, 
        candidates: List[Scene]
    ) -> List[RankedScene]:
        """AI重排序搜索结果"""
        pass
```

**验收标准**: 
- 输入"雨夜追车"能返回向量
- AI能对10个候选结果进行相关性排序

---

#### Day 4 (周四): 搜索引擎开发 🔍
**任务清单**:
- [ ] 实现混合搜索（关键词+向量）
- [ ] 集成多数据源（豆瓣、公开API）
- [ ] 实现筛选功能（年代/地区/类型）
- [ ] 搜索结果格式化

**搜索服务架构**:
```python
class SceneSearchService:
    """场景搜索服务"""
    
    async def search(
        self,
        query: str,
        filters: SearchFilters,
        limit: int = 20
    ) -> SearchResult:
        # 1. 查询向量化
        query_vector = await self.embedder.embed_query(query)
        
        # 2. 向量搜索（Milvus）
        vector_results = await self.vector_search(query_vector, filters)
        
        # 3. 关键词搜索（PostgreSQL）
        keyword_results = await self.keyword_search(query, filters)
        
        # 4. 合并去重
        merged = self.merge_results(vector_results, keyword_results)
        
        # 5. AI重排序
        ranked = await self.embedder.rank_results(query, merged)
        
        return SearchResult(results=ranked[:limit])
```

**验收标准**: 
- 搜索"办公室争吵"返回10-20个相关结果
- 筛选条件能正常工作

---

#### Day 5 (周五): API接口开发 🌐
**任务清单**:
- [ ] 创建FastAPI路由
- [ ] 实现搜索API `/api/search`
- [ ] 实现收藏API `/api/favorites`
- [ ] 实现历史记录API `/api/history`
- [ ] 添加API文档（Swagger）

**核心API**:
```python
@app.post("/api/search", response_model=SearchResponse)
async def search_scenes(
    request: SearchRequest,
    service: SceneSearchService = Depends()
):
    """
    搜索影视场景
    
    - **query**: 场景描述（如"雨夜追车"）
    - **filters**: 筛选条件（年代、地区、类型）
    """
    results = await service.search(
        query=request.query,
        filters=request.filters,
        limit=request.limit
    )
    return SearchResponse(results=results)

@app.post("/api/favorites")
async def add_favorite(
    scene_id: str,
    user_id: str = Depends(get_current_user)
):
    """添加收藏"""
    pass
```

**验收标准**: 
- Swagger文档可访问 `/docs`
- API能通过Postman测试

---

#### Day 6-7 (周末): 扣子Agent配置 🎭
**任务清单**:
- [ ] 注册扣子开发者账号
- [ ] 创建"影视场景搜索"Agent
- [ ] 配置工作流组件
- [ ] 对接后端API
- [ ] 测试完整流程

**扣子工作流设计**:
```
用户输入: "帮我搜雨夜追车的场景"
    ↓
[豆包理解组件] → 提取关键词
    ↓
[HTTP请求组件] → 调用 /api/search
    ↓
[结果展示组件] → 格式化输出
    ↓
用户看到: 剧照 + 片名 + 时间点
```

**验收标准**: 
- 在豆包里能搜索到场景
- 结果显示正常

---

### Week 2: B模块完善 + 前端优化

#### Day 8-9 (周一-周二): B模块功能增强
**任务清单**:
- [ ] 批量搜索优化（减少API调用）
- [ ] 搜索结果缓存（Redis）
- [ ] 收藏夹管理功能
- [ ] 历史记录功能
- [ ] 导出功能（PDF/Excel）

**验收标准**: 
- 搜索响应时间 < 3秒
- 支持批量导出参考清单

---

#### Day 10-11 (周三-周四): 前端界面开发
**任务清单**:
- [ ] 创建简单Web界面（React）
- [ ] 搜索框组件
- [ ] 结果列表组件
- [ ] 筛选器组件
- [ ] 收藏组件

**验收标准**: 
- Web界面能独立运行
- 界面美观、响应式

---

#### Day 12-14 (周五-周日): B模块测试优化
**任务清单**:
- [ ] 单元测试（pytest）
- [ ] 集成测试
- [ ] 性能测试
- [ ] Bug修复
- [ ] 文档更新

**验收标准**: 
- 测试覆盖率 > 60%
- 无P0/P1级别Bug
- 通过内测

---

## 🎯 Week 2-3: A模块开发（剧本拆解）

### 目标
实现剧本上传、AI自动拆分场景和分镜、导演编辑界面

### 核心功能

#### 1. 剧本解析服务
```python
class ScriptParser:
    """剧本解析服务"""
    
    async def parse_script(self, file: UploadFile) -> Script:
        """解析上传的剧本文件"""
        # 支持格式: PDF, DOCX, TXT, FDX
        pass
    
    async def extract_scenes(self, script: Script) -> List[Scene]:
        """提取所有场景"""
        # AI识别场景边界
        pass
    
    async def generate_shots(self, scene: Scene) -> List[Shot]:
        """为场景生成分镜建议"""
        # AI生成分镜脚本
        pass
```

#### 2. A模块API
```python
@app.post("/api/scripts/upload")
async def upload_script(file: UploadFile):
    """上传剧本文件"""
    pass

@app.get("/api/scripts/{script_id}/scenes")
async def get_scenes(script_id: str):
    """获取剧本的所有场景"""
    pass

@app.post("/api/scenes/{scene_id}/shots")
async def generate_shots(scene_id: str):
    """为场景生成分镜"""
    pass
```

#### 3. 数据库表
```sql
-- 剧本表
CREATE TABLE scripts (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    file_path VARCHAR(500),
    parsed_content JSONB,
    created_at TIMESTAMP
);

-- 分镜表
CREATE TABLE shots (
    id UUID PRIMARY KEY,
    scene_id UUID,
    shot_number INTEGER,
    shot_type VARCHAR(50), -- 镜头类型
    camera_angle VARCHAR(50), -- 机位
    description TEXT,
    duration INTEGER -- 时长(秒)
);
```

---

## 🎯 Week 3-4: A+B合并

### 数据流打通
```
用户上传剧本
    ↓
A模块: 解析剧本 → 提取场景列表
    ↓
每个场景 → B模块: 搜索相似参考
    ↓
合并结果: 场景 + 参考库
    ↓
导演查看: 场景A有3个参考、场景B有5个参考
```

### 合并API
```python
@app.post("/api/scripts/{script_id}/search-references")
async def search_references_for_script(
    script_id: str,
    auto_search: bool = False
):
    """
    为剧本的所有场景搜索参考
    
    - auto_search: 是否自动为所有场景搜索
    """
    # 1. 获取剧本的所有场景
    scenes = await get_scenes(script_id)
    
    # 2. 为每个场景搜索参考
    results = []
    for scene in scenes:
        references = await search_service.search(
            query=scene.description,
            limit=5
        )
        results.append({
            "scene": scene,
            "references": references
        })
    
    return results
```

---

## 📋 技术规格

### API接口汇总

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| B | `/api/search` | POST | 搜索影视场景 |
| B | `/api/favorites` | GET/POST/DELETE | 收藏管理 |
| B | `/api/history` | GET | 搜索历史 |
| A | `/api/scripts/upload` | POST | 上传剧本 |
| A | `/api/scripts/{id}/scenes` | GET | 获取场景列表 |
| A | `/api/scenes/{id}/shots` | POST | 生成分镜 |
| A+B | `/api/scripts/{id}/search-references` | POST | 为剧本搜参考 |

### 技术栈
- **后端**: FastAPI + Python 3.10+
- **数据库**: PostgreSQL 14 + Milvus 2.3
- **缓存**: Redis 7
- **AI模型**: 豆包大模型 API
- **前端**: React 18 + TypeScript
- **部署**: Docker + Docker Compose

---

## ✅ 里程碑检查点

### Week 1 结束
- [ ] B模块基础API可用
- [ ] 扣子Agent能搜索场景
- [ ] 数据库和AI模型接入完成

### Week 2 结束
- [ ] B模块功能完整（搜索+收藏+导出）
- [ ] Web界面可用
- [ ] 通过内测

### Week 3 结束
- [ ] A模块完成（剧本上传+解析）
- [ ] A+B数据流打通

### Week 4 结束
- [ ] A+B完整工作流可用
- [ ] 扣子Agent上线
- [ ] 开始用户测试

---

## 🚀 下一步行动

1. **确认本计划** - 您review并提出修改
2. **Day 1 开始** - 项目初始化
3. **创建代码仓库** - 初始化项目结构

**确认后，我们立即开始B模块开发！** 🎬
