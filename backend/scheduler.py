from apscheduler.schedulers.background import BackgroundScheduler
from backend.scraper import fetch_all
from backend.news_store import update_news

scheduler = BackgroundScheduler()


def scrape_job():
    print("[Scheduler] Running scrape job...")
    try:
        new_items = fetch_all()
        update_news(new_items)
        print(f"[Scheduler] Done. Updated {len(new_items)} items.")
    except Exception as e:
        print(f"[Scheduler] Error: {e}")


def start_scheduler():
    scheduler.add_job(scrape_job, "interval", minutes=30, id="news_scraper")
    scheduler.start()
    print("[Scheduler] Started. Will scrape every 30 minutes.")


def stop_scheduler():
    scheduler.shutdown()
