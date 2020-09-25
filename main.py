import json
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from scrapers.scrape_amazon_canada import scrape_amazon_canada
from scrapers.scrape_walmart_canada import scrape_walmart_canada
from utils.comms import (
    build_sms_update_message,
    send_sms_update,
    send_desktop_notification,
)

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

AMAZON_CANADA_ASINS = {
    "ps5_disc": "B08GSC5D9G",
    "ps5_digital": "B08GS1N24H",
    "pulse_3d_headset": "B08GSBRR9Q",
}

WALMART_CANADA_PATHS = {
    "ps5_disc": "en/ip/playstation5-console/6000202198562",
    "ps5_digital": "en/ip/playstation5-digital-edition/6000202198823",
    "pulse_3d_headset": "en/ip/playstation5-pulse-3d-wireless-headset/6000202197222",
}


def poll_availability():
    logger.info("Polling product availability")
    results = []

    amazon_asins = AMAZON_CANADA_ASINS.values()
    for index, asin in enumerate(amazon_asins):
        results.append(scrape_amazon_canada(asin))

    walmart_paths = WALMART_CANADA_PATHS.values()
    for index, path in enumerate(walmart_paths):
        results.append(scrape_walmart_canada(path))

    logger.info(f"Polling results:\n{json.dumps(results, indent = 4)}")

    available_products = [res for res in results if res["available"]]

    if available_products:
        logger.info(f"Available products found!")
        message = build_sms_update_message(available_products)
        send_sms_update(message)
        send_desktop_notification(title="Available products found!", message=message)


def main():
    try:
        poll_availability()
    except Exception as error:
        logger.error(error)


if __name__ == "__main__":
    main()
