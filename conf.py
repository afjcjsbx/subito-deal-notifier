import os

from logger_config import get_logger

logger = get_logger('Config')

class Config:
    """Configuration class for environment variables and application settings."""

    # Directory to save data
    DATA_FOLDER = "data/"
    SCHEDULE_INTERVAL_MINUTES = 15

    # Telegram bot configuration
    BOT_TOKEN = os.getenv('SUBITO_TELEGRAM_BOT_TOKEN')
    BOT_CHAT_ID = os.getenv('SUBITO_TELEGRAM_BOT_CHAT_ID')

    # COLD_START parameter
    COLD_START = os.getenv('SUBITO_COLD_START', 'true').lower() == 'true'

    # API Keys
    OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
    DEEP_SEEK_API_KEY = os.getenv('DEEP_SEEK_API_KEY')

    # DeepSeek Configuration
    deep_seek_endpoint_v3 = "https://deepseek-v3-websearch.p.rapidapi.com/deepseek-v3/completion"
    deep_seek_max_tokens = 512
    deep_seek_temperature = 0.1
    deep_seek_top_p = 0.9
    deep_seek_search_web = True

for var in ["BOT_TOKEN", "BOT_CHAT_ID", "OPEN_AI_API_KEY", "DEEP_SEEK_API_KEY"]:
    if getattr(Config, var) is None:
        logger.warning(f"⚠️  Environment variable '{var}' is not set. This may cause errors during execution.")
