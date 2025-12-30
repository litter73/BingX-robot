import ccxt
import requests
import time
import threading
from flask import Flask
from datetime import datetime

# ================= 設定區 =================
# 🔴 你的鑰匙 (必填)
CHANNEL_ACCESS_TOKEN = 'mR/GvB60ZUzjk3aX9c8FXIjytbCHh/APRVJGnPEEcq4doMTmGIWwwzBpLTqauXvCiz2+lLbT1fGVhm9PChGcARMVgowZzbbrTLYG30jcvFnZMS6D1sSEhzGTgiKWgVgm/TdINv3INFgcB6rrXbmdJgdB04t89/1O/w1cDnyilFU='
USER_ID = 'U69361ba216609afedd5ff9a53378f165'

SYMBOL = 'BTCUSDT'
THRESHOLD = 0.5  # 波動閥值
# =========================================

# 1. 建立一個假的網站伺服器 (為了騙過 Render，讓它以為我們是網站)
app = Flask(__name__)

@app.route('')
def home():
    return "🤖 BingX 機器人正在背景運作中..."

# 2. 定義機器人的核心邏輯
def run_bot():
    print(f"🚀 背景監控啟動: {SYMBOL}")
    exchange = ccxt.bingx({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})
    last_price = 0
    
    # 發送啟動通知
    send_line_msg(f"雲端機器人已上線！\n監控目標: {SYMBOL}")

    while True
        try
            ticker = exchange.fetch_ticker(SYMBOL)
            price = ticker['last']
            
            if last_price == 0
                last_price = price
                print(f"🔒 初始鎖定: {price}")
            else
                change = ((price - last_price)  last_price)  100
                print(f"監控中... {price} (波動 {change:.2f}%)") # 雲端 Log
                
                if abs(change) = THRESHOLD
                    emoji = "🔥 暴漲" if change > 0 else "🩸 暴跌"
                    msg = f"【BingX 警報】\n{emoji} {SYMBOL}\n現價: {price}\n幅度: {change:.2f}%"
                    send_line_msg(msg)
                    last_price = price

            time.sleep(60) # 雲端版建議改為 60 秒檢查一次，節省資源

        except Exception as e
            print(f錯誤 {e})
            time.sleep(60)

# LINE 發送函式
def send_line_msg(msg):
    url = 'httpsapi.line.mev2botmessagepush'
    headers = {'Authorization' f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    data = {'to' USER_ID, 'messages' [{'type' 'text', 'text' msg}]}
    try
        requests.post(url, headers=headers, json=data)
    except
        pass

# 3. 讓機器人在「背景執行緒」跑，主執行緒留給網站
def start_background_loop():
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()

# 程式入口
if __name__ == '__main__'
    start_background_loop() # 啟動機器人

    app.run(host='0.0.0.0', port=8080) # 啟動網站










