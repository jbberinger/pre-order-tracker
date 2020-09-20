# Pre-Order Tracker

### Scrapes the web for pre-order availability. Inspired by the 2020 PS5 launch scarcity.

## Supported Websites
- Amazon Canada

## Requirements
- Python 3.8.1
- AWS account for sending SMS updates with SNS
- .env file for secrets

## Environment Variables
AWS_PROFILE_NAME=(aws settings profile to use with AWS)

SNS_REGION_NAME=(SMS messages can only originate from certain regions)

PHONE_NUMBERS=(space separated list of phone numbers to update via SMS)