import logging
import sys
import os
import requests
import time

import telegram
from dotenv import load_dotenv

from exception import (
    UnexpectedResponseCode,
    # NoneInMandatoryValue,
    InvalidTokens)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('YANDEX_TOKEN')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def send_message(bot, message):
    """Sending message in telegram chat."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'Message sent successfully: {message}')
    except Exception as error:
        logging.error(f'Error while sending message: {error}')


def get_api_answer(current_timestamp):
    """Getting answer from yandex_hw api."""
    logging.debug('Getting response')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Error while getting response: {error}')

    if response.status_code == 200:
        response = response.json()
        logging.debug(response)
        return response
    else:
        raise UnexpectedResponseCode


def check_response(response):
    """Checking if the response from yandex api has proper format."""
    logging.debug('Checking response')
    if (not isinstance(response, dict)
       or not isinstance(response['homeworks'], list)):
        raise TypeError
    logging.debug('Response is valid')
    return response['homeworks']


def parse_status(homework):
    """Parsing status of homeworks from response."""
    logging.debug('Start parsing hw status')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    # Код ниже не пропускает тест 'test_parse_status_no_homework_name_key'
    # По идее ведь, если бы я оставил как было и присваивал без get,
    # то в случае отсутствующего значения у меня бы выбрасывалась ошибка,
    # которая отловилась бы в main()
    # if homework_status is None or homework_name is None:
    #     logging.error('Invalid values in hw details')
    #     raise NoneInMandatoryValue

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checking virtual env tokens."""
    logging.debug('Checking tokens')
    if not PRACTICUM_TOKEN:
        logging.critical('RACTICUM_TOKEN is missing')
        return False
    if not TELEGRAM_TOKEN:
        logging.critical('TELEGRAM_TOKEN is missing')
        return False
    if not TELEGRAM_CHAT_ID:
        logging.critical('TELEGRAM_CHAT_ID is missing')
        return False
    return True


def main():
    """Основная логика работы бота."""
    logging.info('Starting bot')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    if check_tokens() is True:
        logging.debug('Tokens are valid')
    else:
        logging.critical('TOKENS ARE NOT VALID')
        raise InvalidTokens
    while True:
        try:
            last_err_msg = ''
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            logging.error(error)
            time.sleep(RETRY_TIME)
            if last_err_msg != error:
                send_message(bot, error)


if __name__ == '__main__':
    main()
