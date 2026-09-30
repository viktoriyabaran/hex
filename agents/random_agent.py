import random

from game import HexGame

from .agent import IAgent


class RandomAgent(IAgent):
    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        return random.choice(game.legal_moves())