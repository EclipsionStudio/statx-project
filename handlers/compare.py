from modules.global_init import bot
from modules import auto_delete, get_data
from modules.create_diagram import compare_diag
from modules.faceit_requests import FaceitStats as fs
from modules.global_init import logger
from rich import print

def compare_handler(message):
    """
    Compares the stats of two players based on user input.
    """
    prompt = message.text
    prompt = prompt.replace("/compare", "").strip()

    logger.debug(prompt)

    # Split the prompt into player names
    player_names = fs().search_nicknames(prompt)

    if len(player_names) != 2:
        msg, _ = get_data(message, "compare-error-count")
        notif = bot.send_message(message.chat.id, msg)
        auto_delete(notif, 2)
        return False

    nik1, nik2 = player_names[0], player_names[-1]

    # Get user IDs
    user_id1 = fs().get_player_id(nik1)
    user_id2 = fs().get_player_id(nik2)

    print(user_id1, user_id2)

    if not user_id1 or not user_id2:
        missing_players = []
        if not user_id1:
            missing_players.append(nik1)
        if not user_id2: 
            missing_players.append(nik2)

        msg, _ = get_data(message, "compare-error-not-found")
        notif = bot.send_message(message.chat.id, msg)
        auto_delete(notif, 2)
        return False

    # Get statistics for both players
    stats1 = fs().get_player_stats(user_id1)
    stats2 = fs().get_player_stats(user_id2)

    if not stats1 or not stats2:
        no_stats_players = []
        if not stats1:
            no_stats_players.append(nik1)
        if not stats2:
            no_stats_players.append(nik2)
        
        msg, _ = get_data(message, "compare-error-no-stats", {"players": ", ".join(no_stats_players)})
        notif = bot.send_message(message.chat.id, msg)
        auto_delete(notif, 2)
        return False


    msg, _ = get_data(message, "compare-processing")
    status = bot.send_message(message.chat.id, msg + "\n[⬜⬜⬜]")

    try:
        bot.edit_message_text("Analysing FACEIT\n[🟩⬜⬜]", message.chat.id, status.message_id)
        # Rebuild stats
        rebuilded_stats1, keys_1 = fs().rebuilding(stats1)
        rebuilded_stats2, keys_2 = fs().rebuilding(stats2)

        # Find common keys (stats to compare)
        needed_keys = fs().find_best_match(prompt, keys_1)

        # Extract relevant stats
        bot.edit_message_text("Asking PHI\n[🟩🟩⬜]\n\nThe statistics displayed may differ from those requested.", message.chat.id, status.message_id)
        extracted_stats1 = fs().extract_stat(rebuilded_stats1, needed_keys)
        extracted_stats2 = fs().extract_stat(rebuilded_stats2, needed_keys)

        bot.edit_message_text("Analysing stats\n[🟩🟩🟩]", message.chat.id, status.message_id)
        # Create comparison output
        comparison_text = f"COMPARISON: {nik1} vs {nik2}\n\n"

        print(extracted_stats1, extracted_stats2)
        ptxt = ""
        for key in needed_keys.get("player"):
            ptxt += f"{key}:\n"
            ptxt += f"৹ {nik1}:{extracted_stats1.get("player", {}).get(key, "N/A")}\n"
            ptxt += f"৹ {nik2}:{extracted_stats2.get("player", {}).get(key, "N/A")}\n"
        
        ttx = ""
        for key in needed_keys.get("maps"):
            ttx += f"{key}:\n"
            for key2 in needed_keys.get("maps").get(key):
                ttx += f"৹ {nik1}:{key2}:{extracted_stats1.get("maps", {}).get(key, {}).get(key2, "N/A")}\n"
                ttx += f"৹ {nik2}:{key2}:{extracted_stats2.get("maps", {}).get(key, {}).get(key2, "N/A")}\n"


    
        visual = comparison_text + ptxt + ttx + "\n<may be inaccurate>\n@stat_x_bot"

        bot.delete_message(message.chat.id, status.message_id)
        try:
            diagr = compare_diag({"player": nik1, "stats": extracted_stats1}, {"player": nik2, "stats": extracted_stats2})
            bot.send_photo(message.chat.id, photo=diagr, caption=visual)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, text=visual)

    except Exception as e:
        logger.error(f"Error during comparison: {e}")
        bot.edit_message_text(f"Error during comparison: {e}", message.chat.id, status.message_id)