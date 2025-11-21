import os
import requests
import feedparser
import datetime
from urllib.parse import quote

# 設定關鍵字
KEYWORDS = "房地產 OR 房市 OR 房價"
NEWS_LIMIT = 5

def get_google_news():
    encoded_keywords = quote(KEYWORDS)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keywords}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    print(f"正在抓取新聞: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    news_list = []
    if feed.entries:
        for entry in feed.entries[:NEWS_LIMIT]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published
            })
    else:
        print("⚠️ 警告：沒有抓到任何新聞，可能是關鍵字太冷門或是 Google 暫時擋住。")
        
    return news_list

def send_line_notify(news_list):
    token = os.environ.get("LINE_NOTIFY_TOKEN")
    
    if not token:
        print("錯誤：找不到 LINE_NOTIFY_TOKEN")
        return

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
    
    # --- 終極修正區 ---
    # 我們手動把網址拼起來，避開任何複製貼上的隱形字元問題
    part1 = "https://"
    part2 = "notify-api.line.me"
    part3 = "/api/notify"
    url = part1 + part2 + part3
    # ----------------
    
    try:
        print(f"準備連線到: {url}")
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            print("✅ 成功發送 LINE 通知！")
        else:
            print(f"❌ 發送失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            raise Exception("LINE API 回傳錯誤")
            
    except Exception as e:
        print(f"連線發生致命錯誤: {e}")
        raise e

if __name__ == "__main__":
    print("程式開始執行...")
    news = get_google_news()
    send_line_notify(news)
    print("程式執行結束")
