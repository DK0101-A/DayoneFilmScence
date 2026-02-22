"""
腾讯云VOD视频搜索服务
使用腾讯云点播API搜索视频素材
"""

from tencentcloud.vod.v20180717 import vod_client, models
from tencentcloud.common import credential
from typing import List, Dict, Any
import httpx


class TencentVODService:
    """腾讯云VOD视频搜索服务"""

    # 配置
    APP_ID = "1312079725"
    SECRET_ID = "AKIDZEhy3rSrofMrBLK7oMiuvnW5TkvxqYAc"
    SECRET_KEY = "PcfbNyOuMQWSCpUQHyTlrnX5RdfWAbsx"
    REGION = "ap-beijing"

    def __init__(self):
        self.cred = credential.Credential(self.SECRET_ID, self.SECRET_KEY)
        self.client = vod_client.VodClient(self.cred, self.REGION)

    async def search(
        self, keywords: List[str], limit: int = 10, **kwargs
    ) -> List[Dict[str, Any]]:
        """搜索视频"""
        results = []

        for keyword in keywords[:2]:
            try:
                req = models.SearchMediaRequest()
                req.Text = keyword
                req.Limit = str(limit)
                req.SubAppId = int(self.APP_ID)

                # 发送请求
                resp = self.client.SearchMedia(req)

                # 解析结果
                if hasattr(resp, "MediaInfoSet") and resp.MediaInfoSet:
                    for item in resp.MediaInfoSet:
                        # 获取视频基本信息
                        basic_info = item.BasicInfo or {}
                        media_name = getattr(basic_info, "Name", "")

                        if not media_name:
                            continue

                        # 获取播放地址
                        play_url = ""
                        if hasattr(item, "TranscodeInfo") and item.TranscodeInfo:
                            transcode = item.TranscodeInfo
                            if (
                                hasattr(transcode, "TranscodeSet")
                                and transcode.TranscodeSet
                            ):
                                for t in transcode.TranscodeSet[:1]:
                                    if hasattr(t, "Url"):
                                        play_url = t.Url or ""
                                        break

                        # 获取封面
                        cover_url = ""
                        if hasattr(basic_info, "CoverUrl") and basic_info.CoverUrl:
                            cover_url = basic_info.CoverUrl

                        # 获取视频时长
                        duration = 0
                        if hasattr(item, "MetaData") and item.MetaData:
                            duration = getattr(item.MetaData, "Duration", 0) or 0

                        results.append(
                            {
                                "title": media_name,
                                "original_title": media_name,
                                "year": "",
                                "rating": 0,
                                "images": {"large": cover_url},
                                "summary": f"来源: 腾讯云VOD | 时长: {duration}秒",
                                "source": "tencent_vod",
                                "url": play_url,
                                "type": "movie",
                                "duration": duration,
                            }
                        )

            except Exception as e:
                print(f"腾讯云VOD搜索失败: {keyword}, 错误: {e}")
                # 尝试使用HTTP接口
                results.extend(await self._search_http(keyword, limit))

        return results

    async def _search_http(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """使用HTTP接口搜索（备用方案）"""
        results = []

        try:
            # 腾讯云VOD HTTP接口需要生成签名，比较复杂
            # 这里使用简单的HTTP请求尝试
            url = f"https://vod.tencentcloudapi.com/?Action=SearchMedia&Text={keyword}&Limit={limit}&Region=ap-beijing&SecretId={self.SECRET_ID}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # 解析响应...
                    print(f"腾讯云VOD HTTP响应: {data}")

        except Exception as e:
            print(f"腾讯云VOD HTTP搜索失败: {e}")

        return results


# 全局实例
tencent_vod_service = TencentVODService()
