# monitor_ff_bot/main.py
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import warnings
from bs4 import XMLParsedAsHTMLWarning

# Ignorar aviso sobre XML sendo interpretado como HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Constantes
URL = "https://dl.dir.freefiremobile.com/common/OB50/BR/"
CACHE_FILE = "cache.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_file_list():
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        return [a['href'] for a in soup.find_all("a") if a.get("href") and not a["href"].startswith("../")]
    except Exception as e:
        print("Erro ao buscar lista:", e)
        return []


def send_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        )
    except Exception as e:
        print("Erro ao enviar Telegram:", e)


def monitor():
    current_files = get_file_list()

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            old_files = json.load(f)
    else:
        old_files = []

    novos = list(set(current_files) - set(old_files))

    if novos:
        msg = "📦 *Novos arquivos adicionados:*\n" + "\n".join(URL + x for x in novos)
        send_telegram(msg)

    with open(CACHE_FILE, "w") as f:
        json.dump(current_files, f)


if __name__ == "__main__":
    while True:
        monitor()
        time.sleep(300)  # 5 minutos
