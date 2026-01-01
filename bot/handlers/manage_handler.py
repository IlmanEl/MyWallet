"""
Handlers for managing transactions (delete, edit)
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.database import db
from utils.config import Config

logger = logging.getLogger(__name__)


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent transactions for deletion"""

    user_id = update.effective_user.id
    if user_id != Config.USER_TELEGRAM_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этому боту.")
        return

    try:
        # Get last 10 transactions
        transactions = db.get_recent_transactions(Config.USER_TELEGRAM_ID, limit=10)

        if not transactions:
            await update.message.reply_text("📭 У вас пока нет транзакций для удаления.")
            return

        # Build message with transactions
        message = "🗑️ <b>Последние транзакции:</b>\n\n"
        keyboard = []

        for i, t in enumerate(transactions, 1):
            type_emoji = "💰" if t['type'] == 'income' else "💸"
            currency_symbol = "₴" if t.get('currency', 'UAH') == 'UAH' else "$"
            team_flag = " [Команда]" if t.get('is_team_finance') else ""

            date_str = t['date'][:10] if t.get('date') else 'без даты'

            message += f"{i}. {type_emoji} <b>{t['amount']:.2f} {currency_symbol}</b>{team_flag}\n"
            message += f"   📁 {t.get('category', 'Без категории')}\n"
            message += f"   📝 {t.get('description', 'Без описания')}\n"
            message += f"   📅 {date_str}\n\n"

            # Add delete button for each transaction
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ Удалить #{i}",
                    callback_data=f"delete_tx_{t['id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])

        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in delete_command: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent transactions for deletion (from callback)"""

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if user_id != Config.USER_TELEGRAM_ID:
        await query.edit_message_text("⛔ У вас нет доступа к этому боту.")
        return

    try:
        # Get last 10 transactions
        transactions = db.get_recent_transactions(Config.USER_TELEGRAM_ID, limit=10)

        if not transactions:
            await query.edit_message_text("📭 У вас пока нет транзакций для удаления.")
            return

        # Build message with transactions
        message = "🗑️ <b>Последние транзакции:</b>\n\n"
        keyboard = []

        for i, t in enumerate(transactions, 1):
            type_emoji = "💰" if t['type'] == 'income' else "💸"
            currency_symbol = "₴" if t.get('currency', 'UAH') == 'UAH' else "$"
            team_flag = " [Команда]" if t.get('is_team_finance') else ""

            date_str = t['date'][:10] if t.get('date') else 'без даты'

            message += f"{i}. {type_emoji} <b>{t['amount']:.2f} {currency_symbol}</b>{team_flag}\n"
            message += f"   📁 {t.get('category', 'Без категории')}\n"
            message += f"   📝 {t.get('description', 'Без описания')}\n"
            message += f"   📅 {date_str}\n\n"

            # Add delete button for each transaction
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ Удалить #{i}",
                    callback_data=f"delete_tx_{t['id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in delete_callback: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def confirm_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete transaction after confirmation"""

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if user_id != Config.USER_TELEGRAM_ID:
        await query.edit_message_text("⛔ У вас нет доступа к этому боту.")
        return

    try:
        # Extract transaction ID from callback data
        transaction_id = query.data.replace('delete_tx_', '')

        # Get transaction details before deleting
        transaction = db.get_transaction_by_id(transaction_id)

        if not transaction:
            await query.edit_message_text("❌ Транзакция не найдена.")
            return

        # Delete transaction
        db.delete_transaction(transaction_id)

        type_emoji = "💰" if transaction['type'] == 'income' else "💸"
        currency_symbol = "₴" if transaction.get('currency', 'UAH') == 'UAH' else "$"

        message = f"✅ <b>Транзакция удалена!</b>\n\n"
        message += f"{type_emoji} {transaction['amount']:.2f} {currency_symbol}\n"
        message += f"📁 {transaction.get('category', 'Без категории')}\n"
        message += f"📝 {transaction.get('description', 'Без описания')}"

        keyboard = [
            [InlineKeyboardButton("🗑️ Удалить еще", callback_data="delete")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]
        ]

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in confirm_delete_callback: {e}")
        await query.edit_message_text(f"❌ Ошибка при удалении: {str(e)}")


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent transactions for editing"""

    user_id = update.effective_user.id
    if user_id != Config.USER_TELEGRAM_ID:
        await update.message.reply_text("⛔ У вас нет доступа к этому боту.")
        return

    try:
        # Get last 10 transactions
        transactions = db.get_recent_transactions(Config.USER_TELEGRAM_ID, limit=10)

        if not transactions:
            await update.message.reply_text("📭 У вас пока нет транзакций для редактирования.")
            return

        # Build message with transactions
        message = "✏️ <b>Последние транзакции:</b>\n\n"
        keyboard = []

        for i, t in enumerate(transactions, 1):
            type_emoji = "💰" if t['type'] == 'income' else "💸"
            currency_symbol = "₴" if t.get('currency', 'UAH') == 'UAH' else "$"
            team_flag = " [Команда]" if t.get('is_team_finance') else ""

            date_str = t['date'][:10] if t.get('date') else 'без даты'

            message += f"{i}. {type_emoji} <b>{t['amount']:.2f} {currency_symbol}</b>{team_flag}\n"
            message += f"   📁 {t.get('category', 'Без категории')}\n"
            message += f"   📝 {t.get('description', 'Без описания')}\n"
            message += f"   📅 {date_str}\n\n"

            # Add edit button for each transaction
            keyboard.append([
                InlineKeyboardButton(
                    f"✏️ Изменить #{i}",
                    callback_data=f"edit_tx_{t['id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])

        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in edit_command: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent transactions for editing (from callback)"""

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    if user_id != Config.USER_TELEGRAM_ID:
        await query.edit_message_text("⛔ У вас нет доступа к этому боту.")
        return

    try:
        # Get last 10 transactions
        transactions = db.get_recent_transactions(Config.USER_TELEGRAM_ID, limit=10)

        if not transactions:
            await query.edit_message_text("📭 У вас пока нет транзакций для редактирования.")
            return

        # Build message with transactions
        message = "✏️ <b>Последние транзакции:</b>\n\n"
        keyboard = []

        for i, t in enumerate(transactions, 1):
            type_emoji = "💰" if t['type'] == 'income' else "💸"
            currency_symbol = "₴" if t.get('currency', 'UAH') == 'UAH' else "$"
            team_flag = " [Команда]" if t.get('is_team_finance') else ""

            date_str = t['date'][:10] if t.get('date') else 'без даты'

            message += f"{i}. {type_emoji} <b>{t['amount']:.2f} {currency_symbol}</b>{team_flag}\n"
            message += f"   📁 {t.get('category', 'Без категории')}\n"
            message += f"   📝 {t.get('description', 'Без описания')}\n"
            message += f"   📅 {date_str}\n\n"

            # Add edit button for each transaction
            keyboard.append([
                InlineKeyboardButton(
                    f"✏️ Изменить #{i}",
                    callback_data=f"edit_tx_{t['id']}"
                )
            ])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_main")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in edit_callback: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def show_edit_options_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show edit options for a transaction"""

    query = update.callback_query
    await query.answer()

    try:
        # Extract transaction ID
        transaction_id = query.data.replace('edit_tx_', '')

        # Store transaction ID in context
        context.user_data['edit_transaction_id'] = transaction_id

        # Get transaction details
        transaction = db.get_transaction_by_id(transaction_id)

        if not transaction:
            await query.edit_message_text("❌ Транзакция не найдена.")
            return

        type_emoji = "💰" if transaction['type'] == 'income' else "💸"
        currency_symbol = "₴" if transaction.get('currency', 'UAH') == 'UAH' else "$"
        team_flag = " [Команда]" if transaction.get('is_team_finance') else ""

        message = f"✏️ <b>Редактирование транзакции:</b>\n\n"
        message += f"{type_emoji} <b>{transaction['amount']:.2f} {currency_symbol}</b>{team_flag}\n"
        message += f"📁 {transaction.get('category', 'Без категории')}\n"
        message += f"📝 {transaction.get('description', 'Без описания')}\n"
        message += f"📅 {transaction['date'][:10] if transaction.get('date') else 'без даты'}\n\n"
        message += "Что хотите изменить?"

        keyboard = [
            [InlineKeyboardButton("💵 Сумма", callback_data=f"edit_amount_{transaction_id}")],
            [InlineKeyboardButton("📁 Категория", callback_data=f"edit_category_{transaction_id}")],
            [InlineKeyboardButton("📝 Описание", callback_data=f"edit_description_{transaction_id}")],
            [InlineKeyboardButton("💱 Валюта", callback_data=f"edit_currency_{transaction_id}")],
            [InlineKeyboardButton("👥 Команда/Личное", callback_data=f"toggle_team_{transaction_id}")],
            [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_tx_{transaction_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="edit")]
        ]

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in show_edit_options_callback: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def toggle_team_finance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle is_team_finance flag"""

    query = update.callback_query
    await query.answer()

    try:
        transaction_id = query.data.replace('toggle_team_', '')

        # Get current transaction
        transaction = db.get_transaction_by_id(transaction_id)

        if not transaction:
            await query.edit_message_text("❌ Транзакция не найдена.")
            return

        # Toggle the flag
        new_value = not transaction.get('is_team_finance', False)

        db.update_transaction(transaction_id, {'is_team_finance': new_value})

        status = "Командные деньги" if new_value else "Личные деньги"

        await query.answer(f"✅ Изменено на: {status}", show_alert=True)

        # Show updated edit options
        context.user_data['edit_transaction_id'] = transaction_id
        await show_edit_options_callback(update, context)

    except Exception as e:
        logger.error(f"Error in toggle_team_finance_callback: {e}")
        await query.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
