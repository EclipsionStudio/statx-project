import requests
import re
import json
from decouple import config


class FaceitStats:
    @staticmethod
    def get_player_id(nickname):
        url = f"https://open.faceit.com/data/v4/players?nickname={nickname}"
        headers = {"Authorization": f"Bearer {config("FACEIT_API_SERVER")}"}
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json().get("player_id")
        else:
            print(f"Error when getting player ID: {response.json()}")
            return None

    @staticmethod
    def get_player_stats(player_id):
        url = f"https://open.faceit.com/data/v4/players/{player_id}/stats/cs2"
        headers = {"Authorization": f"Bearer {config("FACEIT_API_SERVER")}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error when retrieving statistics: {response.json()}")
            return None

    @staticmethod
    def find_best_match(query, expressions):
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {config("DEEPSEEK_API")}"},
            data=json.dumps(
                {
                    "model": config("MODEL"),
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Choose which of the following expressions is behind the user query. Query: {query}. Expressions: {', '.join(expressions)}. Return ONLY the expression itself as the answer.",
                        }
                    ],
                    "max_tokens": 10000,
                }
            ),
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]

    @staticmethod
    def rebuilding(changeable):
        result = [{"": {}}]
        line = -1
        for key, value in changeable.items():
            line += 1
            if line in [0, 1]:
                result[0][""][key] = value
            elif line == 2:
                for lifetime_key, lifetime_value in value.items():
                    result[0][""][lifetime_key] = lifetime_value
            else:
                for i, map in enumerate(value):
                    result.append({map["label"]: {}})
                    for stats_key, stats_value in map["stats"].items():
                        result[i + 1][map["label"]][stats_key] = stats_value
        return result
    
    @staticmethod
    def make_expressions(changeable):
        result = []
        for map in changeable:
            map_name = "" if next(iter(map)) == "" else next(iter(map))
            for key in map[map_name].keys():
                result.append(f"{map_name} {key}".strip())
        return result

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

    @staticmethod
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


if __name__ == "__main__":
    FaceitStats().main()
