# -*- coding: utf-8 -*-
"""
LLM摘要和评级模块
使用大模型生成新闻摘要、PM Insight和星级评分
"""
import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI

from config import LLM_CONFIG

logger = logging.getLogger(__name__)


class LLMSummarizer:
    """使用LLM生成新闻摘要和评级"""

    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端"""
        api_key = LLM_CONFIG["api_key"]
        if not api_key:
            logger.warning("未设置OPENAI_API_KEY，将使用简单摘要模式")
            return
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=LLM_CONFIG["base_url"],
            )
            logger.info("LLM客户端初始化成功")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")

    def summarize_batch(self, news_list: List[Dict]) -> List[Dict]:
        """批量生成摘要和评级"""
        if not self.client:
            return self._fallback_summarize(news_list)

        if not news_list:
            return []

        # 构建批量prompt
        articles_text = ""
        for i, news in enumerate(news_list, 1):
            articles_text += f"""
---
Article {i}:
Title: {news.get('title', 'N/A')}
Source: {news.get('source', 'N/A')}
URL: {news.get('url', 'N/A')}
Summary: {news.get('summary', 'N/A')[:300]}
---
"""

        prompt = f"""You are a senior tech Product Manager with expertise in AI, hardware, IoT, and consumer electronics.
Analyze each news article below and provide:

1. **PM Insight**: A 1-2 sentence product manager's perspective focusing on:
   - System trade-offs (compute, power, cost, latency)
   - Supply chain / BOM implications
   - User experience / deployment challenges
   - Edge computing / on-device AI considerations
   Write in a technical, concise style. Focus on "why this matters for product decisions."

2. **Star Rating** (1-5): Rate based on industry impact and relevance to AI/hardware/IoT professionals:
   - ⭐⭐⭐⭐⭐ = Game-changing, industry-shifting
   - ⭐⭐⭐⭐ = Major development, high impact
   - ⭐⭐⭐ = Notable, moderate impact
   - ⭐⭐ = Minor interest, niche relevance
   - ⭐ = Low relevance

Output MUST be valid JSON array. Each element:
{{"index": 1, "pm_insight": "...", "stars": 4, "category": "AI_Hardware|IoT|LLM|Product|Funding|Regulation|Other"}}

Articles to analyze:
{articles_text}
"""

        try:
            response = self.client.chat.completions.create(
                model=LLM_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are a tech industry analyst. Output only valid JSON, no markdown fences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=LLM_CONFIG["max_tokens"],
                temperature=LLM_CONFIG["temperature"],
            )

            content = response.choices[0].message.content.strip()

            # 清理可能的markdown代码块标记
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()

            results = json.loads(content)

            # 合并结果
            for i, news in enumerate(news_list):
                if i < len(results):
                    news["pm_insight"] = results[i].get("pm_insight", "")
                    news["stars"] = results[i].get("stars", 3)
                    news["category"] = results[i].get("category", news.get("category", "Other"))
                else:
                    news.setdefault("pm_insight", "")
                    news.setdefault("stars", 3)

            logger.info(f"LLM摘要生成成功，共{len(news_list)}条")
            return news_list

        except json.JSONDecodeError as e:
            logger.error(f"LLM返回JSON解析失败: {e}\nRaw: {content[:500]}")
            return self._fallback_summarize(news_list)
        except Exception as e:
            logger.error(f"LLM摘要生成失败: {e}")
            return self._fallback_summarize(news_list)

    def generate_trend_comment(self, news_list: List[Dict]) -> str:
        """生成趋势点评"""
        if not self.client or not news_list:
            return self._fallback_trend(news_list)

        titles = "\n".join([f"- {n.get('title', '')} ({n.get('source', '')})" for n in news_list[:10]])

        prompt = f"""Based on today's AI/tech news headlines, write a 2-3 sentence "Today's Trend Analysis" in English.
Focus on: key themes, industry direction, what a PM should pay attention to.
Be insightful, concise, and technical. No fluff.

Headlines:
{titles}
"""

        try:
            response = self.client.chat.completions.create(
                model=LLM_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "You are a sharp tech industry analyst. Be concise and insightful."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"趋势点评生成失败: {e}")
            return self._fallback_trend(news_list)

    def _fallback_summarize(self, news_list: List[Dict]) -> List[Dict]:
        """无LLM时的简单摘要"""
        for news in news_list:
            news.setdefault("pm_insight", news.get("summary", "")[:200])
            news.setdefault("stars", 3)
            news.setdefault("category", news.get("category", "Other"))
        return news_list

    def _fallback_trend(self, news_list: List[Dict]) -> str:
        """无LLM时的简单趋势"""
        if not news_list:
            return "No news available for trend analysis."
        return f"Today's digest covers {len(news_list)} articles across AI, hardware, and IoT domains. Key themes include product launches, technical breakthroughs, and industry consolidation."
