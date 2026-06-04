#!/usr/bin/env python3
"""测试API易API Key"""

import httpx
import json

api_key = "sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
base_url = "https://api.apiyi.com/v1"

print("🧪 测试API易连接...")
print("=" * 50)

try:
    # 测试Gemini 2.0 Flash
    print("📡 调用Gemini 2.0 Flash...")

    response = httpx.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gemini-2.0-flash",
            "messages": [
                {"role": "user", "content": "分析影视场景：雨夜追车，推荐3部相似电影"}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        },
        timeout=30.0,
    )

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print("✅ API调用成功！")
        print()
        print("🎬 AI响应：")
        print(content[:300] + "...")
        print()
        print("💰 使用量：")
        usage = result.get("usage", {})
        print(f"  Prompt tokens: {usage.get('prompt_tokens', 0)}")
        print(f"  Completion tokens: {usage.get('completion_tokens', 0)}")
        print(f"  Total tokens: {usage.get('total_tokens', 0)}")
    else:
        print(f"❌ 错误：{response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ 测试失败：{e}")
