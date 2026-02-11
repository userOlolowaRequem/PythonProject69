import re
import time
import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot

URL = "https://lk.msu.ru/course/view?id=4098"
CHECK_EVERY = 5

BOT_TOKEN = "7690125049:AAHnSghqS5kxSmsR35M6Hdq0EVUmAVmmv2U"
CHAT_ID = 5165667315

PAT = re.compile(r"(\d+)\s*/\s*(\d+)")

def fetch_pair():
    r = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    strong = soup.find("strong", string=re.compile(r"Записалось\s*/\s*всего\s*мест"))
    if not strong:
        raise RuntimeError("Не найден блок 'Записалось / всего мест'")

    text = strong.parent.get_text(" ", strip=True)
    m = PAT.search(text)
    if not m:
        raise RuntimeError("Не нашёл X/Y")

    return int(m.group(1)), int(m.group(2))

async def send(msg: str):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)

async def main():
    last = None
    await send("Старт мониторинга мест на МФК.")

    while True:
        try:
            cur = fetch_pair()
            if cur != last:
                if last is not None:
                    await send(f"Изменилось: {last[0]}/{last[1]} → {cur[0]}/{cur[1]}")
                last = cur

            if cur == (499, 500):
                await send("🔥 Появилось место: стало 499/500!")
        except Exception as e:
            # чтобы не спамить, можно слать ошибки реже — но оставлю просто так
            await send(f"Ошибка при проверке: {e}")

        await asyncio.sleep(CHECK_EVERY)

if True:
    asyncio.run(main())