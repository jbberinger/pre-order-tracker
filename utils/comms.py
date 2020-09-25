import boto3
import botocore
import logging
import os
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

AWS_PROFILE_NAME = os.environ["AWS_PROFILE_NAME"]
SNS_REGION_NAME = os.environ["SNS_REGION_NAME"]
PHONE_NUMBERS = os.environ["PHONE_NUMBERS"].split(" ")

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


def send_desktop_notification(title=None, message=None):
    subprocess.call(["notify-send", title, message])
