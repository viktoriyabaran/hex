import math
import random

from game import HexGame


class Node:
    def __init__(self, game, move=None, parent=None):
        self.game = game # state
        self.move = move # move that led to the state we have now
        self.parent = parent
        self.children = []
        self.untried = game.legal_moves()
        self.player_moved = parent.game.current_player if parent else -game.current_player # who made that move
        self.visits = 0
        self.wins = 0
        # AMAF optimisation ("all moves as first")
        # this stats playouts where this move's cell ended up with this player's color at any point
        self.amaf_visits = 0
        self.amaf_wins = 0

    def is_terminal(self):
        return self.game.winner != 0 or not self.game.legal_moves()

    def is_fully_expanded(self):
        return len(self.untried) == 0

    def expand(self):
        move = self.untried.pop()
        simulation = self.game.copy()

        simulation.play(*move)

        child = Node(simulation, move, self)
        self.children.append(child)
        return child

    def best_child(self, c=1.4, k=500):
        def ucb(child):
            beta = math.sqrt(k / (3 * child.visits + k))
            real = child.wins / child.visits
            amaf = child.amaf_wins / child.amaf_visits # never 0: a child's own playouts count for AMAF too
            exploit = (1 - beta) * real + beta * amaf
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)

    def rollout(self):
        board = [row[:] for row in self.game.board]
        if self.game.winner != 0:
            return self.game.winner, board

        empty = [(r, c) for r in range(len(board)) for c in range(len(board)) if board[r][c] == 0]
        random.shuffle(empty)
        player = self.game.current_player
        for r, c in empty:
            board[r][c] = player
            player = -player

        sim = HexGame(len(board), board)
        return (1 if sim.check_winner(1) else -1), board

    def backpropagate(self, winner, board):
        self.visits += 1

        if winner == self.player_moved:
            self.wins += 1.0

        for child in self.children:
            row, col = child.move
            if board[row][col] == child.player_moved:
                child.amaf_visits += 1
                if winner == child.player_moved:
                    child.amaf_wins += 1.0

        if self.parent:
            self.parent.backpropagate(winner, board)