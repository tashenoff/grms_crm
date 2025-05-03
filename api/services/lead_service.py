import logging
from api.utils.database import get_db
from api.models.lead import Lead
from api.utils.helpers import clean_amount
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class LeadService:
    """Service class for lead operations"""
    
    @staticmethod
    def get_all_leads():
        """
        Get all leads with related information
        
        Returns:
            list: List of lead dictionaries
        """
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get leads
            cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
            lead_rows = cursor.fetchall()
            logger.debug(f'Found {len(lead_rows)} leads')
            
            # Create Lead objects
            leads = [Lead(row) for row in lead_rows]
            
            # Process phone relationships
            phone_to_leads = {}
            for lead in leads:
                if lead.normalized_phone:
                    if lead.normalized_phone not in phone_to_leads:
                        phone_to_leads[lead.normalized_phone] = []
                    phone_to_leads[lead.normalized_phone].append(lead.id)
            
            # Add related information
            for lead in leads:
                if lead.normalized_phone and lead.normalized_phone in phone_to_leads:
                    lead.related_leads = phone_to_leads[lead.normalized_phone]
                    lead.related_count = len(phone_to_leads[lead.normalized_phone])
                else:
                    lead.related_leads = [lead.id]
                    lead.related_count = 1
            
            # Convert to dictionaries for JSON response
            return [lead.to_dict() for lead in leads]
        except Exception as e:
            logger.error(f'Error in get_all_leads: {e}')
            raise
    
    @staticmethod
    def get_lead_by_id(lead_id):
        """
        Get lead by ID with related information
        
        Args:
            lead_id (int): Lead ID
            
        Returns:
            dict: Lead dictionary or None if not found
        """
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get lead by ID
            cursor.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
            lead_row = cursor.fetchone()
            
            if not lead_row:
                return None
            
            # Create Lead object
            lead = Lead(lead_row)
            
            # Get related leads by phone
            if lead.normalized_phone:
                cursor.execute('SELECT id FROM leads WHERE phone = ? AND id != ?', 
                               (lead.phone, lead_id))
                related_leads = [row['id'] for row in cursor.fetchall()]
                lead.related_leads = related_leads + [lead_id]
                lead.related_count = len(related_leads) + 1
            
            return lead.to_dict()
        except Exception as e:
            logger.error(f'Error in get_lead_by_id for lead_id {lead_id}: {e}')
            raise
    
    @staticmethod
    def get_user_leads_by_phone(phone):
        """
        Get all leads for a specific phone number
        
        Args:
            phone (str): Phone number
            
        Returns:
            list: List of order dictionaries
        """
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get all leads with the given phone number that have order details
            cursor.execute('''
                SELECT id, order_details, created_at 
                FROM leads 
                WHERE phone = ? AND order_details IS NOT NULL AND order_details != "" 
                ORDER BY created_at DESC
            ''', (phone,))
            
            leads = cursor.fetchall()
            
            # Format as order list
            from api.utils.helpers import format_date
            orders = [
                {
                    'id': lead['id'], 
                    'details': lead['order_details'], 
                    'created_at': format_date(lead['created_at'])
                } 
                for lead in leads
            ]
            
            logger.debug(f'Found {len(orders)} orders for phone {phone}')
            return orders
        except Exception as e:
            logger.error(f'Error in get_user_leads_by_phone for phone {phone}: {e}')
            raise
    
    @staticmethod
    def get_stats(start_date=None, end_date=None):
        """
        Get statistics for leads
        
        Args:
            start_date (str, optional): Start date for filtering
            end_date (str, optional): End date for filtering
            
        Returns:
            dict: Statistics
        """
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Base query
            query = 'SELECT status, COUNT(*) as count FROM leads'
            params = []
            
            # Add date filtering
            if start_date or end_date:
                query += ' WHERE'
                
                if start_date:
                    query += ' created_at >= ?'
                    params.append(start_date)
                    
                if end_date:
                    if start_date:
                        query += ' AND'
                    query += ' created_at <= ?'
                    params.append(end_date)
            
            # Group by status
            query += ' GROUP BY status'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Format results
            stats = {
                'accepted': 0,
                'in_progress': 0,
                'declined': 0,
                'new': 0,
                'delivery': 0,
                'total': 0
            }
            
            for row in results:
                status = row['status'] if row['status'] else 'new'
                count = row['count']
                stats[status] = count
                stats['total'] += count
            
            # Get unique clients count
            unique_query = '''
                SELECT COUNT(DISTINCT phone) as unique_clients 
                FROM leads 
                WHERE phone IS NOT NULL AND phone != ""
            '''
            unique_params = []
            
            if start_date or end_date:
                unique_query += ' AND'
                
                if start_date:
                    unique_query += ' created_at >= ?'
                    unique_params.append(start_date)
                    
                if end_date:
                    if start_date:
                        unique_query += ' AND'
                    unique_query += ' created_at <= ?'
                    unique_params.append(end_date)
            
            cursor.execute(unique_query, unique_params)
            unique_clients = cursor.fetchone()['unique_clients']
            stats['unique_clients'] = unique_clients
            
            # Calculate revenue from accepted leads
            revenue_query = 'SELECT total_amount FROM leads WHERE status = ?'
            revenue_params = ['accepted']
            
            if start_date:
                revenue_query += ' AND created_at >= ?'
                revenue_params.append(start_date)
            if end_date:
                revenue_query += ' AND created_at <= ?'
                revenue_params.append(end_date)
            
            cursor.execute(revenue_query, revenue_params)
            amount_rows = cursor.fetchall()
            
            # Sum up the revenue
            total_revenue = sum(clean_amount(row['total_amount']) for row in amount_rows)
            stats['revenue'] = round(total_revenue, 2)
            
            return stats
        except Exception as e:
            logger.error(f'Error in get_stats: {e}')
            raise
    
    @staticmethod
    def reset_database():
        """Reset the database"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Delete all leads and reset AUTOINCREMENT counter
        cursor.execute('DELETE FROM leads')
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='leads'")
        
        conn.commit()
        conn.close()
        
        return True

    @staticmethod
    def create_lead(lead_data):
        """Create a new lead"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Extract values from lead_data
        telegram_id = lead_data.get('telegram_id', 0)
        username = lead_data.get('username', 'Аноним')
        message = lead_data.get('message', '')
        status = lead_data.get('status', 'new')
        client_name = lead_data.get('client_name', '')
        company = lead_data.get('company', '')
        phone = lead_data.get('phone', '')
        city = lead_data.get('city', '')
        address = lead_data.get('address', '')
        order_details = lead_data.get('order_details', '')
        total_amount = lead_data.get('total_amount', '')
        order_date = lead_data.get('order_date', '')
        source = lead_data.get('source', 'сайт')
        created_at = lead_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Insert new lead
        cursor.execute('''
            INSERT INTO leads (
                telegram_id, username, message, status, client_name, company, 
                phone, city, address, order_details, total_amount, order_date, 
                source, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            telegram_id, username, message, status, client_name, company, 
            phone, city, address, order_details, total_amount, order_date, 
            source, created_at
        ))
        
        # Get the ID of the newly inserted lead
        lead_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return lead_id

    @staticmethod
    def update_lead(lead_id, update_data):
        """Update lead status and executor info"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if lead exists
        cursor.execute('SELECT id FROM leads WHERE id = ?', (lead_id,))
        lead = cursor.fetchone()
        
        if not lead:
            conn.close()
            return False
        
        # Build update query based on available fields in update_data
        update_fields = []
        params = []
        
        for field, value in update_data.items():
            if field in ['status', 'executor_id', 'executor_username', 
                        'executor_first_name', 'client_name', 'company', 
                        'phone', 'city', 'address', 'order_details', 
                        'total_amount', 'order_date', 'source']:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            conn.close()
            return True  # Nothing to update
        
        # Add lead_id to params
        params.append(lead_id)
        
        # Update lead
        cursor.execute(f'''
            UPDATE leads 
            SET {', '.join(update_fields)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        conn.close()
        
        return True

    @staticmethod
    def delete_lead(lead_id):
        """Delete a lead"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if lead exists
        cursor.execute('SELECT id FROM leads WHERE id = ?', (lead_id,))
        lead = cursor.fetchone()
        
        if not lead:
            conn.close()
            return False
        
        # Delete lead
        cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        
        conn.commit()
        conn.close()
        
        return True 