import os
import json
import sqlite3
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Используем токен напрямую, если переменная окружения не установлена
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7793871539:AAEZ5Jw6_X96YnOUZMPptfogx4ej-SrQJns')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# Database setup
def init_db():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            executor_id INTEGER,
            executor_username TEXT,
            executor_first_name TEXT,
            client_name TEXT,
            company TEXT,
            phone TEXT,
            city TEXT,
            address TEXT,
            order_details TEXT,
            total_amount TEXT,
            order_date TEXT,
            source TEXT DEFAULT 'сайт',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
        )
    ''')
    
    # Add columns if they don't exist
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN executor_id INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN executor_username TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN executor_first_name TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    # Add new structured fields if they don't exist
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN client_name TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN company TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN phone TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN city TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN address TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN order_details TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN total_amount TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN order_date TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'сайт'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

init_db()

def get_sender_info(message):
    """Extract sender information from message"""
    # Check for channel post
    sender_chat = message.get('sender_chat')
    if sender_chat:
        return {
            'id': sender_chat.get('id'),
            'username': sender_chat.get('username', 'Аноним')
        }
    
    # Check for regular message
    sender = message.get('from')
    if sender:
        return {
            'id': sender.get('id'),
            'username': sender.get('username', 'Аноним')
        }
    
    return None

def create_status_buttons(lead_id):
    """Create buttons for lead status updates"""
    return [
        [{'text': 'Оплачено', 'callback_data': f'status_accepted_{lead_id}'},
         {'text': 'В работе', 'callback_data': f'status_in_progress_{lead_id}'},
         {'text': 'Доставка', 'callback_data': f'status_delivery_{lead_id}'},
         {'text': 'Отказ', 'callback_data': f'status_declined_{lead_id}'}]
    ]

def parse_message_text(text):
    """
    Parse message text into structured fields
    Expected format может быть разным, включая:
    
    1. Простой формат:
    Клиент: Иван Иванов
    Телефон: +7 (123) 456-78-90
    
    2. Формат с эмодзи:
    👤 Клиент: Иван Иванов
    📞 Телефон: +7 (123) 456-78-90
    
    3. Сложный формат с вложенной структурой:
    👤 Клиент: Менеджер
    📞 Телефон: Имя клиента
    📍 Адрес: +7 (123) 456-78-90
    📦 Заказ: Город
    💰 Сумма: Адрес
    📅 Дата: 🆕 Новый заказ! 👤 Клиент: Реальное имя клиента...
    """
    parsed_data = {
        'client_name': '',
        'company': '',
        'phone': '',
        'city': '',
        'address': '',
        'order_details': '',
        'total_amount': '',
        'order_date': '',
        'source': ''
    }
    
    # Default to original text if parsing fails
    parsed_data['original_text'] = text
    
    # Try to parse structured fields
    try:
        # Словарь соответствия эмодзи полям
        emoji_mappings = {
            '👤': 'client_name',   # Клиент
            '🏢': 'company',       # Компания
            '📱': 'phone',         # Телефон (альтернативный)
            '📞': 'phone',         # Телефон
            '🏙️': 'city',          # Город
            '📍': 'address',       # Адрес
            '📦': 'order_details', # Заказ
            '💰': 'total_amount',  # Сумма
            '🕒': 'order_date',    # Время (альтернативный)
            '📅': 'order_date'     # Дата
        }
        
        # Словарь соответствия ключевых слов полям
        key_mappings = {
            'клиент': 'client_name',
            'имя': 'client_name',
            'фио': 'client_name',
            'компания': 'company',
            'организация': 'company',
            'фирма': 'company',
            'телефон': 'phone',
            'тел': 'phone',
            'номер': 'phone',
            'город': 'city',
            'населенный пункт': 'city',
            'адрес': 'address',
            'местоположение': 'address',
            'заказ': 'order_details',
            'товар': 'order_details',
            'услуга': 'order_details',
            'описание': 'order_details',
            'сумма': 'total_amount',
            'общая сумма': 'total_amount',
            'цена': 'total_amount',
            'стоимость': 'total_amount',
            'дата': 'order_date',
            'время': 'order_date',
            'срок': 'order_date'
        }
        
        # Проверяем, есть ли в сообщении строка с "🆕 Новый заказ!"
        # Если есть, то это сложная структура с вложенной информацией
        complex_format = False
        nested_data_start = None
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if '🆕 Новый заказ!' in line:
                complex_format = True
                nested_data_start = i
                break
        
        # Проверяем, есть ли в сообщении строки с "шт. x" - это признак заказа
        order_lines = []
        for i, line in enumerate(lines):
            if 'шт. x' in line and '₸' in line:
                order_lines.append(line.strip())
        
        # Если это сложная структура, обрабатываем её отдельно
        if complex_format and nested_data_start is not None:
            # Сначала обрабатываем первую часть сообщения (до "🆕 Новый заказ!")
            first_part_lines = lines[:nested_data_start]
            
            # Затем обрабатываем вторую часть (после "🆕 Новый заказ!")
            second_part = ' '.join(lines[nested_data_start:])
            
            # Извлекаем информацию из второй части (она содержит реальные данные клиента)
            # Ищем все поля с эмодзи во второй части
            for emoji, field in emoji_mappings.items():
                if emoji in second_part:
                    parts = second_part.split(emoji)
                    for i in range(1, len(parts)):
                        part = parts[i].strip()
                        if ':' in part:
                            value = part.split(':', 1)[1].strip()
                            # Обрезаем значение до следующего эмодзи, если оно есть
                            for e in emoji_mappings.keys():
                                if e in value:
                                    value = value.split(e)[0].strip()
                            
                            # Если это поле заказа, сохраняем всё, что идёт после него до следующего эмодзи
                            if field == 'order_details':
                                if order_lines:
                                    parsed_data[field] = '\n'.join(order_lines)
                                else:
                                    parsed_data[field] = value
                            else:
                                parsed_data[field] = value
            
            # Если не нашли некоторые поля во второй части, ищем их в первой части
            for i, line in enumerate(first_part_lines):
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем наличие эмодзи в начале строки
                for emoji, field in emoji_mappings.items():
                    if emoji in line and not parsed_data[field]:
                        parts = line.split(emoji, 1)[1].strip()
                        if ':' in parts:
                            value = parts.split(':', 1)[1].strip()
                            parsed_data[field] = value
                            break
            
            # Если общая сумма не найдена, ищем её специально
            if not parsed_data['total_amount']:
                for line in lines:
                    if '💰 Общая сумма:' in line:
                        parsed_data['total_amount'] = line.split('💰 Общая сумма:', 1)[1].strip()
                        break
            
            # Если дата не найдена, ищем её специально
            if not parsed_data['order_date']:
                for line in lines:
                    if '🕒 Дата:' in line:
                        parsed_data['order_date'] = line.split('🕒 Дата:', 1)[1].strip()
                        break
        else:
            # Обычная обработка для простой структуры
            # Сначала извлекаем все поля с эмодзи
            extracted_fields = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем наличие эмодзи в начале строки
                for emoji, field in emoji_mappings.items():
                    if emoji in line:
                        parts = line.split(emoji, 1)[1].strip()
                        if ':' in parts:
                            value = parts.split(':', 1)[1].strip()
                            extracted_fields[field] = value
                            break
            
            # Если найдены строки заказа, сохраняем их
            if order_lines:
                extracted_fields['order_details'] = '\n'.join(order_lines)
            
            # Проверяем, есть ли смещение полей (случай с менеджером Catzilla)
            if 'client_name' in extracted_fields and extracted_fields.get('client_name') == 'Catzilla':
                # Это менеджер, а не клиент - происходит смещение полей
                # Правильная структура:
                # client_name = phone (alex)
                # phone = address (+77761604911)
                # address = order_details (абая 8)
                # order_details = order_lines (Заглушка...)
                
                # Сохраняем оригинальные значения
                manager_name = extracted_fields.get('client_name', '')
                client_name = extracted_fields.get('phone', '')
                phone = extracted_fields.get('address', '')
                city = extracted_fields.get('order_details', '')
                address = extracted_fields.get('total_amount', '')
                
                # Проверяем, что телефон похож на телефон (содержит + и цифры)
                if phone and ('+' in phone or any(c.isdigit() for c in phone)):
                    # Это похоже на смещение полей, применяем коррекцию
                    parsed_data['client_name'] = client_name
                    parsed_data['phone'] = phone
                    parsed_data['city'] = city
                    parsed_data['address'] = address
                    
                    # Сохраняем информацию о менеджере
                    logger.info(f'Detected message from manager: {manager_name}')
                    
                    # Если есть строки заказа, используем их
                    if order_lines:
                        parsed_data['order_details'] = '\n'.join(order_lines)
                else:
                    # Если не похоже на смещение, используем оригинальные значения
                    parsed_data.update(extracted_fields)
                
                # Проверяем наличие ключевых слов для полей, которые не были найдены
                for line in lines:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    for keyword, field in key_mappings.items():
                        if keyword in key and not parsed_data[field]:
                            parsed_data[field] = value
                            break
        
        # Проверяем, что все поля заполнены корректно
        # Телефон должен содержать цифры и быть длиннее 5 символов
        if parsed_data['phone'] and (len(parsed_data['phone']) < 5 or not any(c.isdigit() for c in parsed_data['phone'])):
            # Это может быть не телефон, ищем настоящий телефон в других полях
            for field in ['address', 'city', 'client_name']:
                if parsed_data[field] and ('+' in parsed_data[field] or any(c.isdigit() for c in parsed_data[field])):
                    # Нашли похожий на телефон текст в другом поле
                    real_phone = parsed_data[field]
                    # Если это поле клиента, сохраняем значение телефона в поле телефона
                    if field == 'client_name':
                        parsed_data['phone'] = real_phone
                    else:
                        # Меняем местами значения
                        parsed_data['phone'], parsed_data[field] = real_phone, parsed_data['phone']
        
        # Проверяем, что имя клиента не содержит телефон
        if parsed_data['client_name'] and '+' in parsed_data['client_name'] and any(c.isdigit() for c in parsed_data['client_name']):
            # Это может быть телефон, а не имя клиента
            if not parsed_data['phone']:
                parsed_data['phone'] = parsed_data['client_name']
                parsed_data['client_name'] = ''
        
        # Если город и адрес перепутаны (город обычно короче адреса)
        if parsed_data['city'] and parsed_data['address'] and len(parsed_data['city']) > len(parsed_data['address']):
            parsed_data['city'], parsed_data['address'] = parsed_data['address'], parsed_data['city']
        
        # Если заказ содержит только одно слово, это может быть не заказ
        if parsed_data['order_details'] and len(parsed_data['order_details'].split()) == 1:
            # Проверяем, может ли это быть город
            if not parsed_data['city'] and parsed_data['order_details'].isalpha():
                parsed_data['city'] = parsed_data['order_details']
                parsed_data['order_details'] = ''
                
    except Exception as e:
        logger.error(f'Error parsing message text: {e}')
    
    return parsed_data

def save_message(message):
    """Save the message to the database and return the lead_id"""
    message_text = message.get('text', '')
    message_id = message.get('message_id')
    
    # Extract sender information
    sender_info = get_sender_info(message)
    if not sender_info:
        logger.warning("Could not extract sender info")
        return None
    
    sender_id = sender_info.get('id')
    username = sender_info.get('username', 'Аноним')
    
    # Parse message for structured data
    parsed_data = parse_message_text(message_text)
    
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    try:
        # Ensure user exists in the database
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username)
            VALUES (?, ?)
        ''', (sender_id, username))
        
        # Insert message as a lead
        cursor.execute('''
            INSERT INTO leads (
                telegram_id, username, message, 
                client_name, phone, city, address, 
                order_details, total_amount, order_date, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sender_id, 
            username, 
            message_text,
            parsed_data.get('client_name', ''),
            parsed_data.get('phone', ''),
            parsed_data.get('city', ''),
            parsed_data.get('address', ''),
            parsed_data.get('order_details', ''),
            parsed_data.get('total_amount', ''),
            parsed_data.get('order_date', ''),
            parsed_data.get('source', 'telegram')
        ))
        
        # Get the last inserted ID
        lead_id = cursor.lastrowid
        logger.info(f"Message saved with lead_id: {lead_id}")
        
        conn.commit()
        return lead_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving message: {e}")
        return None
    finally:
        conn.close()

def get_updates(offset=None):
    """Get updates from Telegram API"""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates'
        params = {
            'timeout': 100,
            'offset': offset,
            'allowed_updates': ['message', 'channel_post', 'callback_query']
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 409:
            logger.warning('Conflict error, retrying...')
            time.sleep(10)  # Increased delay
            return get_updates(offset)
        
        response.raise_for_status()
        result = response.json()
        if result.get('ok'):
            return result
        else:
            logger.error(f'Error in updates response: {result.get("description", "Unknown error")}')
            return {'ok': False, 'description': 'Error in response'}
    except Exception as e:
        logger.error(f'Error getting updates: {e}')
        return {'ok': False, 'description': str(e)}

def answer_callback_query(callback_query_id, text=None, show_alert=True):
    """Send callback query answer to Telegram without logging to CRM"""
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text, "show_alert": show_alert}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")

def send_message(chat_id, text, buttons=None, lead_id=None):
    """Send message to Telegram chat with optional buttons"""
    try:
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }

        if buttons:
            data['reply_markup'] = json.dumps({'inline_keyboard': buttons})

        response = requests.post(f'{TELEGRAM_API_URL}/sendMessage', json=data)
        response.raise_for_status()

        result = response.json()
        if result.get('ok'):
            message_id = result['result']['message_id']
            logger.info(f'Sent message with ID: {message_id}')
            
            # Если указан lead_id, сохраняем соответствие message_id -> lead_id
            if lead_id:
                save_message_id(lead_id, message_id)
            
            return message_id
        else:
            logger.error(f'Error sending message: {result}')
            return None

    except Exception as e:
        logger.error(f'Error sending message: {e}')
        return None

def edit_message(chat_id, message_id, text, buttons=None):
    """Edit message in Telegram chat"""
    try:
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text
        }

        if buttons:
            data['reply_markup'] = {
                'inline_keyboard': buttons
            }

        response = requests.post(f'{TELEGRAM_API_URL}/editMessageText', json=data)
        response.raise_for_status()
        
        logger.info(f'Edited message: {message_id}')
        
    except Exception as e:
        logger.error(f'Error editing message: {e}')

def delete_message(chat_id, message_id):
    """Delete a message from Telegram chat"""
    try:
        data = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        
        response = requests.post(f'{TELEGRAM_API_URL}/deleteMessage', json=data)
        response.raise_for_status()
        
        logger.info(f'Deleted message: {message_id}')
        
        # Отмечаем сообщение как удаленное в БД, если такая запись есть
        mark_message_deleted(message_id)
        
        return True
    except Exception as e:
        logger.error(f'Error deleting message: {e}')
        return False

def parse_callback_data(data):
    """Parse callback data from button click (Handles 'status_{status_key}_{lead_id}')"""    
    try:
        # Expected format: status_{status_key}_{lead_id}
        # Особая обработка для статуса 'in_progress', так как он содержит подчеркивание
        if 'status_in_progress_' in data:
            status = 'in_progress'
            lead_id = data.split('status_in_progress_')[1]
            # Validate lead_id is an integer
            try:
                int(lead_id)
                return status, lead_id
            except ValueError:
                logger.error(f'Invalid lead_id in callback data: {data}')
                return None, None
        else:
            # Обработка других статусов
            parts = data.split('_')
            if len(parts) == 3 and parts[0] == 'status':
                status = parts[1] # e.g., 'delivery', 'accepted'
                lead_id = parts[2] # e.g., '4'
                # Validate lead_id is an integer
                try:
                    int(lead_id)
                    return status, lead_id
                except ValueError:
                    logger.error(f'Invalid lead_id in callback data: {data}')
                    return None, None
            else:
                logger.warning(f'Unexpected callback data format: {data}')
                return None, None

    except Exception as e:
        logger.error(f'Error parsing callback data: {data}, Error: {e}')
        return None, None

def get_status_text(status):
    """Get human-readable status text"""
    return {
        'accepted': 'Оплачено',
        'in_progress': 'В работе',
        'delivery': 'Доставка',
        'declined': 'Отказ'
    }.get(status, 'Неизвестный статус')

def update_lead_status(lead_id, status, executor_info):
    """Update lead status in database"""
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Update lead status and add executor
    cursor.execute('''
        UPDATE leads 
        SET status = ?, executor_id = ?, executor_username = ?, executor_first_name = ?
        WHERE id = ?
    ''', (status, executor_info['id'], executor_info['username'], 
          executor_info['first_name'], int(lead_id)))
    
    conn.commit()
    conn.close()
    
    logger.info(f'Updated lead status: lead_id={lead_id}, status={status}, executor={executor_info["username"]}')

def get_lead_by_id(lead_id):
    """Get lead information from database"""
    conn = sqlite3.connect('crm.db')
    # Возвращаем строки как словари для доступа по ключу
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads WHERE id = ?', (int(lead_id),))
    lead = cursor.fetchone()
    conn.close()
    return lead

def handle_callback_query(callback_query):
    """Handle callback query from button click"""
    try:
        logger.info('=== START handle_callback_query ===')
        
        # Get message ID from callback query
        message_id = callback_query.get('message', {}).get('message_id')
        if not message_id:
            logger.warning('No message ID in callback query')
            return
            
        data = callback_query.get('data', '')
        if not data:
            logger.warning('No callback data')
            return
            
        # Parse callback data
        status, lead_id = parse_callback_data(data)
        if not status or not lead_id:
            return
            
        logger.info(f'Parsed status: {status}, lead_id: {lead_id}, message_id: {message_id}')
        
        # Get executor information
        executor_info = {
            'id': callback_query.get('from', {}).get('id'),
            'username': callback_query.get('from', {}).get('username'),
            'first_name': callback_query.get('from', {}).get('first_name')
        }
        
        # Get lead information before update
        lead = get_lead_by_id(lead_id)
        if not lead:
            logger.error(f'Lead not found: {lead_id}')
            return
            
        # Ограничение: только исполнитель, принявший заявку, может менять статус далее
        existing_executor = lead['executor_id']
        if existing_executor and existing_executor != executor_info['id']:
            # Оповещаем, что изменить статус может только тот, кто принял заявку
            answer_callback_query(callback_query.get('id'), 'Изменять статус может только исполнитель задачи.')
            return
        
        # Сохраняем оригинальный текст сообщения, чтобы не потерять структуру
        original_message_text = callback_query.get('message', {}).get('text', '')
        
        # Update lead status
        update_lead_status(lead_id, status, executor_info)
        
        # Get updated lead information
        updated_lead = get_lead_by_id(lead_id)
        if updated_lead:
            # Format status text
            status_text = get_status_text(status)
            
            # Создаем новый текст сообщения, сохраняя структуру оригинального сообщения
            # Удаляем старую информацию о статусе и исполнителе, если она есть
            new_text = original_message_text
            
            # Удаляем старую информацию о статусе и исполнителе
            status_index = new_text.find('\n📊 Статус:')
            if status_index != -1:
                new_text = new_text[:status_index]
            
            # Добавляем новую информацию о статусе и исполнителе
            new_text += f'\n\n📊 Статус: {status_text}\n👨‍💼 Исполнитель: {updated_lead[7]} (@{updated_lead[6]})'
            
            # Edit message with new text and keep buttons
            buttons = create_status_buttons(lead_id)
            edit_message(TELEGRAM_CHAT_ID, message_id, new_text, buttons)
        
        logger.info('=== END handle_callback_query ===')
            
    except Exception as e:
        logger.error(f'Error handling callback query: {e}')
        send_message(TELEGRAM_CHAT_ID, f'Ошибка при обновлении статуса: {str(e)}')

def process_callback_query(update, last_update_id):
    """Process callback query from button click"""
    callback_query = update.get('callback_query')
    if not callback_query:
        return last_update_id, False
        
    logger.info('=== CALLBACK QUERY RECEIVED ===')
    logger.info(f'Callback data: {callback_query.get("data", "No data")}')
    
    handle_callback_query(callback_query)
    return update['update_id'] + 1, True

def process_message(update, last_update_id):
    """Process a new message update"""
    message = update.get('message', None) or update.get('channel_post', None)
    if not message:
        logger.warning("No message or channel post in update")
        return
    
    logger.info(f"Received message from chat {message.get('chat', {}).get('id')}")
    
    # Check if message is from the target chat
    if 'chat' in message and message['chat']['id'] == int(TELEGRAM_CHAT_ID):
        logger.info("Message is from target chat")
        logger.info("Saving message to database")
        
        # Save message to database
        lead_id = save_message(message)
        
        if lead_id:
            # Construct response message
            msg_text = f"🆕 *Новая заявка #{lead_id}*\n\n"
            
            if 'text' in message:
                msg_text += f"📝 *Сообщение:* {message['text']}\n"
            
            # Extract user info
            sender = message.get('from')
            if sender:
                username = sender.get('username', 'Неизвестно')
                first_name = sender.get('first_name', 'Аноним')
                msg_text += f"\n👤 *От:* {first_name}"
                if username:
                    msg_text += f" (@{username})"
            
            # Delete original message
            delete_message(message['chat']['id'], message['message_id'])
            
            # Send formatted message with buttons
            send_message(message['chat']['id'], msg_text, create_status_buttons(lead_id), lead_id)
        else:
            logger.error("Failed to save message")
    else:
        logger.info("Message is not from target chat, ignoring")

def get_lead_message_mapping():
    """
    Получение маппинга заявок и сообщений Telegram
    """
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Выбираем все активные заявки с сообщениями
    cursor.execute('''
        SELECT l.id, l.status, m.message_id 
        FROM leads l
        JOIN lead_messages m ON l.id = m.lead_id
        WHERE m.is_deleted = 0
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    # Преобразуем результаты в словарь {lead_id: (status, message_id)}
    mapping = {lead_id: (status, message_id) for lead_id, status, message_id in results}
    return mapping

def sync_lead_statuses():
    """
    Синхронизирует статусы заявок в Telegram с актуальными данными из БД
    """
    logger.info("=== Начало синхронизации статусов заявок ===")
    try:
        # Получаем маппинг заявок и сообщений
        mapping = get_lead_message_mapping()
        
        for lead_id, (old_status, message_id) in mapping.items():
            # Получаем актуальные данные заявки
            lead = get_lead_by_id(lead_id)
            
            # Если статус изменился, обновляем сообщение
            if lead and lead['status'] != old_status:
                logger.info(f"Обновление статуса заявки в Telegram: {lead_id} с {old_status} на {lead['status']}")
                
                # Формируем текст сообщения
                msg_text = f"🆕 *Заявка #{lead['id']}*\n\n"
                if lead['client_name']:
                    msg_text += f"👤 *Клиент:* {lead['client_name']}\n"
                if lead['phone']:
                    msg_text += f"📞 *Телефон:* {lead['phone']}\n"
                if lead['message']:
                    msg_text += f"📝 *Сообщение:* {lead['message']}\n"
                
                # Добавляем информацию о статусе и исполнителе
                status_text = get_status_text(lead['status'])
                msg_text += f"\n🔄 *Статус:* {status_text}"
                
                if lead['executor_username']:
                    msg_text += f"\n👨‍💼 *Исполнитель:* {lead['executor_username']}"
                
                # Обновляем сообщение
                edit_message(
                    TELEGRAM_CHAT_ID, 
                    message_id, 
                    msg_text,
                    create_status_buttons(lead_id)
                )
    except Exception as e:
        logger.error(f"Ошибка при синхронизации статусов: {e}")
    
    logger.info("=== Завершение синхронизации статусов заявок ===")

# Проверка существования таблицы lead_messages
def ensure_lead_messages_table():
    """
    Создает таблицу для хранения идентификаторов сообщений для заявок, если её нет
    """
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lead_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            message_id INTEGER,
            is_deleted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
    ''')
    
    conn.commit()
    conn.close()


# Функция для сохранения идентификатора сообщения для заявки
def save_message_id(lead_id, message_id):
    """
    Сохраняет идентификатор отправленного сообщения для заявки
    """
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lead_messages (lead_id, message_id)
        VALUES (?, ?)
    ''', (lead_id, message_id))
    
    conn.commit()
    conn.close()

