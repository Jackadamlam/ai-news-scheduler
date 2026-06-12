# -*- coding: utf-8 -*-
"""
AI每日新闻推送系统 - 主程序入口
"""
import argparse
import sys
import os
import logging

from config import get_current_datetime
from news_fetcher import NewsFetcher
from llm_summarizer import LLMSummarizer
from markdown_generator import MarkdownGenerator
from scheduler import NewsScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_directories():
    for d in ['output', 'logs', 'data']:
        os.makedirs(d, exist_ok=True)


def run_once():
    """立即执行一次新闻获取 + LLM摘要"""
    logger.info("=" * 60)
    logger.info(f"执行时间: {get_current_datetime()}")
    logger.info("=" * 60)

    try:
        # 1. 获取新闻
        fetcher = NewsFetcher()
        news_list = fetcher.fetch_all_news()
        if not news_list:
            logger.warning("未获取到任何新闻")
            return None
        logger.info(f"获取到 {len(news_list)} 条新闻")

        # 2. LLM摘要和评级
        summarizer = LLMSummarizer()
        news_list = summarizer.summarize_batch(news_list)
        trend_comment = summarizer.generate_trend_comment(news_list)

        # 3. 生成文档
        generator = MarkdownGenerator()
        document = generator.generate_document(news_list, trend_comment)
        filepath = generator.save_document(document)

        # 4. 统计
        summary = generator.generate_daily_summary(news_list)
        logger.info("=" * 60)
        logger.info(f"文档: {filepath}")
        logger.info(f"新闻数: {summary['total_count']}")
        logger.info(f"来源: {summary['sources']}")
        logger.info("=" * 60)

        return filepath

    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        return None


def run_scheduler():
    logger.info("启动定时任务模式")
    scheduler = NewsScheduler()
    scheduler.run()


def main():
    parser = argparse.ArgumentParser(description="AI每日新闻推送系统")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--once', action='store_true', help='立即执行一次')
    group.add_argument('--scheduler', action='store_true', help='启动定时任务')
    args = parser.parse_args()

    ensure_directories()

    if args.once:
        run_once()
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
