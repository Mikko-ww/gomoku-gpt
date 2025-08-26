# LLM 路由器使用指南

LLM路由器是一个统一的大语言模型接口，支持 OpenRouter、DeepSeek 和 xAI 三个平台。

## 功能特性

- 🔀 **统一接口**: 一套API访问多个LLM平台
- 🎯 **智能路由**: 自动选择可用的提供商
- ⚙️  **灵活配置**: 支持配置文件和环境变量
- 📝 **标准格式**: 统一的消息和响应格式
- 🔄 **自动切换**: 提供商故障时可自动切换
- 🛡️  **错误处理**: 完善的错误处理和重试机制

## 快速开始

### 1. 配置API密钥

复制并编辑配置文件：
```bash
cp config_template.py config.py
```

在 `config.py` 中填入你的API密钥：
```python
API_KEYS = {
    "openrouter": {
        "api_key": "your_openrouter_api_key",
        "default_model": "openai/gpt-3.5-turbo"
    },
    "deepseek": {
        "api_key": "your_deepseek_api_key", 
        "default_model": "deepseek-chat"
    },
    "xai": {
        "api_key": "your_xai_api_key",
        "default_model": "grok-beta"
    }
}
```

### 2. 基本使用

```python
from llm_router import LLMRouter

# 初始化路由器
router = LLMRouter()

# 简单聊天
response = router.simple_chat(
    system="你是一个有用的助手",
    user="什么是五子棋？"
)
print(response)
```

### 3. 指定提供商和模型

```python
# 使用特定提供商
response = router.simple_chat(
    system="你是助手",
    user="解释人工智能",
    provider="deepseek",
    model="deepseek-chat"
)

# 使用OpenRouter的免费模型
response = router.simple_chat(
    system="你是助手", 
    user="写一首诗",
    provider="openrouter",
    model="openai/gpt-oss-20b:free"
)
```

### 4. 高级用法

```python
from llm_router import LLMMessage

# 使用消息列表格式
messages = [
    LLMMessage(role="system", content="你是五子棋专家"),
    LLMMessage(role="user", content="五子棋开局有什么技巧？"),
    LLMMessage(role="assistant", content="开局建议走天元..."),
    LLMMessage(role="user", content="那防守呢？")
]

response = router.chat_completion(
    messages=messages,
    temperature=0.8,
    max_tokens=500
)

print(f"回复: {response.content}")
print(f"模型: {response.model}")
print(f"Token使用: {response.usage}")
```

## 配置选项

### 环境变量配置
如果不想使用配置文件，可以设置环境变量：
```bash
export LLM_DEFAULT_PROVIDER="openrouter"
export OPENROUTER_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key" 
export XAI_API_KEY="your_key"
```

### 支持的提供商和模型

#### OpenRouter
- `openai/gpt-3.5-turbo` - 快速，性价比高
- `openai/gpt-4` - 最强性能  
- `anthropic/claude-3-sonnet` - 平衡性能
- `openai/gpt-oss-20b:free` - 免费选项

#### DeepSeek
- `deepseek-chat` - 通用聊天模型
- `deepseek-coder` - 代码专用模型

#### xAI  
- `grok-beta` - Grok Beta版本

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| provider | str | None | 指定提供商 |
| model | str | None | 指定模型 |
| temperature | float | 0.7 | 温度参数 |
| max_tokens | int | 1000 | 最大token数 |

## API 参考

### LLMRouter 类

#### 方法

- `simple_chat(system, user, provider=None, **kwargs)` - 简单聊天接口
- `chat_completion(messages, provider=None, model=None, **kwargs)` - 完整聊天接口  
- `get_available_providers()` - 获取可用提供商
- `set_default_provider(provider)` - 设置默认提供商

### 数据类

#### LLMMessage
```python
@dataclass
class LLMMessage:
    role: str      # "system", "user", "assistant"
    content: str   # 消息内容
```

#### LLMResponse  
```python
@dataclass
class LLMResponse:
    content: str                    # 回复内容
    model: str                      # 使用的模型
    usage: Optional[Dict[str, Any]] # Token使用情况
    finish_reason: Optional[str]    # 完成原因
```

## 运行测试

运行测试脚本验证配置：
```bash
python test_llm_router.py
```

测试会验证：
- ✅ 提供商连接性
- ✅ 模型切换
- ✅ 消息格式
- ✅ 错误处理

## 在五子棋项目中使用

在 `main.py` 中，原来的 `call_llm` 函数已经被替换为使用LLM路由器：

```python
def call_llm(system: str, user: str) -> str:
    """使用LLM路由器调用大语言模型"""
    try:
        response = llm_router.simple_chat(system=system, user=user)
        return response
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        return ""
```

现在你可以通过修改配置文件来切换不同的LLM提供商，而无需修改游戏代码。

## 故障排除

### 常见问题

1. **ImportError: No module named 'config'**
   - 确保已经创建了 `config.py` 文件
   - 或者使用环境变量配置

2. **API调用失败**
   - 检查API密钥是否正确
   - 检查网络连接
   - 查看错误日志了解详细信息

3. **没有可用的提供商**
   - 确保至少配置了一个有效的API密钥
   - 检查配置文件格式是否正确

### 调试建议

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.INFO)
```

查看可用提供商：
```python
router = LLMRouter()
print("可用提供商:", router.get_available_providers())
```

## 扩展开发

要添加新的LLM提供商：

1. 继承 `BaseLLMProvider` 类
2. 实现 `chat_completion` 方法
3. 在 `LLMRouter.PROVIDERS` 中注册

```python
class NewProvider(BaseLLMProvider):
    def chat_completion(self, messages, model=None, **kwargs):
        # 实现API调用逻辑
        pass

# 注册提供商
LLMRouter.PROVIDERS["newprovider"] = NewProvider
```