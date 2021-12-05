import logging
import sys
import os
import requests
import time
import telegram
from pprint import pprint
from dotenv import load_dotenv

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
    level=logging.DEBUG,
    stream=sys.stdout,
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def send_message(bot, message):
    """Sending message in telegram chat"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f'Message sent successfully: {message}')
    except Exception as error:
        logging.error(f'Error while sending message: {error}')


def get_api_answer(current_timestamp):
    """Getting answer from yandex_hw api"""
    logging.debug('Getting response')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        raise BaseException('StatusCode is not 200')


def check_response(response):
    """Checking if the response from yandex api has proper format"""
    logging.debug('Checking response')
    if not isinstance(response, dict):
        raise TypeError
    if not isinstance(response['homeworks'], list):
        raise TypeError
    if 'homeworks' not in response:
        raise KeyError
    return response['homeworks']


def parse_status(homework):
    """Parsing status of homeworks from response"""
    logging.debug('Start parsing hw status')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checking virtual env tokens"""
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
    last_err_msg = ''
    logging.info('Starting bot')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.debug('Checking tokens')
    if check_tokens() is True:
        logging.debug('Tokens are valid')
    else:
        logging.critical('TOKENS ARE NOT VALID')
        raise BaseException('Invalid tokens')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            pprint(homeworks)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            logging.error(error)
            time.sleep(RETRY_TIME)
            if last_err_msg != error:
                send_message(bot, error)


if __name__ == '__main__':
    main()
