import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Ошибка: API_ID и API_HASH должны быть указаны в файле .env")
        return
    
    print("🔐 Создаем сессию для получения session string...")
    
    # Create temporary client
    with TelegramClient("temp_session", int(api_id), api_hash) as client:
        # Get the session string
        session_string = client.session.save()
        print("\n✅ Ваш SESSION_STRING (добавьте его в .env файл):\n")
        print(session_string)
        print("\n⚠️ Сохраните этот токен в надежном месте и никому не передавайте!")
    
    # Clean up temporary session file
    try:
        os.remove("temp_session.session")
    except:
        pass

if __name__ == "__main__":
    main() 