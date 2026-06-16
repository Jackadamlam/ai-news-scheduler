# -*- coding: utf-8 -*-
"""
社媒KOL监控模块
监控Twitter/X、HuggingFace、GitHub等平台的AI行业动态
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from config import SOCIAL_MEDIA_ACCOUNTS

logger = logging.getLogger(__name__)


class SocialMediaMonitor:
    """社媒KOL热点监控"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_all_social_news(self) -> List[Dict]:
        """获取所有社媒热点"""
        all_news = []

        # 1. HuggingFace Trending Papers
        try:
            hf_news = self._fetch_huggingface_papers()
            all_news.extend(hf_news)
            logger.info(f"HuggingFace Papers: {len(hf_news)} 条")
        except Exception as e:
            logger.warning(f"HuggingFace获取失败: {e}")

        # 2. GitHub Trending AI
        try:
            gh_news = self._fetch_github_trending()
            all_news.extend(gh_news)
            logger.info(f"GitHub Trending: {len(gh_news)} 条")
        except Exception as e:
            logger.warning(f"GitHub Trending获取失败: {e}")

        logger.info(f"社媒监控总计: {len(all_news)} 条")
        return all_news

    def _fetch_huggingface_papers(self, limit: int = 5) -> List[Dict]:
        """获取HuggingFace热门论文"""
        papers = []
        try:
            url = "https://huggingface.co/api/daily_papers"
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                return papers

            data = resp.json()
            for item in data[:limit]:
                paper = item.get('paper', {})
                papers.append({
                    'title': paper.get('title', 'Unknown'),
                    'summary': paper.get('summary', '')[:300],
                    'url': f"https://huggingface.co/papers/{paper.get('id', '')}",
                    'source': 'HuggingFace Papers',
                    'category': 'AI_Research',
                    'published': datetime.now().isoformat(),
                })
        except Exception as e:
            logger.error(f"HuggingFace API错误: {e}")
        return papers

    def _fetch_github_trending(self, limit: int = 5) -> List[Dict]:
        """获取GitHub Trending AI项目"""
        repos = []
        try:
            url = "https://api.github.com/search/repositories"
            since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            params = {
                'q': f'AI OR LLM OR machine-learning created:>{since}',
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit,
            }
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code != 200:
                return repos

            data = resp.json()
            for item in data.get('items', [])[:limit]:
                repos.append({
                    'title': f"🔥 {item['full_name']} - {item.get('description', '')[:100]}",
                    'summary': f"⭐ {item['stargazers_count']} stars | {item.get('language', 'N/A')} | {item.get('description', '')[:200]}",
                    'url': item['html_url'],
                    'source': 'GitHub Trending',
                    'category': 'AI_OpenSource',
                    'published': item.get('created_at', ''),
                })
        except Exception as e:
            logger.error(f"GitHub API错误: {e}")
        return repos


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = SocialMediaMonitor()
    news = monitor.fetch_all_social_news()
    for n in news:
        print(f"[{n['source']}] {n['title'][:80]}")
