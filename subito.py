import json
import logging
import os
import random
import re
import time
import urllib.parse
from typing import Optional

import httpx
import schedule
from bs4 import BeautifulSoup

# Configuration of the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)
logger = logging.getLogger('subito-deal-notifier')

# Directory to save data
DATA_FOLDER = "data/"

"""
Parameters
"""

SCHEDULE_INTERVAL_MINUTES = 15

# Telegram bot configuration (replace with your credentials)
BOT_TOKEN = 'your_bot_token_here'
BOT_CHAT_ID = 'your_chat_id_here'


def telegram_bot_send_deal(message: str) -> None:
    """
    Send a message via the Telegram bot.

    :param message: The message to send
    :return: The bot's response in the form of a JSON dictionary
    """
    send_text = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={BOT_CHAT_ID}&parse_mode=Markdown&text={urllib.parse.quote(message)}'

    proxy = "http://212.237.59.187:58080"
    proxies = {"http://": proxy, "https://": proxy}

    fetch_with_backoff(url=send_text, proxies=None, max_retries=10)
    time.sleep(1) # To avoid Telegram API: 429 Too Many Requests

    return None


def fetch_with_backoff(url: str, proxies=None, max_retries: int = 3, retry_delay: int = 1) -> Optional[httpx.Response]:
    """
    Makes HTTP requests with exponential backoff logic in case of errors.

    :param url: The URL to obtain data from
    :param proxies: The proxy to use (optional)
    :param max_retries: Maximum number of retries in case of an error
    :param retry_delay: The initial delay in seconds between retries
    :return: The HTTP response, or None if all attempts fail
    """
    base_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "it-IT;it;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    for attempt in range(max_retries):
        if attempt > 0:
            logger.info("Retry n: %d for url: %s", attempt, url)

        try:
            # Configure the httpx client with or without proxy
            client_args = {
                "headers": base_headers,
                "follow_redirects": True,
                "timeout": 30.0,
            }
            if proxies:
                client_args["proxies"] = proxies

            with httpx.Client(**client_args) as client:
                response = client.get(url)
                response.raise_for_status()
                return response
        except (httpx.RequestError, httpx.HTTPStatusError) as error:
            logger.error("Failed to fetch data (%s) from %s, waiting %d seconds before retry", error, url, retry_delay)
            time.sleep(retry_delay)
            retry_delay = retry_delay * 2 + random.uniform(0, 1)

    logger.error("Maximum retry attempts reached for %s", url)
    return None


def extract_price_from_html(html_response: str) -> Optional[int]:
    """
    Extracts the price from the HTML response.

    :param html_response: The HTML response of the page
    :return: The extracted price as integer or None if not found
    """
    # Initialise BeautifulSoup with the HTML source
    soup = BeautifulSoup(html_response, 'html.parser')

    # Search for the <p> tag containing the price class
    price_tag = soup.find('p',
                          class_='index-module_price__N7M2x SmallCard-module_price__yERv7 index-module_small__4SyUf')
    if price_tag:
        # Extract the text from the <p> tag and remove any spaces
        price_text = price_tag.get_text().strip()

        # Use a regex to extract the number from the price text
        price_match = re.search(r'(\d+)', price_text.replace(u'\xa0', u' '))  # Sostituisce gli spazi non-breaking

        if price_match:
            return int(price_match.group(1))  # Return the price as an integer

    # If no price is found, register a warning
    logger.warning("Price not found in HTML")

    # Return None if price not found
    return None


def load_urls_from_json(file_path: str) -> list:
    """
    Loads the list of URLs and their filters from a JSON file.

    :param file_path: The path to the JSON file containing the URLs and filters
    :return: A list of dictionaries with URLs and associated filters
    """
    if not os.path.exists(file_path):
        logger.error("JSON file not found: %s", file_path)
        return []

    with open(file_path, "r") as file:
        try:
            urls_data = json.load(file)
            logger.info("Uploaded %d URLs from file %s", len(urls_data), file_path)
            return urls_data
        except json.JSONDecodeError as e:
            logger.error("Error in parsing of JSON file: %s", str(e))
            return []


