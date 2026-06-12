# -*- coding: utf-8 -*-
"""
AI每日新闻推送系统配置文件
"""
import os
from datetime import datetime

# 定时任务配置
SCHEDULE_CONFIG = {
    "start_hour": 7,    # 开始时间
    "end_hour": 24,     # 结束时间
    "interval_hours": 3,  # 间隔小时数
    "timezone": "Asia/Shanghai"
}

# 新闻源配置
NEWS_SOURCES = {
    "rss_feeds": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://www.artificialintelligence-news.com/feed/",
        "https://syncedreview.com/feed/",
        "https://ai.googleblog.com/feeds/posts/default?alt=rss",
        "https://openai.com/blog/rss/",
        "https://www.deepmind.com/blog/rss.xml",
    ],
    "tech_news_sites": [
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/"},
        {"name": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence"},
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/"},
        {"name": "AI News", "url": "https://www.artificialintelligence-news.com/"},
        {"name": "Synced", "url": "https://syncedreview.com/"},
        {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/"},
    ],
    "hardware_sources": [
        {"name": "AnandTech", "url": "https://www.anandtech.com/"},
        {"name": "Tom's Hardware", "url": "https://www.tomshardware.com/"},
        {"name": "HotHardware", "url": "https://www.hothardware.com/"},
        {"name": "VideoCardz", "url": "https://videocardz.com/"},
    ],
    "funding_sources": [
        {"name": "Crunchbase News", "url": "https://news.crunchbase.com/"},
        {"name": "PitchBook", "url": "https://pitchbook.com/news"},
        {"name": "CB Insights", "url": "https://www.cbinsights.com/research/"},
    ]
}

# 关键词配置
KEYWORDS = {
    "companies": [
        "OpenAI", "Google", "Anthropic", "Qwen", "Xiaomi", "Deepseek",
        "Meta", "Microsoft", "NVIDIA", "Apple", "Samsung", "Huawei",
        "Baidu", "ByteDance", "Alibaba", "Tencent", "AMD", "Intel",
        "Qualcomm", "Tesla", "Figure AI", "Boston Dynamics", "Unitree"
    ],
    "hardware": [
        "AI chip", "GPU", "TPU", "NPU", "neural processing unit",
        "AI accelerator", "edge AI", "AI hardware", "AI server",
        "AI processor", "machine learning chip", "inference chip",
        "training chip", "AI computing", "H100", "H200", "B100", "B200",
        "A100", "MI300", "Gaudi", "Graviton", "Trainium", "Inferentia"
    ],
    "iot_devices": [
        "AI IoT", "smart device", "smart speaker", "smart display",
        "smart home", "smart wearable", "AI pin", "AI glasses",
        "AI earbuds", "AI headphones", "audio hardware",
        "voice assistant", "smart camera", "smart lock",
        "AI robot", "humanoid robot", "drone"
    ],
    "topics": [
        "artificial intelligence", "machine learning", "deep learning",
        "generative AI", "LLM", "large language model", "foundation model",
        "AI safety", "AI regulation", "AI ethics", "AI governance",
        "data governance", "AI standard", "AI framework",
        "computer vision", "natural language processing", "NLP",
        "reinforcement learning", "autonomous driving", "AI agent"
    ]
}

# Obsidian配置
OBSIDIAN_CONFIG = {
    "vault_path": os.path.expanduser("~/Documents/Obsidian/Daily AI News"),
    "template": """---
title: AI行业每日新闻速递
date: {date}
time: {time}
tags: [AI, 新闻, 行业动态, {date_tag}]
created: {datetime}
---

# 🤖 AI行业每日新闻速递

> 📅 **日期**: {date} {time}
> 📊 **新闻数量**: {count} 条
> 🔍 **覆盖领域**: 产品发布 | 硬件动态 | IoT设备 | 融资并购 | 技术突破 | 行业规范

---

## 📰 今日热点新闻

{news_content}

---

## 📈 今日趋势点评

{trend_comment}

---

## 📋 数据来源

{sources}

---

> 💡 **使用说明**: 
> - 点击标题可跳转至原文
> - 使用 `#AI` `#新闻` `#行业动态` 标签可快速检索
> - 在Obsidian中打开可查看完整链接

---

*本报告由AI新闻推送系统自动生成，数据更新时间: {datetime}*
""",
    "news_template": """
### {index}. {title}

**一句话摘要**: {summary}

**信息来源**: {source}

**原文链接**: [{title}]({url})

---

"""
}

# 文件路径配置
PATHS = {
    "output_dir": "output",
    "logs_dir": "logs",
    "data_dir": "data"
}

def get_current_date():
    """获取当前日期"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%H:%M:%S")

def get_current_datetime():
    """获取当前完整时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date_tag():
    """获取日期标签"""
    return datetime.now().strftime("%Y%m%d")
