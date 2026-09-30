from agents.structures.mcts_node import Node
from game import HexGame

from .agent import IAgent


# returns a cell where `player` wins right away, or None
def find_winning_move(game: HexGame, player: int) -> tuple[int, int] | None:
    simulation = game.copy()
    for row, col in game.legal_moves():
        simulation.board[row][col] = player
        if simulation.check_winner(player):
            return (row, col)
        simulation.board[row][col] = 0
    return None


class MCTSAgent(IAgent):
    iterations = 400

    def __init__(self, iter = 400):
        self.iterations = iter

    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        me = game.current_player
        move = find_winning_move(game, me) or find_winning_move(game, -me)
        if move:
            return move

        root = Node(game)

        for _ in range(self.iterations):
            node = root

            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child()

            if not node.is_terminal() and not node.is_fully_expanded():
                node = node.expand()

            winner, board = node.rollout()
            node.backpropagate(winner, board)

        best = max(root.children, key=lambda c: c.visits)
        return best.move

