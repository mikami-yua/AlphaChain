# AlphaChain 系统架构

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        AlphaChain System                        │
├─────────────────────────────────────────────────────────────────┤
│  User Interface Layer                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   CLI UI    │  │  Web UI     │  │  API Layer  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  AI Agent Layer                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                CryptoAgent (LangChain)                     ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        ││
│  │  │ Analysis    │  │ Signal      │  │ Interactive │        ││
│  │  │ Engine      │  │ Generator   │  │ Chat        │        ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘        ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Data Processing Layer                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                DataAggregator                              ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        ││
│  │  │ Data        │  │ Data        │  │ Data        │        ││
│  │  │ Cleaning    │  │ Normalization│  │ Fusion     │        ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘        ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Data Source Layer                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │ Bloomberg   │  │ TradingView │  │ Glassnode   │  │DefiLlama││
│  │ (Paid API)  │  │ (Mixed)     │  │ (Paid API)  │  │(Free)   ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Data Model Layer                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ CryptoData  │  │ PriceData   │  │TradingSignal│            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  Utility Layer                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Helpers     │  │ Validators  │  │ Formatters  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 数据流图

```
用户请求
    ↓
┌─────────────┐
│ CryptoAgent │ ← 配置管理
└─────────────┘
    ↓
┌─────────────┐
│DataAggregator│
└─────────────┘
    ↓
┌─────┬─────┬─────┬─────┐
│Bloom│TView│Glass│Defi │ ← 数据源
└─────┴─────┴─────┴─────┘
    ↓
┌─────────────┐
│ 数据标准化   │
└─────────────┘
    ↓
┌─────────────┐
│ 技术分析     │
└─────────────┘
    ↓
┌─────────────┐
│ AI分析引擎   │
└─────────────┘
    ↓
┌─────────────┐
│ 交易信号     │
└─────────────┘
    ↓
用户输出
```

## 模块依赖关系

```
main.py
├── config.py
├── src/agents/crypto_agent.py
│   ├── src/data_sources/data_aggregator.py
│   │   ├── src/data_sources/bloomberg.py
│   │   ├── src/data_sources/tradingview.py
│   │   ├── src/data_sources/glassnode.py
│   │   └── src/data_sources/defillama.py
│   ├── src/models/crypto_data.py
│   ├── src/models/trading_signal.py
│   └── src/utils/helpers.py
└── test_*.py
```

## 当前实现状态

### ✅ 已实现
- 项目基础架构
- 数据模型定义
- 数据源接口设计
- 配置管理系统
- 基础工具函数

### 🚧 部分实现
- AI Agent框架 (需要LangChain)
- 数据源API集成
- 数据聚合逻辑

### ❌ 未实现
- 实际交易功能
- Web界面
- 数据库集成
- 高级分析功能

## 技术栈

```
Frontend (Future)
├── React/Vue.js
└── WebSocket

Backend
├── Python 3.8+
├── LangChain
├── Pydantic
├── aiohttp
└── asyncio

Data Sources
├── Bloomberg API
├── TradingView API
├── Glassnode API
└── DefiLlama API

Storage (Future)
├── SQLite/PostgreSQL
├── Redis (Cache)
└── InfluxDB (Time Series)
```

## 部署架构 (未来)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   API Gateway   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  AlphaChain     │
                    │  Application    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   (Future)      │
                    └─────────────────┘
```

## 开发环境设置

```bash
# 1. 克隆项目
git clone <repository>
cd AlphaChain

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 5. 运行测试
python test_basic.py
python test_no_api.py

# 6. 启动应用
python main.py
```

## 扩展点

### 1. 数据源扩展
- 添加新的数据源只需实现 `BaseDataSource` 接口
- 在 `DataAggregator` 中注册新数据源

### 2. 分析算法扩展
- 在 `CryptoAgent` 中添加新的分析方法
- 实现自定义技术指标

### 3. 输出格式扩展
- 支持多种输出格式 (JSON, CSV, PDF)
- 添加图表生成功能

### 4. 存储扩展
- 支持多种数据库后端
- 实现数据同步机制
