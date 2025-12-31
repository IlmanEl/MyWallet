from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards.inline_keyboards import Keyboards
from services.export_service import export_service
from utils.config import Config
from utils.helpers import get_date_range
import logging
import os

logger = logging.getLogger(__name__)


async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle export request"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📤 Экспорт в Excel\n\nВыберите период для экспорта:",
        reply_markup=Keyboards.stats_period()
    )

    # Set flag that we're in export mode
    context.user_data['export_mode'] = True


async def export_period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export data for selected period"""
    query = update.callback_query
    await query.answer()

    # Check if we're in export mode
    if not context.user_data.get('export_mode'):
        return

    period_map = {
        'period_day': 'day',
        'period_week': 'week',
        'period_month': 'month',
        'period_year': 'year'
    }

    period = period_map.get(query.data, 'month')
    start_date, end_date = get_date_range(period)

    processing_msg = await query.edit_message_text("📊 Генерирую Excel файл...")

    user_id = Config.USER_TELEGRAM_ID

    try:
        # Generate Excel file
        filepath = export_service.export_to_excel(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Send file to user
        with open(filepath, 'rb') as file:
            await query.message.reply_document(
                document=file,
                filename=os.path.basename(filepath),
                caption="✅ Ваш финансовый отчет в Excel"
            )

        # Cleanup
        os.remove(filepath)

        await processing_msg.edit_text(
            "✅ Excel файл отправлен!",
            reply_markup=Keyboards.back_to_main()
        )

        # Clear export mode
        context.user_data.pop('export_mode', None)

    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        await processing_msg.edit_text(
            "Произошла ошибка при генерации Excel файла.",
            reply_markup=Keyboards.back_to_main()
        )


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export command"""
    context.user_data['export_mode'] = True

    await update.message.reply_text(
        "📤 Экспорт в Excel\n\nВыберите период для экспорта:",
        reply_markup=Keyboards.stats_period()
    )
