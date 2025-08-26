#!/usr/bin/env python3
"""
LLM路由器交互式演示
"""
from llm_router import LLMRouter
from logger import logger

def interactive_demo():
    """交互式演示"""
    print("🤖 LLM路由器交互式演示")
    print("=" * 40)
    
    # 初始化路由器
    try:
        from config import API_KEYS, DEFAULT_PROVIDER
        config = {
            "default_provider": DEFAULT_PROVIDER,
            "providers": API_KEYS
        }
        router = LLMRouter(config)
        print(f"✅ 使用配置文件初始化成功")
    except ImportError:
        router = LLMRouter()
        print(f"⚠️  使用环境变量初始化")
    
    # 显示可用提供商
    available = router.get_available_providers()
    if not available:
        print("❌ 没有可用的提供商，请检查配置")
        return
    
    print(f"📡 可用提供商: {', '.join(available)}")
    print(f"🎯 默认提供商: {router.default_provider}")
    print()
    
    # 交互循环
    print("💬 开始对话！输入 'quit' 退出，'switch' 切换提供商")
    print("=" * 40)
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 再见！")
                break
            
            if user_input.lower() == 'switch':
                print(f"📡 可用提供商: {available}")
                new_provider = input("选择提供商: ").strip()
                if new_provider in available:
                    router.set_default_provider(new_provider)
                    print(f"✅ 已切换到: {new_provider}")
                else:
                    print("❌ 无效的提供商")
                continue
            
            if not user_input:
                continue
            
            # 调用LLM
            print("🤖 正在思考...")
            try:
                response = router.simple_chat(
                    system="你是一个友善的AI助手，请简洁回答。",
                    user=user_input,
                    max_tokens=200
                )
                print(f"🤖 AI ({router.default_provider}): {response}")
            except Exception as e:
                print(f"❌ 调用失败: {e}")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    interactive_demo()