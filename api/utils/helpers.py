from datetime import datetime
import re

def format_date(date_str):
    """
    Format date string to display format
    
    Args:
        date_str (str): Date string in format '%Y-%m-%d %H:%M:%S'
        
    Returns:
        str: Formatted date string
    """
    try:
        # Try to parse as datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except:
        # If parsing fails, return original string
        return date_str

def normalize_phone(phone):
    """
    Normalize phone number by removing all non-digit characters except '+'
    
    Args:
        phone (str): Phone number
        
    Returns:
        str: Normalized phone number
    """
    if not phone:
        return ''
    return ''.join(c for c in phone if c.isdigit() or c == '+')

def clean_amount(amount_str):
    """
    Clean amount string by removing non-digit characters except '.'
    
    Args:
        amount_str (str): Amount string
        
    Returns:
        float: Cleaned amount as float, or 0.0 if conversion fails
    """
    if not amount_str:
        return 0.0
    
    # Remove spaces and non-breaking spaces
    cleaned = amount_str.replace(' ', '').replace('\u00A0', '')
    # Keep only digits and dots
    cleaned = re.sub(r'[^0-9.]', '', cleaned)
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0 