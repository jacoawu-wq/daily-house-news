import os
import requests
import feedparser
import datetime
from urllib.parse import quote

KEYWORDS = "房地產 OR 房市 OR 房價"
NEWS_LIMIT = 5

def get_google_news():
    encoded_keywords = quote(KEYWORDS)
    rss_url = f"[https://news.google.com/rss/search?q=](https://news.google.com/rss/search?q=){encoded_keywords}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    feed = feedparser.parse(rss_url)
    news_list = []
    for entry in feed.entries[:NEWS_LIMIT]:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return news_list

def send_line_notify(news_list):
    token = os.environ.get("LINE_NOTIFY_TOKEN")
    if not token:
        print("錯誤：找不到 LINE_NOTIFY_TOKEN")
        return
    today_str = datetime.date.today().strftime("%Y/%m/%d")
    message = f"\n🏠 【房市早報】 {today_str}\n" + "-" * 20 + "\n"
    if not news_list:
        message += "今日沒有相關新聞。"
    else:
        for idx, news in enumerate(news_list, 1):
            message += f"{idx}. {news['title']}\n🔗 {news['link']}\n\n"
    message += "-" * 20 + "\n祝你有美好的一天！"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"message": message}
    requests.post("[https://notify-api.line.me/api/notify](https://notify-api.line.me/api/notify)", headers=headers, data=payload)

if __name__ == "__main__":
    news = get_google_news()
    send_line_notify(news)

