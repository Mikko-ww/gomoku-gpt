# LLM路由器配置文件
# 复制这个文件为config.py并填入你的API密钥

# 默认提供商 (openrouter, deepseek, xai)
DEFAULT_PROVIDER = "xai"

# API密钥配置
API_KEYS = {
    # OpenRouter配置
    "openrouter": {
        "api_key": "your_openrouter_api_key_here",
        "default_model": "openai/gpt-3.5-turbo",  # 也可以使用免费的 "openai/gpt-oss-20b:free"
    },
    
    # DeepSeek配置
    "deepseek": {
        "api_key": "your_deepseek_api_key_here",
        "default_model": "deepseek-chat",
    },
    
    # xAI配置
    "xai": {
        "api_key": "your_xai_api_key_here", 
        "default_model": "grok-beta",
    }
}

# 模型推荐配置
RECOMMENDED_MODELS = {
    "openrouter": [
        "openai/gpt-3.5-turbo",      # 快速，性价比高
        "openai/gpt-4",              # 最强性能
        "anthropic/claude-3-sonnet", # 平衡性能
        "openai/gpt-oss-20b:free",   # 免费选项
    ],
    "deepseek": [
        "deepseek-chat",      # 通用聊天模型
        "deepseek-coder",     # 代码专用模型
    ],
    "xai": [
        "grok-beta",          # Grok Beta版本
    ]
}

# 默认参数配置
DEFAULT_PARAMS = {
    "temperature": 0.7,
    "max_tokens": 1000,
}