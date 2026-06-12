# -*- coding: utf-8 -*-
"""
新闻获取和解析模块
从RSS和网页源获取AI行业新闻
"""
import requests
import feedparser
import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import time
import random

from config import NEWS_SOURCES, KEYWORDS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NewsFetcher:
    """新闻获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,zh-CN;q=0.3',
        })
        self.news_cache = []

    def fetch_rss_feeds(self) -> List[Dict]:
        """从RSS源获取新闻"""
        all_news = []
        for feed_url in NEWS_SOURCES["rss_feeds"]:
            try:
                logger.info(f"RSS: {feed_url}")
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:15]:
                    news = self._parse_rss_entry(entry, feed_url)
                    if news and self._is_relevant(news):
                        all_news.append(news)
                time.sleep(random.uniform(0.3, 1.0))
            except Exception as e:
                logger.warning(f"RSS失败 {feed_url}: {e}")
        return all_news

    def fetch_web_sources(self) -> List[Dict]:
        """从网页源获取新闻"""
        all_news = []
        for source in NEWS_SOURCES["web_sources"]:
            try:
                logger.info(f"Web: {source['name']}")
                news_list = self._scrape_page(source["url"], source["name"])
                all_news.extend(news_list)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                logger.warning(f"Web失败 {source['name']}: {e}")
        return all_news

    def _parse_rss_entry(self, entry, source_url: str) -> Optional[Dict]:
        """解析RSS条目"""
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            summary = entry.get('summary', entry.get('description', ''))
            summary = BeautifulSoup(summary, 'html.parser').get_text()[:500].strip()

            if not title or not link:
                return None

            return {
                'title': title,
                'summary': summary,
                'url': link,
                'source': self._guess_source(source_url, title),
                'published': entry.get('published', ''),
            }
        except Exception:
            return None

    def _scrape_page(self, url: str, source_name: str) -> List[Dict]:
        """爬取网页新闻列表"""
        news_list = []
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 通用文章提取
            articles = soup.find_all(['article', 'div', 'li', 'h2', 'h3'],
                                     class_=re.compile(r'post|article|story|entry|item|card|title|headline', re.I))

            if not articles:
                # 回退：找所有带链接的标题
                articles = soup.find_all(['h2', 'h3', 'h4'])

            for el in articles[:20]:
                news = self._extract_from_element(el, url, source_name)
                if news and self._is_relevant(news):
                    news_list.append(news)
        except Exception as e:
            logger.warning(f"爬取失败 {url}: {e}")
        return news_list

    def _extract_from_element(self, el, base_url: str, source_name: str) -> Optional[Dict]:
        """从HTML元素提取新闻"""
        try:
            # 找链接
            link_el = el.find('a', href=True) if el.name != 'a' else el
            if not link_el or not link_el.get('href'):
                return None

            link = link_el['href']
            if link.startswith('/'):
                from urllib.parse import urljoin
                link = urljoin(base_url, link)
            elif not link.startswith('http'):
                return None

            title = link_el.get_text().strip()
            if len(title) < 10:
                return None

            # 找摘要
            parent = el.parent if el.name in ['h2', 'h3', 'h4'] else el
            desc_el = parent.find(['p', 'div'], class_=re.compile(r'excerpt|summary|desc|lead|intro', re.I))
            summary = desc_el.get_text().strip()[:500] if desc_el else ''

            return {
                'title': title,
                'summary': summary,
                'url': link,
                'source': source_name,
                'published': '',
            }
        except Exception:
            return None

    def _is_relevant(self, news: Dict) -> bool:
        """判断新闻是否AI/硬件/IoT相关"""
        text = (news.get('title', '') + ' ' + news.get('summary', '')).lower()
        all_kw = (KEYWORDS['companies'] + KEYWORDS['hardware'] +
                  KEYWORDS['iot_devices'] + KEYWORDS['topics'])
        return any(kw.lower() in text for kw in all_kw)

    def _guess_source(self, url: str, title: str) -> str:
        """从URL推断来源名称"""
        mapping = {
            'theverge': 'The Verge', 'techcrunch': 'TechCrunch',
            'wired': 'Wired', 'arstechnica': 'Ars Technica',
            'tomshardware': "Tom's Hardware", 'artificialintelligence-news': 'AI News',
            'syncedreview': 'Synced', 'googleblog': 'Google AI Blog',
            'openai': 'OpenAI Blog', 'ithome': 'IT之家',
            'leiphone': '雷峰网', 'ifanr': '爱范儿',
        }
        for key, name in mapping.items():
            if key in url.lower():
                return name
        return url.split('/')[2] if '/' in url else 'Unknown'

    def fetch_all_news(self) -> List[Dict]:
        """获取所有新闻"""
        all_news = []

        logger.info("=== 开始获取RSS源 ===")
        rss_news = self.fetch_rss_feeds()
        all_news.extend(rss_news)
        logger.info(f"RSS: {len(rss_news)}条")

        logger.info("=== 开始获取网页源 ===")
        web_news = self.fetch_web_sources()
        all_news.extend(web_news)
        logger.info(f"Web: {len(web_news)}条")

        # 去重
        seen = set()
        unique = []
        for n in all_news:
            key = n['title'].lower().strip()[:80]
            if key not in seen:
                seen.add(key)
                unique.append(n)

        logger.info(f"去重后: {len(unique)}条")
        self.news_cache = unique
        return unique

    def get_top_news(self, count: int = 8) -> List[Dict]:
        """获取置顶新闻"""
        if not self.news_cache:
            self.fetch_all_news()
        return self.news_cache[:count]


if __name__ == "__main__":
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_news()
    print(f"\n获取到 {len(news)} 条新闻:")
    for i, item in enumerate(news[:5], 1):
        print(f"\n{i}. [{item['source']}] {item['title']}")
        print(f"   {item['url']}")
