# CRM Bot System

## Описание
Система управления заявками с:
- Telegram-ботом для обработки заказов
- Веб-интерфейсом для менеджеров
- Отслеживанием статусов (Новая, В работе, Доставка, Завершена)

## Установка
1. Клонировать репозиторий
2. Установить зависимости:
```bash
pip install -r requirements.txt
```
3. Настроить `.env` файл (пример в `.env.example`)

## Запуск
### Бэкенд (Flask API)
```bash
python app.py
```

### Бот (crm_bot.py)
```bash
python crm_bot.py
```

### Веб-интерфейс (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Основные компоненты
- `app.py` - Flask API (бэкенд)
- `crm_bot.py` - Telegram бот (работает через API)
- `/frontend` - Next.js приложение (фронтенд)

## Конфигурация
Скопировать `.env.example` в `.env` и задать:
- `TELEGRAM_TOKEN` - токен бота
- `DATABASE_URL` - строка подключения к БД
- `API_URL` - адрес API (по умолчанию `http://localhost:5000`)

## Порты по умолчанию
- Flask API: 5000
- Next.js: 3000
- Бот: зависит от конфигурации Telegram
