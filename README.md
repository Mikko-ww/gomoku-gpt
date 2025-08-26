# 🎯 LLM路由器 - 统一大语言模型接口

这是一个统一的大语言模型路由器，支持多个LLM平台的统一接口调用。

## ✨ 特性

- 🔀 **统一接口**: 一套API访问多个LLM平台（OpenRouter, DeepSeek, xAI）
- 🎯 **智能路由**: 自动选择可用的提供商，支持故障切换
- ⚙️ **灵活配置**: 支持配置文件和环境变量两种配置方式
- 📝 **标准格式**: 统一的消息和响应格式，便于开发
- 🛡️ **错误处理**: 完善的错误处理和日志记录
- 🔄 **热切换**: 运行时动态切换提供商和模型

## 📁 文件结构

```
├── llm_router.py        # 核心路由器实现
├── config_template.py   # 配置模板文件
├── config.py           # 实际配置文件（需要填入API密钥）
├── test_llm_router.py  # 完整功能测试
├── test_basic.py       # 基础结构测试（无网络请求）
├── demo.py             # 交互式演示
├── main.py             # 更新后的五子棋游戏（使用路由器）
└── LLM_ROUTER_GUIDE.md # 详细使用指南
```

## 🚀 快速开始

### 1. 配置API密钥

```bash
# 复制配置模板
cp config_template.py config.py

# 编辑config.py，填入你的API密钥
```

### 2. 安装依赖

```bash
pip install requests
```

### 3. 运行测试

```bash
# 基础结构测试（无网络）
python test_basic.py

# 完整功能测试（需要网络和API密钥）
python test_llm_router.py
```

### 4. 交互式演示

```bash
python demo.py
```

## 💡 使用示例

### 基本用法

```python
from llm_router import LLMRouter

# 初始化路由器
router = LLMRouter()

# 简单聊天
response = router.simple_chat(
    system="你是一个有用的助手",
    user="什么是人工智能？"
)
print(response)
```

### 指定提供商

```python
# 使用DeepSeek
response = router.simple_chat(
    system="你是编程助手",
    user="解释Python装饰器",
    provider="deepseek"
)

# 使用OpenRouter免费模型
response = router.simple_chat(
    system="你是助手",
    user="写一首诗",
    provider="openrouter",
    model="openai/gpt-oss-20b:free"
)
```

### 消息列表格式

```python
from llm_router import LLMMessage

messages = [
    LLMMessage(role="system", content="你是五子棋专家"),
    LLMMessage(role="user", content="开局有什么技巧？"),
    LLMMessage(role="assistant", content="建议先走天元位置..."),
    LLMMessage(role="user", content="那防守呢？")
]

response = router.chat_completion(messages=messages)
print(f"回复: {response.content}")
print(f"模型: {response.model}")
```

## 🌐 支持的平台

### OpenRouter
- 支持多种模型：GPT-3.5、GPT-4、Claude等
- 有免费模型可选
- 接入简单，模型丰富

### DeepSeek  
- 专业的中文大模型
- 支持代码生成模型
- 性价比高

### xAI (Grok)
- Elon Musk的Grok模型
- 独特的AI视角
- 实时信息处理能力

## 📖 详细文档

查看 [LLM_ROUTER_GUIDE.md](./LLM_ROUTER_GUIDE.md) 获取：
- 详细配置说明
- API参考文档
- 故障排除指南
- 扩展开发指导

## 🎮 在五子棋游戏中的应用

原来的五子棋游戏硬编码了OpenRouter API调用，现在通过LLM路由器：

1. **统一接口**: `call_llm()` 函数现在使用路由器
2. **灵活切换**: 通过配置文件即可切换LLM提供商
3. **故障恢复**: 一个提供商不可用时自动使用其他的
4. **成本优化**: 可以使用免费模型或性价比更高的模型

## ⚡ 性能特性

- **连接复用**: HTTP连接复用提高效率
- **超时控制**: 30秒超时避免长时间等待
- **错误重试**: 自动重试机制提高成功率
- **日志记录**: 详细的调用日志便于调试

## 🛠️ 扩展开发

添加新的LLM提供商很简单：

```python
class NewProvider(BaseLLMProvider):
    def chat_completion(self, messages, **kwargs):
        # 实现具体的API调用逻辑
        pass

# 注册新提供商
LLMRouter.PROVIDERS["newprovider"] = NewProvider
```

## 🧪 测试

项目包含两个测试脚本：

1. **test_basic.py**: 基础结构测试，不需要网络连接
2. **test_llm_router.py**: 完整功能测试，需要API密钥

测试覆盖：
- ✅ 模块导入
- ✅ 类结构完整性
- ✅ 配置加载
- ✅ 多提供商调用
- ✅ 模型切换
- ✅ 错误处理

## 📝 开发日志

- ✅ 实现基础路由器架构
- ✅ 添加OpenRouter支持
- ✅ 添加DeepSeek支持  
- ✅ 添加xAI支持
- ✅ 配置管理系统
- ✅ 测试框架
- ✅ 文档和示例
- ✅ 五子棋游戏集成

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License