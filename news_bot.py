import os
import requests
import feedparser
import datetime
from urllib.parse import quote

# ==========================================
# 設定區 (Settings)
# ==========================================
# 1. LINE Notify 的網址 (我把它拉出來，避免複製錯誤)
LINE_API = "https://notify-api.line.me/api/notify"

# 2. 搜尋關鍵字
KEYWORDS = "房地產 OR 房市 OR 房價"

# 3.新聞數量
NEWS_LIMIT = 5
# ==========================================

def get_google_news():
    """從 Google News RSS 抓取新聞"""
    encoded_keywords = quote(KEYWORDS)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keywords}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    print(f"正在抓取新聞: {rss_url}")
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
    """發送訊息到 LINE Notify"""
    token = os.environ.get("LINE_NOTIFY_TOKEN")
    
    if not token:
        raise ValueError("錯誤：找不到 LINE_NOTIFY_TOKEN，請檢查 GitHub Secrets 設定")

    today_str = datetime.date.today().strftime("%Y/%m/%d")
    
    message = f"\n🏠 【房市早報】 {today_str}\n"
    message += "-" * 20 + "\n"
    
    if not news_list:
        message += "今日沒有相關新聞。"
    else:
        for idx, news in enumerate(news_list, 1):
            title = news['title']
            link = news['link']
            message += f"{idx}. {title}\n🔗 {link}\n\n"
    
    message += "-" * 20 + "\n祝你有美好的一天！"

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"message": message}
    
    print("準備連線到 LINE API...")
    
    # 3. 這裡改成使用上面的變數，這樣最安全
    response = requests.post(LINE_API, headers=headers, data=payload)
    
    if response.status_code == 200:
        print("✅ 成功發送 LINE 通知！")
    else:
        raise Exception(f"發送失敗，狀態碼: {response.status_code}, 原因: {response.text}")

if __name__ == "__main__":
    print("程式開始執行...")
    news = get_google_news()
    send_line_notify(news)
    print("程式執行結束")
