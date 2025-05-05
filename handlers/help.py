from modules import get_data
from modules.global_init import bot

def help_handler(message):
    text, markup = get_data(message, "help")
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")