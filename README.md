# Subito Deals Notifier 

## Overview
This script monitors websites for changes in content, such as new listings, and sends notifications via a Telegram bot. It can be used to track specific pages and apply filters such as price range or shipping availability.

The program performs the following:

- Periodically fetches specified URLs.
- Extracts relevant content and applies filters.
- Detects changes compared to previous checks.
- Sends notifications for new or updated content through Telegram.

## Features

- **Periodic Monitoring**: Checks specified URLs at a customizable interval.
- **Filter Support**: Only alerts for changes matching specific criteria (e.g., price range, shipping).
- **Telegram Notifications**: Sends updates to a configured Telegram bot and chat.
- **Caching**: Avoids redundant notifications using a local cache.
- **Exponential Backoff**: Handles failed requests with retry logic. 

## Requirements

### Python Packages

The following Python libraries are required:

- httpx
- schedule
- BeautifulSoup4
- logging
- json

Install them with:

>pip install httpx schedule beautifulsoup4
 
## Setup
1. Telegram Bot Configuration
Create a bot on Telegram using BotFather. Obtain:

BOT_TOKEN: The token for your bot.
BOT_CHAT_ID: The chat ID where notifications should be sent.
Update the script:

set them as env vars

```python
BOT_TOKEN = os.environ['SUBITO_TELEGRAM_BOT_TOKEN']
BOT_CHAT_ID = os.environ['SUBITO_TELEGRAM_BOT_CHAT_ID']
```

2. JSON File for URLs
Create a JSON file (e.g., subito_urls.json) to define the URLs to monitor and their filters. Example format:

```json
[
  {
    "url": "https://www.subito.it/annunci-italia/vendita/usato/?q=iphone+16",
    "filters": {
      "min_price": 500,
      "max_price": 800,
      "shipping_available": true
    }
  },
  {
    "url": "https://www.subito.it/annunci-italia/vendita/usato/?q=playstation+5",
    "filters": {
      "max_price": 350
    }
  }
]
```

3. Data Directory
Ensure a directory named data exists for caching results:

```bash
mkdir data
```

Usage
Run the Script
Execute the script using:

```bash
python subito.py
```

The script will:

1. Load the URLs from the JSON file.
2. Fetch and analyze the content of each URL.
3. Notify via Telegram if new content is detected.

### Parameters

- **SCHEDULE_INTERVAL_MINUTES**: Interval in minutes between checks (default: 15).
  - Update this variable to customize:
    ```python
    SCHEDULE_INTERVAL_MINUTES = 15
    ```
  
## Customization

1. Filters
Modify the **apply_filters** function to implement custom logic for filtering content.

2. Extracting Information
Update the **extract_price_from_html** and **extract_all_div_blocks** functions to match the structure of the target websites.

3. Logging
Logs are stored in the console. To enable file logging:

```python
logging.basicConfig(
    filename='monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)
```

## Troubleshooting

1. **Empty Results**: Ensure the **extract_*** functions are correctly parsing the website's HTML structure.
2. **Telegram Errors**: Verify the bot token and chat ID.
3. **Connection Issues**: Adjust proxy settings in the **telegram_bot_send_deal** function.

## License
This script is open-source. Modify and distribute as needed.