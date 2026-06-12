# AI每日新闻推送系统

自动获取AI行业热点新闻，生成Obsidian格式的Markdown文档，支持定时推送。

## 功能特性

- **多源新闻聚合**：RSS订阅、网页爬虫，覆盖主流AI媒体
- **智能分类**：产品发布、AI硬件、IoT设备、融资并购、技术突破、行业规范
- **Obsidian格式**：自动生成带YAML frontmatter的Markdown文档
- **定时推送**：每天7:00-24:00，每3小时自动执行
- **云端部署**：支持GitHub Actions、云服务器、Docker、Serverless等多种方案

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 立即执行一次

```bash
python main.py --once
```

### 3. 启动定时任务

```bash
python main.py --scheduler
```

### 4. 查看系统状态

```bash
python main.py --status
```

## 输出示例

生成的Markdown文档保存在 `output/` 目录，格式如下：

```markdown
---
title: AI行业每日新闻速递
date: 2024-01-15
tags: [AI, 新闻, 行业动态, 20240115]
---

# 🤖 AI行业每日新闻速递

## 📰 今日热点新闻

### 1. OpenAI发布GPT-5，性能大幅提升

**一句话摘要**: OpenAI今日正式发布GPT-5模型，推理能力显著增强。

**信息来源**: TechCrunch

**原文链接**: [OpenAI发布GPT-5](https://example.com/news)

---

## 📈 今日趋势点评

今日AI行业新闻共收录8条，主要集中在产品发布领域...
```

## 配置说明

编辑 `config.py` 文件：

- `SCHEDULE_CONFIG`：定时任务配置
- `NEWS_SOURCES`：新闻源配置
- `KEYWORDS`：关键词配置
- `OBSIDIAN_CONFIG`：Obsidian模板配置

## 云端部署

详见 [deploy_guide.md](deploy_guide.md)，支持：

- GitHub Actions（推荐，免费）
- 云服务器（阿里云/腾讯云）
- Docker容器
- Serverless（AWS Lambda/阿里云函数）

## 项目结构

```
Daily News/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── news_fetcher.py      # 新闻获取模块
├── markdown_generator.py # Markdown生成器
├── scheduler.py         # 定时任务调度器
├── requirements.txt     # 依赖包
├── deploy_guide.md      # 部署指南
├── output/              # 输出目录
├── logs/                # 日志目录
└── data/                # 数据目录
```

## 自定义新闻源

在 `config.py` 中添加新的RSS源：

```python
NEWS_SOURCES = {
    "rss_feeds": [
        "https://your-rss-feed.com/feed/",
        # ... 其他源
    ],
}
```

## 常见问题

**Q: 如何修改定时时间？**
A: 编辑 `config.py` 中的 `SCHEDULE_CONFIG`

**Q: 如何添加新闻源？**
A: 编辑 `config.py` 中的 `NEWS_SOURCES`

**Q: 如何查看运行日志？**
A: 查看 `logs/` 目录下的日志文件

## License

MIT
