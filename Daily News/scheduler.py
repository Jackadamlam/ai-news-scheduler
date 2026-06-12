# -*- coding: utf-8 -*-
"""
定时任务调度器
负责定时执行新闻获取和文档生成任务
"""
import schedule
import time
import logging
from datetime import datetime
import threading
import signal
import sys

from config import SCHEDULE_CONFIG
from news_fetcher import NewsFetcher
from markdown_generator import MarkdownGenerator

# 配置日志
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
    """新闻推送定时任务调度器"""
    
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.generator = MarkdownGenerator()
        self.is_running = False
        self.last_run_time = None
        self.run_count = 0
        
        # 确保日志目录存在
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
    def job(self):
        """执行新闻获取和文档生成任务"""
        current_time = datetime.now()
        logger.info(f"=" * 60)
        logger.info(f"定时任务开始执行: {current_time}")
        logger.info(f"这是第 {self.run_count + 1} 次执行")
        
        try:
            # 1. 获取新闻
            logger.info("步骤1: 开始获取AI行业新闻...")
            news_list = self.fetcher.fetch_all_news()
            logger.info(f"获取到 {len(news_list)} 条新闻")
            
            if not news_list:
                logger.warning("未获取到任何新闻，跳过本次执行")
                return
                
            # 2. 生成Markdown文档
            logger.info("步骤2: 生成Obsidian格式文档...")
            document = self.generator.generate_document(news_list)
            
            # 3. 保存文档
            logger.info("步骤3: 保存文档...")
            filepath = self.generator.save_document(document)
            
            # 4. 生成统计信息
            summary = self.generator.generate_daily_summary(news_list)
            
            # 更新状态
            self.last_run_time = current_time
            self.run_count += 1
            
            logger.info(f"任务执行成功!")
            logger.info(f"文档已保存至: {filepath}")
            logger.info(f"新闻统计: 共{summary['total_count']}条，主要领域: {summary['top_category']}")
            logger.info(f"分类分布: {summary['categories']}")
            logger.info(f"来源分布: {summary['sources']}")
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)
            
        logger.info(f"定时任务执行完成: {datetime.now()}")
        logger.info(f"=" * 60)
    
    def should_run_now(self) -> bool:
        """检查当前是否应该执行任务"""
        current_hour = datetime.now().hour
        start_hour = SCHEDULE_CONFIG["start_hour"]
        end_hour = SCHEDULE_CONFIG["end_hour"]
        
        return start_hour <= current_hour < end_hour
    
    def setup_schedule(self):
        """设置定时任务"""
        interval = SCHEDULE_CONFIG["interval_hours"]
        
        # 设置每3小时执行一次
        # 使用at方法指定具体时间点
        schedule_times = []
        for hour in range(7, 24, 3):  # 7, 10, 13, 16, 19, 22
            time_str = f"{hour:02d}:00"
            schedule.every().day.at(time_str).do(self.job)
            schedule_times.append(time_str)
            
        logger.info(f"定时任务已设置:")
        logger.info(f"  执行时间: 每天 {', '.join(schedule_times)}")
        logger.info(f"  间隔: 每 {interval} 小时")
        logger.info(f"  时区: {SCHEDULE_CONFIG['timezone']}")
        
        return schedule_times
    
    def run(self):
        """启动调度器"""
        logger.info("=" * 60)
        logger.info("AI新闻推送系统启动")
        logger.info("=" * 60)
        
        # 设置定时任务
        schedule_times = self.setup_schedule()
        
        # 立即执行一次（可选）
        logger.info("执行首次新闻获取...")
        self.job()
        
        # 开始定时循环
        logger.info("进入定时任务循环...")
        logger.info("按 Ctrl+C 停止程序")
        
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
                # 每小时输出一次状态
                if datetime.now().minute == 0:
                    logger.info(f"调度器运行中... 下次执行时间: {schedule.next_run()}")
                    
        except KeyboardInterrupt:
            logger.info("接收到停止信号，正在关闭...")
            self.stop()
            
    def stop(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        logger.info("调度器已停止")
        
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'run_count': self.run_count,
            'next_run': str(schedule.next_run()) if schedule.jobs else None,
            'schedule_config': SCHEDULE_CONFIG
        }

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"接收到信号 {signum}，正在停止...")
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建并启动调度器
    scheduler = NewsScheduler()
    scheduler.run()
