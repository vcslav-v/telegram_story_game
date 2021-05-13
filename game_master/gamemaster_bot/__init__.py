"""Main module gamemaster_bot project."""
import telebot
from os import environ

DB_URL = environ.get('DB_URL') or 'http://127.0.0.1:8000/{item}/{cmd}'

bot = telebot.TeleBot(
    environ.get('TG_TOKEN')
)
