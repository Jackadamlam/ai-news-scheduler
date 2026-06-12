# -*- coding: utf-8 -*-
"""
AI每日新闻推送系统 - 主程序入口
支持两种运行模式：
1. 立即执行一次
2. 定时任务模式
"""
import argparse
import sys
import os
import logging

from config import get_current_datetime
from news_fetcher import NewsFetcher
from markdown_generator import MarkdownGenerator
from scheduler import NewsScheduler

# 配置日志
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
    """确保必要的目录存在"""
    dirs = ['output', 'logs', 'data']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            logger.info(f"创建目录: {d}")

def run_once():
    """立即执行一次新闻获取"""
    logger.info("=" * 60)
    logger.info("开始执行单次新闻获取任务")
    logger.info(f"执行时间: {get_current_datetime()}")
    logger.info("=" * 60)
    
    try:
        # 1. 获取新闻
        fetcher = NewsFetcher()
        news_list = fetcher.fetch_all_news()
        
        if not news_list:
            logger.warning("未获取到任何新闻")
            return None
            
        logger.info(f"成功获取 {len(news_list)} 条新闻")
        
        # 2. 生成文档
        generator = MarkdownGenerator()
        document = generator.generate_document(news_list)
        
        # 3. 保存文档
        filepath = generator.save_document(document)
        
        # 4. 输出统计
        summary = generator.generate_daily_summary(news_list)
        
        logger.info("=" * 60)
        logger.info("任务执行完成!")
        logger.info(f"文档保存位置: {filepath}")
        logger.info(f"新闻总数: {summary['total_count']}")
        logger.info(f"主要领域: {summary['top_category']}")
        logger.info(f"分类分布:")
        for cat, count in summary['categories'].items():
            logger.info(f"  - {cat}: {count}条")
        logger.info("=" * 60)
        
        return filepath
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        return None

def run_scheduler():
    """启动定时任务模式"""
    logger.info("=" * 60)
    logger.info("启动定时任务模式")
    logger.info("=" * 60)
    
    scheduler = NewsScheduler()
    scheduler.run()

def print_status():
    """打印系统状态"""
    from scheduler import NewsScheduler
    
    scheduler = NewsScheduler()
    status = scheduler.get_status()
    
    print("\n" + "=" * 60)
    print("AI新闻推送系统状态")
    print("=" * 60)
    print(f"运行状态: {'运行中' if status['is_running'] else '已停止'}")
    print(f"上次执行: {status['last_run_time'] or '未执行'}")
    print(f"执行次数: {status['run_count']}")
    print(f"下次执行: {status['next_run'] or '无'}")
    print(f"定时配置:")
    print(f"  - 开始时间: {status['schedule_config']['start_hour']}:00")
    print(f"  - 结束时间: {status['schedule_config']['end_hour']}:00")
    print(f"  - 间隔时间: {status['schedule_config']['interval_hours']}小时")
    print("=" * 60 + "\n")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI每日新闻推送系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --once          # 立即执行一次
  python main.py --scheduler     # 启动定时任务模式
  python main.py --status        # 查看系统状态
  python main.py                 # 默认启动定时任务模式
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--once', action='store_true', help='立即执行一次新闻获取')
    group.add_argument('--scheduler', action='store_true', help='启动定时任务模式')
    group.add_argument('--status', action='store_true', help='查看系统状态')
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_directories()
    
    # 根据参数执行相应功能
    if args.once:
        run_once()
    elif args.status:
        print_status()
    elif args.scheduler or len(sys.argv) == 1:
        # 默认启动定时任务模式
        run_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
