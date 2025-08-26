"""
大语言模型路由器 - 统一各大平台API接口
支持平台：OpenRouter, DeepSeek, xAI
"""
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests

from logger import logger


@dataclass
class LLMMessage:
    """标准化的消息格式"""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """标准化的响应格式"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
    
    @abstractmethod
    def chat_completion(
        self, 
        messages: List[LLMMessage], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """聊天完成接口"""
        pass
    
    def _make_request(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """通用HTTP请求方法"""
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API 提供商"""
    
    def __init__(self, api_key: str, default_model: str = "openai/gpt-3.5-turbo"):
        super().__init__(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_model=default_model
        )
    
    def chat_completion(
        self, 
        messages: List[LLMMessage], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Mikko-ww/gomoku-gpt",
            "X-Title": "Gomoku GPT"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        logger.info(f"调用 OpenRouter API - 模型: {model}")
        data = self._make_request(url, headers, payload)
        
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", model or self.default_model),
            usage=usage,
            finish_reason=choice.get("finish_reason")
        )


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API 提供商"""
    
    def __init__(self, api_key: str, default_model: str = "deepseek-chat"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            default_model=default_model
        )
    
    def chat_completion(
        self, 
        messages: List[LLMMessage], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        logger.info(f"调用 DeepSeek API - 模型: {model}")
        data = self._make_request(url, headers, payload)
        
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", model or self.default_model),
            usage=usage,
            finish_reason=choice.get("finish_reason")
        )


class XAIProvider(BaseLLMProvider):
    """xAI (Grok) API 提供商"""
    
    def __init__(self, api_key: str, default_model: str = "grok-beta"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            default_model=default_model
        )
    
    def chat_completion(
        self, 
        messages: List[LLMMessage], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        logger.info(f"调用 xAI API - 模型: {model}")
        data = self._make_request(url, headers, payload)
        
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", model or self.default_model),
            usage=usage,
            finish_reason=choice.get("finish_reason")
        )


class LLMRouter:
    """LLM路由器 - 统一管理多个LLM提供商"""
    
    PROVIDERS = {
        "openrouter": OpenRouterProvider,
        "deepseek": DeepSeekProvider,
        "xai": XAIProvider
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化LLM路由器
        
        Args:
            config: 配置字典，格式为:
            {
                "default_provider": "openrouter",
                "providers": {
                    "openrouter": {
                        "api_key": "your_key",
                        "default_model": "openai/gpt-3.5-turbo"
                    },
                    "deepseek": {
                        "api_key": "your_key",
                        "default_model": "deepseek-chat"
                    },
                    "xai": {
                        "api_key": "your_key",
                        "default_model": "grok-beta"
                    }
                }
            }
        """
        self.config = config or self._load_config_from_env()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = self.config.get("default_provider", "openrouter")
        
        # 初始化提供商
        self._initialize_providers()
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {
            "default_provider": os.getenv("LLM_DEFAULT_PROVIDER", "openrouter"),
            "providers": {}
        }
        
        # OpenRouter配置
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            config["providers"]["openrouter"] = {
                "api_key": openrouter_key,
                "default_model": os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-3.5-turbo")
            }
        
        # DeepSeek配置
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            config["providers"]["deepseek"] = {
                "api_key": deepseek_key,
                "default_model": os.getenv("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat")
            }
        
        # xAI配置
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            config["providers"]["xai"] = {
                "api_key": xai_key,
                "default_model": os.getenv("XAI_DEFAULT_MODEL", "grok-beta")
            }
        
        return config
    
    def _initialize_providers(self):
        """初始化所有配置的提供商"""
        for provider_name, provider_config in self.config.get("providers", {}).items():
            if provider_name in self.PROVIDERS:
                try:
                    provider_class = self.PROVIDERS[provider_name]
                    self.providers[provider_name] = provider_class(**provider_config)
                    logger.info(f"成功初始化 {provider_name} 提供商")
                except Exception as e:
                    logger.error(f"初始化 {provider_name} 提供商失败: {e}")
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.providers.keys())
    
    def set_default_provider(self, provider_name: str):
        """设置默认提供商"""
        if provider_name not in self.providers:
            raise ValueError(f"提供商 {provider_name} 不可用")
        self.default_provider = provider_name
        logger.info(f"默认提供商已设置为: {provider_name}")
    
    def chat_completion(
        self, 
        messages: Optional[List[LLMMessage]] = None,
        system: Optional[str] = None,
        user: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表（优先级高于system/user）
            system: 系统消息（便利方法）
            user: 用户消息（便利方法）
            provider: 指定提供商，不指定则使用默认提供商
            model: 指定模型
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            LLMResponse: 标准化响应
        """
        # 如果没有提供messages，则从system和user构建
        if messages is None:
            messages = []
            if system:
                messages.append(LLMMessage(role="system", content=system))
            if user:
                messages.append(LLMMessage(role="user", content=user))
        
        if not messages:
            raise ValueError("必须提供messages或者system/user参数")
        
        # 选择提供商
        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            raise ValueError(f"提供商 {provider_name} 不可用")
        
        provider_instance = self.providers[provider_name]
        logger.info(f"message: {messages}")
        try:
            response = provider_instance.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            logger.info(f"成功调用 {provider_name} - 模型: {response.model}")
            logger.info(f"response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"调用 {provider_name} 失败: {e}")
            # 如果有其他可用提供商，可以考虑自动切换
            raise
    
    def simple_chat(
        self, 
        system: str, 
        user: str, 
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简单聊天接口，直接返回内容字符串
        
        Args:
            system: 系统消息
            user: 用户消息
            provider: 指定提供商
            **kwargs: 其他参数
            
        Returns:
            str: 回复内容
        """
        response = self.chat_completion(
            system=system,
            user=user,
            provider=provider,
            **kwargs
        )
        return response.content


# 全局LLM路由器实例
llm_router = None

def get_llm_router() -> LLMRouter:
    """获取全局LLM路由器实例"""
    global llm_router
    if llm_router is None:
        llm_router = LLMRouter()
    return llm_router

def init_llm_router(config: Optional[Dict[str, Any]] = None) -> LLMRouter:
    """初始化全局LLM路由器"""
    global llm_router
    llm_router = LLMRouter(config)
    return llm_router