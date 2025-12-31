from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    """Inline keyboards for bot"""

    @staticmethod
    def main_menu():
        """Main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💸 Добавить расход", callback_data="add_expense"),
                InlineKeyboardButton("💰 Добавить доход", callback_data="add_income")
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="stats"),
                InlineKeyboardButton("💼 Баланс", callback_data="balance")
            ],
            [
                InlineKeyboardButton("📁 Категории", callback_data="categories"),
                InlineKeyboardButton("📤 Экспорт Excel", callback_data="export")
            ],
            [
                InlineKeyboardButton("🤖 AI рекомендации", callback_data="recommendations")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def transaction_type():
        """Transaction type selection"""
        keyboard = [
            [
                InlineKeyboardButton("💸 Расход", callback_data="type_expense"),
                InlineKeyboardButton("💰 Доход", callback_data="type_income")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def category_selection(categories: list, callback_prefix: str = "cat"):
        """Category selection keyboard"""
        keyboard = []
        row = []

        for i, category in enumerate(categories):
            emoji = category.get('emoji', '')
            name = category['name']
            button_text = f"{emoji} {name}" if emoji else name

            row.append(InlineKeyboardButton(
                button_text,
                callback_data=f"{callback_prefix}_{category['id']}"
            ))

            # 2 buttons per row
            if len(row) == 2:
                keyboard.append(row)
                row = []

        # Add remaining button
        if row:
            keyboard.append(row)

        # Add back button
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_method():
        """Payment method selection"""
        keyboard = [
            [
                InlineKeyboardButton("💵 Наличные", callback_data="payment_cash"),
                InlineKeyboardButton("💳 Карта", callback_data="payment_card")
            ],
            [
                InlineKeyboardButton("🔄 Перевод", callback_data="payment_transfer")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def stats_period():
        """Statistics period selection"""
        keyboard = [
            [
                InlineKeyboardButton("📅 День", callback_data="period_day"),
                InlineKeyboardButton("📅 Неделя", callback_data="period_week")
            ],
            [
                InlineKeyboardButton("📅 Месяц", callback_data="period_month"),
                InlineKeyboardButton("📅 Год", callback_data="period_year")
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirmation(yes_callback: str = "confirm_yes", no_callback: str = "confirm_no"):
        """Confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Да", callback_data=yes_callback),
                InlineKeyboardButton("❌ Нет", callback_data=no_callback)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_main():
        """Back to main menu"""
        keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]]
        return InlineKeyboardMarkup(keyboard)
