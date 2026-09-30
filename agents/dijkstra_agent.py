import random
from heapq import heappop, heappush

from game import HexGame, neighbors

INF = float("inf")

# really the same logic with 0/1 BFS (shortest path agent) - just different ways to find the path

def distance_to_connect(game: HexGame, player: int) -> float:
    n = game.board_size
    dist = [[INF] * n for _ in range(n)]
    queue = []

    start_cells = (
        [(0, col) for col in range(n)]
        if player == 1
        else [(row, 0) for row in range(n)]
    )

    for row, col in start_cells:
        val = game.board[row][col]
        if val != -player:
            cost = 0 if val == player else 1
            dist[row][col] = cost
            heappush(queue, (cost, row, col))

    while queue:
        d, row, col = heappop(queue)
        if d != dist[row][col]:
            continue

        if (player == 1 and row == n - 1) or (player == -1 and col == n - 1):
            return d

        for nrow, ncol in neighbors(row, col, n):
            val = game.board[nrow][ncol]
            if val == -player:
                continue

            cost = 0 if val == player else 1
            new_dist = d + cost

            if new_dist < dist[nrow][ncol]:
                dist[nrow][ncol] = new_dist
                heappush(queue, (new_dist, nrow, ncol))

    return INF


class DijkstraAgent:
    def choose_next_move(self, game: HexGame) -> tuple[int, int]:
        current_player = game.current_player
        best_moves = []
        best_score = -INF

        for row, col in game.legal_moves():
            simulation = game.copy()
            simulation.play(row, col)
            if simulation.winner == current_player:
                return (row, col)

            score = distance_to_connect(
                simulation, -current_player
            ) - distance_to_connect(simulation, current_player)

            if score > best_score:
                best_moves = [(row, col)]
                best_score = score
            elif score == best_score:
                best_moves.append((row, col))

        return random.choice(best_moves)
