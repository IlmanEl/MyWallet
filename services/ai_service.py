from openai import OpenAI
from utils.config import Config
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=Config.OPENAI_API_KEY)


class AIService:
    """OpenAI AI service for various NLP tasks"""

    @staticmethod
    def categorize_transaction(description: str, amount: float, transaction_type: str, available_categories: list) -> str:
        """Automatically categorize a transaction using GPT-4"""
        try:
            categories_str = ", ".join(available_categories)

            prompt = f"""Проанализируй финансовую транзакцию и определи наиболее подходящую категорию.

Описание: {description}
Сумма: {amount} грн
Тип: {"расход" if transaction_type == "expense" else "доход"}

Доступные категории: {categories_str}

Верни ТОЛЬКО название категории из списка выше, без дополнительного текста."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )

            category = response.choices[0].message.content.strip()
            logger.info(f"AI categorized: {category}")
            return category

        except Exception as e:
            logger.error(f"Error in AI categorization: {e}")
            return "Другое"

    @staticmethod
    def parse_natural_language_transaction(text: str, available_categories: list) -> dict:
        """Parse natural language transaction input"""
        try:
            categories_str = ", ".join(available_categories)

            prompt = f"""Извлеки информацию о финансовой транзакции из текста на русском или украинском языке.

Текст: "{text}"

Доступные категории: {categories_str}

Верни ответ строго в формате JSON:
{{
  "amount": <число>,
  "type": "income" или "expense",
  "category": "<категория из списка>",
  "description": "<краткое описание>",
  "payment_method": "cash" или "card" или null
}}

Если информация не указана явно, используй логические предположения."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Parsed transaction: {result}")
            return result

        except Exception as e:
            logger.error(f"Error parsing NLP transaction: {e}")
            return {}

    @staticmethod
    def generate_financial_recommendations(transactions_data: list) -> str:
        """Generate personalized financial recommendations"""
        try:
            summary = AIService._summarize_transactions(transactions_data)

            prompt = f"""Ты финансовый советник. На основе данных о тратах за последний период, дай персональные рекомендации.

{summary}

Дай 3-5 конкретных рекомендаций по оптимизации бюджета. Будь конструктивным и практичным."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )

            recommendations = response.choices[0].message.content.strip()
            logger.info("Financial recommendations generated")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return "Не удалось сгенерировать рекомендации."

    @staticmethod
    def _summarize_transactions(transactions: list) -> str:
        """Summarize transactions for AI analysis"""
        category_totals = {}
        total_expense = 0

        for t in transactions:
            if t['type'] == 'expense':
                category = t.get('category', 'Другое')
                category_totals[category] = category_totals.get(category, 0) + t['amount']
                total_expense += t['amount']

        summary = f"Общие траты: {total_expense:.2f} грн\n\nРаспределение по категориям:\n"
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            summary += f"- {category}: {amount:.2f} грн ({percentage:.1f}%)\n"

        return summary


ai_service = AIService()
