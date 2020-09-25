import logging
from time import sleep
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from requests import get, HTTPError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

POLL_RATE = 30
GET_RETRIES = 5
GET_RETRY_RATE = 1


def get_page(url):
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


def get_page_selenium(url):
    driver_path = "/usr/bin/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    )
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    driver.get(url)
    return driver.page_source


def remove_whitespace(text):
    return text.replace("\n", "").replace("\r", "").strip()
