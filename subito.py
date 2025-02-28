import json
import os
import re
import time
import random
import asyncio
import schedule
import threading
import urllib.parse

from conf import Config
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from http_client import HttpClient
from llm import LLM
from logger_config import get_logger
from subito_ad import SubitoAd
from async_processor import AsyncProcessor

logger = get_logger('subito-deal-notifier')

processor = AsyncProcessor()


def telegram_bot_send_deal(message: str) -> bool:
    """
    Send a message via the Telegram bot.

    :param message: The message to send
    :return: The bot's response in the form of a JSON dictionary
    """
    send_text = f'https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage?chat_id={Config.BOT_CHAT_ID}&parse_mode=Markdown&text={urllib.parse.quote(message)}'

    proxy = "http://212.237.59.187:58080"
    proxies = {"http://": proxy, "https://": proxy}

    HttpClient.fetch_with_backoff(url=send_text, proxies=None, max_retries=10)
    time.sleep(1)  # To avoid Telegram API: 429 Too Many Requests

    return True


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


def extract_price_from_html(html_response: str) -> Optional[int]:
    """
    Extracts the price from the HTML response, handling thousand separators.

    :param html_response: The HTML response of the page
    :return: The extracted price as integer or None if not found
    """
    soup = BeautifulSoup(html_response, 'html.parser')
    price_tag = soup.find('p',
                          class_='index-module_price__N7M2x SmallCard-module_price__yERv7 index-module_small__4SyUf')
    if price_tag:
        price_text = price_tag.get_text().strip()
        # Remove thousand separators (dots) and extract digits
        price_cleaned = price_text.replace('.', '').replace(',', '').replace(u'\xa0', u' ')
        price_match = re.search(r'(\d+)', price_cleaned)
        if price_match:
            return int(price_match.group(1))
    logger.warning("Price not found in HTML")
    return None


def extract_title_from_html(html_response: str) -> Optional[str]:
    """
    Extracts the title from the HTML response, using a flexible tag search.

    :param html_response: The HTML response of the page
    :return: The extracted title or None if not found
    """
    soup = BeautifulSoup(html_response, 'html.parser')
    # Look for various tag possibilities where the title might be located
    title_tag = soup.find('h2',
                          class_='index-module_title__Zvu61 SmallCard-module_title__RfMb- index-module_small__4SyUf')
    if not title_tag:
        # Try alternative ways if the specific class isn't found
        title_tag = soup.find('h2') or soup.find('span', class_='title') or soup.find('div', class_='title')
    if title_tag:
        return title_tag.get_text().strip()
    logger.warning("Title not found in HTML")
    return None


def extract_shipment_from_html(html_response: str) -> Optional[bool]:
    """
    Extracts the shipment availability from the HTML response.

    :param html_response: The HTML response of the page
    :return: True if shipment is available, False otherwise
    """
    return "spedizione disponibile" in html_response.lower()


async def report_change_async(url_data: dict) -> None:
    """
    Asynchronous version of report_change to allow async task execution.
    """
    url = url_data.get("url")
    filters = url_data.get("filters", {})

    response = HttpClient.fetch_with_backoff(url)  # Fetch in a non-blocking way
    if not response:
        return

    html_response = response.text
    current_announcements = []

    if 'subito' in url:
        div_blocks = extract_all_div_blocks(html_response)
        for div_block in div_blocks:
            announcement_link = extract_first_link(div_block)
            if apply_filters(div_block, filters) and announcement_link:
                current_announcements.append((announcement_link, div_block))

    file_name = ''.join(x for x in url if x.isalpha()) + "_cache.txt"
    cache_file_path = os.path.join(Config.DATA_FOLDER, file_name)
    cached_announcements = set()

    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as cache_file:
            cached_announcements = set(cache_file.read().splitlines())
    elif not Config.COLD_START:
        logger.info("Cache file not found. Initializing cache for %s without sending notifications.", url)
        with open(cache_file_path, "w") as cache_file:
            cache_file.write("\n".join([link for link, _ in current_announcements]))
        return

    new_announcements = [item for item in current_announcements if item[0] not in cached_announcements]

    if new_announcements:
        for announcement, div_block in new_announcements:
            price = extract_price_from_html(div_block)
            title = extract_title_from_html(div_block)
            shipment = "Yes" if extract_shipment_from_html(div_block) else "No"

            details = SubitoAd(announcement)
            details.extract_data()

            # print(details.to_json())

            async def heavy_function(product_title: str, product_description: str, product_price: float):
                """Simulates a time-consuming task."""
                print(f"🔄 Processing task: {title}...")
                # Assicurati che LLM.compute_score sia un'operazione asincrona

                print(f"✅ Task: {title} completed.")

            if price and price >= 100:
                llm = LLM.compute_score(details.product_title, details.product_description, details.product_price)

                if llm is None:
                    print("⚠️ LLM.compute_score ha restituito None. Impossibile elaborare il messaggio.")
                    return

                message = (
                    f"🔗 Annuncio: {announcement}\n\n"
                    f"📌 Titolo: {title if title else 'Sconosciuto'}\n"
                    f"💶 Prezzo: {price if price else 'Sconosciuto'}€\n"
                    f"🚚 Spedizione: {shipment}\n"
                    f"⭐️ Punteggio: {llm['score']}\n"
                    f"🧐 Valutazione: {llm['reasoning']}\n"
                    f"🔍 Caratteristiche: {llm['product_feature']}\n"
                )

            else:
                message = (
                    f"🔗 Link: {announcement}\n\n"
                    f"📚 Title: {title if title else 'Unknown'}\n"
                    f"💰 Price: {price if price else 'Unknown'}€\n"
                    f"📦 Shipment: {shipment}\n"
                )

            logger.info(message)
            telegram_bot_send_deal(message)

        with open(cache_file_path, "a") as cache_file:
            for announcement, _ in new_announcements:
                cache_file.write(announcement + "\n")
    else:
        logger.info("No change detected for %s", url)


async def scan_urls_async(file_path: str = "subito_urls.json") -> None:
    """
    Asynchronous version of scan_urls to allow async execution.
    """
    urls_data = load_urls_from_json(file_path)

    # Esegui le coroutine in parallelo
    await asyncio.gather(*(report_change_async(url_data) for url_data in urls_data))


async def main_loop() -> None:
    """
    Main loop that runs the periodic scanning of URLs.
    """
    logger.info("Starting subito-deal-notifier with COLD_START=%s", Config.COLD_START)

    # Esegui la prima scansione all'avvio
    await scan_urls_async()

    # Programma la scansione periodica
    schedule.every(Config.SCHEDULE_INTERVAL_MINUTES).minutes.do(lambda: asyncio.create_task(scan_urls_async()))

    while True:
        try:
            schedule.run_pending()
            await asyncio.sleep(1)
        except Exception as e:
            logger.error("An error occurred: %s", str(e))


def run_asyncio_loop(loop):
    """
    Runs an asyncio event loop in a separate thread.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == "__main__":
    # Crea il loop principale per il main
    main_loop_thread = threading.Thread(target=lambda: asyncio.run(main_loop()), daemon=True)

    # Crea un secondo loop per la coda
    queue_loop = asyncio.new_event_loop()
    queue_thread = threading.Thread(target=run_asyncio_loop, args=(queue_loop,), daemon=True)

    # Avvia entrambi i thread
    main_loop_thread.start()
    queue_thread.start()

    # Ora avviamo processor.process_queue() nel loop corretto
    asyncio.run_coroutine_threadsafe(processor.process_queue(), queue_loop)

    # Mantieni il processo in esecuzione
    main_loop_thread.join()
    queue_thread.join()
