from flask import Flask
import requests

app = Flask(__name__)

# بياناتك
TOKEN = "7620242555:AAH0pW6_k9K1_rV3O-YFfB-E7z2C9j3w1I8"
CHAT_ID = "5378417066"
API_KEYS = ["7ef0a2d27c0947b881021dbb81aa361a", "f05c270723654dc186db83c8e1c4cc45"]
SYMBOLS = "BTC/USD,ETH/USD,XAU/USD"

@app.route('/')
def home():
    return "<h1>Bot is Online</h1><a href='/scan'>Click here to Test Telegram</a>"

@app.route('/scan')
def scan():
    try:
        # 1. نجيب الأسعار
        price_text = "🎯 الأسعار الآن:\n"
        for key in API_KEYS:
            url = f"https://api.twelvedata.com/price?symbol={SYMBOLS}&apikey={key}"
            data = requests.get(url, timeout=10).json()
            
            # معالجة داتا TwelveData لو رجعت كذا عملة
            if "status" not in str(data): 
                for s in SYMBOLS.split(','):
                    if s in data:
                        price_text += f"💰 {s}: {data[s]['price']}\n"
                break
        
        # 2. نبعت لتليجرام
        tel_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(tel_url, json={'chat_id': CHAT_ID, 'text': price_text})
        
        return f"DONE! Check Telegram. <br> {price_text}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
