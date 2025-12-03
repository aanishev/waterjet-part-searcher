from telebot.types import BotCommand

from config import branch, API_TOKEN_MAIN, API_TOKEN_TEST
import telebot

if branch == "test":
    bot = telebot.TeleBot(API_TOKEN_TEST, parse_mode="HTML")
else:
    bot = telebot.TeleBot(API_TOKEN_MAIN, parse_mode="HTML")