import pytest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import patch

# Добавляем корневую директорию проекта в Python path
# для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from api import create_app

@pytest.fixture
def app():
    """Создает тестовое приложение Flask"""
    app = create_app()
    app.config.update({
        'TESTING': True,
    })
    yield app

@pytest.fixture
def client(app):
    """Создает тестовый клиент Flask"""
    return app.test_client()

@pytest.fixture
def test_db():
    """
    Создает временную тестовую БД для изолированного тестирования
    
    Использование:
    def test_something(test_db):
        # Код теста с изолированной БД
        pass
    """
    # Создаем временный файл для тестовой БД
    db_fd, db_path = tempfile.mkstemp()
    
    # Создаем подключение и схему БД
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Создаем таблицы для тестов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # Создаем тестовые данные
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', 
                  (123456789, 'test_user', 'Тест', '2023-01-01 00:00:00'))
    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', 
                  (987654321, 'test_user2', 'Тест2', '2023-01-02 00:00:00'))
    
    # Добавляем тестовые заявки
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