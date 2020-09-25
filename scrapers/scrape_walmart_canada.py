import logging
from bs4 import BeautifulSoup
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from utils.get_pages import get_page, get_page_selenium
from utils.helpers import remove_whitespace

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


def scrape_walmart_canada(path):
    logger.info(f"Scraping Walmart Canada availability for {path}")

    OUT_OF_STOCK_ONLINE = "Out of stock online"

    url = f"https://www.walmart.ca/{path}"

    availability = {
        "available": False,
        "availability_description": None,
        "company": "Walmart Canada",
        "product_title": None,
        "url": url,
    }

    # get html
    walmart_page = get_page_selenium(url)

    try:
        soup = BeautifulSoup(walmart_page, "html.parser")

        # get relevant text
        raw_product_title = soup.find(
            attrs={"data-automation": "product-title"}
        ).get_text()
        raw_availability_description = soup.find(
            attrs={"data-automation": "online-only-label"}
        ).get_text()

        # clean up text
        product_title = remove_whitespace(raw_product_title)
        availability_description = remove_whitespace(raw_availability_description)

        availability["product_title"] = product_title
        availability["availability_description"] = availability_description

        if availability_description != OUT_OF_STOCK_ONLINE:
            availability["available"] = True
    except Exception as error:
        logger.error(error)

    return availability
