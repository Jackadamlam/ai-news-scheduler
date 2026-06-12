# -*- coding: utf-8 -*-
"""
Obsidian Markdown文档生成器
生成符合PM视角的AI行业新闻纪要
"""
import os
from datetime import datetime
from typing import List, Dict
import logging

from config import get_current_date, get_current_time, get_current_datetime, get_date_tag

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Obsidian Markdown文档生成器"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _stars_display(self, stars: int) -> str:
        """生成星级显示"""
        stars = max(1, min(5, stars or 3))
        return "⭐" * stars

    def _generate_news_item(self, news: Dict, index: int) -> str:
        """生成单条新闻"""
        url = news.get('url', '#')
        title = news.get('title', 'Unknown')
        source = news.get('source', 'Unknown')
        stars = self._stars_display(news.get('stars', 3))
        pm_insight = news.get('pm_insight', news.get('summary', '')[:200])
        # 截断过长的PM Insight
        if len(pm_insight) > 300:
            pm_insight = pm_insight[:297] + "..."

        return f"""- **[{title}]({url})** ({source} | {stars})
  - **PM Insight**: {pm_insight}

"""

    def generate_document(self, news_list: List[Dict], trend_comment: str = "") -> str:
        """生成完整的Obsidian文档"""
        date = get_current_date()
        time_str = get_current_time()
        datetime_str = get_current_datetime()
        date_tag = get_date_tag()

        # 生成新闻内容
        news_content = ""
        for i, news in enumerate(news_list, 1):
            news_content += self._generate_news_item(news, i)

        # 趋势点评
        if not trend_comment:
            trend_comment = f"Today's digest covers {len(news_list)} articles across AI, hardware, and IoT domains. Key themes include product launches, technical breakthroughs, and industry consolidation."

        doc = f"""---
date: {date}
type: daily_brief
tags: [AI_Hardware, PM_Insight, Daily_News, {date_tag}]
llm_status: {'ONLINE' if news_list and news_list[0].get('pm_insight') else 'FALLBACK'}
---

# 📡 Strategic Intel & Geek Radar

> 📅 **Date**: {date} {time_str}
> 📊 **Articles**: {len(news_list)}
> 🔍 **Sources**: RSS + Web (The Verge, TechCrunch, Wired, Ars Technica, IT之家, 雷峰网, 爱范儿)

---

## 🚀 Industry & System Trade-offs (RSS)

{news_content}

---

## 📈 Today's Trend Analysis

{trend_comment}

---

> 💡 **Legend**: ⭐⭐⭐⭐⭐ = Game-changing | ⭐⭐⭐⭐ = Major impact | ⭐⭐⭐ = Notable | ⭐⭐ = Niche | ⭐ = Low relevance
>
> *Generated at {datetime_str} by AI News Scheduler*
"""

        return doc

    def save_document(self, document: str, filename: str = None) -> str:
        """保存文档到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            filename = f"{timestamp}_AI_Strategic_Intel.md"

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(document)

        logger.info(f"文档已保存: {filepath}")
        return filepath

    def generate_daily_summary(self, news_list: List[Dict]) -> Dict:
        """生成每日摘要统计"""
        sources = {}
        for n in news_list:
            s = n.get('source', 'Unknown')
            sources[s] = sources.get(s, 0) + 1
        return {
            'total_count': len(news_list),
            'sources': sources,
            'generated_at': get_current_datetime(),
        }


if __name__ == "__main__":
    test_news = [
        {
            'title': 'Anthropic releases Claude Fable 5',
            'summary': 'Next-gen frontier model with SOTA performance.',
            'url': 'https://example.com/news1',
            'source': 'The Verge',
            'stars': 5,
            'pm_insight': 'Frontier model deployment requires massive inference compute with >1TB/s memory bandwidth.',
            'category': 'LLM',
        },
        {
            'title': 'Apple on-device AI for Siri',
            'summary': 'Edge inference for calendar parsing.',
            'url': 'https://example.com/news2',
            'source': 'Ars Technica',
            'stars': 4,
            'pm_insight': 'On-device AI demonstrates edge inference killer app—low-latency, privacy-preserving.',
            'category': 'AI_Hardware',
        },
    ]
    gen = MarkdownGenerator()
    doc = gen.generate_document(test_news)
    print(doc)
