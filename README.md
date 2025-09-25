# AlphaChain - Crypto AI Agent (开发中)

一个基于LangChain的AI智能体项目框架，用于分析财报并执行加密货币交易操作。

> ⚠️ **项目状态**: 当前处于开发阶段，核心框架已搭建完成，但部分功能尚未完全实现和测试。

## 项目概述

AlphaChain是一个模块化的加密货币分析系统，旨在通过集成多个数据源和AI技术来提供全面的市场分析和交易建议。项目采用异步架构设计，支持多种数据源的聚合分析。

## 当前项目状态

### ✅ 已完成
- 项目基础架构和目录结构
- 数据模型定义 (CryptoData, PriceData, TradingSignal等)
- 数据源接口设计 (Bloomberg, TradingView, Glassnode, DefiLlama)
- 配置管理系统
- 基础工具函数
- 数据聚合器框架

### 🚧 开发中
- AI Agent核心功能 (需要LangChain依赖)
- 数据源实际API集成测试
- 交易信号生成逻辑
- 交互式对话功能

### ❌ 未实现
- 实际交易执行功能
- 回测系统
- Web界面
- 数据库持久化
- 风险管理模块

## 项目架构

详细的系统架构说明请参考 [ARCHITECTURE.md](./ARCHITECTURE.md)

### 系统流程图

```
用户请求 → CryptoAgent → DataAggregator → 数据源
    ↓
数据聚合 → 技术分析 → AI分析引擎 → 交易信号 → 用户输出
```

### 核心模块

1. **CryptoAgent**: AI智能体，基于LangChain
2. **DataAggregator**: 数据聚合器，统一多数据源
3. **DataSources**: 四大数据源接口
4. **Models**: 数据模型定义
5. **Utils**: 工具函数库

## 项目结构

```
AlphaChain/
├── src/
│   ├── agents/           # AI智能体模块 (框架完成，功能待实现)
│   │   ├── crypto_agent.py
│   │   └── __init__.py
│   ├── data_sources/     # 数据源模块 (接口完成，API集成待测试)
│   │   ├── bloomberg.py      # 需要API密钥
│   │   ├── tradingview.py    # 部分功能无需API
│   │   ├── glassnode.py      # 需要API密钥
│   │   ├── defillama.py      # 无需API密钥
│   │   ├── data_aggregator.py
│   │   └── __init__.py
│   ├── models/           # 数据模型 (已完成)
│   │   ├── crypto_data.py
│   │   ├── trading_signal.py
│   │   └── __init__.py
│   ├── utils/            # 工具函数 (已完成)
│   │   ├── helpers.py
│   │   └── __init__.py
│   └── __init__.py
├── config.py             # 配置管理 (已完成)
├── main.py              # 主程序入口 (框架完成)
├── test_basic.py        # 基础测试 (已通过)
├── test_no_api.py       # 无API测试 (部分通过)
├── requirements.txt     # 依赖包
├── env.example         # 环境变量示例
└── README.md
```

## 数据源状态

### 🔑 需要API密钥
- **Bloomberg**: 专业金融数据，需要付费API
- **Glassnode**: 链上数据分析，需要API密钥

### ⚠️ 部分功能可用
- **TradingView**: 部分公开功能可用，完整功能需要认证
- **DefiLlama**: 搜索功能可用，价格数据API可能有变化

### 🆓 推荐免费替代
- **CoinGecko API**: 完全免费，数据丰富
- **CoinCap API**: 完全免费，实时数据
- **CryptoCompare API**: 免费额度充足

## 安装和测试

### 1. 基础环境设置

```bash
# 克隆项目
git clone <repository-url>
cd AlphaChain

# 安装基础依赖
pip install pydantic pydantic-settings loguru aiohttp

# 运行基础测试
python test_basic.py
```

### 2. 完整功能测试 (需要API密钥)

```bash
# 安装完整依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入API密钥

# 运行完整测试
python main.py
```

### 3. 数据源测试

```bash
# 测试无API密钥的数据源
python test_no_api.py
```

## 核心模块说明

### 1. 数据模型 (src/models/)
- **CryptoData**: 主要数据结构，包含价格、技术指标、市场情绪等
- **PriceData**: 价格数据，支持多时间戳和多数据源
- **TradingSignal**: 交易信号，包含信号类型、强度、置信度等
- **TechnicalIndicator**: 技术指标，支持多种指标类型

### 2. 数据源 (src/data_sources/)
- **BaseDataSource**: 抽象基类，定义统一接口
- **各数据源实现**: 继承基类，实现具体API调用
- **DataAggregator**: 聚合多个数据源，统一数据格式

### 3. AI智能体 (src/agents/)
- **CryptoAgent**: 主智能体，基于LangChain
- 支持多种分析类型和交易信号生成
- 交互式对话功能

### 4. 工具函数 (src/utils/)
- 数据格式化、验证、计算等辅助功能

## 开发计划

### 短期目标 (1-2周)
- [ ] 完善DefiLlama数据源集成
- [ ] 添加CoinGecko等免费数据源
- [ ] 实现基础的技术指标计算
- [ ] 完善AI Agent核心功能

### 中期目标 (1-2月)
- [ ] 实现完整的交易信号生成
- [ ] 添加回测功能
- [ ] 实现风险管理模块
- [ ] 添加数据库持久化

### 长期目标 (3-6月)
- [ ] 开发Web界面
- [ ] 实现自动交易功能
- [ ] 添加更多技术指标
- [ ] 支持更多交易所

## 技术栈

- **Python 3.8+**: 主要开发语言
- **LangChain**: AI智能体框架
- **Pydantic**: 数据验证和序列化
- **aiohttp**: 异步HTTP客户端
- **asyncio**: 异步编程支持
- **loguru**: 日志管理

## 注意事项

1. **开发状态**: 项目仍在开发中，部分功能可能不稳定
2. **API限制**: 某些数据源需要API密钥，注意使用限制
3. **网络依赖**: 需要稳定的网络连接
4. **风险提示**: 仅供学习和研究使用，不构成投资建议

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。