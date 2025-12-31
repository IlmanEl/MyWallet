import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for MyWallet bot"""

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    USER_TELEGRAM_ID = int(os.getenv('USER_TELEGRAM_ID', 0))

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    VOICE_FILES_DIR = os.path.join(BASE_DIR, 'voice_files')

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_KEY': cls.SUPABASE_KEY,
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'USER_TELEGRAM_ID': cls.USER_TELEGRAM_ID,
        }

        missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file."
            )

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.VOICE_FILES_DIR, exist_ok=True)
