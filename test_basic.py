#!/usr/bin/env python3
"""
简单的LLM路由器结构测试（不需要网络请求）
"""
import sys
import os

def test_import():
    """测试导入"""
    print("🔍 测试模块导入...")
    try:
        from llm_router import LLMRouter, LLMMessage, LLMResponse
        print("✅ LLM路由器模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_structure():
    """测试类结构"""
    print("🔍 测试类结构...")
    
    # 这个测试不需要网络请求
    from llm_router import LLMRouter, LLMMessage, LLMResponse
    
    # 测试数据类
    message = LLMMessage(role="user", content="test")
    assert message.role == "user"
    assert message.content == "test"
    print("✅ LLMMessage 类测试通过")
    
    response = LLMResponse(content="test response", model="test-model")
    assert response.content == "test response"
    assert response.model == "test-model"
    print("✅ LLMResponse 类测试通过")
    
    # 测试路由器初始化（使用空配置）
    router = LLMRouter({"providers": {}})
    assert router is not None
    print("✅ LLMRouter 类初始化测试通过")
    
    return True

def test_config():
    """测试配置加载"""
    print("🔍 测试配置加载...")
    
    try:
        from config import API_KEYS, DEFAULT_PROVIDER
        print(f"✅ 配置文件加载成功，默认提供商: {DEFAULT_PROVIDER}")
        print(f"   配置的提供商: {list(API_KEYS.keys())}")
        return True
    except ImportError:
        print("⚠️  配置文件未找到，将使用环境变量")
        return True

if __name__ == "__main__":
    print("🚀 LLM路由器结构测试")
    print("=" * 40)
    
    tests = [
        ("模块导入", test_import),
        ("类结构", test_structure), 
        ("配置加载", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}\n")
    
    print("=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有结构测试通过！")
        print("\n📝 下一步:")
        print("1. 安装依赖: pip install requests")
        print("2. 配置API密钥（编辑 config.py）")
        print("3. 运行完整测试: python test_llm_router.py")
        print("4. 运行演示: python demo.py")
    else:
        print("❌ 部分测试失败，请检查实现")