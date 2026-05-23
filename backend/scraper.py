import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re
import hashlib

# AI新闻 RSS 源
RSS_FEEDS = [
    # 国内源
    {
        "name": "36氪AI",
        "url": "https://36kr.com/feed",
        "category": "科技",
        "source": "36氪"
    },
    {
        "name": "IT之家AI",
        "url": "https://www.ithome.com/rss/",
        "category": "科技",
        "source": "IT之家"
    },
    {
        "name": "少数派",
        "url": "https://sspai.com/feed",
        "category": "产品",
        "source": "少数派"
    },
    # 海外源
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "大模型",
        "source": "TechCrunch"
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "产品",
        "source": "The Verge"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "大模型",
        "source": "VentureBeat"
    },
]

# 关键词匹配分类
CATEGORY_KEYWORDS = {
    "大模型": ["gpt", "llm", "大模型", "language model", "claude", "gemini", "llama", "transformer", "chatgpt", "openai", "deepseek", "文心", "通义", "千问", "豆包", "智谱", "百川", "minimax", "moonshot", "月之暗面", "零一万物"],
    "AIGC": ["aigc", "生成式", "生成", "sora", "midjourney", "stable diffusion", "dall-e", "图像生成", "视频生成", "音乐生成", "ai绘画", "ai写作", "文生图", "文生视频"],
    "机器人": ["robot", "机器人", "humanoid", "boston dynamics", "optimus", "具身", "人形"],
    "芯片": ["chip", "芯片", "gpu", "nvidia", "英伟达", "amd", "tpu", "算力", "华为昇腾", "寒武纪"],
    "医疗AI": ["医疗", "medical", "diagnosis", "诊断", "health", "drug", "药物", "医学"],
    "自动驾驶": ["自动驾驶", "autonomous", "self-driving", "waymo", "tesla fsd", "智能驾驶", "无人车"],
    "开源": ["开源", "open source", "open-source", "hugging face", "huggingface", "github"],
    "政策": ["法案", "regulation", "监管", "policy", "法规", "合规", "备案", "治理"],
    "投资": ["融资", "投资", "valuation", "ipo", "收购", "funding", "series", "估值", "独角兽"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

# 中文AI新闻网页爬取源（无RSS）
WEB_SCRAPERS = [
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "category": "大模型",
        "source": "量子位",
        "selectors": {
            "list": "article, .post-item, .news-item, a[href*='qbitai.com']",
            "title": "h2, h3, .title, .entry-title",
            "link": "a",
            "summary": "p, .excerpt, .summary"
        }
    },
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/",
        "category": "大模型",
        "source": "机器之心",
        "selectors": {
            "list": "article, .article-item, .news-item",
            "title": "h4, h3, .title",
            "link": "a",
            "summary": "p, .desc"
        }
    },
]


def classify_news(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return "科技"


def generate_id(title: str, url: str) -> str:
    raw = f"{title}{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def parse_time(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
        except Exception:
            pass
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6]).strftime("%Y-%m-%d")
        except Exception:
            pass
    return datetime.now().strftime("%Y-%m-%d")


def clean_html(html_str: str) -> str:
    if not html_str:
        return ""
    soup = BeautifulSoup(html_str, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text[:500]


def fetch_rss(feed_config: dict) -> list:
    news_list = []
    try:
        feed = feedparser.parse(feed_config["url"], request_headers=HEADERS)
        for entry in feed.entries[:15]:
            title = entry.get("title", "").strip()
            if not title:
                continue

            summary = ""
            if hasattr(entry, "summary"):
                summary = clean_html(entry.summary)
            elif hasattr(entry, "description"):
                summary = clean_html(entry.description)

            if not summary and hasattr(entry, "content"):
                summary = clean_html(entry.content[0].get("value", ""))

            url = entry.get("link", "")
            time_str = parse_time(entry)
            category = classify_news(title, summary)
            tag = "hot" if any(kw in title.lower() for kw in ["gpt", "openai", "google", "apple", "meta", "发布", "release", "launch", "突破", "首个", "开源", "融资"]) else ""

            news_list.append({
                "id": generate_id(title, url),
                "title": title,
                "summary": summary or title,
                "source": feed_config["source"],
                "time": time_str,
                "category": category,
                "tag": tag,
                "url": url
            })
    except Exception as e:
        print(f"[Scraper] Error fetching {feed_config['name']}: {e}")

    return news_list


def fetch_web(scraper_config: dict) -> list:
    news_list = []
    try:
        resp = httpx.get(scraper_config["url"], headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        selectors = scraper_config["selectors"]

        items = soup.select(selectors["list"])[:15]
        for item in items:
            title_el = item.select_one(selectors["title"])
            link_el = item.select_one(selectors["link"])
            summary_el = item.select_one(selectors["summary"])

            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 5:
                continue

            url = link_el.get("href", "") if link_el else ""
            if url and not url.startswith("http"):
                url = scraper_config["url"].rstrip("/") + url

            summary = summary_el.get_text(strip=True) if summary_el else title
            time_str = datetime.now().strftime("%Y-%m-%d")
            category = classify_news(title, summary)
            tag = "hot" if any(kw in title for kw in ["发布", "开源", "融资", "突破", "首个"]) else ""

            news_list.append({
                "id": generate_id(title, url),
                "title": title,
                "summary": summary[:500],
                "source": scraper_config["source"],
                "time": time_str,
                "category": category,
                "tag": tag,
                "url": url
            })
    except Exception as e:
        print(f"[Scraper] Error fetching web {scraper_config['name']}: {e}")

    return news_list


def fetch_all() -> list:
    all_news = []

    # 爬取RSS源
    for feed in RSS_FEEDS:
        print(f"[Scraper] Fetching RSS: {feed['name']}...")
        news = fetch_rss(feed)
        all_news.extend(news)
        print(f"[Scraper] Got {len(news)} items from {feed['name']}")

    # 爬取中文网页源
    for scraper in WEB_SCRAPERS:
        print(f"[Scraper] Fetching Web: {scraper['name']}...")
        news = fetch_web(scraper)
        all_news.extend(news)
        print(f"[Scraper] Got {len(news)} items from {scraper['name']}")

    # 去重
    seen_ids = set()
    unique_news = []
    for item in all_news:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_news.append(item)

    # 按时间倒序
    unique_news.sort(key=lambda x: x["time"], reverse=True)
    print(f"[Scraper] Total: {len(unique_news)} unique news items")
    return unique_news
