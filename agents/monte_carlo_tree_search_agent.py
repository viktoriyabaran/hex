from agents.helpers.mcts_node import Node
from game import HexGame

from .agent import IAgent


class MCTSAgent(IAgent):
    iterations = 400

    def __init__(self, iter = 400):
        self.iterations = iter

    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        root = Node(game)

        for _ in range(self.iterations):
            node = root

            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child()

            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            winner = node.rollout()
            node.backpropagate(winner)

        best = max(root.children, key=lambda c: c.visits)
        return best.move

