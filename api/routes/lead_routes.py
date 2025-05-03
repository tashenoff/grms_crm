import logging
from flask import jsonify, render_template, request
from api.routes import leads_bp
from api.services.lead_service import LeadService
import os
import requests
import json

# Configure logging
logger = logging.getLogger(__name__)

# Telegram API settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7793871539:AAEZ5Jw6_X96YnOUZMPptfogx4ej-SrQJns')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002506448215')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

def send_lead_to_telegram(lead_data, lead_id):
    """Отправляет заявку в Telegram"""
    try:
        # Формируем текст сообщения
        msg_text = f"🆕 *Новая заявка #{lead_id}*\n\n"
        
        if lead_data.get('client_name'):
            msg_text += f"👤 *Клиент:* {lead_data.get('client_name')}\n"
        
        if lead_data.get('phone'):
            msg_text += f"📞 *Телефон:* {lead_data.get('phone')}\n"
        
        if lead_data.get('message'):
            msg_text += f"📝 *Сообщение:* {lead_data.get('message')}\n"
        
        if lead_data.get('order_details'):
            msg_text += f"📦 *Детали заказа:* {lead_data.get('order_details')}\n"
        
        if lead_data.get('total_amount'):
            msg_text += f"💰 *Сумма:* {lead_data.get('total_amount')}\n"
        
        if lead_data.get('source'):
            msg_text += f"🔍 *Источник:* {lead_data.get('source')}\n"
        
        # Создаем кнопки статусов
        buttons = [
            [
                {'text': 'Оплачено', 'callback_data': f'status_accepted_{lead_id}'},
                {'text': 'В работе', 'callback_data': f'status_in_progress_{lead_id}'},
                {'text': 'Доставка', 'callback_data': f'status_delivery_{lead_id}'},
                {'text': 'Отказ', 'callback_data': f'status_declined_{lead_id}'}
            ]
        ]
        
        # Отправляем сообщение в Telegram
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg_text,
            'parse_mode': 'Markdown',
            'reply_markup': json.dumps({'inline_keyboard': buttons})
        }
        
        response = requests.post(f'{TELEGRAM_API_URL}/sendMessage', json=data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            message_id = result['result']['message_id']
            logger.info(f'Sent lead #{lead_id} to Telegram with message ID: {message_id}')
            
            # Сохраняем связь между заявкой и сообщением
            save_lead_message_mapping(lead_id, message_id)
            
            return True
        else:
            logger.error(f'Error sending lead to Telegram: {result}')
            return False
    
    except Exception as e:
        logger.error(f'Error sending lead to Telegram: {e}')
        return False

def save_lead_message_mapping(lead_id, message_id):
    """Сохраняет связь между заявкой и сообщением в Telegram"""
    try:
        import sqlite3
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        
        # Создаем таблицу, если она не существует
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
        
        # Сохраняем связь
        cursor.execute('''
            INSERT INTO lead_messages (lead_id, message_id)
            VALUES (?, ?)
        ''', (lead_id, message_id))
        
        conn.commit()
        conn.close()
        logger.info(f'Saved lead #{lead_id} - message #{message_id} mapping')
        return True
    except Exception as e:
        logger.error(f'Error saving lead-message mapping: {e}')
        return False

@leads_bp.route('/')
def index():
    """Index page route"""
    logger.debug('Handling index request')
    try:
        # Get all leads
        leads = LeadService.get_all_leads()
        return render_template('index.html', leads=leads)
    except Exception as e:
        logger.error(f'Error in index: {e}')
        raise

@leads_bp.route('/leads')
def get_leads():
    """Get all leads"""
    logger.debug('Handling leads request')
    try:
        # Get all leads
        leads = LeadService.get_all_leads()
        return jsonify(leads)
    except Exception as e:
        logger.error(f'Error in get_leads: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/lead_details/<int:lead_id>', methods=['GET'])
def get_lead_details(lead_id):
    """Get lead details by ID"""
    logger.debug(f'Handling lead details request for ID: {lead_id}')
    try:
        # Get lead by ID
        lead = LeadService.get_lead_by_id(lead_id)
        
        if not lead:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify(lead)
    except Exception as e:
        logger.error(f'Error in get_lead_details: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/user_leads/<phone>', methods=['GET'])
def get_user_leads(phone):
    """Get user leads by phone number"""
    logger.debug(f'Handling user leads request for phone: {phone}')
    try:
        # Get user leads by phone
        orders = LeadService.get_user_leads_by_phone(phone)
        return jsonify({'orders': orders})
    except Exception as e:
        logger.error(f'Error in get_user_leads for phone {phone}: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    try:
        # Get filtering parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Get statistics
        stats = LeadService.get_stats(start_date, end_date)
        return jsonify(stats)
    except Exception as e:
        logger.error(f'Error in get_stats: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/reset', methods=['POST'])
def reset_db():
    """Reset database"""
    try:
        # Reset database
        success = LeadService.reset_database()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f'Error in reset_db: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/create_lead', methods=['POST'])
def create_lead():
    """Create a new lead"""
    logger.debug('Handling create lead request')
    try:
        # Get lead data from request
        lead_data = request.json
        
        # Create lead in database
        lead_id = LeadService.create_lead(lead_data)
        
        # Отправляем заявку в Telegram
        send_lead_to_telegram(lead_data, lead_id)
        
        return jsonify({'id': lead_id}), 201
    except Exception as e:
        logger.error(f'Error in create_lead: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/update_lead/<int:lead_id>', methods=['POST'])
def update_lead(lead_id):
    """Update lead status"""
    logger.debug(f'Handling update lead request for ID: {lead_id}')
    try:
        # Get update data from request
        update_data = request.json
        
        # Update lead
        success = LeadService.update_lead(lead_id, update_data)
        
        if not success:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error in update_lead: {e}')
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/delete_lead/<int:lead_id>', methods=['POST'])
def delete_lead(lead_id):
    """Delete lead"""
    logger.debug(f'Handling delete lead request for ID: {lead_id}')
    try:
        # Delete lead
        success = LeadService.delete_lead(lead_id)
        
        if not success:
            return jsonify({'error': 'Lead not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error in delete_lead: {e}')
        return jsonify({'error': str(e)}), 500 