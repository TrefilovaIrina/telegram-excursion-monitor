# Telegram Excursion Monitor Bot

Бот для мониторинга Telegram-чатов на предмет сообщений об экскурсиях, турах и гидах. Когда в отслеживаемых чатах появляются сообщения с ключевыми словами, бот отправляет уведомление в ваш личный чат.

## Возможности

- Мониторинг нескольких чатов одновременно
- Настраиваемый список ключевых слов
- Уведомления содержат информацию об отправителе и прямую ссылку на сообщение
- Подробное логирование работы бота
- Безопасная авторизация через session string

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/telegram-excursion-monitor.git
cd telegram-excursion-monitor
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Получите `API_ID` и `API_HASH` на сайте [my.telegram.org/apps](https://my.telegram.org/apps)

2. Узнайте свой `CHAT_ID`, написав боту [@userinfobot](https://t.me/userinfobot)

3. Создайте файл `.env` на основе `.env.example` и заполните `API_ID` и `API_HASH`

4. Получите SESSION_STRING:
```bash
python get_session_string.py
```
Скопируйте полученный токен и добавьте его в `.env` файл как `SESSION_STRING`

5. Добавьте остальные параметры в `.env`:
```env
API_ID=your_api_id
API_HASH=your_api_hash
YOUR_CHAT_ID=your_chat_id
TARGET_CHATS=chat_id1,chat_id2,chat_id3
SESSION_STRING=your_session_string
```

## Запуск

```bash
python bot.py
```

## Логирование

Бот ведет логи в файл `bot.log` и выводит их в консоль. В логах отображается:
- Статус подключения
- Список доступных чатов
- Обработка новых сообщений
- Ошибки и предупреждения

## Ключевые слова для мониторинга

По умолчанию бот отслеживает следующие слова:
- экскурсия/экскурсии
- гид/гиды
- тур/туры
- поездка
- экскурсовод
- организовать тур
- куда поехать
- групповая экскурсия
- экскурсионная программа

Список можно изменить в файле `bot.py` в переменной `keywords`.

## Безопасность

- Не публикуйте файл `.env` и SESSION_STRING в публичном доступе
- Используйте виртуальное окружение
- Регулярно обновляйте зависимости

## Лицензия

MIT 