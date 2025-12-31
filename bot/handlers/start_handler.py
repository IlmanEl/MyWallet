from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards.inline_keyboards import Keyboards
from utils.config import Config
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id

    # Check if user is authorized (single-user mode)
    if user_id != Config.USER_TELEGRAM_ID:
        await update.message.reply_text(
            "Извините, этот бот предназначен только для личного использования."
        )
        return

    welcome_message = """👋 Привет! Я MyWallet - твой персональный финансовый помощник.

Я помогу тебе:
📝 Вести учет доходов и расходов
🎤 Распознавать голосовые сообщения о тратах
📸 Сканировать чеки и автоматически добавлять их
🤖 Автоматически категоризировать транзакции
📊 Показывать детальную статистику
📤 Экспортировать данные в Excel
💡 Давать персональные финансовые рекомендации

Как добавить транзакцию:
1. Используй кнопки ниже
2. Отправь мне сообщение: "Потратил 500 на такси"
3. Отправь голосовое сообщение
4. Отправь фото чека

Выбери действие:"""

    await update.message.reply_text(
        welcome_message,
        reply_markup=Keyboards.main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🔍 Справка по командам:

/start - Главное меню
/balance - Текущий баланс
/stats - Статистика
/export - Экспорт в Excel
/recommend - AI рекомендации
/help - Эта справка

📝 Способы добавления транзакций:

1️⃣ Текстом:
"Потратил 500 на еду"
"Получил 10000 зарплата"

2️⃣ Голосом:
Просто отправь голосовое сообщение с описанием траты

3️⃣ Фото чека:
Отправь фотографию чека, я извлеку всю информацию

4️⃣ Кнопками:
Используй меню для структурированного ввода"""

    await update.message.reply_text(help_text)


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu callback"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Выбери действие:",
        reply_markup=Keyboards.main_menu()
    )
