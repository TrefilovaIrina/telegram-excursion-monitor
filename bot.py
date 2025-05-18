import os
import logging
from typing import Set
from dotenv import load_dotenv
from telethon import TelegramClient, events
import asyncio

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExcursionMonitorBot:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_id = self._get_env_int("API_ID")
        self.api_hash = self._get_env_str("API_HASH")
        self.your_chat_id = self._get_env_int("YOUR_CHAT_ID")
        self.target_chat_ids = self._get_target_chats()
        
        # Keywords to monitor
        self.keywords = [
            "экскурсия", "экскурсии", "гид", "гиды", "тур", "туры",
            "поездка", "экскурсовод", "гид по", "организовать тур",
            "куда поехать", "групповая экскурсия", "экскурсионная программа"
        ]
        
        # Initialize client
        session_path = os.path.join(os.getcwd(), "excursion_monitor.session")
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        self.available_chat_ids: Set[int] = set()

    def _get_env_str(self, key: str) -> str:
        """Get string environment variable with error handling."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Environment variable {key} is not set")
        return value

    def _get_env_int(self, key: str) -> int:
        """Get integer environment variable with error handling."""
        try:
            return int(self._get_env_str(key))
        except ValueError:
            raise ValueError(f"Environment variable {key} must be an integer")

    def _get_target_chats(self) -> list:
        """Get and validate target chat IDs from environment."""
        chats_str = self._get_env_str("TARGET_CHATS")
        try:
            return [int(chat_id.strip()) for chat_id in chats_str.split(',')]
        except ValueError:
            raise ValueError("TARGET_CHATS must be comma-separated integers")

    async def handle_new_message(self, event):
        """Handle new message events."""
        try:
            logger.info(f"Новое сообщение из чата {event.chat_id}: {event.text}")
            logger.info(f"💬 Проверяем chat_id: {event.chat_id} против: {self.available_chat_ids}")

            if event.chat_id not in self.available_chat_ids:
                logger.warning(f"⚠️ Чат {event.chat_id} не отслеживается. Пропускаем.")
                return

            if any(keyword in event.text.lower() for keyword in self.keywords):
                message = await self._prepare_notification(event)
                await self.client.send_message(self.your_chat_id, message)
                logger.info("✅ Уведомление отправлено.")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения: {e}", exc_info=True)

    async def _prepare_notification(self, event):
        """Prepare notification message with sender and chat info."""
        try:
            sender = await event.get_sender()
            if hasattr(sender, 'first_name'):
                sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
            elif hasattr(sender, 'title'):
                sender_name = sender.title
            else:
                sender_name = "Неизвестный отправитель"
        except Exception:
            sender_name = "Не удалось получить отправителя"

        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', None) or getattr(chat, 'username', None) or str(event.chat_id)
        link = f"https://t.me/{chat.username}/{event.id}" if getattr(chat, 'username', None) else "Ссылка недоступна"

        return (
            f"🔔 Обнаружено ключевое слово!\n\n"
            f"Чат: {chat_title}\n"
            f"От: {sender_name}\n"
            f"Сообщение: {event.text}\n\n"
            f"{link}"
        )

    async def initialize_chats(self):
        """Initialize available chats for monitoring."""
        dialogs = await self.client.get_dialogs()
        logger.info("📋 Список всех чатов:")
        
        for d in dialogs:
            raw_id = d.entity.id
            full_chat_id = int(f"-100{raw_id}") if d.entity.__class__.__name__ == "Channel" else raw_id
            
            logger.info(f"{d.name} — {raw_id}")
            logger.info(f"🔁 Сравниваю {full_chat_id} ∈ {self.target_chat_ids}")
            
            if full_chat_id in self.target_chat_ids:
                self.available_chat_ids.add(full_chat_id)
                logger.info(f"✅ Добавлен в мониторинг: {d.name} — {full_chat_id}")

        logger.info(f"🎯 Итого доступно чатов для отслеживания: {self.available_chat_ids}")
        
        if not self.available_chat_ids:
            logger.warning("❗ Ни один из чатов не был добавлен. Проверь TARGET_CHAT_IDS в .env!")

    async def start(self):
        """Start the bot."""
        try:
            logger.info("🚀 Запуск бота...")
            
            # Register message handler
            self.client.on(events.NewMessage)(self.handle_new_message)
            
            # Start client and initialize chats
            await self.client.start()
            await self.initialize_chats()
            
            me = await self.client.get_me()
            logger.info(f"🟢 Авторизовано как: {me.first_name} {me.last_name or ''}")
            
            # Run until disconnected
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
            raise
        finally:
            await self.client.disconnect()
            logger.info("👋 Бот остановлен")

def main():
    """Main entry point."""
    bot = ExcursionMonitorBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    main() 