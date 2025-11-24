import os
import requests
import feedparser
import datetime
import json
from urllib.parse import quote

# ==========================================
# 設定區 (進階篩選版)
# ==========================================

# 1. 定義主題
TOPICS = "房地產 OR 房市 OR 房價 OR 建案 OR 預售屋 OR 重劃區"

# 2. 定義地區：鎖定六都
LOCATIONS = "台北 OR 新北 OR 桃園 OR 台中 OR 台南 OR 高雄"

# 3. 組合關鍵字
KEYWORDS = f"({TOPICS}) AND ({LOCATIONS})"

# 4. 新聞數量
NEWS_LIMIT = 10

# 5. 廣告/建案 識別關鍵字
AD_KEYWORDS = ["建案", "預售", "重劃區", "開賣", "熱銷", "總價", "萬起", "登場", "公開"]
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
            title = entry.title
            
            # 自動標記建案/廣編
            if any(ad_word in title for ad_word in AD_KEYWORDS):
                title = f"{title} (建案/廣編)"
            
            news_list.append({
                "title": title,
                "link": entry.link,
                "published": entry.published
            })
    else:
        print("⚠️ 警告：沒有抓到任何新聞。")
        
    return news_list

def send_line_broadcast(news_list):
    """
    使用 Messaging API 的 'Flex Message' 功能
    讓標題直接變成超連結，版面更美觀
    """
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN，請檢查 GitHub Secrets")
        return

    today_str = datetime.date.today().strftime("%Y/%m/%d")

    # --- 建構 Flex Message 內容 (JSON) ---
    
    # 1. 新聞列表元件
    news_components = []
    if not news_list:
        news_components.append({
            "type": "text",
            "text": "今日沒有相關新聞。",
            "color": "#aaaaaa"
        })
    else:
        for idx, news in enumerate(news_list, 1):
            news_components.append({
                "type": "text",
                "text": f"{idx}. {news['title']}",
                "wrap": True,        # 允許換行
                "color": "#0066cc",  # 設定為連結藍色
                "decoration": "underline", # 加上底線，讓它看起來像連結
                "size": "sm",
                "action": {          # 設定點擊動作
                    "type": "uri",
                    "label": "Open",
                    "uri": news['link']
                },
                "margin": "md"       # 增加一點間距
            })

    # 2. 組合完整的 Bubble Container
    bubble_content = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🏠 六都房市/建案快訊",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#1DB446" # LINE 綠色
                },
                {
                    "type": "text",
                    "text": today_str,
                    "size": "xs",
                    "color": "#aaaaaa",
                    "margin": "sm"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": news_components
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "separator", # 分隔線
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "祝您投資順利！",
                    "size": "xs",
                    "color": "#aaaaaa",
                    "align": "center",
                    "margin": "md"
                }
            ]
        }
    }

    # 3. 設定發送 Payload
    payload = {
        "messages": [
            {
                "type": "flex",
                "altText": f"🏠 房市快訊 {today_str}", # 這是在聊天列表顯示的預覽文字
                "contents": bubble_content
            }
        ]
    }
    # -------------------------------------

    url = "https://api.line.me/v2/bot/message/broadcast"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("準備發送 Flex Message...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ 成功發送 LINE 通知！")
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
    send_line_broadcast(news)
    print("程式執行結束")
