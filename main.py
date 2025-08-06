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

print(f"[INFO] TOKEN: {'OK' if TELEGRAM_TOKEN else 'MISSING'} | CHAT_ID: {TELEGRAM_CHAT_ID}")


def get_file_list():
    try:
        print("[INFO] Buscando lista de arquivos...")
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        arquivos = [a['href'] for a in soup.find_all("a") if a.get("href") and not a["href"].startswith("../")]
        print(f"[INFO] {len(arquivos)} arquivos encontrados.")
        return arquivos
    except Exception as e:
        print("[ERRO] Falha ao buscar lista:", e)
        return []


def send_telegram(text):
    try:
        print("[INFO] Enviando mensagem para o Telegram...")
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        )
        print("[INFO] Status Telegram:", r.status_code)
        if r.status_code != 200:
            print("[ERRO] Resposta do Telegram:", r.text)
    except Exception as e:
        print("[ERRO] Falha ao enviar Telegram:", e)


def monitor():
    current_files = get_file_list()

    if current_files:
        print("[INFO] Enviando lista de arquivos detectados...")
        msg = "📦 *Arquivos detectados:*
" + "\n".join(URL + x for x in current_files)
        send_telegram(msg)

    with open(CACHE_FILE, "w") as f:
        json.dump(current_files, f)


if __name__ == "__main__":
    print("[INFO] Monitoramento iniciado!")
    monitor()  # Envia na primeira execução
    while True:
        time.sleep(300)  # 5 minutos
        monitor()
