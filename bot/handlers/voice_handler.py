from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards.inline_keyboards import Keyboards
from services.voice_service import voice_service
from services.ai_service import ai_service
from services.categorization_service import categorization_service
from services.database import db
from models.transaction import Transaction
from utils.config import Config
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice message"""
    user_id = update.effective_user.id

    if user_id != Config.USER_TELEGRAM_ID:
        return

    try:
        # Send "processing" message
        processing_msg = await update.message.reply_text("🎤 Распознаю голосовое сообщение...")

        # Download voice file
        voice = update.message.voice
        voice_file = await voice.get_file()

        # Ensure voice files directory exists
        Config.ensure_directories()

        voice_path = os.path.join(Config.VOICE_FILES_DIR, f"voice_{datetime.now().timestamp()}.ogg")
        await voice_file.download_to_drive(voice_path)

        # Transcribe
        transcription = voice_service.transcribe_voice(voice_path)

        if not transcription:
            await processing_msg.edit_text("Не удалось распознать голосовое сообщение.")
            voice_service.cleanup_voice_file(voice_path)
            return

        # Parse with AI
        expense_categories = categorization_service.get_available_categories('expense')
        income_categories = categorization_service.get_available_categories('income')
        all_categories = expense_categories + income_categories

        parsed = ai_service.parse_natural_language_transaction(transcription, all_categories)

        # Cleanup voice file
        voice_service.cleanup_voice_file(voice_path)

        if not parsed or 'amount' not in parsed:
            await processing_msg.edit_text(
                f"🎤 Распознано: \"{transcription}\"\n\nНе удалось извлечь информацию о транзакции."
            )
            return

        # Create transaction
        transaction = Transaction(
            amount=parsed.get('amount', 0),
            type=parsed.get('type', 'expense'),
            category=parsed.get('category', 'Другое'),
            description=parsed.get('description', transcription),
            payment_method=parsed.get('payment_method'),
            date=datetime.now(),
            user_telegram_id=Config.USER_TELEGRAM_ID,
            ai_categorized=True,
            voice_transcription=transcription
        )

        # Confirmation message
        type_emoji = "💸" if transaction.type == "expense" else "💰"
        type_text = "Расход" if transaction.type == "expense" else "Доход"

        confirmation = f"""🎤 Распознано:

📝 Текст: "{transcription}"

{type_emoji} {type_text}: {transaction.amount} грн
📁 Категория: {transaction.category}

Сохранить?"""

        context.user_data['pending_transaction'] = transaction.to_dict()

        await processing_msg.edit_text(
            confirmation,
            reply_markup=Keyboards.confirmation("save_transaction", "cancel_transaction")
        )

    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке голосового сообщения."
        )
