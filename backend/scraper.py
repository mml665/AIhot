import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import re
import hashlib

# AI新闻 RSS 源
RSS_FEEDS = [
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
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "category": "科技",
        "source": "Ars Technica"
    },
    {
        "name": "MIT Tech Review",
        "url": "https://www.technologyreview.com/feed/",
        "category": "科技",
        "source": "MIT Tech Review"
    },
]

# 关键词匹配分类
CATEGORY_KEYWORDS = {
    "大模型": ["gpt", "llm", "大模型", "language model", "claude", "gemini", "llama", "transformer", "chatgpt", "openai", "deepseek", "文心", "通义"],
    "AIGC": ["aigc", "生成式", "生成", "sora", "midjourney", "stable diffusion", "dall-e", "图像生成", "视频生成", "音乐生成"],
    "机器人": ["robot", "机器人", "humanoid", "boston dynamics", "optimus", "具身"],
    "芯片": ["chip", "芯片", "gpu", "nvidia", "英伟达", "amd", "tpu", "算力"],
    "医疗AI": ["医疗", "medical", "diagnosis", "诊断", "health", "drug", "药物"],
    "自动驾驶": ["自动驾驶", "autonomous", "self-driving", "waymo", "tesla fsd"],
    "开源": ["开源", "open source", "open-source", "hugging face", "huggingface"],
    "政策": ["法案", "regulation", "监管", "policy", "法规", "合规"],
    "投资": ["融资", "投资", "valuation", "ipo", "收购", "funding", "series"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


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
            tag = "hot" if any(kw in title.lower() for kw in ["gpt", "openai", "google", "apple", "meta", "发布", "release", "launch"]) else ""

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


def fetch_all() -> list:
    all_news = []
    for feed in RSS_FEEDS:
        print(f"[Scraper] Fetching {feed['name']}...")
        news = fetch_rss(feed)
        all_news.extend(news)
        print(f"[Scraper] Got {len(news)} items from {feed['name']}")

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
