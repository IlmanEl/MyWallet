from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards.inline_keyboards import Keyboards
from services.vision_service import vision_service
from services.categorization_service import categorization_service
from services.database import db
from models.transaction import Transaction
from utils.config import Config
from utils.helpers import get_currency_symbol
from utils.date_helper import get_current_date
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo message (receipt)"""
    user_id = update.effective_user.id

    if user_id != Config.USER_TELEGRAM_ID:
        return

    try:
        # Send "processing" message
        processing_msg = await update.message.reply_text("📸 Обрабатываю чек...")

        # Download photo
        photo = update.message.photo[-1]  # Get highest resolution
        photo_file = await photo.get_file()

        # Ensure temp directory exists
        Config.ensure_directories()

        photo_path = os.path.join(Config.TEMP_DIR, f"receipt_{datetime.now().timestamp()}.jpg")
        await photo_file.download_to_drive(photo_path)

        # Process with Vision API
        expense_categories = categorization_service.get_available_categories('expense')
        receipt_data = vision_service.process_receipt(photo_path, expense_categories)

        if not receipt_data or 'amount' not in receipt_data:
            await processing_msg.edit_text(
                "Не удалось извлечь информацию из чека. Попробуйте добавить транзакцию вручную."
            )
            os.remove(photo_path)
            return

        # Upload receipt image to Supabase storage
        receipt_url = db.upload_receipt_image(
            photo_path,
            f"receipt_{user_id}_{datetime.now().timestamp()}.jpg"
        )

        # Cleanup local file
        os.remove(photo_path)

        # Create transaction
        transaction = Transaction(
            amount=receipt_data.get('amount', 0),
            type='expense',
            category=receipt_data.get('category', 'Другое'),
            description=f"Магазин: {receipt_data.get('store', 'неизвестно')}",
            payment_method='card',  # Assume card for receipt
            date=get_current_date(),  # Формат ДД.ММ.ГГГГ
            user_telegram_id=Config.USER_TELEGRAM_ID,
            ai_categorized=True,
            receipt_image_url=receipt_url
        )

        # Build items list
        items_text = ""
        if receipt_data.get('items'):
            items_list = receipt_data['items'][:5]  # Show first 5 items
            items_text = "\n📦 Товары: " + ", ".join(items_list)
            if len(receipt_data['items']) > 5:
                items_text += f" (+{len(receipt_data['items']) - 5} еще)"

        # Confirmation message
        confirmation = f"""📸 Чек обработан:

💸 Сумма: {transaction.amount} {get_currency_symbol(transaction.currency)}
📅 Дата: {receipt_data.get('date', 'сегодня')}
🏪 Магазин: {receipt_data.get('store', 'неизвестно')}
📁 Категория: {transaction.category}{items_text}

Сохранить?"""

        context.user_data['pending_transaction'] = transaction.to_dict()

        await processing_msg.edit_text(
            confirmation,
            reply_markup=Keyboards.confirmation("save_transaction", "cancel_transaction")
        )

    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке фото чека."
        )
