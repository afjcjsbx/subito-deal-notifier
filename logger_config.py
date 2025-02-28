# logger_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

def get_logger(name: str) -> logging.Logger:
    """Restituisce un logger con il nome specificato."""
    return logging.getLogger(name)
