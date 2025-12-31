import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from utils.config import Config

# Import handlers
from bot.handlers.start_handler import (
    start_command,
    help_command,
    back_to_main_callback
)
from bot.handlers.transaction_handler import (
    add_expense_callback,
    add_income_callback,
    receive_amount,
    receive_category_callback,
    receive_description,
    receive_payment_method_callback,
    process_text_transaction,
    save_transaction_callback,
    cancel_transaction_callback,
    cancel_conversation,
    balance_command,
    AMOUNT,
    CATEGORY,
    DESCRIPTION,
    PAYMENT_METHOD
)
from bot.handlers.voice_handler import handle_voice_message
from bot.handlers.photo_handler import handle_photo_message
from bot.handlers.stats_handler import (
    stats_callback,
    stats_period_callback,
    recommendations_callback,
    stats_command
)
from bot.handlers.export_handler import (
    export_callback,
    export_period_callback,
    export_command
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot"""

    # Validate configuration
    try:
        Config.validate()
        Config.ensure_directories()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # === CONVERSATION HANDLER FOR ADDING TRANSACTIONS ===
    transaction_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_expense_callback, pattern='^add_expense$'),
            CallbackQueryHandler(add_income_callback, pattern='^add_income$'),
        ],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
            CATEGORY: [CallbackQueryHandler(receive_category_callback, pattern='^cat_')],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            PAYMENT_METHOD: [CallbackQueryHandler(receive_payment_method_callback, pattern='^payment_')],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
    )

    # === COMMAND HANDLERS ===
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('balance', balance_command))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(CommandHandler('export', export_command))

    # === CONVERSATION HANDLER ===
    application.add_handler(transaction_conv_handler)

    # === CALLBACK QUERY HANDLERS ===
    # Main menu navigation
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern='^back_main$'))

    # Stats and recommendations
    application.add_handler(CallbackQueryHandler(stats_callback, pattern='^stats$'))
    application.add_handler(CallbackQueryHandler(recommendations_callback, pattern='^recommendations$'))

    # Balance
    application.add_handler(CallbackQueryHandler(
        lambda u, c: balance_command(u, c),
        pattern='^balance$'
    ))

    # Export
    application.add_handler(CallbackQueryHandler(export_callback, pattern='^export$'))

    # Period selection (can be for stats or export)
    async def period_router(update, context):
        """Route period selection to stats or export based on context"""
        if context.user_data.get('export_mode'):
            await export_period_callback(update, context)
        else:
            await stats_period_callback(update, context)

    application.add_handler(CallbackQueryHandler(period_router, pattern='^period_'))

    # Transaction confirmation
    application.add_handler(CallbackQueryHandler(save_transaction_callback, pattern='^save_transaction$'))
    application.add_handler(CallbackQueryHandler(cancel_transaction_callback, pattern='^cancel_transaction$'))

    # === MESSAGE HANDLERS ===
    # Voice messages
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Photo messages (receipts)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    # Text messages (natural language transactions)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        process_text_transaction
    ))

    # === ERROR HANDLER ===
    async def error_handler(update, context):
        """Log errors"""
        logger.error(f"Update {update} caused error {context.error}")

    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Starting MyWallet bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
