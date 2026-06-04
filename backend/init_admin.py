#!/usr/bin/env python3
"""
初始化脚本
创建默认管理员账户
"""

import asyncio
import sys

sys.path.insert(0, "/Users/seven/Desktop/v/backend")

from app.services.auth_service import UserAuthService


async def init():
    print("🚀 初始化 Day One Film AI...")
    print()

    auth_service = UserAuthService()

    # 创建默认管理员
    try:
        result = await auth_service.register(
            username="admin",
            email="admin@dayonefilm.ai",
            password="admin123",
            is_admin=True,
        )
        print("✅ 管理员账户创建成功！")
        print(f"   邮箱: admin@dayonefilm.ai")
        print(f"   密码: admin123")
        print(f"   用户ID: {result['id']}")
        print()
        print("⚠️  请在生产环境修改默认密码！")
    except ValueError as e:
        if "邮箱已被注册" in str(e) or "用户名已存在" in str(e):
            print("ℹ️  管理员账户已存在，跳过创建")
        else:
            print(f"❌ 错误: {e}")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

    print()
    print("🎉 初始化完成！")
    print()
    print("默认管理员登录信息:")
    print("  邮箱: admin@dayonefilm.ai")
    print("  密码: admin123")


if __name__ == "__main__":
    asyncio.run(init())
