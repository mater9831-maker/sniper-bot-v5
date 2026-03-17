from flask import Flask
import requests
import time

app = Flask(__name__)

# --- بياناتك الشخصية ---
TOKEN = "7620242555:AAH0pW6_k9K1_rV3O-YFfB-E7z2C9j3w1I8"
CHAT_ID = "5378417066"
API_KEYS = [
    "7ef0a2d27c0947b881021dbb81aa361a",
    "f05c270723654dc186db83c8e1c4cc45",
    "91b51a5171cc4b0586c33c6f99dbf9bf",
    "6bcf1a53b42a426a877420bd7d93b8d4",
    "f40ff31fe00d4bd5a2aecc13d58cfc32"
]
SYMBOLS = "BTC/USD,ETH/USD,XAU/USD"

@app.route('/')
def home():
    return "<h1>🎯 Sniper Bot V5 is Running</h1><a href='/scan'>Click here to Test Telegram</a>"

@app.route('/scan')
def scan():
    price_text = "🎯 تقرير الأسعار اللحظي:\n\n"
    api_success = False
    last_error = "None"

    # 1. محاولة جلب الأسعار من API
    for key in API_KEYS:
        try:
            url = f"https://api.twelvedata.com/price?symbol={SYMBOLS}&apikey={key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and "status" not in str(data):
                for s in SYMBOLS.split(','):
                    if s in data:
                        price = data[s].get('price', 'N/A')
                        price_text += f"💰 {s}: `{price}`\n"
                api_success = True
                break
        except Exception as e:
            last_error = f"API Error: {str(e)}"
            continue

    if not api_success:
        return f"❌ فشل جلب الأسعار. السبب: {last_error}"

    # 2. محاولة الإرسال لتليجرام (مع نظام إعادة المحاولة لحل مشكلة الـ DNS)
    for i in range(3): 
        try:
            tel_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            res = requests.post(tel_url, json={'chat_id': CHAT_ID, 'text': price_text, 'parse_mode': 'Markdown'}, timeout=15)
            if res.status_code == 200:
                return f"✅ DONE! Telegram Sent.<br><pre>{price_text}</pre>"
        except Exception as e:
            last_error = str(e)
            time.sleep(5) # استنى 5 ثواني لو فيه مشكلة في الشبكة وجرب تاني
            
    return f"❌ السيرفر لسه مش شايف تليجرام. السبب: {last_error}"

if __name__ == "__main__":
    # البورت الإجباري لـ Hugging Face
    app.run(host="0.0.0.0", port=7860)
