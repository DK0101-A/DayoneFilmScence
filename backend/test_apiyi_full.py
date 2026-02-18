#!/usr/bin/env python3
"""测试API易Provider（独立脚本，避免循环导入）"""

import sys

sys.path.insert(0, "/Users/seven/Desktop/v/backend")

import httpx
import json
import asyncio


class SimpleAPIYiTest:
    """简化版API易测试"""

    def __init__(self, api_key, model="gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.apiyi.com/v1"

    async def test_scene_understanding(self, query="雨夜追车"):
        """测试场景理解"""
        print(f'🎬 测试场景理解: "{query}"')
        print("-" * 50)

        messages = [
            {
                "role": "user",
                "content": f"""分析影视场景："{query}"

输出JSON格式：
{{
    "scene_elements": ["核心要素1", "核心要素2"],
    "mood": "情绪描述",
    "similar_movies": ["电影1（年份）", "电影2（年份）"],
    "keywords": {{"zh": ["中文词"], "en": ["english"]}}
}}""",
            }
        ]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2500,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    # 解析JSON
                    try:
                        data = json.loads(content.strip())
                        print("✅ API调用成功！")
                        print()
                        print("🤖 AI分析结果:")
                        print(f"  场景要素: {data.get('scene_elements', [])}")
                        print(f"  情绪: {data.get('mood', '')}")
                        print(f"  推荐影片: {data.get('similar_movies', [])}")
                        print()

                        usage = result.get("usage", {})
                        print(f"💰 Token用量: {usage.get('total_tokens', 0)}")
                        print(
                            f"💵 成本: ¥{usage.get('total_tokens', 0) * 0.003 / 1000:.4f}"
                        )

                        return True
                    except:
                        print(f"⚠️  JSON解析失败，原始响应:\n{content[:200]}")
                        return False
                else:
                    print(f"❌ API错误: {response.status_code}")
                    print(response.text)
                    return False

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False


async def main():
    print("🚀 Day One Film AI - API易测试")
    print("=" * 60)
    print()

    api_key = "sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"

    # 测试Gemini 2.0 Flash
    tester = SimpleAPIYiTest(api_key, model="gemini-2.0-flash")
    success = await tester.test_scene_understanding("雨夜追车")

    print()
    print("=" * 60)
    if success:
        print("🎉 测试通过！API易配置成功！")
        print()
        print("✅ 可以开始开发：")
        print("  - B模块: 场景搜索")
        print("  - A模块: 剧本拆解")
        print("  - 双模型: Flash + Claude")
    else:
        print("❌ 测试失败，请检查配置")


if __name__ == "__main__":
    asyncio.run(main())
