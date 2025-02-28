import time

import httpcore
import httpx
import random

from logger_config import get_logger
from typing import Optional, Dict, Any, Union

logger = get_logger('http-client')


class HttpClient:

    @staticmethod
    def fetch_with_backoff(
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json: Optional[Union[Dict[str, Any], str]] = None,
            proxies: Optional[Union[Dict[str, str], str]] = None,
            max_retries: int = 5,
            retry_delay: int = 3,
            max_delay: int = 300,
            debug: bool = False
    ) -> Optional[httpx.Response]:
        """
        Makes HTTP requests with exponential backoff logic in case of errors.

        :param url: The URL to obtain data from
        :param method: The HTTP method to use (GET, POST, PUT, DELETE, PATCH)
        :param headers: Optional headers for the request
        :param data: Optional form data for requests
        :param json: Optional JSON data for requests
        :param proxies: The proxy to use (optional, can be dict or string)
        :param max_retries: Maximum number of retries in case of an error
        :param retry_delay: The initial delay in seconds between retries
        :param max_delay: The maximum delay between retries
        :param debug: Enables verbose logging if True
        :return: The HTTP response, or None if all attempts fail
        """

        method = method.upper()
        allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        if method not in allowed_methods:
            raise ValueError(f"Unsupported HTTP method {method}. Allowed: {allowed_methods}")

        # Error codes that should NOT be retried
        non_retry_status_codes = {400, 401, 403, 404, 422}

        # Convert proxies if provided as a string
        if isinstance(proxies, str):
            proxies = {"http": proxies, "https": proxies}

        for attempt in range(max_retries):
            if attempt > 0:
                logger.info(f"Retry {attempt} for {url}")

            try:
                client_args = {
                    "headers": headers or {},
                    "follow_redirects": True
                }
                if proxies:
                    client_args["proxies"] = proxies

                timeout = httpx.Timeout(60.0, connect=60.0)

                with httpx.Client(**client_args, timeout=timeout) as client:
                    response = client.request(method, url, data=data, json=json)

                    if debug:
                        logger.info(
                            "Request method: %s, URL: %s, Headers: %s, Content: %s",
                            response.request.method,
                            response.request.url,
                            response.request.headers,
                            response.request.content,
                        )

                    response.raise_for_status()
                    return response

            except httpx.HTTPStatusError as http_err:
                status_code = http_err.response.status_code if http_err.response else None
                if status_code in non_retry_status_codes:
                    logger.error(f"Non-retryable HTTP error {status_code} on {url}")
                    return None  # No retry for certain status codes

                logger.warning(f"HTTP error {status_code} for {url}, retrying in {retry_delay}s")

            except httpx.RequestError as req_err:
                logger.error(f"Network error: {req_err}. Retrying in {retry_delay} seconds...")

            except httpcore.ConnectError as conn_err:
                logger.error(f"Connection error: {conn_err}. Retrying in {retry_delay} seconds...")

            # Wait before retrying with backoff + jitter
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2 + random.uniform(0.5, 1.5), max_delay)

        logger.error(f"Maximum retry attempts reached for {url}")
        return None
