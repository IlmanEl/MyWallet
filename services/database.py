from supabase import create_client, Client
from utils.config import Config
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """Supabase database service"""

    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )

    # ===== TRANSACTIONS =====

    def add_transaction(self, transaction_data: Dict) -> Dict:
        """Add a new transaction"""
        try:
            response = self.client.table('transactions').insert(transaction_data).execute()
            logger.info(f"Transaction added: {response.data}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise

    def get_transactions(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get transactions with optional filters"""
        try:
            query = self.client.table('transactions').select('*').eq('user_telegram_id', user_id)

            if start_date:
                query = query.gte('date', start_date.isoformat())

            if end_date:
                query = query.lte('date', end_date.isoformat())

            if transaction_type:
                query = query.eq('type', transaction_type)

            if category:
                query = query.eq('category', category)

            query = query.order('date', desc=True).limit(limit)

            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []

    def get_recent_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get most recent transactions"""
        try:
            response = (
                self.client.table('transactions')
                .select('*')
                .eq('user_telegram_id', user_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {e}")
            return []

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict]:
        """Get a single transaction by ID"""
        try:
            response = self.client.table('transactions').select('*').eq('id', transaction_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching transaction: {e}")
            return None

    def update_transaction(self, transaction_id: str, update_data: Dict) -> Dict:
        """Update a transaction"""
        try:
            response = self.client.table('transactions').update(update_data).eq('id', transaction_id).execute()
            logger.info(f"Transaction updated: {transaction_id}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            raise

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction"""
        try:
            self.client.table('transactions').delete().eq('id', transaction_id).execute()
            logger.info(f"Transaction deleted: {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return False

    def get_balance(self, user_id: int) -> Dict:
        """Get current balance by currency - simple income minus expenses"""
        try:
            transactions = self.get_transactions(user_id, limit=10000)

            # Group by currency
            balances = {}

            for t in transactions:
                currency = t.get('currency', 'UAH')
                category = t.get('category', '')
                description = t.get('description', '').lower()

                if currency not in balances:
                    balances[currency] = {
                        'income': 0,
                        'expense': 0,
                        'balance': 0
                    }

                amount = t['amount']

                # Skip internal transfers (наличные на карту) - they are not real expenses
                is_internal_transfer = (
                    category == 'Переводы' and
                    ('на карту' in description or ('налич' in description and 'карт' in description))
                )

                if t['type'] == 'income':
                    balances[currency]['income'] += amount
                elif not is_internal_transfer:  # Only count real expenses
                    balances[currency]['expense'] += amount

                # Calculate balance
                balances[currency]['balance'] = balances[currency]['income'] - balances[currency]['expense']

            return balances
        except Exception as e:
            logger.error(f"Error calculating balance: {e}")
            return {}

    # ===== CATEGORIES =====

    def get_categories(self, category_type: Optional[str] = None) -> List[Dict]:
        """Get all categories, optionally filtered by type"""
        try:
            query = self.client.table('categories').select('*')

            if category_type:
                query = query.eq('type', category_type)

            response = query.order('name').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def add_category(self, category_data: Dict) -> Dict:
        """Add a new category"""
        try:
            response = self.client.table('categories').insert(category_data).execute()
            logger.info(f"Category added: {response.data}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            raise

    def get_category_by_name(self, name: str, category_type: str) -> Optional[Dict]:
        """Get category by name and type"""
        try:
            response = self.client.table('categories').select('*').eq('name', name).eq('type', category_type).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching category: {e}")
            return None

    # ===== STATISTICS =====

    def get_category_stats(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        transaction_type: str
    ) -> List[Dict]:
        """Get spending/income by category for a date range"""
        try:
            transactions = self.get_transactions(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                transaction_type=transaction_type,
                limit=10000
            )

            category_totals = {}
            for t in transactions:
                category = t.get('category', 'Без категории')
                category_totals[category] = category_totals.get(category, 0) + t['amount']

            stats = [
                {'category': cat, 'total': total}
                for cat, total in category_totals.items()
            ]

            stats.sort(key=lambda x: x['total'], reverse=True)
            return stats

        except Exception as e:
            logger.error(f"Error calculating category stats: {e}")
            return []

    # ===== AI RECOMMENDATIONS =====

    def add_recommendation(self, recommendation_data: Dict) -> Dict:
        """Add an AI recommendation"""
        try:
            response = self.client.table('ai_recommendations').insert(recommendation_data).execute()
            logger.info(f"Recommendation added")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error adding recommendation: {e}")
            raise

    def get_recommendations(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Get AI recommendations"""
        try:
            query = self.client.table('ai_recommendations').select('*').eq('user_telegram_id', user_id)

            if unread_only:
                query = query.eq('is_read', False)

            response = query.order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            return []

    def mark_recommendation_read(self, recommendation_id: str) -> bool:
        """Mark recommendation as read"""
        try:
            self.client.table('ai_recommendations').update({'is_read': True}).eq('id', recommendation_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking recommendation as read: {e}")
            return False

    # ===== STORAGE (for receipt images) =====

    def upload_receipt_image(self, file_path: str, file_name: str) -> Optional[str]:
        """Upload receipt image to Supabase storage"""
        try:
            with open(file_path, 'rb') as file:
                response = self.client.storage.from_('receipts').upload(
                    file_name,
                    file
                )

            if response:
                public_url = self.client.storage.from_('receipts').get_public_url(file_name)
                logger.info(f"Receipt uploaded: {public_url}")
                return public_url

            return None
        except Exception as e:
            logger.error(f"Error uploading receipt: {e}")
            return None


db = Database()
