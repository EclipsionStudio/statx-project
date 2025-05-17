from modules import get_data, next_step, ask, auto_delete
from modules.global_init import bot
from modules import global_init
from modules.database.main import Database as db
from modules.faceit_requests import FaceitStats

# text, markup = get_data(message, "login-1-alredy")


def login_handler(message):
    with global_init.get_session() as session:
        login_setted = db.set_faceit_userid(session=session, message=message)

    auto_delete(message)
    if not login_setted:
        text, markup = get_data(message, "login-start") 
        bmsg = bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
        bot.register_next_step_handler(message, username_checkout, bmsg)
    else:
        text, markup = get_data(message, "login-start-already") 
        bmsg = bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
        bot.register_next_step_handler(message, confirm_edit, bmsg)


def confirm_edit(message, bmsg):
    auto_delete(message)
    auto_delete(bmsg)
    if ask(message):
        return
    
    text, markup = get_data(message, "login-start")
    bmsg = bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.register_next_step_handler(message, username_checkout, bmsg)

def username_checkout(message, bmsg):
    auto_delete(message)
    auto_delete(bmsg)
    if next_step(message):
        return
    
    text, markup = get_data(message, "login-checkout")
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    
    username = message.text

    if username.startswith("https://www.faceit.com/"):
        username = username[24:].split("/")[-1]
        uid = FaceitStats().get_player_id(username)
        
    elif not username.startswith("https://www.faceit.com/"):
        uid = FaceitStats().get_player_id(username)
    else:
        text, markup = get_data(message, "login-link-error")
        m_error = bot.send_message(message.chat.id, text=text, reply_markup=markup, parse_mode="HTML")
        auto_delete(m_error, 2)

    if uid != "Error":
        text, markup = get_data(message, "login-sure") 
        bmsg = bot.send_message(chat_id=message.chat.id, text=text.format(user=username), reply_markup=markup, parse_mode="HTML")
        bot.register_next_step_handler(message, login_end, uid, username, bmsg)
    else:
        text, markup = get_data(message, "login-profile-error")
        m_error = bot.send_message(message.chat.id, text=text, reply_markup=markup, parse_mode="HTML")
        auto_delete(m_error, 2)


def login_end(message, faceit_id, username, bmsg):
    auto_delete(message)
    auto_delete(bmsg)
    if next_step(message):
        return
    if ask(message):
        return
    
    uid = str(faceit_id)

    with global_init.get_session() as session:
        facit_id = db.set_faceit_userid(session=session, message=message, set_user_id=uid, set_user_name=username, get_faceit_id=True)

    text, markup = get_data(message, "login-success")
    m_info = bot.send_message(message.chat.id, text.format(fid=facit_id, fn=username), reply_markup=markup, parse_mode="HTML")
    auto_delete(m_info, 2)