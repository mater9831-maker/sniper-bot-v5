from flask import Flask, render_template, jsonify, request
import requests
import statistics
import time
import os 

app = Flask(__name__)

# --- 🔑 إمبراطورية المفاتيح الخماسية (4000 طلب/يوم) ---
API_KEYS = [
    "7ef0a2d27c0947b881021dbb81aa361a", 
    "f05c270723654dc186db83c8e1c4cc45", 
    "91b51a5171cc4b0586c33c6f99dbf9bf", 
    "6bcf1a53b42a426a877420bd7d93b8d4", 
    "f40ff31fe00d4bd5a2aecc13d58cfc32"
]

TELEGRAM_TOKEN = "7999325456:AAGVt1-cb1gbzKQ4DVDylpUDl6AmTUCIxO4"
TELEGRAM_CHAT_ID = "1114994571"

SYMBOLS = ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "GBP/JPY", "EUR/JPY", "USD/CAD", "NZD/USD", "BTC/USD"]
current_key_index = 0

def get_pip_value(symbol):
    if "JPY" in symbol or "XAU" in symbol or "BTC" in symbol:
        return 0.10 if ("XAU" in symbol or "BTC" in symbol) else 0.01
    return 0.0001

def analyze_vsa(candles):
    curr, prev = candles[0], candles[1]
    avg_vol = statistics.mean([c["volume"] for c in candles[:20]])
    spread = curr["high"] - curr["low"]
    close_pos = (curr["close"] - curr["low"]) / spread if spread > 0 else 0
    if curr["volume"] > avg_vol * 1.5 and curr["low"] < prev["low"] and close_pos > 0.6:
        return "BUY", "Shakeout"
    if curr["volume"] > avg_vol * 1.5 and curr["high"] > prev["high"] and close_pos < 0.4:
        return "SELL", "Upthrust"
    return None, None

@app.route('/scan')
def scan():
    global current_key_index
    found_signals = []
    for symbol in SYMBOLS:
        time.sleep(2) 
        for _ in range(len(API_KEYS)):
            api_key = API_KEYS[current_key_index]
            url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&outputsize=30&apikey={api_key}"
            try:
                data = requests.get(url).json()
                if "code" in data and (data["code"] == 429 or data.get("status") == "error"):
                    current_key_index = (current_key_index + 1) % len(API_KEYS)
                    continue
                if "values" in data:
                    candles = [{"open": float(c["open"]), "close": float(c["close"]), "high": float(c["high"]), "low": float(c["low"]), "volume": float(c.get("volume", 1))} for c in data["values"]]
                    sma = sum([c["close"] for c in candles[:20]]) / 20
                    trend = "bullish" if candles[0]["close"] > sma else "bearish"
                    sig, model = analyze_vsa(candles)
                    if sig and ((sig == "BUY" and trend == "bullish") or (sig == "SELL" and trend == "bearish")):
                        price = candles[0]["close"]
                        pip = get_pip_value(symbol)
                        sl = price - (4 if "XAU" in symbol else 40*pip) if sig == "BUY" else price + (4 if "XAU" in symbol else 40*pip)
                        tp = price + (12 if "XAU" in symbol else 120*pip) if sig == "BUY" else price - (12 if "XAU" in symbol else 120*pip)
                        msg = f"🎯 إشارة قناص: {symbol}\nنموذج: {model}\nنوع: {sig}\n📍 السعر: {price:.2f}\n🛑 ستوب: {sl:.2f}\n✅ هدف: {tp:.2f}"
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
                        found_signals.append(symbol)
                    break 
            except:
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                continue
    status_text = f"✅ فحص Render مكتمل.\nالمفتاح النشط: رقم {current_key_index + 1}\nإشارات: {len(found_signals)}"
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": status_text})
    return jsonify({"status": "Scan Complete"})

@app.route('/')
def home(): return "Sniper Bot is Running on Render!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
