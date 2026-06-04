#!/bin/bash
# 快速推送脚本 - Day One Film AI

cd /Users/seven/Desktop/v

echo "🚀 推送代码到 GitHub..."
echo "========================"
echo ""

# 检查远程
git remote -v

echo ""
echo "提交本地更改..."
git add -A
git commit -m "Update from local - $(date '+%Y-%m-%d %H:%M:%S')" || echo "没有新更改需要提交"

echo ""
echo "推送到 GitHub..."
echo "提示：如果要求输入用户名密码，请输入："
echo "  用户名：你的GitHub用户名"
echo "  密码：你的GitHub Personal Access Token"
echo ""

git push origin main

echo ""
echo "✅ 完成！"
