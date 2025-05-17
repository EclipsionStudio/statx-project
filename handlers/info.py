from modules import auto_delete, get_data
from modules.database.main import Database as db
from modules.faceit_requests import FaceitStats as fs
from modules.global_init import bot
from modules.global_init import logger
from modules import global_init
import time
from rich import print

def info_handler(message):
    prompt: str = message.text
    prompt = prompt.replace("/info", "").strip()

    logger.debug(prompt)

    if not prompt:
        prompt = "Kills, Win Rate, Headshots"
        
    logger.debug("search niknames")
    nik = fs().search_nicknames(prompt)

    if len(nik) == 0:
        with global_init.get_session() as session:
            nik = db.get_user(session=session, message=message).faceit_username
    else:
        nik = nik[0]
        prompt = prompt.replace(f'"{nik[0]}"', "").strip()

    user_id = fs().get_player_id(nik)

    if not user_id:
        msg, _ = get_data(message, "info-nick-error")
        notif = bot.send_message(message.chat.id, msg)
        auto_delete(notif, 2)
        return False

    msg, _ = get_data(message, "info")
    status = bot.send_message(message.chat.id, msg+"\n[⬜⬜⬜]")
    logger.debug("get stats")
    stats = fs().get_player_stats(user_id)

    if stats:
        logger.debug("Analysing Faceit")
        bot.edit_message_text("Analysing FACEIT\n[🟩⬜⬜]", message.chat.id, status.message_id)
        rebuilded_stats, keys_ = fs().rebuilding(stats)

        logger.debug("Fetching PHI-4")
        bot.edit_message_text("Asking PHI\n[🟩🟩⬜]\n\nThe statistics displayed may differ from those requested.", message.chat.id, status.message_id)
        time.sleep(3)
        needed_keys = fs().find_best_match(prompt, keys_)
        
        logger.debug("Searching values")
        bot.edit_message_text("Searching Stats\n[🟩🟩🟩]", message.chat.id, status.message_id)
        result = fs().extract_stat(rebuilded_stats, needed_keys)
        
        print(result)

        if not nik:
            nik = "Anonim"

        visual1 = ""

        try:
            if result.get("player"):
                visual1 += "GLOBALS:\n"
                for stat, val in result.get("player").items():
                    visual1 += f"৹ {stat}: {val}\n"
        except Exception:
            pass
            # visual1 += "Sorry, something went wrong\n"

        visual2 = ""
        try:
            visual2 += "\n"
            if result.get("maps"):
                for map_, data in result.get("maps").items():
                    visual2 += f"MAP: {map_}\n"
                    for stat, val in data.items():
                        visual2 += f"৹ {stat}: {val}\n"
        except Exception:
            pass

        if not visual1 and not visual2:
            visual1 = "Stats not Found )\n"

        print(visual1, visual2, )

        visual = f"STATS FOR {nik}\n" + visual1 + visual2 + "\n<may be inaccurate>\n@stat_x_bot"

        bot.edit_message_text(visual, message.chat.id, status.message_id)

        
    else:
        logger.debug("no stats")


