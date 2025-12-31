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

# 這裡改成清單 (List)，想監控什麼幣就在這裡加，格式一定要是 'XXX/USDT'
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT']

THRESHOLD = 1.0 # 波動閥值 (%) -> 多幣監控建議稍微調高一點，避免太吵
# ==========================================

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 BingX 多幣監控機器人運作中..."

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

def run_bot():
    exchange = ccxt.bingx({
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })

    print(f"🚀 多幣背景監控啟動: {SYMBOLS}")
    send_line_msg(f"雲端機器人已升級！\n正在監控: {', '.join(SYMBOLS)}")

    # 建立一個字典來存放「每個幣」的上次價格
    # 格式會像這樣: {'BTC/USDT': 90000, 'ETH/USDT': 3000}
    last_prices = {}

    while True:
        # 用 for 迴圈，一個一個輪流檢查
        for symbol in SYMBOLS:
            try:
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']

                # 如果是第一次執行這個幣，先記錄價格
                if symbol not in last_prices:
                    last_prices[symbol] = price
                    print(f"🔒 初始鎖定 {symbol}: {price}")
                    time.sleep(1) # 休息一下避免請求太快
                    continue

                # 讀取這個幣上次的價格
                old_price = last_prices[symbol]
                
                # 計算波動
                change = ((price - old_price) / old_price) * 100

                print(f"監控 {symbol}: {price} (波動 {change:.2f}%)")

                # 判斷是否觸發通知
                if abs(change) >= THRESHOLD:
                    emoji = "🔥 暴漲" if change > 0 else "🩸 暴跌"
                    
                    msg = f"【BingX 警報】\n{emoji} {symbol}\n現價: {price}\n幅度: {change:.2f}%"
                    send_line_msg(msg)
                    
                    last_prices[symbol] = price # 更新該幣種的基準價格

            except Exception as e:
                print(f"檢查 {symbol} 時發生錯誤: {e}")
            
            # 每次換下一個幣之前，稍微休息 1 秒 (避免太快被交易所擋)
            time.sleep(1)

        # 跑完一輪所有幣種後，休息 60 秒再開始下一輪
        print("--- 等待下一輪檢查 ---")
        time.sleep(60)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
