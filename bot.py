import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Для Jupyter: не используем sys.stdout.reconfigure (он не поддерживается)
# Просто логируем в файл и подавляем ошибку в консоли
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Загрузка .env
load_dotenv()

# Чтение переменных
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")
your_chat_id = int(os.getenv("YOUR_CHAT_ID"))
target_chats = [int(x) for x in os.getenv("TARGET_CHATS", "").split(",")]

# Ключевые слова
KEYWORDS = [
    "экскурсия", "экскурсии", "гид", "гиды", "тур", "туры",
    "поездка", "экскурсовод", "гид по", "организовать тур",
    "куда поехать", "групповая экскурсия", "экскурсионная программа"
]

# Клиент
client = TelegramClient(StringSession(session_string), api_id, api_hash)
available_chat_ids = set()

# Обработка новых сообщений
@client.on(events.NewMessage)
async def handler(event):
    try:
        if event.chat_id not in available_chat_ids:
            return

        if any(word in event.text.lower() for word in KEYWORDS):
            message = await format_alert(event)
            await client.send_message(your_chat_id, message)
            logger.info(f"🔔 Сообщение отправлено в {your_chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)

# Формирование уведомления
async def format_alert(event):
    try:
        sender = await event.get_sender()
        sender_name = (
            f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip()
            if hasattr(sender, 'first_name') else getattr(sender, 'title', 'Неизвестный')
        )
        sender_id = getattr(sender, 'id', 'неизв.')
    except:
        sender_name = "Не удалось получить отправителя"
        sender_id = "N/A"

    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', None) or getattr(chat, 'username', None) or str(event.chat_id)
        username = getattr(chat, 'username', None)
        link = f"https://t.me/{username}/{event.id}" if username else "🔒 Ссылка недоступна"
    except:
        chat_title = str(event.chat_id)
        link = "❓ Не удалось получить ссылку"

    return (
        f"🔔 Обнаружено ключевое слово!\n\n"
        f"Чат: {chat_title}\n"
        f"От: {sender_name} (ID: {sender_id})\n"
        f"Сообщение:\n{event.text}\n\n"
        f"{link}"
    )

# Инициализация доступных чатов
async def init_chats():
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        chat_id = dialog.id
        if chat_id in target_chats:
            available_chat_ids.add(chat_id)
            logger.info(f"✅ Добавлен в мониторинг: {dialog.name} (ID: {chat_id})")
    if not available_chat_ids:
        logger.warning("❗ Ни один чат не найден среди TARGET_CHATS")

# Запуск бота
async def run_bot():
    await client.start()
    await init_chats()
    me = await client.get_me()
    logger.info(f"🟢 Авторизовано как: {me.first_name} ({me.id})")
    print("🎯 Бот запущен и отслеживает:", available_chat_ids)
    await client.run_until_disconnected()

# Если ты запускаешь в Jupyter
import nest_asyncio
import asyncio
nest_asyncio.apply()
await run_bot()
