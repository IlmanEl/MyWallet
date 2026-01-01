"""
Category management handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.database import db
from utils.config import Config

logger = logging.getLogger(__name__)

# Conversation states
CATEGORY_NAME, CATEGORY_TYPE, CATEGORY_EMOJI = range(3)


async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category management menu"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
        [InlineKeyboardButton("📋 Список категорий", callback_data="list_categories")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
    ]

    await query.edit_message_text(
        "📁 <b>Управление категориями</b>\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def list_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all categories"""
    query = update.callback_query
    await query.answer()

    categories = db.get_categories()

    # Group by type
    expense_cats = [c for c in categories if c['type'] == 'expense']
    income_cats = [c for c in categories if c['type'] == 'income']

    message = "📁 <b>Ваши категории:</b>\n\n"

    message += "💸 <b>Расходы:</b>\n"
    for cat in expense_cats:
        emoji = cat.get('emoji', '')
        name = cat['name']
        message += f"  {emoji} {name}\n"

    message += "\n💰 <b>Доходы:</b>\n"
    for cat in income_cats:
        emoji = cat.get('emoji', '')
        name = cat['name']
        message += f"  {emoji} {name}\n"

    keyboard = [
        [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
        [InlineKeyboardButton("◀️ Назад", callback_data="categories")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding new category"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "➕ <b>Добавление новой категории</b>\n\nВведите название категории:",
        parse_mode='HTML'
    )

    return CATEGORY_NAME


async def receive_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive category name"""
    category_name = update.message.text

    context.user_data['new_category_name'] = category_name

    keyboard = [
        [
            InlineKeyboardButton("💸 Расход", callback_data="cattype_expense"),
            InlineKeyboardButton("💰 Доход", callback_data="cattype_income")
        ]
    ]

    await update.message.reply_text(
        f"Название: <b>{category_name}</b>\n\nВыберите тип категории:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    return CATEGORY_TYPE


async def receive_category_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive category type"""
    query = update.callback_query
    await query.answer()

    category_type = query.data.replace('cattype_', '')
    context.user_data['new_category_type'] = category_type

    type_text = "Расход" if category_type == 'expense' else "Доход"

    await query.edit_message_text(
        f"Название: <b>{context.user_data['new_category_name']}</b>\n"
        f"Тип: <b>{type_text}</b>\n\n"
        "Введите эмодзи для категории (или отправьте /skip чтобы пропустить):",
        parse_mode='HTML'
    )

    return CATEGORY_EMOJI


async def receive_category_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive category emoji and save"""
    emoji = update.message.text if update.message.text != '/skip' else '📌'

    category_data = {
        'name': context.user_data['new_category_name'],
        'type': context.user_data['new_category_type'],
        'emoji': emoji
    }

    try:
        db.add_category(category_data)

        type_text = "расхода" if category_data['type'] == 'expense' else "дохода"

        await update.message.reply_text(
            f"✅ Категория {category_data['type']} создана!\n\n"
            f"{emoji} <b>{category_data['name']}</b>\n"
            f"Тип: {type_text}",
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error adding category: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при создании категории: {str(e)}"
        )

    # Clear context
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_category_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel category creation"""
    await update.message.reply_text("❌ Создание категории отменено.")
    context.user_data.clear()
    return ConversationHandler.END
