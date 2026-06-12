# -*- coding: utf-8 -*-
"""
定时任务调度器
"""
import schedule
import time
import logging
from datetime import datetime
import signal
import sys
import os

from config import SCHEDULE_CONFIG
from news_fetcher import NewsFetcher
from llm_summarizer import LLMSummarizer
from markdown_generator import MarkdownGenerator

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsScheduler:

    def __init__(self):
        self.fetcher = NewsFetcher()
        self.summarizer = LLMSummarizer()
        self.generator = MarkdownGenerator()
        self.is_running = False
        self.last_run_time = None
        self.run_count = 0

    def job(self):
        current_time = datetime.now()
        logger.info(f"{'=' * 60}")
        logger.info(f"定时任务开始: {current_time} (第{self.run_count + 1}次)")

        try:
            # 1. 获取新闻
            news_list = self.fetcher.fetch_all_news()
            if not news_list:
                logger.warning("未获取到新闻，跳过")
                return
            logger.info(f"获取到 {len(news_list)} 条新闻")

            # 2. LLM摘要和评级
            news_list = self.summarizer.summarize_batch(news_list)
            trend_comment = self.summarizer.generate_trend_comment(news_list)

            # 3. 生成文档
            document = self.generator.generate_document(news_list, trend_comment)
            filepath = self.generator.save_document(document)

            # 4. 统计
            summary = self.generator.generate_daily_summary(news_list)
            self.last_run_time = current_time
            self.run_count += 1

            logger.info(f"文档: {filepath}")
            logger.info(f"新闻数: {summary['total_count']}, 来源: {summary['sources']}")
        except Exception as e:
            logger.error(f"任务失败: {e}", exc_info=True)

        logger.info(f"{'=' * 60}")

    def setup_schedule(self):
        schedule_times = []
        for hour in range(7, 24, 3):
            time_str = f"{hour:02d}:00"
            schedule.every().day.at(time_str).do(self.job)
            schedule_times.append(time_str)
        logger.info(f"定时: 每天 {', '.join(schedule_times)}")
        return schedule_times

    def run(self):
        logger.info("AI新闻推送系统启动")
        self.setup_schedule()
        self.job()  # 立即执行一次
        self.is_running = True
        logger.info("进入定时循环...")

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_running = False
        schedule.clear()
        logger.info("调度器已停止")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    scheduler = NewsScheduler()
    scheduler.run()
