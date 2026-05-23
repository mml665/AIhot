# AIhot

AI 热点新闻聚合网站，自动抓取全球 AI 领域最新资讯，支持分类筛选、关键词搜索、暗色主题切换。

## 在线访问

**https://aihot-xyy.up.railway.app**

## 功能

- 自动爬取 AI 新闻（TechCrunch、The Verge、VentureBeat 等 RSS 源）
- 每 30 分钟自动更新
- 按分类筛选（大模型、AIGC、机器人、芯片、医疗 AI 等）
- 关键词搜索高亮
- 暗色/亮色主题切换
- 响应式设计，适配手机端

## 技术栈

- **前端**: HTML + CSS + JavaScript
- **后端**: Python FastAPI + Uvicorn
- **爬虫**: feedparser + BeautifulSoup + httpx
- **定时任务**: APScheduler
- **部署**: Railway

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py

# 访问
# http://localhost:8000
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/news` | 获取新闻列表，支持 `?category=` 和 `?q=` 筛选 |
| GET | `/api/categories` | 获取所有分类 |
| POST | `/api/refresh` | 手动触发新闻爬取 |

## 项目结构

```
AIhot/
├── backend/
│   ├── main.py          # FastAPI 应用入口
│   ├── scraper.py       # 新闻爬取逻辑
│   ├── scheduler.py     # 定时任务
│   └── news_store.py    # 数据存储
├── css/style.css        # 样式
├── js/main.js           # 前端逻辑
├── index.html           # 主页面
├── data/news.json       # 新闻数据
├── requirements.txt     # Python 依赖
└── run.py               # 本地启动脚本
```

## License

MIT
