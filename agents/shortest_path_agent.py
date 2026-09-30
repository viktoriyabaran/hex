import random
from collections import deque

from game import HexGame, neighbors

INF  = float("inf")

# bridge is a cell two steps away that shares two empty neighbors
# they're a good way to win

BRIDGES = [
    ((-2, 1), (-1, 0), (-1, 1)),
    ((-1, 2), (-1, 1), (0, 1)),
    ((1, 1), (0, 1), (1, 0)),
    ((2, -1), (1, 0), (1, -1)),
    ((1, -2), (1, -1), (0, -1)),
    ((-1, -1), (0, -1), (-1, 0)),
]

def bridges(board, row, col, size):
    result = []
    for (dr, dc), (ar, ac), (br, bc) in BRIDGES:
        nr, nc = row + dr, col + dc
        if not (0 <= nr < size and 0 <= nc < size):
            continue
        if board[row + ar][col + ac] == 0 and board[row + br][col + bc] == 0:
            result.append((nr, nc))
    return result

def distance_to_connect(game: HexGame, player: int) -> float:
    n = game.board_size
    dist = [[INF] * n for _ in range(n)]
    queue = deque()

    start_cells = (
        [(0, col) for col in range(n)] if player == 1 else [(row, 0) for row in range(n)]
    )

    for row, col in start_cells:
        val = game.board[row][col]
        if val != -player:
            cost = 0 if val == player else 1
            dist[row][col] = cost
            if cost == 0:
                queue.appendleft((row, col))
            else:
                queue.append((row, col))

    while queue:
        row, col = queue.popleft()
        d = dist[row][col]

        if (player == 1 and row == n - 1) or (player == -1 and col == n - 1):
            return d

        for nrow, ncol in neighbors(row, col, n) + bridges(game.board, row, col, n):
            val = game.board[nrow][ncol]
            if val == -player:
                continue

            cost = 0 if val == player else 1
            new_dist = d + cost

            if new_dist < dist[nrow][ncol]:
                dist[nrow][ncol] = new_dist
                if cost == 0:
                    queue.appendleft((nrow, ncol))
                else:
                    queue.append((nrow, ncol))

    return INF

class ShortestPathAgent:
    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        current_player = game.current_player
        best_moves =  []
        best_score = -INF

        for row, col in game.legal_moves():
            simulation = game.copy()
            simulation.play(row, col)
            if simulation.winner == current_player:
                return (row, col)

            score = distance_to_connect(simulation, -current_player) - distance_to_connect(simulation, current_player)

            if score > best_score:
                best_moves = [(row, col)]
                best_score = score
            elif score == best_score:
                best_moves.append((row, col))

        return random.choice(best_moves)
