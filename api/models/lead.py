from api.utils.helpers import format_date, normalize_phone

class Lead:
    """Model class for leads"""
    
    def __init__(self, db_row):
        """
        Initialize Lead from database row
        
        Args:
            db_row (sqlite3.Row): Database row
        """
        self.id = db_row['id']
        self.telegram_id = db_row['telegram_id']
        self.username = db_row['username'] or 'Аноним'
        self.message = db_row['message']
        self.status = db_row['status'] if db_row['status'] else 'new'
        self.executor_id = db_row['executor_id']
        self.executor_username = db_row['executor_username'] or ''
        self.executor_first_name = db_row['executor_first_name'] or ''
        self.client_name = db_row['client_name'] if db_row['client_name'] else ''
        self.company = db_row['company'] if db_row['company'] else ''
        self.phone = db_row['phone'] if db_row['phone'] else ''
        self.normalized_phone = normalize_phone(self.phone)
        self.city = db_row['city'] if db_row['city'] else ''
        self.address = db_row['address'] if db_row['address'] else ''
        self.order_details = db_row['order_details'] if db_row['order_details'] else ''
        self.total_amount = db_row['total_amount'] if db_row['total_amount'] else ''
        self.order_date = db_row['order_date'] if db_row['order_date'] else ''
        self.source = db_row['source'] if db_row['source'] else 'сайт'
        self.created_at = format_date(db_row['created_at'])
        
        # These will be populated later if needed
        self.related_leads = []
        self.related_count = 1
    
    def to_dict(self):
        """
        Convert lead to dictionary for JSON response
        
        Returns:
            dict: Lead data
        """
        return {
            'id': self.id,
            'username': self.username,
            'message': self.message,
            'created_at': self.created_at,
            'status': self.status,
            'client_name': self.client_name,
            'company': self.company,
            'phone': self.phone,
            'normalized_phone': self.normalized_phone,
            'city': self.city,
            'address': self.address,
            'order_details': self.order_details,
            'total_amount': self.total_amount,
            'order_date': self.order_date,
            'source': self.source,
            'executor_username': self.executor_username,
            'executor_first_name': self.executor_first_name,
            'related_leads': self.related_leads,
            'related_count': self.related_count
        } 