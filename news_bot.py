import os
import requests
import feedparser
import datetime
from urllib.parse import quote

# 1. 設定關鍵字
KEYWORDS = "房地產 OR 房市 OR 房價"
NEWS_LIMIT = 5

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
        # 如果沒設定 Token，直接報錯讓程式變紅色
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
    
    # 2. 這裡拿掉了 try-except 保護網
    # 如果網址有錯或連線失敗，程式會直接報錯 (亮紅燈)
    print("準備連線到 LINE API...")
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
    
    if response.status_code == 200:
        print("✅ 成功發送 LINE 通知！")
    else:
        # 如果 LINE 拒絕 (例如 Token 錯)，也直接報錯
        raise Exception(f"發送失敗，狀態碼: {response.status_code}, 原因: {response.text}")

if __name__ == "__main__":
    print("程式開始執行...")
    news = get_google_news()
    send_line_notify(news)
    print("程式執行結束")
