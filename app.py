from flask import Flask
import requests

app = Flask(__name__)

TOKEN = "7620242555:AAH0pW6_k9K1_rV3O-YFfB-E7z2C9j3w1I8"
CHAT_ID = "5378417066"
API_KEYS = ["7ef0a2d27c0947b881021dbb81aa361a", "f05c270723654dc186db83c8e1c4cc45", "91b51a5171cc4b0586c33c6f99dbf9bf", "6bcf1a53b42a426a877420bd7d93b8d4", "f40ff31fe00d4bd5a2aecc13d58cfc32"]

@app.route('/scan')
def scan():
    key = API_KEYS[0]
    # 1. فحص TwelveData أولاً
    try:
        td_res = requests.get(f"https://api.twelvedata.com/price?symbol=BTC/USD&apikey={key}", timeout=10)
        td_data = td_res.json()
        price = td_data.get('price', 'N/A')
    except Exception as e:
        return f"❌ TwelveData Down: {str(e)}"

    # 2. محاولة إرسال تليجرام مع نظام إعادة محاولة
    tel_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': f"✅ السعر الآن: {price}"}
    
    try:
        # بنحاول نكلم تليجرام 3 مرات لو فشل
        for _ in range(3):
            try:
                r = requests.post(tel_url, data=payload, timeout=20)
                if r.status_code == 200:
                    return f"✅ Success! BTC: {price} sent to Telegram."
            except:
                continue
        return "❌ DNS Error: Server can't find Telegram. Try again in 1 minute."
    except Exception as e:
        return f"❌ Telegram Connection Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
