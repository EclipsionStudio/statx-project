from telebot import types
from modules import global_init
from translations import translations
from modules.global_init import bot
from modules.database.main import Database as db
import time
from modules.global_init import logger

data = "main loaded"


def get_data(
    message, msg_id, only_txt=False
) -> tuple[str, types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup | None] | str:
    with global_init.get_session() as session:
        lang = db.get_lang(session=session, message=message)

    data = translations[lang][msg_id]

    if not data:
        return f"Message not found: {msg_id}", None

    text = "".join(data["msg"])

    if "key" in data:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for row in data["key"].values():
            buttons = [types.KeyboardButton(text=btn) for btn in row]
            markup.add(*buttons)

    elif "inline" in data:
        markup = types.InlineKeyboardMarkup()
        for row in data["inline"].values():
            buttons = [
                types.InlineKeyboardButton(text=btn_text, callback_data=callback)
                for btn_text, callback in row.items()
            ]
            markup.add(*buttons)
    else:
        markup = None

    if not only_txt:
        return text, markup
    return text


def next_step(message):
    with global_init.get_session() as session:
        lang = db.get_lang(session=session, message=message)

    if message.text in translations[lang]["cancel"]:
        hintid = bot.send_message(message.chat.id, "^_^")
        time.sleep(1)
        bot.delete_message(message.chat.id, hintid.message_id)
        return True
    else:
        return False


def ask(message):
    with global_init.get_session() as session:
        lang = db.get_lang(session=session, message=message)
    if message.text.lower() == translations[lang]["answers"]["yes"]:
        return False
    else:
        hintid = bot.send_message(message.chat.id, ":|")
        auto_delete(hintid, 1)
        return True


def auto_delete(message, delay=0):
    time.sleep(delay)
    bot.delete_message(message.chat.id, message.message_id)


def bot_info():
    logger.info(f"BOT '{bot.get_me().full_name}' started now!")
    logger.info(f"username: @{bot.get_me().username}")
    logger.info(f"bot id: {bot.get_me().id}")
