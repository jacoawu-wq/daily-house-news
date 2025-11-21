import os
import requests
import feedparser
import datetime
from urllib.parse import quote

# 設定搜尋關鍵字 (你可以自己修改這裡)
KEYWORDS = "房地產 OR 房市 OR 房價"
# 設定要抓取的新聞數量
NEWS_LIMIT = 5

def get_google_news():
    """從 Google News RSS 抓取新聞"""
    encoded_keywords = quote(KEYWORDS)
    # Google News RSS 網址 (針對台灣地區)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keywords}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    print(f"正在抓取新聞: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    news_list = []
    
    # 整理新聞內容
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
        print("錯誤：找不到 LINE_NOTIFY_TOKEN，請檢查 GitHub Secrets 設定")
        return

    # 取得今天的日期
    today_str = datetime.date.today().strftime("%Y/%m/%d")
    
    # 組合訊息內容
    message = f"\n🏠 【房市早報】 {today_str}\n"
    message += "-" * 20 + "\n"
    
    if not news_list:
        message += "今日沒有相關新聞。"
    else:
        for idx, news in enumerate(news_list, 1):
            # 清理標題 (有時候標題會太長或包含來源，這裡保持原樣即可)
            title = news['title']
            link = news['link']
            message += f"{idx}. {title}\n🔗 {link}\n\n"
    
    message += "-" * 20 + "\n祝你有美好的一天！"

    # 發送到 LINE
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"message": message}
    
    try:
        # 這裡是修正後的乾淨網址，解決了之前的錯誤
        response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
        if response.status_code == 200:
            print("成功發送 LINE 通知！")
        else:
            print(f"發送失敗，狀態碼: {response.status_code}")
    except Exception as e:
        print(f"發送過程發生錯誤: {e}")

if __name__ == "__main__":
    print("程式開始執行...")
    news = get_google_news()
    send_line_notify(news)
    print("程式執行結束")
