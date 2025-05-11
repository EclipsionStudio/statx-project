import requests
import re
from decouple import config
from modules.global_init import logger

API_KEY = config("FACEIT_API_SERVER")
DP_KEY = config("DEEPSEEK_API")

MODEL = config("MODEL")

HEADERS_API = {"Authorization": f"Bearer {API_KEY}"}
HEADERS_DP = {"Authorization": f"Bearer {DP_KEY}"}

API_PREF = "https://open.faceit.com/data/v4"
DP_PREF = "https://openrouter.ai/api/v1"

REQ = (
    "Choose which of the following expressions is behind the user query. "
    "Query: {query}. Expressions: {exp}. "
    "Return ONLY the expression itself as the answer."
)


def api_request(method, url, headers=None, data=None):
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Error: {err}")
    return None


def get_player_id(nickname):
    url = f"{API_PREF}/players?nickname={nickname}"
    response = api_request("GET", url, headers=HEADERS_API)

    return response.get("player_id") if response else None


def get_player_stats(player_id):
    url = f"{API_PREF}/players/{player_id}/stats/cs2"

    return api_request("GET", url, headers=HEADERS_API)


def find_best_match(query, expressions):
    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": REQ.format(query=query, exp=",".join(expressions)),
            }
        ],
        "max_tokens": 10000,
    }
    response = requests.post(
        f"{DP_PREF}/chat/completions", headers=HEADERS_DP, json=data
    )
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def rebuilding(changeable):
    result = [{"": {}}]
    keys = list(changeable.items())

    for idx, (key, value) in enumerate(keys):
        if idx == 0:
            result[0][""][key] = value
        elif idx == 1:
            result[0][""][key] = value
        elif idx == 2 and isinstance(value, dict):
            result[0][""].update(value)
        else:
            if not isinstance(value, list):
                continue
            for map_item in value:
                if (
                    not isinstance(map_item, dict)
                    or "label" not in map_item
                    or "stats" not in map_item
                ):
                    continue
                label = map_item["label"]
                stats = map_item["stats"]
                result.append({label: {}})
                result[-1][label].update(stats)

    return result


def make_expressions(changeable):
    return [
        " ".join(item.keys()).strip()
        for item in changeable
        if item and any(item.values())
    ]


def extract_stat(best_match, rebuilded_stats):
    if best_match.split()[0] in [
        "Dust2",
        "Vertigo",
        "Train",
        "Mirage",
        "Overpass",
        "Ancient",
        "Anubis",
        "Nuke",
    ]:
        for item in rebuilded_stats:
            if next(iter(item)) == best_match.split()[0]:
                return item[best_match.split()[0]][" ".join(best_match.split()[1:])]
    return rebuilded_stats[0][""][best_match]


def main(request, mode, comparison_mode):
    if mode == "1":
        query = request
        if query.count('"') % 2 == 1 or query.count('"') == 0 or query.count('"') > 2:
            return "Error: Enter the player's nickname correctly"

        nickname_match = re.search(r'"(.*?)"', query)
        if not nickname_match:
            return "Error: Invalid format for player nickname."

        nickname = nickname_match.group(1)
        player_id = get_player_id(nickname)
        if player_id:
            stats = get_player_stats(player_id)
            if stats:
                rebuilded_stats = rebuilding(stats)
                expressions = make_expressions(rebuilded_stats)
                query = query.replace(f'"{nickname}"', "").strip()
                best_match = find_best_match(query, expressions)
                result = extract_stat(best_match, rebuilded_stats)
                return f"The {best_match.lower()} for {nickname} is {result}"
            else:
                return "Error: Failed to get player's statistics!"
        else:
            return "Error: This nickname does not exist!"

    elif mode == "2":
        query = request
        if comparison_mode not in ["max", "min"]:
            return "Error: Enter the correct query (max/min)"

        if query.count('"') % 2 == 1 or query.count('"') == 0:
            return "Error: Enter the players' nicknames correctly"

        players = {}
        for i in range(int(query.count('"') / 2)):
            nickname_match = re.search(r'"(.*?)"', query)
            if not nickname_match:
                continue

            nickname = nickname_match.group(1)
            player_id = get_player_id(nickname)
            if player_id:
                stats = get_player_stats(player_id)
                if stats:
                    rebuilded_stats = rebuilding(stats)
                    expressions = make_expressions(rebuilded_stats)
                    best_match = find_best_match(query, expressions)
                    players[nickname] = extract_stat(best_match, rebuilded_stats)
                    query = query.replace(f'"{nickname}"', "").strip()

        if players:
            sorted_players = sorted(players.items(), key=lambda item: item[1], reverse=(comparison_mode == "max"))
            return f"{comparison_mode.capitalize()} number of {best_match.lower()} has {sorted_players[0][0]} ({sorted_players[0][1]})"
        else:
            return "Error: No valid players found or their statistics were not fetched correctly."
    else:
        return "Error: Invalid mode! Choose 1 or 2"


if __name__ == "__main__":
    main()
