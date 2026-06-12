# -*- coding: utf-8 -*-
"""
Obsidian Markdown文档生成器
负责生成符合Obsidian格式的新闻纪要文档
"""
import os
from datetime import datetime
from typing import List, Dict
import logging

from config import OBSIDIAN_CONFIG, get_current_date, get_current_time, get_current_datetime, get_date_tag

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    """Obsidian Markdown文档生成器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
    
    def generate_news_content(self, news_list: List[Dict]) -> str:
        """生成新闻内容部分"""
        content = ""
        
        for i, news in enumerate(news_list, 1):
            news_block = OBSIDIAN_CONFIG["news_template"].format(
                index=i,
                title=news.get('title', '未知标题'),
                summary=news.get('summary', '暂无摘要'),
                source=news.get('source', '未知来源'),
                url=news.get('url', '#')
            )
            content += news_block
            
        return content
    
    def generate_sources_section(self, news_list: List[Dict]) -> str:
        """生成数据来源部分"""
        sources = set()
        for news in news_list:
            source = news.get('source', '')
            if source:
                sources.add(source)
                
        sources_text = ""
        for i, source in enumerate(sorted(sources), 1):
            sources_text += f"{i}. {source}\n"
            
        return sources_text
    
    def generate_trend_comment(self, news_list: List[Dict]) -> str:
        """生成趋势点评"""
        if not news_list:
            return "暂无足够数据生成趋势点评。"
        
        # 分析新闻分类分布
        categories = {}
        for news in news_list:
            cat = news.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
        
        # 找出主要趋势
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 生成点评
        comment = ""
        
        # 第一句：总体概述
        comment += f"今日AI行业新闻共收录{len(news_list)}条，"
        if top_categories:
            comment += f"主要集中在{top_categories[0][0]}领域"
            if len(top_categories) > 1:
                comment += f"和{top_categories[1][0]}领域"
            comment += "。"
        
        # 第二句：具体分析
        if len(news_list) >= 3:
            top_news = news_list[:3]
            companies_mentioned = []
            for news in top_news:
                title = news.get('title', '')
                # 检测提到的公司
                from config import KEYWORDS
                for company in KEYWORDS['companies']:
                    if company.lower() in title.lower():
                        companies_mentioned.append(company)
                        
            if companies_mentioned:
                unique_companies = list(set(companies_mentioned))[:3]
                comment += f"今日重点关注的企业包括{'、'.join(unique_companies)}等。"
        
        # 第三句：展望
        comment += "建议持续关注技术突破和商业化进展，把握行业发展脉搏。"
        
        return comment
    
    def generate_document(self, news_list: List[Dict], title_suffix: str = "") -> str:
        """生成完整的Obsidian文档"""
        # 准备模板数据
        date = get_current_date()
        time_str = get_current_time()
        datetime_str = get_current_datetime()
        date_tag = get_date_tag()
        
        # 生成各部分内容
        news_content = self.generate_news_content(news_list)
        sources = self.generate_sources_section(news_list)
        trend_comment = self.generate_trend_comment(news_list)
        
        # 组装完整文档
        document = OBSIDIAN_CONFIG["template"].format(
            date=date,
            time=time_str,
            date_tag=date_tag,
            datetime=datetime_str,
            count=len(news_list),
            news_content=news_content,
            trend_comment=trend_comment,
            sources=sources
        )
        
        return document
    
    def save_document(self, document: str, filename: str = None) -> str:
        """保存文档到文件"""
        if filename is None:
            # 生成文件名：YYYY-MM-DD_HHMM_AI新闻.md
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            filename = f"{timestamp}_AI新闻.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(document)
                
            logger.info(f"文档已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存文档失败: {e}")
            raise
    
    def generate_daily_summary(self, news_list: List[Dict]) -> Dict:
        """生成每日摘要统计"""
        categories = {}
        sources = {}
        
        for news in news_list:
            # 统计分类
            cat = news.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
            
            # 统计来源
            source = news.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
            
        return {
            'total_count': len(news_list),
            'categories': categories,
            'sources': sources,
            'top_category': max(categories.items(), key=lambda x: x[1])[0] if categories else '无',
            'generated_at': get_current_datetime()
        }

# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_news = [
        {
            'title': 'OpenAI发布GPT-5，性能大幅提升',
            'summary': 'OpenAI今日正式发布GPT-5模型，在多项基准测试中表现出色，推理能力显著增强。',
            'url': 'https://example.com/news1',
            'source': 'TechCrunch',
            'category': '产品发布'
        },
        {
            'title': 'NVIDIA推出新一代AI芯片B200',
            'summary': 'NVIDIA发布Blackwell架构B200 GPU，AI训练性能提升30倍，能效比大幅提升。',
            'url': 'https://example.com/news2',
            'source': 'VentureBeat',
            'category': 'AI硬件'
        },
        {
            'title': 'AI初创公司Anthropic完成20亿美元融资',
            'summary': 'Anthropic宣布完成新一轮20亿美元融资，估值达到600亿美元，将用于扩大AI安全研究。',
            'url': 'https://example.com/news3',
            'source': 'Crunchbase News',
            'category': '融资并购'
        }
    ]
    
    generator = MarkdownGenerator()
    doc = generator.generate_document(test_news)
    print(doc)
