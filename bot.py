import requests, time, re, os, threading
from flask import Flask

#  
TOKEN = "9029188133:AAEv6m77gCm_ZUv-eI_7IgpBlRjxq7yMbB0"
URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(name)

@app.route('/')
def home():
    return "البوت شغال ✅"

watching = {}

def send(chat_id, text):
    try:
        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

def bot_loop():
    print("البوت شغال...")
    offset = 0
    while True:
        try:
            r = requests.get(f"{URL}/getUpdates", params={"offset": offset, "timeout": 10}).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                if "message" not in u:
                    continue
                chat_id = u["message"]["chat"]["id"]
                text = u["message"].get("text", "").strip()
                clean = re.sub(r'\D', '', text)
                if clean.isdigit() and len(clean) >= 9:
                    if len(clean) == 9:
                        clean = "967" + clean
                    watching[chat_id] = {"number": clean, "start": time.time(), "last_remind": time.time()}
                    send(chat_id, f"✅ مسكت الرقم: {clean}\nبدأت مراقبته 24 ساعة\nكل ساعة بذكرك\n\nافحصه الان: https://wa.me/{clean}\nاذا طلب الكود = افتك ✅\nاذا قال محظور = لسه ❌\n\nاذا افتك ارسل: افتك")
                    continue
                if text == "/start":
                    send(chat_id, "اهلا 👋\nارسل اي رقم واتساب، وانا براقبه 24 ساعة\nمثال: 967771234567")
                    continue
                if text == "افتك":
                    if chat_id in watching:
                        num = watching[chat_id]["number"]
                        send(chat_id, f"🎉 مبروك! الرقم {num} افتك ✅")
                        del watching[chat_id]
                    continue
                if text == "/stop":
                    if chat_id in watching:
                        del watching[chat_id]
                        send(chat_id, "⏹️ وقفت المراقبة")
                    continue
            now = time.time()
            for chat_id, data in list(watching.items()):
                passed = now - data["start"]
                if passed > 24*3600:
                    send(chat_id, f"⏰ انتهت 24 ساعة للرقم {data['number']}")
                    del watching[chat_id]
                    continue
                if now - data["last_remind"] >= 3600:
                    data["last_remind"] = now
                    left = int((24*3600 - passed)//3600)
                    send(chat_id, f"🔔 حان وقت فحص الرقم: {data['number']}\nباقي {left} ساعة\nافحصه: https://wa.me/{data['number']}\nاذا افتك ارسل: افتك")
            time.sleep(2)
        except Exception as e:
            print(e)
            time.sleep(3)

threading.Thread(target=bot_loop, daemon=True).start()

if name == "main":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
