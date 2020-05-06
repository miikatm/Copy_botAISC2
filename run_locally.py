import json
import random

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Human, Bot, Computer

from bot import MyBot
from examples.worker_rush import WorkerRushBot

def main():
    with open("botinfo.json") as f:
        info = json.load(f)

    race = Race[info["race"]]

    lista_kartoista = ["(2)DreamcatcherLE", "(2)RedshiftLE", "AcolyteLE", "AbyssalReefLE"]
    random_kartta = random.choice(lista_kartoista)

    run_game(maps.get(random_kartta), [
        #Human(Race.Terran),
        Bot(race, MyBot()),
        Computer(Race.Random, Difficulty.VeryHard)
        #Bot(race, WorkerRushBot())
    ], realtime=False, step_time_limit=2.0, game_time_limit=(60*20), save_replay_as="test.SC2Replay")
    #], realtime=True, save_replay_as="test.SC2Replay")

if __name__ == '__main__':
    main()
