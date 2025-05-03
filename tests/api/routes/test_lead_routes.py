import pytest
import json
from unittest.mock import patch, MagicMock
from api import create_app

class TestLeadRoutes:
    """API тесты для маршрутов заявок"""
    
    @pytest.fixture
    def app(self):
        """Создает тестовое приложение Flask"""
        # Для тестов используем тестовую конфигурацию
        app = create_app()
        app.config.update({
            'TESTING': True,
        })
        return app
    
    @pytest.fixture
    def client(self, app):
        """Создает тестовый клиент Flask"""
        return app.test_client()
    
    @pytest.fixture
    def mock_lead_service(self):
        """Создает мок для LeadService"""
        with patch('api.routes.lead_routes.LeadService') as mock_service:
            yield mock_service
    
    def test_get_leads(self, client, mock_lead_service):
        """Проверяет получение списка заявок"""
        # Arrange
        mock_leads = [
            {
                'id': 1,
                'client_name': 'Иван Иванов',
                'status': 'new',
                'phone': '+7 (123) 456-78-90',
                'normalized_phone': '+71234567890',
                'created_at': '2023-05-01 12:00:00'
            },
            {
                'id': 2,
                'client_name': 'Петр Петров',
                'status': 'accepted',
                'phone': '+7 (987) 654-32-10',
                'normalized_phone': '+79876543210',
                'created_at': '2023-05-02 14:00:00'
            }
        ]
        mock_lead_service.get_all_leads.return_value = mock_leads
        
        # Act
        response = client.get('/leads')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[1]['id'] == 2
        
        # Проверяем, что сервис был вызван
        mock_lead_service.get_all_leads.assert_called_once()
    
    def test_get_lead_details_success(self, client, mock_lead_service):
        """Проверяет получение деталей существующей заявки"""
        # Arrange
        lead_id = 1
        mock_lead = {
            'id': lead_id,
            'client_name': 'Иван Иванов',
            'status': 'new',
            'phone': '+7 (123) 456-78-90',
            'normalized_phone': '+71234567890',
            'created_at': '2023-05-01 12:00:00',
            'related_leads': [1],
            'related_count': 1
        }
        mock_lead_service.get_lead_by_id.return_value = mock_lead
        
        # Act
        response = client.get(f'/lead_details/{lead_id}')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == lead_id
        assert data['client_name'] == 'Иван Иванов'
        assert data['status'] == 'new'
        
        # Проверяем, что сервис был вызван с правильным ID
        mock_lead_service.get_lead_by_id.assert_called_once_with(lead_id)
    
    def test_get_lead_details_not_found(self, client, mock_lead_service):
        """Проверяет получение несуществующей заявки"""
        # Arrange
        lead_id = 999
        mock_lead_service.get_lead_by_id.return_value = None
        
        # Act
        response = client.get(f'/lead_details/{lead_id}')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        
        # Проверяем, что сервис был вызван с правильным ID
        mock_lead_service.get_lead_by_id.assert_called_once_with(lead_id)
    
    def test_get_stats(self, client, mock_lead_service):
        """Проверяет получение статистики"""
        # Arrange
        mock_stats = {
            'total': 10,
            'new': 3,
            'accepted': 5,
            'in_progress': 1,
            'declined': 1,
            'unique_clients': 8,
            'revenue': 15000.0
        }
        mock_lead_service.get_stats.return_value = mock_stats
        
        # Act
        response = client.get('/stats')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 10
        assert data['new'] == 3
        assert data['accepted'] == 5
        assert data['revenue'] == 15000.0
        
        # Проверяем, что сервис был вызван без параметров
        mock_lead_service.get_stats.assert_called_once_with(None, None)
    
    def test_get_stats_with_filters(self, client, mock_lead_service):
        """Проверяет получение статистики с фильтрами"""
        # Arrange
        mock_stats = {
            'total': 5,
            'new': 2,
            'accepted': 3,
            'in_progress': 0,
            'declined': 0,
            'unique_clients': 4,
            'revenue': 9000.0
        }
        mock_lead_service.get_stats.return_value = mock_stats
        
        # Act
        response = client.get('/stats?start_date=2023-05-01&end_date=2023-05-31')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 5
        
        # Проверяем, что сервис был вызван с параметрами
        mock_lead_service.get_stats.assert_called_once_with('2023-05-01', '2023-05-31')
    
    def test_user_leads(self, client, mock_lead_service):
        """Проверяет получение заявок пользователя по телефону"""
        # Arrange
        phone = '+71234567890'
        mock_orders = [
            {
                'id': 1,
                'details': 'Заказ №1',
                'created_at': '2023-05-01 12:00:00'
            },
            {
                'id': 3,
                'details': 'Заказ №3',
                'created_at': '2023-05-10 15:30:00'
            }
        ]
        mock_lead_service.get_user_leads_by_phone.return_value = mock_orders
        
        # Act
        response = client.get(f'/user_leads/{phone}')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'orders' in data
        assert len(data['orders']) == 2
        
        # Проверяем, что сервис был вызван с правильным телефоном
        mock_lead_service.get_user_leads_by_phone.assert_called_once_with(phone)
    
    def test_reset_db(self, client, mock_lead_service):
        """Проверяет сброс базы данных"""
        # Arrange
        mock_lead_service.reset_database.return_value = True
        
        # Act
        response = client.post('/reset')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Проверяем, что сервис был вызван
        mock_lead_service.reset_database.assert_called_once() 