def apply_filters(html_response: str, filters: dict) -> bool:
    """
    Applies the provided filters to the HTML content of the page.

    :param html_response: The HTML response of the page
    :param filters: The filters to be applied (minimum price, maximum price, shipping availability)
    :return: True if the filters are met, False otherwise
    """
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    shipping_available = filters.get("shipping_available")

    # Example: Extracting price from HTML content (to be adapted according to page structure)
    # Suppose the price is in a <span class=‘price’> tag, extracting it with a regex or HTML parsing
    price_found = extract_price_from_html(html_response)
    shipping_found = "spedizione disponibile" in html_response.lower()

    # Controlla se il prezzo rispetta i limiti
    if price_found is not None:
        if min_price and price_found < min_price:
            logger.info("Price %d below minimum (%d)", price_found, min_price)
            return False
        if max_price and price_found > max_price:
            logger.info("Price %d higher than maximum (%d)", price_found, max_price)
            return False

    # Controlla se la spedizione è disponibile
    if shipping_available is not None and shipping_available != shipping_found:
        logger.info("Shipping not available")
        return False

    return True


def extract_all_div_blocks(html_response: str) -> list:
    """
    Extracts all div blocks with the class specified by the HTML source.

    :param html_response: The HTML response of the page
    :return: A list of HTML strings for each div block found
    """
    soup = BeautifulSoup(html_response, 'html.parser')

    # Find all divs with the specified class (here it modifies according to the structure of the page)
    div_blocks = soup.find_all('div', class_='SmallCard-module_card__3hfzu items__item item-card item-card--small')

    # Returns a list of div blocks as HTML strings
    return [block.prettify() for block in div_blocks]


def extract_first_link(html_content: str) -> Optional[str]:
    """
    Extracts the first link from the given HTML block.

    :param html_content: HTML string
    :return: The first link found or None if it does not exist
    """
    # Analyses HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the first <a> tag
    first_link_tag = soup.find('a')

    # If the <a> tag exists, return the href attribute
    if first_link_tag and 'href' in first_link_tag.attrs:
        return first_link_tag['href']

    # If no link is found, returns None
    return None


def report_change(url_data: dict) -> None:
    """
    Checks if there are changes for a given URL and applies filters.

    :param url_data: A dictionary with the URL and associated filters
    """
    url = url_data.get("url")
    filters = url_data.get("filters", {})

    # Make request
    response = fetch_with_backoff(url)
    if not response:
        return

    html_response = response.text

    # Extract all div blocks of the current advertisements
    current_announcements = []
    if 'subito' in url:
        div_blocks = extract_all_div_blocks(html_response)
        for div_block in div_blocks:
            announcement_link = extract_first_link(div_block)

            # Apply filters and, if satisfied, add to list of current listings
            if apply_filters(div_block, filters) and announcement_link:
                current_announcements.append(announcement_link)

    # Load the cache of already notified announcements
    file_name = ''.join(x for x in url if x.isalpha()) + "_cache.txt"
    cache_file_path = os.path.join(DATA_FOLDER, file_name)
    cached_announcements = set()
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as cache_file:
            cached_announcements = set(cache_file.read().splitlines())

    # Filter ads not yet notified
    new_announcements = [link for link in current_announcements if link not in cached_announcements]

    # Notify only new announcements and update cache
    if new_announcements:
        for announcement in new_announcements:
            telegram_bot_send_deal(f"New ad: {announcement}")
            logger.info("New ad -> %s", announcement)

        # Update the cache file by adding new announcements
        with open(cache_file_path, "a") as cache_file:
            for announcement in new_announcements:
                cache_file.write(announcement + "\n")
    else:
        logger.info("No change detected for %s", url)


def scan_urls(file_path: str = "subito_urls.json") -> None:
    """
    Scans a list of URLs from a JSON file and checks for changes for each.

    :param file_path: The path to the JSON file containing the URLs and filters
    """
    urls_data = load_urls_from_json(file_path)

    for url_data in urls_data:
        report_change(url_data)
        time.sleep(1)


def main() -> None:
    logger.info("Starting subito-deal-notifier")
    scan_urls()

    schedule.every(SCHEDULE_INTERVAL_MINUTES).minutes.do(scan_urls)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error("An error occurred: %s", str(e))


if __name__ == "__main__":
    main()
