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


def scrape_amazon_canada(asin):
    logger.info(f"Scraping Amazon Canada availability for {asin}")

    CURRENTLY_UNAVAILABLE = "Currently unavailable."
    IN_STOCK = "In Stock."

    url = f"https://www.amazon.ca/gp/product/{asin}"

    availability = {
        "available": False,
        "availability_description": None,
        "company": "Amazon Canada",
        "product_title": None,
        "url": url,
    }

    # get html
    amazon_page = get_page_selenium(url)

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
