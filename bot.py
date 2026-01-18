import os
import requests
from datetime import datetime

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден! Добавь переменную окружения TOKEN в Env.")

MAIN_CHANNEL_ID = -1003623180236   # основной канал
LOG_CHANNEL_ID  = -1003535405887   # лог канал
BANNED_FILE = "banned_users.txt"

# Загружаем забаненных
if os.path.exists(BANNED_FILE):
    with open(BANNED_FILE, "r") as f:
        banned = set(line.strip() for line in f)
else:
    banned = set()

def send_message(chat_id, text):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    full_text = f"[{timestamp}]\n{text}"
    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                         data={"chat_id": chat_id, "text": full_text})
    print(f"{chat_id}: {resp.status_code}, {resp.text}")

def main():
    offset = 0
    print("Бот запущен ✅")
    while True:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=60&offset={offset}"
        try:
            updates = requests.get(url).json()
        except Exception as e:
            print("Ошибка getUpdates:", e)
            continue

        if not updates.get("result"):
            continue

        for upd in updates["result"]:
            offset = upd["update_id"] + 1

            if "message" not in upd:
                continue

            msg = upd["message"]
            user_id = str(msg["from"]["id"])
            text = msg.get("text", "")
            
            if user_id in banned:
                continue  # игнорим забаненных

            # Игнорируем команды /start
            if text.startswith("/start"):
                continue

            # Формируем сообщение
            user_info = f"Пользователь: {msg['from'].get('username','нет юзернейма')} ({user_id})"
            msg_text = f"{user_info}\n{text}"

            # Отправляем в основной канал
            send_message(MAIN_CHANNEL_ID, msg_text)

            # Отправляем в лог канал
            send_message(LOG_CHANNEL_ID, msg_text)

if __name__ == "__main__":
    main()
