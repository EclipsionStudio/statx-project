import time
# from turtle import reset
import requests
import re
import json
from decouple import config
from modules.global_init import logger
from rich import print

REQ = "Choose which of the following expressions is behind the user query. Query: {query}. Expressions: {exp} return in format '{s}//{k}'. split stats by ', '. you can display more than just statistics. Return the full key and card if you have one. without additional messages. The statistics key should not be map_stats or global_stats. Only the element from the list. If player statistics, then just specify <statistic_name>//<none>"


class FaceitStats:
    def __init__(self):
        pass

    def get_player_id(self, nickname):
        url = f"https://open.faceit.com/data/v4/players?nickname={nickname}"
        headers = {"Authorization": f"Bearer {config("FACEIT_API_SERVER")}"}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json().get("player_id")
        else:
            print(f"Error when getting player ID: {response.json()}")
            return None

    def get_player_stats(self, player_id):
        url = f"https://open.faceit.com/data/v4/players/{player_id}/stats/cs2"
        headers = {"Authorization": f"Bearer {config("FACEIT_API_SERVER")}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error when retrieving statistics: {response.json()}")
            return None
    
    def search_nicknames(self, txt):
        return re.findall(r'["\'](.*?)["\']', txt)
         

    def find_best_match(self, query, expressions):
        s1 = time.time()

        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config("ROUTER_API")}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "microsoft/phi-4",
            "messages": [
            {
                "role": "user",
                "content": REQ.format(query=query, exp=expressions, s="{statistic key}", k="{map or none}",)
            }
            ],
            
        })
        )

        res = response.json()["choices"][0]["message"]["content"]

        logger.debug(f"fetching: {round(time.time()-s1, 3)} secs \n     -: {res}")
        result = {"player": [], "maps": {}}
        stats = res.replace("`","").strip().split(", ")
        
        for stat in stats:
            try:
                if stat.count("//") != 0:
                    name, type_ = stat.split("//")
                    name = name.strip()
                    type_ = type_.strip()
                else:
                    name = stat.strip()
                    type_ = "none"

                if type_ == "none" and name in expressions["global_stats"]:
                    result["player"].append(name)
                elif type_ in expressions["maps"] and name in expressions["map_stats"]:
                    if not result.get("maps", {}).get(type_, None):
                        result["maps"][type_] = []
                    
                    result["maps"][type_].append(name)
            except Exception:
                logger.debug("Error, skipping parameter!")


        
        return result
        

    def rebuilding(self, changeable):
        global_stats = changeable.get('lifetime', {})
        maps, map_names, map_stats_keys = {}, [], set()

        for segment in changeable.get('segments', []):
            if segment.get('type') == 'Map':
                map_name = segment.get('label')
                stats = segment.get('stats', {})
                if map_name:
                    maps[map_name] = stats
                    map_names.append(map_name)
                    map_stats_keys.update(stats.keys())
                    
        return ({
            'global': global_stats,
            'maps': maps
        }, 
        {
            'global_stats': list(global_stats.keys()),
            'maps': map_names,
            'map_stats': list(map_stats_keys)
        })

    def main(self):
        mode = input("Choose mode (1 - single player, 2 - compare player) -> ")
        if mode == "1":
            query = input("Enter your request -> ")
            if (
                query.count('"') % 2 == 1
                or query.count('"') == 0
                or query.count('"') > 2
            ):
                print("Enter the player's nickname correctly")
                return
            nickname = re.search(r'"(.*?)"', query).group(1)
            player_id = self.get_player_id(nickname)
            if player_id:
                stats = self.get_player_stats(player_id)
                if stats:
                    rebuilded_stats = self.rebuilding(stats)
                    expressions = self.make_expressions(rebuilded_stats)
                    query = query.replace(f'"{nickname}"', "").strip()
                    best_match = self.find_best_match(query, expressions)
                    result = self.extract_stat(best_match, rebuilded_stats)
                    print(f"The {best_match.lower()} for {nickname} is {result}")
                else:
                    print("Error! Failed to get player's statistics!")
            else:
                print("Error! This nickname does not exist!")
        elif mode == "2":
            self.compare_players()


    def extract_stat(self, rebuilded_stats, needed_keys):
        player = {}
        maps = {}

        if needed_keys.get("player"):
            for stat in needed_keys.get("player"):
                player[stat] = rebuilded_stats.get("global").get(stat, "Sorry, we can`t find this stat :(")
        
        if needed_keys.get("maps"):
            for map, data in needed_keys.get("maps").items():
                maps[map] = {}
                for stat in data:
                    maps[map][stat] = rebuilded_stats.get("maps").get(map).get(stat, "Sorry, we can`t find this stat :(")
        
        return {
            "player": player,
            "maps": maps
        }


    def compare_players(self):
        query = input("Enter your request -> ")
        choice = input("You want to get the largest or smallest value (max/min) -> ")
        if choice not in ["max", "min"]:
            print("Enter the correct query (max/min)")
            return
        if query.count('"') % 2 == 1 or query.count('"') == 0:
            print("Enter the players' nicknames correctly")
            return
        players = {}
        for i in range(int(query.count('"') / 2)):
            nickname = re.search(r'"(.*?)"', query).group(1)
            player_id = self.get_player_id(nickname)
            if player_id:
                stats = self.get_player_stats(player_id)
                if stats:
                    if i == 0:
                        rebuilded_stats = self.rebuilding(stats)
                        expressions = self.make_expressions(rebuilded_stats)
                        best_match = self.find_best_match(query, expressions)
                    players[nickname] = self.extract_stat(best_match, rebuilded_stats)
        sorted_players = sorted(
            players.items(), key=lambda item: item[1], reverse=(choice == "max")
        )
        print(
            f"{choice.capitalize()} number of {best_match.lower()} has {sorted_players[0][0]} ({sorted_players[0][1]})"
        )

# FaceitStats().main()