# homework_bot

Telegram bot for my personal use that checks my homework status in **Yandex.Practicum** (Russian Online Platform) and send me the recent updates.

Stack: Python 3, python-telegram-bot
### How start project:

Clone a repository and go to command line:

```sh
git@github.com:eraline/api_yamdb.git
```

```sh
cd homework_bot
```

Create and activate virtual environment:

```sh
python3 -m venv env
```
For Windows:
```sh
source env/Scripts/activate  
```
For Linux:
```sh
source env/bin/activate  
```

Install dependencies from a file requirements.txt:

```sh
python3 -m pip install --upgrade pip
```

```sh
pip install -r requirements.txt
```

Create a file with environment variables
```sh
touch .env
```
Add PRAKTIKUM_TOKEN, TELEGRAM_TOKEN and TELEGRAM_CHAT_ID to .env file

Start project:

```sh
python homework.py
```