# Функция для отметки сообщения как удаленного
def mark_message_deleted(message_id):
    """
    Помечает сообщение как удаленное
    """
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE lead_messages 
        SET is_deleted = 1 
        WHERE message_id = ?
    ''', (message_id,))
    
    conn.commit()
    conn.close()

def main():
    """Start the bot"""
    logger.info('Starting CRM bot')
    logger.info(f'Using chat ID: {TELEGRAM_CHAT_ID}')
    
    # Подготавливаем необходимые таблицы
    ensure_lead_messages_table()
    
    last_update_id = None
    last_sync_time = 0
    sync_interval = 10  # Синхронизировать каждые 10 секунд
    
    # Send startup message
    chat_id = TELEGRAM_CHAT_ID
    startup_msg = "🤖 *CRM Telegram Bot запущен*\n\nБот готов принимать и обрабатывать заявки."
    send_message(chat_id, startup_msg)
    logger.info("Startup message sent successfully")
    
    # Main loop
    while True:
        try:
            # Проверяем, нужно ли сделать синхронизацию
            current_time = time.time()
            if current_time - last_sync_time > sync_interval:
                sync_lead_statuses()
                last_sync_time = current_time
            
            # Обрабатываем обновления
            updates = get_updates(last_update_id)
            
            if updates.get('result'):
                logger.info(f"Received {len(updates['result'])} updates")
                for update in updates['result']:
                    if 'update_id' in update:
                        last_update_id = update['update_id'] + 1
                    
                    # Обрабатываем обновления
                    if 'callback_query' in update:
                        process_callback_query(update, last_update_id)
                    elif 'message' in update:
                        process_message(update, last_update_id)
            
            # Пауза для снижения нагрузки
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    ensure_lead_messages_table()
    main()
