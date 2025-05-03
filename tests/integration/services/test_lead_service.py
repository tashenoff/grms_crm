import pytest
import sqlite3
import os
import tempfile
from api.services.lead_service import LeadService
from unittest.mock import patch, MagicMock

class TestLeadService:
    """Интеграционные тесты для сервиса LeadService"""
    
    @pytest.fixture
    def test_db(self):
        """Создает временную тестовую БД"""
        # Создаем временный файл для тестовой БД
        db_fd, db_path = tempfile.mkstemp()
        
        # Создаем подключение и схему БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Создаем таблицы для тестов
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем тестовые данные
        cursor.execute('''
            INSERT INTO leads (
                telegram_id, username, message, status, client_name, phone, 
                total_amount, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            123456789, 'test_user', 'Test message', 'new',
            'Иван Иванов', '+7 (123) 456-78-90', '1 500.00', 
            '2023-05-01 12:00:00'
        ))
        
        cursor.execute('''
            INSERT INTO leads (
                telegram_id, username, message, status, client_name, phone,
                total_amount, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            987654321, 'test_user2', 'Test message 2', 'accepted',
            'Петр Петров', '+7 (987) 654-32-10', '2 500.00',
            '2023-05-02 14:00:00'
        ))
        
        conn.commit()
        conn.close()
        
        # Патчим функцию get_db, чтобы она возвращала подключение к тестовой БД
        with patch('api.utils.database.get_db') as mock_get_db:
            # Настраиваем мок для возврата подключения к тестовой БД
            def get_test_db():
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                return conn
            
            mock_get_db.side_effect = get_test_db
            
            # Передаем управление тестовой функции
            yield
        
        # Удаляем временную БД после завершения теста
        os.close(db_fd)
        os.unlink(db_path)
    
    def test_get_all_leads(self, test_db):
        """Проверяет получение всех заявок"""
        # Act
        leads = LeadService.get_all_leads()
        
        # Assert
        assert len(leads) == 2
        assert leads[0]['status'] == 'accepted'
        assert leads[1]['status'] == 'new'
        
        # Проверяем нормализацию телефона
        assert leads[0]['normalized_phone'] == '+79876543210'
        assert leads[1]['normalized_phone'] == '+71234567890'
    
    def test_get_lead_by_id(self, test_db):
        """Проверяет получение заявки по ID"""
        # Act
        lead = LeadService.get_lead_by_id(1)
        
        # Assert
        assert lead is not None
        assert lead['id'] == 1
        assert lead['client_name'] == 'Иван Иванов'
        assert lead['phone'] == '+7 (123) 456-78-90'
    
    def test_get_lead_by_nonexistent_id(self, test_db):
        """Проверяет получение несуществующей заявки"""
        # Act
        lead = LeadService.get_lead_by_id(999)
        
        # Assert
        assert lead is None
    
    def test_get_stats(self, test_db):
        """Проверяет получение статистики"""
        # Act
        stats = LeadService.get_stats()
        
        # Assert
        assert stats['total'] == 2
        assert stats['new'] == 1
        assert stats['accepted'] == 1
        assert stats['unique_clients'] == 2
        
        # Проверяем вычисление суммы выручки
        assert stats['revenue'] == 2500.0  # Только принятые заявки
    
    def test_get_stats_with_date_filter(self, test_db):
        """Проверяет фильтрацию статистики по дате"""
        # Act
        stats = LeadService.get_stats(start_date='2023-05-02')
        
        # Assert
        assert stats['total'] == 1
        assert stats['accepted'] == 1
        assert stats['new'] == 0 