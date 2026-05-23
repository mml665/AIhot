from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import threading

from backend.scraper import fetch_all
from backend.news_store import load_news, update_news

app = FastAPI(title="AIhot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


@app.on_event("startup")
def startup():
    # Run initial scrape in background
    threading.Thread(target=_safe_scrape, daemon=True).start()


def _safe_scrape():
    try:
        from backend.scraper import fetch_all
        from backend.news_store import update_news
        new_items = fetch_all()
        update_news(new_items)
        print(f"[Startup] Scraped {len(new_items)} items")
    except Exception as e:
        print(f"[Startup] Scrape failed: {e}")


@app.get("/api/news")
def get_news(
    category: str = Query(None, description="按分类筛选"),
    q: str = Query(None, description="搜索关键词"),
):
    news = load_news()

    if category and category != "all":
        news = [n for n in news if n.get("category") == category]

    if q:
        q_lower = q.lower()
        news = [
            n for n in news
            if q_lower in n.get("title", "").lower()
            or q_lower in n.get("summary", "").lower()
        ]

    return {"total": len(news), "items": news}


@app.get("/api/categories")
def get_categories():
    news = load_news()
    categories = list({n.get("category", "科技") for n in news})
    categories.sort()
    return {"categories": categories}


@app.post("/api/refresh")
def refresh():
    try:
        new_items = fetch_all()
        update_news(new_items)
        return {"status": "ok", "count": len(new_items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Serve static files
app.mount("/css", StaticFiles(directory=os.path.join(ROOT_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(ROOT_DIR, "js")), name="js")
app.mount("/data", StaticFiles(directory=os.path.join(ROOT_DIR, "data")), name="data")
app.mount("/images", StaticFiles(directory=os.path.join(ROOT_DIR, "images")), name="images")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(ROOT_DIR, "index.html"))
