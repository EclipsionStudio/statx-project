from modules import auto_delete, get_data
from modules import global_init
from modules.global_init import bot
from modules.database.main import Database as db


def start_handler(message):
    with global_init.get_session() as session:
        db.check_user(session=session, message=message)

    text, markup = get_data(message, "start")
    bot.send_message(message.chat.id, text.format(user=message.from_user.username), reply_markup=markup, parse_mode="HTML")
    auto_delete(message)