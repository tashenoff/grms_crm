import pytest
from datetime import datetime
from api.utils.helpers import format_date, normalize_phone, clean_amount

class TestFormatDate:
    """Тесты для функции format_date"""
    
    def test_valid_date_format(self):
        """Проверяет форматирование корректной даты"""
        # Arrange
        date_str = "2023-05-15 14:30:45"
        expected = "2023-05-15 14:30:45"
        
        # Act
        result = format_date(date_str)
        
        # Assert
        assert result == expected
    
    def test_invalid_date_format(self):
        """Проверяет, что некорректная дата возвращается без изменений"""
        # Arrange
        invalid_date = "2023/05/15"
        
        # Act
        result = format_date(invalid_date)
        
        # Assert
        assert result == invalid_date
    
    def test_empty_date(self):
        """Проверяет обработку пустой строки"""
        # Arrange
        empty_date = ""
        
        # Act
        result = format_date(empty_date)
        
        # Assert
        assert result == empty_date

class TestNormalizePhone:
    """Тесты для функции normalize_phone"""
    
    def test_phone_with_formatting(self):
        """Проверяет нормализацию телефона с форматированием"""
        # Arrange
        phone = "+7 (123) 456-78-90"
        expected = "+71234567890"
        
        # Act
        result = normalize_phone(phone)
        
        # Assert
        assert result == expected
    
    def test_phone_with_special_chars(self):
        """Проверяет нормализацию телефона с дополнительными символами"""
        # Arrange
        phone = "+7-123.456/78 90"
        expected = "+71234567890"
        
        # Act
        result = normalize_phone(phone)
        
        # Assert
        assert result == expected
    
    def test_empty_phone(self):
        """Проверяет обработку пустого телефона"""
        # Arrange
        phone = ""
        
        # Act
        result = normalize_phone(phone)
        
        # Assert
        assert result == ""
    
    def test_none_phone(self):
        """Проверяет обработку None вместо строки"""
        # Arrange
        phone = None
        
        # Act
        result = normalize_phone(phone)
        
        # Assert
        assert result == ""

class TestCleanAmount:
    """Тесты для функции clean_amount"""
    
    def test_amount_with_spaces(self):
        """Проверяет очистку суммы с пробелами"""
        # Arrange
        amount = "1 234 567.89"
        expected = 1234567.89
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected
    
    def test_amount_with_currency(self):
        """Проверяет очистку суммы с символом валюты"""
        # Arrange
        amount = "$1,234.56"
        expected = 1234.56
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected
    
    def test_amount_with_non_breaking_space(self):
        """Проверяет очистку суммы с неразрывными пробелами"""
        # Arrange
        amount = "1\u00A0234.56"  # \u00A0 - неразрывный пробел
        expected = 1234.56
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected
    
    def test_invalid_amount(self):
        """Проверяет обработку некорректной суммы"""
        # Arrange
        amount = "не число"
        expected = 0.0
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected
    
    def test_empty_amount(self):
        """Проверяет обработку пустой строки"""
        # Arrange
        amount = ""
        expected = 0.0
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected
    
    def test_none_amount(self):
        """Проверяет обработку None"""
        # Arrange
        amount = None
        expected = 0.0
        
        # Act
        result = clean_amount(amount)
        
        # Assert
        assert result == expected 