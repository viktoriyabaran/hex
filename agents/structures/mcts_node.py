import math
import random


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

    def best_child(self, c=1.4):
        def ucb(child):
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)

    def rollout(self):
        simulation = self.game.copy()

        while True:
            winner = simulation.winner
            if winner != 0:
                return winner
            
            moves = simulation.legal_moves()
            if not moves:
                return None
            
            move = random.choice(moves)
            simulation.play(*move)

    def backpropagate(self, winner):
        self.visits += 1

        if winner == self.player_moved:
            self.wins += 1.0

        if self.parent:
            self.parent.backpropagate(winner)