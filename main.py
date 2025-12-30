import ccxt
import requests
import time
import threading
from flask import Flask
from datetime import datetime

# ================= 設定區 =================
# 🔴 請記得把這裡換回你自己的 Token 和 User ID
CHANNEL_ACCESS_TOKEN = 'mR/GvB60ZUzjk3aX9c8FXIjytbCHh/APRVJGnPEEcq4doMTmGIWwwzBpLTqauXvCiz2+lLbT1fGVhm9PChGcARMVgowZzbbrTLYG30jcvFnZMS6D1sSEhzGTgiKWgVgm/TdINv3INFgcB6rrXbmdJgdB04t89/1O/w1cDnyilFU=' 
USER_ID = 'U69361ba216609afedd5ff9a53378f165'

SYMBOL = 'BTC/USDT'
THRESHOLD = 0.5 # 波動閥值 (%)
# ==========================================

# 1. 建立網站伺服器 (為了騙過 Render 不讓它睡著)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 BingX 機器人正在背景運作中..."

# 2. 定義傳送 LINE 訊息的功能 (使用 LINE Messaging API)
def send_line_msg(msg):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': USER_ID,
        'messages': [{'type': 'text', 'text': msg}]
    }
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"發送失敗: {e}")

# 3. 定義機器人的核心邏輯
def run_bot():
    # 修正字典語法：加上正確的冒號
    exchange = ccxt.bingx({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap'
        }
    })

    # 修正引號：加上雙引號
    print(f"🚀 背景監控啟動: {SYMBOL}")
    
    # 發送啟動訊息
    send_line_msg(f"雲端機器人已上線！\n監控目標: {SYMBOL}")

    last_price = 0

    while True:
        try:
            # 獲取價格
            ticker = exchange.fetch_ticker(SYMBOL)
            price = ticker['last']
            
            # 第一次執行時，先記錄價格，不發通知
            if last_price == 0:
                last_price = price
                print(f"🔒 初始鎖定: {price}")
                time.sleep(60)
                continue

            # 計算波動
            change = ((price - last_price) / last_price) * 100

            # 顯示監控狀態
            print(f"監控中... {price} (波動 {change:.2f}%)")

            # 判斷是否觸發通知
            if abs(change) >= THRESHOLD:
                emoji = "🔥 暴漲" if change > 0 else "🩸 暴跌"
                
                msg = f"【BingX 警報】\n{emoji} {SYMBOL}\n現價: {price}\n幅度: {change:.2f}%"
                send_line_msg(msg)
                
                last_price = price # 更新基準價格

            time.sleep(60) # 每分鐘檢查一次

        except Exception as e:
            print(f"發生錯誤: {e}")
            time.sleep(10)

# 4. 啟動後台執行緒
threading.Thread(target=run_bot, daemon=True).start()

# 5. 啟動網站 (Render 會透過 gunicorn 呼叫這裡)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
