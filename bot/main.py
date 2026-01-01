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
    receive_currency_callback,
    receive_category_callback,
    receive_description,
    receive_payment_method_callback,
    process_text_transaction,
    save_transaction_callback,
    cancel_transaction_callback,
    cancel_conversation,
    balance_command,
    AMOUNT,
    CURRENCY,
    CATEGORY,
    DESCRIPTION,
    PAYMENT_METHOD
)
from bot.handlers.manage_handler import (
    delete_command,
    delete_callback,
    confirm_delete_callback,
    edit_command,
    edit_callback,
    show_edit_options_callback,
    toggle_team_finance_callback
)
from bot.handlers.category_handler import (
    categories_callback,
    list_categories_callback,
    add_category_start,
    receive_category_name,
    receive_category_type,
    receive_category_emoji,
    cancel_category_creation,
    CATEGORY_NAME,
    CATEGORY_TYPE,
    CATEGORY_EMOJI
)
from bot.handlers.exchange_handler import (
    exchange_start,
    receive_from_currency,
    receive_from_amount,
    receive_to_currency,
    receive_to_amount,
    cancel_exchange,
    FROM_CURRENCY,
    FROM_AMOUNT,
    TO_CURRENCY,
    TO_AMOUNT
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
            CURRENCY: [CallbackQueryHandler(receive_currency_callback, pattern='^currency_')],
            CATEGORY: [CallbackQueryHandler(receive_category_callback, pattern='^cat_')],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            PAYMENT_METHOD: [CallbackQueryHandler(receive_payment_method_callback, pattern='^payment_')],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
    )

    # === CONVERSATION HANDLER FOR ADDING CATEGORIES ===
    category_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_category_start, pattern='^add_category$'),
        ],
        states={
            CATEGORY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category_name)],
            CATEGORY_TYPE: [CallbackQueryHandler(receive_category_type, pattern='^cattype_')],
            CATEGORY_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category_emoji)],
        },
        fallbacks=[CommandHandler('cancel', cancel_category_creation)],
    )

    # === CONVERSATION HANDLER FOR CURRENCY EXCHANGE ===
    exchange_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(exchange_start, pattern='^exchange$'),
        ],
        states={
            FROM_CURRENCY: [CallbackQueryHandler(receive_from_currency, pattern='^exchange_from_')],
            FROM_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_from_amount)],
            TO_CURRENCY: [CallbackQueryHandler(receive_to_currency, pattern='^exchange_to_')],
            TO_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_to_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel_exchange)],
    )

    # === COMMAND HANDLERS ===
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('balance', balance_command))
    application.add_handler(CommandHandler('stats', stats_command))
    application.add_handler(CommandHandler('export', export_command))
    application.add_handler(CommandHandler('delete', delete_command))
    application.add_handler(CommandHandler('edit', edit_command))

    # === CONVERSATION HANDLERS ===
    application.add_handler(transaction_conv_handler)
    application.add_handler(category_conv_handler)
    application.add_handler(exchange_conv_handler)

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

    # Delete and Edit handlers
    application.add_handler(CallbackQueryHandler(delete_callback, pattern='^delete$'))
    application.add_handler(CallbackQueryHandler(confirm_delete_callback, pattern='^delete_tx_'))
    application.add_handler(CallbackQueryHandler(edit_callback, pattern='^edit$'))
    application.add_handler(CallbackQueryHandler(show_edit_options_callback, pattern='^edit_tx_'))
    application.add_handler(CallbackQueryHandler(toggle_team_finance_callback, pattern='^toggle_team_'))

    # Category handlers
    application.add_handler(CallbackQueryHandler(categories_callback, pattern='^categories$'))
    application.add_handler(CallbackQueryHandler(list_categories_callback, pattern='^list_categories$'))

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
