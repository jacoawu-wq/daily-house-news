import os
import requests
import feedparser
import datetime
import json
from urllib.parse import quote

# ==========================================
# 設定區
# ==========================================
KEYWORDS = "房地產 OR 房市 OR 房價"
NEWS_LIMIT = 5
# ==========================================

def get_google_news():
    """從 Google News RSS 抓取新聞"""
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
        print("⚠️ 警告：沒有抓到任何新聞。")
        
    return news_list

def send_line_push(news_list):
    """使用 Messaging API 推送訊息"""
    # 從 GitHub Secrets 讀取兩把鑰匙
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN 或 LINE_USER_ID，請檢查 GitHub Secrets")
        return

    # 準備訊息內容
    today_str = datetime.date.today().strftime("%Y/%m/%d")
    text_content = f"🏠 【房市早報】 {today_str}\n"
    text_content += "-" * 20 + "\n"
    
    if not news_list:
        text_content += "今日沒有相關新聞。"
    else:
        for idx, news in enumerate(news_list, 1):
            title = news['title']
            link = news['link']
            text_content += f"{idx}. {title}\n🔗 {link}\n\n"
    
    text_content += "-" * 20 + "\n祝你有美好的一天！"

    # Messaging API 的網址 (這是官方帳號專用的)
    url = "https://api.line.me/v2/bot/message/push"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 這是 Messaging API 的格式
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text_content
            }
        ]
    }
    
    try:
        print("準備使用 Messaging API 推送...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ 成功發送 LINE 通知！(Messaging API)")
        else:
            print(f"❌ 發送失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            raise Exception("LINE API 回傳錯誤")
            
    except Exception as e:
        print(f"連線發生錯誤: {e}")
        raise e

if __name__ == "__main__":
    print("程式開始執行...")
    news = get_google_news()
    send_line_push(news)
    print("程式執行結束")
