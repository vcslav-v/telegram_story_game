"""Main module gamemaster_bot project."""
import telebot
from os import environ
from flask import Flask, request


DB_URL = 'http://' + environ.get('DB_URL') + '/{item}/{cmd}'
APP_URL = 'https://{domain}/'.format(domain=environ.get('DOMAIN'))
BOT_URL = environ.get('BOT_URL')
BOT_TOKEN = environ.get('BOT_TOKEN') or ''
REDIS = environ.get('REDIS') or ''

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


from .handlers import story, chapter, user, message


@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    print('post')
    bot.process_new_updates([
            telebot.types.Update.de_json(
                request.stream.read().decode("utf-8")
            )
    ])
    return 'ok-post', 200


@app.route('/' + BOT_TOKEN, methods=['GET'])
def test():
    print('get')
    return 'ok-get', 200


url = APP_URL + BOT_TOKEN
bot.remove_webhook()
bot.set_webhook(url)
