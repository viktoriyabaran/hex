import random

from .agent import IAgent

from game import HexGame


class RandomAgent(IAgent):
    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        return random.choice(game.legal_moves())