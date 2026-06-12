# -*- coding: utf-8 -*-
"""
新闻获取和解析模块
负责从多个来源获取AI行业新闻
"""
import requests
import feedparser
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import time
import random

from config import NEWS_SOURCES, KEYWORDS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.news_cache = []
        
    def fetch_rss_feeds(self) -> List[Dict]:
        """从RSS源获取新闻"""
        all_news = []
        
        for feed_url in NEWS_SOURCES["rss_feeds"]:
            try:
                logger.info(f"正在获取RSS: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # 每个源取前10条
                    news_item = self._parse_rss_entry(entry, feed_url)
                    if news_item and self._is_ai_related(news_item):
                        all_news.append(news_item)
                        
                time.sleep(random.uniform(0.5, 1.5))  # 随机延迟，避免请求过快
                
            except Exception as e:
                logger.error(f"获取RSS失败 {feed_url}: {e}")
                continue
                
        return all_news
    
    def _parse_rss_entry(self, entry, source_url: str) -> Optional[Dict]:
        """解析RSS条目"""
        try:
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            summary = entry.get('summary', entry.get('description', '')).strip()
            published = entry.get('published', entry.get('updated', ''))
            
            # 清理HTML标签
            summary = BeautifulSoup(summary, 'html.parser').get_text()[:300]
            
            # 解析发布时间
            pub_date = None
            if published:
                try:
                    # 尝试多种日期格式
                    for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                        try:
                            pub_date = datetime.strptime(published[:25], fmt)
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
            
            if not title or not link:
                return None
                
            return {
                'title': title,
                'summary': summary,
                'url': link,
                'source': self._extract_source_name(source_url),
                'published': pub_date,
                'category': self._categorize_news(title, summary)
            }
            
        except Exception as e:
            logger.error(f"解析RSS条目失败: {e}")
            return None
    
    def fetch_web_news(self, url: str, source_name: str) -> List[Dict]:
        """从网页获取新闻列表"""
        news_list = []
        
        try:
            logger.info(f"正在爬取网页: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻标题和链接
            # 这里需要针对不同网站调整选择器
            articles = soup.find_all(['article', 'div', 'li'], class_=re.compile(r'post|article|story|entry|item'))
            
            for article in articles[:15]:  # 取前15条
                news_item = self._parse_web_article(article, url, source_name)
                if news_item and self._is_ai_related(news_item):
                    news_list.append(news_item)
                    
        except Exception as e:
            logger.error(f"爬取网页失败 {url}: {e}")
            
        return news_list
    
    def _parse_web_article(self, article, base_url: str, source_name: str) -> Optional[Dict]:
        """解析网页文章"""
        try:
            # 查找标题
            title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None
                
            title = title_elem.get_text().strip()
            
            # 查找链接
            link_elem = article.find('a', href=True)
            if not link_elem:
                return None
                
            link = link_elem['href']
            
            # 处理相对链接
            if link.startswith('/'):
                from urllib.parse import urljoin
                link = urljoin(base_url, link)
            elif not link.startswith('http'):
                return None
            
            # 查找摘要
            summary_elem = article.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description|desc'))
            summary = summary_elem.get_text().strip()[:300] if summary_elem else ''
            
            return {
                'title': title,
                'summary': summary,
                'url': link,
                'source': source_name,
                'published': datetime.now(),
                'category': self._categorize_news(title, summary)
            }
            
        except Exception as e:
            logger.error(f"解析文章失败: {e}")
            return None
    
    def _is_ai_related(self, news_item: Dict) -> bool:
        """判断新闻是否与AI相关"""
        text = (news_item.get('title', '') + ' ' + news_item.get('summary', '')).lower()
        
        # 检查关键词匹配
        all_keywords = (
            KEYWORDS['companies'] + 
            KEYWORDS['hardware'] + 
            KEYWORDS['iot_devices'] + 
            KEYWORDS['topics']
        )
        
        for keyword in all_keywords:
            if keyword.lower() in text:
                return True
                
        return False
    
    def _categorize_news(self, title: str, summary: str) -> str:
        """对新闻进行分类"""
        text = (title + ' ' + summary).lower()
        
        # 产品发布
        product_keywords = ['launch', 'release', 'announce', 'introduce', 'new feature', 'update', '发布', '上线', '推出']
        if any(kw in text for kw in product_keywords):
            return '产品发布'
        
        # 硬件相关
        hardware_keywords = KEYWORDS['hardware']
        if any(kw.lower() in text for kw in hardware_keywords):
            return 'AI硬件'
        
        # IoT/设备
        iot_keywords = KEYWORDS['iot_devices']
        if any(kw.lower() in text for kw in iot_keywords):
            return 'AI IoT/设备'
        
        # 融资并购
        funding_keywords = ['funding', 'raise', 'acquisition', 'merge', 'invest', 'valuation', '融资', '收购', '并购']
        if any(kw in text for kw in funding_keywords):
            return '融资并购'
        
        # 技术突破
        tech_keywords = ['breakthrough', 'research', 'paper', 'study', 'novel', 'sota', 'state-of-the-art', '突破', '论文', '研究']
        if any(kw in text for kw in tech_keywords):
            return '技术突破'
        
        # 行业规范
        regulation_keywords = ['regulation', 'standard', 'framework', 'governance', 'safety', 'ethics', '规范', '标准', '安全']
        if any(kw in text for kw in regulation_keywords):
            return '行业规范'
        
        return '行业动态'
    
    def _extract_source_name(self, url: str) -> str:
        """从URL提取来源名称"""
        source_map = {
            'techcrunch': 'TechCrunch',
            'theverge': 'The Verge',
            'venturebeat': 'VentureBeat',
            'artificialintelligence-news': 'AI News',
            'syncedreview': 'Synced',
            'googleblog': 'Google AI Blog',
            'openai': 'OpenAI Blog',
            'deepmind': 'DeepMind Blog',
        }
        
        for key, name in source_map.items():
            if key in url.lower():
                return name
                
        return url.split('/')[2] if '/' in url else url
    
    def fetch_all_news(self) -> List[Dict]:
        """获取所有新闻源的新闻"""
        all_news = []
        
        # 1. 获取RSS源新闻
        logger.info("开始获取RSS源新闻...")
        rss_news = self.fetch_rss_feeds()
        all_news.extend(rss_news)
        logger.info(f"RSS获取完成，共 {len(rss_news)} 条")
        
        # 2. 获取网页新闻
        logger.info("开始获取网页新闻...")
        for source in NEWS_SOURCES["tech_news_sites"] + NEWS_SOURCES["hardware_sources"]:
            web_news = self.fetch_web_news(source["url"], source["name"])
            all_news.extend(web_news)
            time.sleep(random.uniform(1, 2))
        logger.info(f"网页新闻获取完成，共 {len(all_news) - len(rss_news)} 条")
        
        # 3. 去重
        all_news = self._deduplicate(all_news)
        
        # 4. 按重要性排序
        all_news = self._sort_by_importance(all_news)
        
        logger.info(f"新闻获取完成，共 {len(all_news)} 条")
        self.news_cache = all_news
        
        return all_news
    
    def _deduplicate(self, news_list: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        unique_news = []
        
        for news in news_list:
            # 使用标题作为去重依据
            title_key = news['title'].lower().strip()
            if title_key not in seen:
                seen.add(title_key)
                unique_news.append(news)
                
        return unique_news
    
    def _sort_by_importance(self, news_list: List[Dict]) -> List[Dict]:
        """按重要性排序"""
        importance_weights = {
            '产品发布': 10,
            '技术突破': 9,
            '融资并购': 8,
            'AI硬件': 7,
            '行业规范': 6,
            'AI IoT/设备': 5,
            '行业动态': 4
        }
        
        def get_importance(news):
            category = news.get('category', '行业动态')
            base_weight = importance_weights.get(category, 0)
            
            # 根据关键词增加权重
            title = news.get('title', '').lower()
            if any(company.lower() in title for company in KEYWORDS['companies'][:5]):
                base_weight += 2
                
            return base_weight
        
        return sorted(news_list, key=get_importance, reverse=True)
    
    def get_top_news(self, count: int = 8) -> List[Dict]:
        """获取置顶新闻"""
        if not self.news_cache:
            self.fetch_all_news()
            
        return self.news_cache[:count]

# 测试代码
if __name__ == "__main__":
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_news()
    
    print(f"\n获取到 {len(news)} 条新闻:")
    for i, item in enumerate(news[:5], 1):
        print(f"\n{i}. {item['title']}")
        print(f"   分类: {item['category']}")
        print(f"   来源: {item['source']}")
        print(f"   链接: {item['url']}")
