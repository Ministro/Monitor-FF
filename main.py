import requests
from bs4 import BeautifulSoup
import json
import os
import time
import warnings
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

URL = "https://dl.dir.freefiremobile.com/common/OB50/BR/"
CACHE_FILE = "cache.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"[INFO] TOKEN: {'OK' if TELEGRAM_TOKEN else 'MISSING'} | CHAT_ID: {TELEGRAM_CHAT_ID}")

def get_file_list():
    try:
        print("[INFO] Buscando lista de arquivos...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        arquivos = [a['href'] for a in soup.find_all("a") if a.get("href") and not a["href"].startswith("../")]
        print(f"[INFO] {len(arquivos)} arquivos encontrados.")
        return arquivos
    except Exception as e:
        print("[ERRO] Falha ao buscar lista:", e)
        return []

def send_telegram_message(text):
    try:
        print("[INFO] Enviando mensagem para o Telegram...")
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        )
        print("[INFO] Status Telegram (mensagem):", r.status_code)
        if r.status_code != 200:
            print("[ERRO] Resposta do Telegram:", r.text)
    except Exception as e:
        print("[ERRO] Falha ao enviar mensagem Telegram:", e)

def send_telegram_photo(photo_url, caption=None):
    try:
        print(f"[INFO] Enviando foto para o Telegram: {photo_url}")
        data = {"chat_id": TELEGRAM_CHAT_ID, "photo": photo_url}
        if caption:
            data["caption"] = caption
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data=data
        )
        print("[INFO] Status Telegram (foto):", r.status_code)
        if r.status_code != 200:
            print("[ERRO] Resposta do Telegram:", r.text)
    except Exception as e:
        print("[ERRO] Falha ao enviar foto Telegram:", e)

def monitor():
    current_files = get_file_list()

    if current_files:
        print("[INFO] Enviando arquivos detectados...")
        # Envia mensagem geral com todos os arquivos
        msg = "📦 *Arquivos detectados:*\n" + "\n".join(URL + x for x in current_files)
        send_telegram_message(msg)

        # Envia fotos separadas para arquivos .png e .jpg
        for arquivo in current_files:
            if arquivo.lower().endswith((".png", ".jpg", ".jpeg")):
                photo_url = URL + arquivo
                caption = f"🖼️ *Imagem detectada:* {arquivo}"
                send_telegram_photo(photo_url, caption)

    with open(CACHE_FILE, "w") as f:
        json.dump(current_files, f)

if __name__ == "__main__":
    print("[INFO] Monitoramento iniciado!")
    monitor()  # Envia na primeira execução
    while True:
        time.sleep(300)  # 5 minutos
        monitor()
