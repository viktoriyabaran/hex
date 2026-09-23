from abc import ABC, abstractmethod

from game import HexGame


class IAgent(ABC):

    @abstractmethod
    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        pass
