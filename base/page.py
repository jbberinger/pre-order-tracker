import logging
import os
from time import sleep
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from requests import get, HTTPError

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


class Page:
    """
    Represents a web page and its data
    """

    AWS_PROFILE_NAME = os.environ["AWS_PROFILE_NAME"]
    SNS_REGION_NAME = os.environ["SNS_REGION_NAME"]
    POLL_RATE = 30
    GET_RETRIES = 5
    GET_RETRY_RATE = 1

    def __init__(self, url: str):
        self.url = url

    def get_page(self):
        # todo: implement selenium with headers to avoid partial page loads
        logger.info(f"GET: {self.url}")
        # needed to spoof request source to navigate bot detection
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }
        res = None
        for attempt in range(self.GET_RETRIES):
            try:
                res = get(self.url, headers=headers)
                status_code = res.status_code
                res.raise_for_status()
                logger.info(f"[{status_code}] OK: {self.url}")
                if res:
                    break
            except HTTPError as e:
                logger.error(e)
                if attempt == self.GET_RETRIES:
                    logger.warning("Max GET retries exceeded")
                    return None
                logger.info("Retrying GET...")
            sleep(self.GET_RETRY_RATE)
        return res.content

    def scrape(self):
        pass

    def transform(self):
        pass
