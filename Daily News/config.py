# -*- coding: utf-8 -*-
"""
AI每日新闻推送系统配置文件
"""
import os
from datetime import datetime

# 定时任务配置
SCHEDULE_CONFIG = {
    "start_hour": 7,
    "end_hour": 24,
    "interval_hours": 3,
    "timezone": "Asia/Shanghai"
}

# LLM配置 (小米MiMo Token Plan API)
LLM_CONFIG = {
    "api_key": os.environ.get("MIMO_API_KEY", ""),
    "model": "mimo-v2.5-pro",
    "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
    "max_tokens": 2000,
    "temperature": 0.3,
}

# 新闻源配置
NEWS_SOURCES = {
    "rss_feeds": [
        # 英文主流科技媒体
        "https://www.theverge.com/rss/index.xml",
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.tomshardware.com/feeds/all",
        # AI专项
        "https://www.artificialintelligence-news.com/feed/",
        "https://syncedreview.com/feed/",
        "https://ai.googleblog.com/feeds/posts/default?alt=rss",
        "https://openai.com/blog/rss/",
    ],
    "web_sources": [
        # 英文
        {"name": "The Verge", "url": "https://www.theverge.com/ai-artificial-intelligence", "lang": "en"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/", "lang": "en"},
        {"name": "Wired", "url": "https://www.wired.com/tag/artificial-intelligence/", "lang": "en"},
        {"name": "Ars Technica", "url": "https://arstechnica.com/ai/", "lang": "en"},
        {"name": "Tom's Hardware", "url": "https://www.tomshardware.com/tech-industry/artificial-intelligence", "lang": "en"},
        # 中文
        {"name": "IT之家", "url": "https://www.ithome.com/tag/AI", "lang": "zh"},
        {"name": "雷峰网", "url": "https://www.leiphone.com/category/ai", "lang": "zh"},
        {"name": "爱范儿", "url": "https://www.ifanr.com/tag/ai", "lang": "zh"},
    ],
}

# 关键词配置
KEYWORDS = {
    "companies": [
        "OpenAI", "Google", "Anthropic", "Qwen", "Xiaomi", "Deepseek",
        "Meta", "Microsoft", "NVIDIA", "Apple", "Samsung", "Huawei",
        "Baidu", "ByteDance", "Alibaba", "Tencent", "AMD", "Intel",
        "Qualcomm", "Tesla", "Figure AI", "Boston Dynamics", "Unitree",
        "Mistral", "Cohere", "Stability AI", "Midjourney", "Runway",
    ],
    "hardware": [
        "AI chip", "GPU", "TPU", "NPU", "neural processing unit",
        "AI accelerator", "edge AI", "AI hardware", "AI server",
        "H100", "H200", "B100", "B200", "A100", "MI300",
        "Gaudi", "Trainium", "Inferentia", "Apple Silicon",
        "liquid cooling", "data center", "inference chip",
    ],
    "iot_devices": [
        "AI IoT", "smart device", "smart speaker", "smart display",
        "smart home", "smart wearable", "AI pin", "AI glasses",
        "AI earbuds", "AI headphones", "audio hardware",
        "voice assistant", "smart camera", "AI robot", "humanoid",
    ],
    "topics": [
        "artificial intelligence", "machine learning", "deep learning",
        "generative AI", "LLM", "large language model", "foundation model",
        "AI safety", "AI regulation", "AI ethics", "AI governance",
        "computer vision", "NLP", "autonomous driving", "AI agent",
        "on-device AI", "edge inference", "AI infrastructure",
        "multimodal", "reasoning", "agentic", "RAG", "fine-tuning",
    ]
}

# 社媒KOL监控配置
SOCIAL_MEDIA_ACCOUNTS = {
    "twitter": [
        # AI模型公司官方
        {"handle": "@OpenAI", "name": "OpenAI", "category": "AI_Model"},
        {"handle": "@AnthropicAI", "name": "Anthropic", "category": "AI_Model"},
        {"handle": "@GoogleDeepMind", "name": "Google DeepMind", "category": "AI_Model"},
        {"handle": "@MistralAI", "name": "Mistral AI", "category": "AI_Model"},
        {"handle": "@huaborz", "name": "Jim Fan (NVIDIA)", "category": "AI_Research"},
        {"handle": "@DrJimFan", "name": "Dr. Jim Fan", "category": "AI_Research"},
        {"handle": "@AndrewYNg", "name": "Andrew Ng", "category": "AI_Research"},
        {"handle": "@kaborz", "name": "Karpathy", "category": "AI_Research"},
        {"handle": "@ylecun", "name": "Yann LeCun (Meta)", "category": "AI_Research"},
        {"handle": "@GaryMarcus", "name": "Gary Marcus", "category": "AI_Research"},
        {"handle": "@hardmaru", "name": "David Ha (Sakana AI)", "category": "AI_Research"},
        {"handle": "@JeffDean", "name": "Jeff Dean (Google)", "category": "AI_Research"},
        # 硬件半导体
        {"handle": "@nvidia", "name": "NVIDIA", "category": "Hardware"},
        {"handle": "@Qualcomm", "name": "Qualcomm", "category": "Hardware"},
        {"handle": "@IntelAI", "name": "Intel AI", "category": "Hardware"},
        {"handle": "@AMDAI", "name": "AMD AI", "category": "Hardware"},
        {"handle": "@xaborz", "name": "Xiaomi AI", "category": "Hardware"},
        # 科技媒体
        {"handle": "@verge", "name": "The Verge", "category": "TechMedia"},
        {"handle": "@TechCrunch", "name": "TechCrunch", "category": "TechMedia"},
        {"handle": "@arstechnica", "name": "Ars Technica", "category": "TechMedia"},
        {"handle": "@WIRED", "name": "Wired", "category": "TechMedia"},
        {"handle": "@haborz", "name": "Hugging Face", "category": "AI_Community"},
        # 中文KOL
        {"handle": "@karminski3", "name": "karminski (AI科普)", "category": "CN_KOL"},
        {"handle": "@dotey", "name": "宝玉 (AI洞察)", "category": "CN_KOL"},
        {"handle": "@宝玉", "name": "宝玉", "category": "CN_KOL"},
        {"handle": "@歸藏", "name": "歸藏 (AI产品)", "category": "CN_KOL"},
    ],
    "wechat_accounts": [
        {"name": "量子位", "category": "AI_Media"},
        {"name": "机器之心", "category": "AI_Media"},
        {"name": "36氪", "category": "Tech_Media"},
        {"name": "芯智讯", "category": "Hardware"},
        {"name": "雷峰网", "category": "AI_Media"},
    ]
}

# Obsidian配置
OBSIDIAN_CONFIG = {
    "vault_path": os.path.expanduser("~/Documents/Obsidian/Daily AI News"),
}

# 文件路径配置
PATHS = {
    "output_dir": "output",
    "logs_dir": "logs",
    "data_dir": "data"
}

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date_tag():
    return datetime.now().strftime("%Y%m%d")
