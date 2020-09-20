import botocore
import boto3
import json
import logging
import os
from bs4 import BeautifulSoup
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from requests import get, HTTPError
from selenium import webdriver
from time import sleep

# https://youtrack.jetbrains.com/issue/PY-39762
# noinspection PyArgumentList
logging.basicConfig(
    format="%(asctime)s %(funcName)20s() %(levelname)-8s  %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            filename="logs/pre-order-tracker.log",
            mode="a",
            maxBytes=10485760,
            backupCount=3,
        ),
        StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

AWS_PROFILE_NAME = os.environ["AWS_PROFILE_NAME"]
SNS_REGION_NAME = os.environ["SNS_REGION_NAME"]
PHONE_NUMBERS = os.environ["PHONE_NUMBERS"].split(" ")
POLL_RATE = 30
GET_RETRIES = 5
GET_RETRY_RATE = 1

AMAZON_CANADA_ASINS = {
    "ps5_disc": "B08GSC5D9G",
    "ps5_digital": "B08GS1N24H",
    "pulse_3d_headset": "B08GSBRR9Q"
}


def get_page(url):
    # todo: implement selenium with headers to avoid partial page loads
    logger.info(f"GET: {url}")
    # needed to spoof request source to navigate bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
    }
    res = None
    for attempt in range(GET_RETRIES):
        try:
            res = get(url, headers=headers)
            status_code = res.status_code
            res.raise_for_status()
            logger.info(f"[{status_code}] OK: {url}")
            if res:
                break
        except HTTPError as e:
            logger.error(e)
            if attempt == GET_RETRIES:
                logger.warning("Max GET retries exceeded")
                return None
            logger.info("Retrying GET...")
        sleep(GET_RETRY_RATE)
    return res.content


def remove_whitespace(text):
    return text.replace("\n", "").replace("\r", "")


def scrape_amazon_canada(asin):
    logger.info(f"Scraping Amazon Canada availability for {asin}")

    CURRENTLY_UNAVAILABLE = "Currently unavailable."
    IN_STOCK = "In Stock."

    url = f"https://www.amazon.ca/gp/product/{asin}"

    availability = {
        "available": False,
        "company": "Amazon Canada",
        "availability_description": None,
        "product_title": None,
        "url": url,
    }

    # get html
    amazon_page = get_page(url)

    try:
        soup = BeautifulSoup(amazon_page, "html.parser")

        # get relevant text
        raw_product_title = soup.find(id="productTitle").get_text()
        raw_availability_description = soup.find(id="availability").span.get_text()

        # clean up text
        product_title = remove_whitespace(raw_product_title)
        availability_description = remove_whitespace(raw_availability_description)

        availability["product_title"] = product_title
        availability["availability_description"] = availability_description

        if availability_description != CURRENTLY_UNAVAILABLE:
            availability["available"] = True
    except Exception as error:
        logger.error(error)

    return availability


def build_sms_update_message(available_products):
    message = "Pre-Order Tracker Update:\n"
    for available_product in available_products:
        company = available_product["company"]
        product_title = available_product["product_title"]
        availability = available_product["availability_description"]
        url = available_product["url"]
        message += (
            f"\n{company}\nProduct:\n{product_title}\n"
            f"Status:\n{availability}\nURL:\n{url}"
        )
    return message


def send_sms_update(message):
    try:
        session = boto3.session.Session(profile_name=AWS_PROFILE_NAME)
        sns = session.client("sns", region_name=SNS_REGION_NAME)
        for number in PHONE_NUMBERS:
            sns.publish(PhoneNumber=number, Message=message)
        logger.info("SMS update SUCCESS")
    except (
        botocore.exceptions.ClientError,
        sns.exceptions.InvalidParameterException,
        sns.exceptions.InternalErrorException,
        sns.exceptions.AuthorizationErrorException,
        sns.exceptions.NotFoundException,
    ) as error:
        logger.error(f"SMS update FAIL: {error}")


def poll_availability():
    logger.info("Polling product availability")
    results = []

    amazon_asins = AMAZON_CANADA_ASINS.values()
    for index, asin in enumerate(amazon_asins):
        results.append(scrape_amazon_canada(asin))
        if index < len(amazon_asins) - 1:
            sleep(1)

    logger.info(f"Polling results:\n{json.dumps(results, indent = 4)}")

    available_products = [res for res in results if res["available"]]

    if available_products:
        logger.info(f"Available products found!")
        message = build_sms_update_message(available_products)
        send_sms_update(message)


def main():
    try:
        poll_availability()
    except Exception as error:
        logger.error(error)


if __name__ == "__main__":
    main()
