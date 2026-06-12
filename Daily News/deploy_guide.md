# AI每日新闻推送系统 - 云端部署指南

## 方案一：GitHub Actions（推荐，免费）

### 1. 创建GitHub仓库

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: AI News Scheduler"
git remote add origin https://github.com/yourusername/ai-news-scheduler.git
git push -u origin main
```

### 2. 配置GitHub Actions

在仓库中创建 `.github/workflows/daily-news.yml`：

```yaml
name: Daily AI News

on:
  schedule:
    # 每天 7:00, 10:00, 13:00, 16:00, 19:00, 22:00 (UTC时间)
    - cron: '0 23,2,5,8,11,14 * * *'  # UTC时间，对应北京时间7/10/13/16/19/22点
  workflow_dispatch:  # 允许手动触发

jobs:
  fetch-news:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run news scheduler
      run: python main.py --once
      
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add output/
        git diff --staged --quiet || git commit -m "Update AI news $(date +'%Y-%m-%d %H:%M')"
        git push
```

### 3. 配置Obsidian同步

在Obsidian中配置GitHub仓库同步：

1. 安装Obsidian Git插件
2. 配置远程仓库地址
3. 设置自动拉取间隔

---

## 方案二：云服务器部署（阿里云/腾讯云）

### 1. 购买云服务器

- 推荐配置：1核2G，Ubuntu 22.04
- 价格：约30-50元/月

### 2. 服务器环境配置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install python3 python3-pip python3-venv -y

# 创建项目目录
mkdir -p /opt/ai-news
cd /opt/ai-news

# 克隆代码
git clone https://github.com/yourusername/ai-news-scheduler.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置Systemd服务

创建服务文件 `/etc/systemd/system/ai-news.service`：

```ini
[Unit]
Description=AI News Scheduler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-news
ExecStart=/opt/ai-news/venv/bin/python main.py --scheduler
Restart=always
RestartSec=10
StandardOutput=append:/var/log/ai-news.log
StandardError=append:/var/log/ai-news-error.log

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-news
sudo systemctl start ai-news

# 查看状态
sudo systemctl status ai-news

# 查看日志
tail -f /var/log/ai-news.log
```

---

## 方案三：Serverless部署（AWS Lambda/阿里云函数）

### 1. 创建Serverless配置文件

创建 `serverless.yml`（以阿里云函数计算为例）：

```yaml
service: ai-news-scheduler

provider:
  name: aliyun
  runtime: python3.10
  region: cn-hangzhou

functions:
  fetch-news:
    handler: handler.main
    timeout: 300
    memorySize: 256
    events:
      - timer:
          cronExpression: '0 0 23,2,5,8,11,14 * * ? *'
          enabled: true
          payload: 'fetch-news'
```

### 2. 创建Handler函数

```python
# handler.py
from main import run_once

def main(event, context):
    """阿里云函数入口"""
    result = run_once()
    return {
        'statusCode': 200,
        'body': f'News fetched successfully: {result}'
    }
```

---

## 方案四：Docker容器部署

### 1. 创建Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建必要目录
RUN mkdir -p output logs data

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 启动命令
CMD ["python", "main.py", "--scheduler"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  ai-news:
    build: .
    container_name: ai-news-scheduler
    restart: unless-stopped
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
    network_mode: host
```

### 3. 部署命令

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## Obsidian配置

### 1. 安装Obsidian

下载地址：https://obsidian.md/

### 2. 配置Vault

1. 打开Obsidian
2. 选择"打开另一个库"
3. 选择 `output` 目录作为Vault位置

### 3. 安装推荐插件

- **Git**：自动同步云端文档
- **Calendar**：按日期查看新闻
- **Tag Wrangler**：管理标签
- **Dataview**：高级查询和统计

### 4. 配置自动同步

在Obsidian设置中：
1. 启用Git插件
2. 配置自动拉取间隔（建议5分钟）
3. 配置远程仓库地址

---

## 常见问题

### Q1: 如何修改定时时间？

编辑 `config.py` 文件中的 `SCHEDULE_CONFIG`：

```python
SCHEDULE_CONFIG = {
    "start_hour": 7,    # 开始时间
    "end_hour": 24,     # 结束时间
    "interval_hours": 3,  # 间隔小时数
    "timezone": "Asia/Shanghai"
}
```

### Q2: 如何添加新闻源？

编辑 `config.py` 文件中的 `NEWS_SOURCES`，添加新的RSS或网站URL。

### Q3: 如何查看运行日志？

- 本地运行：查看 `logs/` 目录下的日志文件
- 服务器部署：查看 `/var/log/ai-news.log`
- Docker部署：使用 `docker-compose logs -f`

### Q4: 如何手动触发一次任务？

```bash
python main.py --once
```

### Q5: 如何查看系统状态？

```bash
python main.py --status
```

---

## 技术支持

如有问题，请查看：
1. 项目README.md
2. 日志文件
3. GitHub Issues
