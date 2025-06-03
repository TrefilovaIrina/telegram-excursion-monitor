import os
import logging
import asyncio
import re
from typing import Set
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Загружаем переменные окружения из .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
YOUR_CHAT_ID = int(os.getenv("YOUR_CHAT_ID"))
TARGET_CHAT_IDS = [int(chat_id.strip()) for chat_id in os.getenv("TARGET_CHATS").split(",")]

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Проверка точных слов через регулярные выражения
def contains_keyword(text: str, keywords: list) -> bool:
    text = text.lower()
    return any(re.search(rf'\b{re.escape(word)}\b', text) for word in keywords)

# Инициализация клиента
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Ключевые слова
KEYWORDS = [
    "экскурсия", "экскурсии", "гид", "гиды", "тур", "туры",
    "поездка", "экскурсовод", "гид по", "организовать тур",
    "куда поехать", "групповая экскурсия", "экскурсионная программа"
]

available_chat_ids: Set[int] = set()

# Формирование уведомления
async def format_alert(event):
    try:
        sender = await event.get_sender()
        if hasattr(sender, "first_name"):
            sender_name = f"{sender.first_name} {getattr(sender, 'last_name', '')}".strip()
            sender_id = sender.id
        else:
            sender_name = "Неизвестный"
            sender_id = "?"

        chat = await event.get_chat()
        chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(event.chat_id)
        link = f"https://t.me/{chat.username}/{event.id}" if getattr(chat, "username", None) else "Ссылка недоступна"

        return (
            f"🔔 Обнаружено ключевое слово!\n\n"
            f"Чат: {chat_title}\n"
            f"От: {sender_name} (ID: {sender_id})\n"
            f"Сообщение:\n{event.text}\n\n"
            f"{link}"
        )
    except Exception as e:
        logger.error("Ошибка при формировании уведомления", exc_info=True)
        return "Ошибка при формировании уведомления."

# Обработка новых сообщений
@client.on(events.NewMessage)
async def handler(event):
    try:
        if event.chat_id not in available_chat_ids:
            return

        if contains_keyword(event.text, KEYWORDS):
            alert = await format_alert(event)
            await client.send_message(YOUR_CHAT_ID, alert)
            logger.info("🔔 Отправлено уведомление.")
    except Exception as e:
        logger.error("Ошибка в обработчике сообщений", exc_info=True)

# Запуск бота
async def run_bot():
    await client.start()
    dialogs = await client.get_dialogs()

    logger.info("📋 Проверяем доступные чаты...")
    for dialog in dialogs:
        if dialog.id in TARGET_CHAT_IDS:
            available_chat_ids.add(dialog.id)
            logger.info(f"✅ Добавлен: {dialog.name} ({dialog.id})")

    if not available_chat_ids:
        logger.warning("⚠️ Ни один чат не добавлен. Проверь TARGET_CHATS")

    logger.info("🚀 Бот запущен.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run_bot())
