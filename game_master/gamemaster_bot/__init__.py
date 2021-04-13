"""Main module gamemaster_bot project."""
import telebot
from os import environ

bot = telebot.TeleBot(
    environ.get('TG_TOKEN')
)
