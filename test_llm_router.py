#!/usr/bin/env python3
"""
LLM路由器测试脚本
测试各种提供商的接口是否正常工作
"""
import asyncio
from llm_router import LLMRouter, LLMMessage
from logger import logger

def test_basic_functionality():
    """测试基本功能"""
    logger.info("开始测试LLM路由器基本功能...")
    
    # 尝试导入配置
    try:
        from config import API_KEYS, DEFAULT_PROVIDER
        config = {
            "default_provider": DEFAULT_PROVIDER,
            "providers": API_KEYS
        }
        router = LLMRouter(config)
        logger.info(f"使用配置文件初始化，默认提供商: {DEFAULT_PROVIDER}")
    except ImportError:
        logger.info("使用环境变量初始化")
        router = LLMRouter()
    
    # 显示可用提供商
    available = router.get_available_providers()
    logger.info(f"可用提供商: {available}")
    
    if not available:
        logger.error("没有可用的提供商，请检查配置")
        return
    
    # 测试简单对话
    test_system = "你是一个五子棋助手。请简短回答。"
    test_user = "五子棋的基本规则是什么？请用一句话回答。"
    
    for provider in available:
        logger.info(f"\n--- 测试 {provider} 提供商 ---")
        try:
            response = router.simple_chat(
                system=test_system,
                user=test_user,
                provider=provider,
                max_tokens=100
            )
            logger.success(f"{provider} 测试成功:")
            logger.info(f"回复: {response}")
        except Exception as e:
            logger.error(f"{provider} 测试失败: {e}")

def test_multiple_providers():
    """测试多提供商切换"""
    logger.info("\n开始测试多提供商切换...")
    
    try:
        from config import API_KEYS, DEFAULT_PROVIDER
        config = {
            "default_provider": DEFAULT_PROVIDER,
            "providers": API_KEYS
        }
        router = LLMRouter(config)
    except ImportError:
        router = LLMRouter()
    
    available = router.get_available_providers()
    
    if len(available) < 2:
        logger.warning("只有一个提供商可用，跳过切换测试")
        return
    
    # 测试切换默认提供商
    for provider in available[:2]:  # 测试前两个
        logger.info(f"\n设置默认提供商为: {provider}")
        router.set_default_provider(provider)
        
        try:
            response = router.simple_chat(
                system="你是助手",
                user="请回答：1+1等于几？",
                max_tokens=50
            )
            logger.success(f"使用 {provider} 成功: {response.strip()}")
        except Exception as e:
            logger.error(f"使用 {provider} 失败: {e}")

def test_message_format():
    """测试消息格式"""
    logger.info("\n开始测试消息格式...")
    
    try:
        from config import API_KEYS, DEFAULT_PROVIDER
        config = {
            "default_provider": DEFAULT_PROVIDER,
            "providers": API_KEYS
        }
        router = LLMRouter(config)
    except ImportError:
        router = LLMRouter()
    
    available = router.get_available_providers()
    if not available:
        logger.error("没有可用的提供商")
        return
    
    # 测试消息列表格式
    messages = [
        LLMMessage(role="system", content="你是一个数学助手"),
        LLMMessage(role="user", content="2+2等于几？"),
        LLMMessage(role="assistant", content="2+2等于4"),
        LLMMessage(role="user", content="那3+3呢？")
    ]
    
    try:
        response = router.chat_completion(
            messages=messages,
            max_tokens=50
        )
        logger.success(f"消息格式测试成功: {response.content}")
        logger.info(f"使用模型: {response.model}")
        logger.info(f"Token使用: {response.usage}")
    except Exception as e:
        logger.error(f"消息格式测试失败: {e}")

def test_model_switching():
    """测试模型切换"""
    logger.info("\n开始测试模型切换...")
    
    try:
        from config import API_KEYS, DEFAULT_PROVIDER, RECOMMENDED_MODELS
        config = {
            "default_provider": DEFAULT_PROVIDER,
            "providers": API_KEYS
        }
        router = LLMRouter(config)
    except ImportError:
        router = LLMRouter()
        RECOMMENDED_MODELS = {
            "openrouter": ["openai/gpt-3.5-turbo", "openai/gpt-oss-20b:free"]
        }
    
    available = router.get_available_providers()
    if not available:
        return
    
    # 测试指定模型
    provider = available[0]
    models_to_test = RECOMMENDED_MODELS.get(provider, [])[:2]  # 测试前两个模型
    
    for model in models_to_test:
        logger.info(f"测试 {provider} 的模型 {model}")
        try:
            response = router.simple_chat(
                system="你是助手",
                user="说hello",
                provider=provider,
                model=model,
                max_tokens=30
            )
            logger.success(f"模型 {model} 测试成功: {response}")
        except Exception as e:
            logger.error(f"模型 {model} 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 LLM路由器测试开始")
    print("=" * 50)
    
    try:
        # 基本功能测试
        test_basic_functionality()
        
        # 多提供商测试
        test_multiple_providers()
        
        # 消息格式测试
        test_message_format()
        
        # 模型切换测试
        test_model_switching()
        
        print("\n" + "=" * 50)
        print("✅ 测试完成")
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        print("\n❌ 测试失败")