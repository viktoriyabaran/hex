from agents.shortest_path_agent import distance_to_connect
from game import HexGame

WIN = 10000
INF  = float("inf")

def evaluate_game(game: HexGame, me: int) -> int:
    return distance_to_connect(game, -me) - distance_to_connect(game, me)

def minimax(game: HexGame, depth: int, me: int, alpha: int, beta: int) -> int:
    if game.winner != 0:
        return WIN + depth if game.winner == me else -WIN - depth
    if depth == 0:
        return evaluate_game(game, me)

    maximizing = game.current_player == me
    best = -INF if maximizing else INF

    for row, col in game.legal_moves():
        simulation = game.copy()
        simulation.play(row, col)

        score = minimax(simulation, depth-1, me, alpha, beta)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)

        if alpha >= beta:
            break

    return best
    

class AlphaBetaAgent:
    depth = 2

    def __init__(self, depth = 2):
        self.depth = depth

    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        best_score = -INF
        best_move = None

        for move in game.legal_moves():
            simulation = game.copy()
            simulation.play(*move)

            score = minimax(simulation, self.depth, game.current_player, best_score, INF)

            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
