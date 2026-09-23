from status import Status

NEIGHBOR_DIRECTIONS = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]

class HexGame:
    board_size: int
    board: list[list[int]]
    current_player: int
    status: Status
    winner: int

    def __init__(self, size, board = None, current_player = None):
        self.board_size = size
        self.board = board if board else empty_board(self.board_size)
        self.current_player = current_player if current_player else 1
        self.status = Status.NOT_STARTED
        self.winner = 0

    def legal_moves(self) -> list[tuple[int, int]]: # TODO: would be really much simpler in one-dim array
        legal_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0: legal_moves.append((i, j))
        return legal_moves
    
    def play(self, row: int, col: int ) -> None:
        if self.status == Status.FINISHED or self.board[row][col] != 0:
           raise ValueError("illegal move")
        
        self.status = Status.IN_PROGRESS
        self.board[row][col] = self.current_player
        if self.check_winner(self.current_player):
            self.status = Status.FINISHED
            self.winner = self.current_player
            return

        self.current_player = -self.current_player

    def check_winner(self, player):
        if player == 1:
            start = [(0, col) for col in range(self.board_size)]
        else:
            start = [(row, 0) for row in range(self.board_size)]

        stack = [cell for cell in start if self.board[cell[0]][cell[1]] == player]
        visited = set(stack)

        while stack:
            row, col = stack.pop()

            if (player == 1 and row == self.board_size - 1) or (player == -1 and col == self.board_size - 1):
                return True

            for nr, nc in neighbors(row, col, self.board_size):
                if (nr, nc) not in visited and self.board[nr][nc] == player:
                    visited.add((nr, nc))
                    stack.append((nr, nc))

        return False

    def copy(self) -> "HexGame":
       game = HexGame(self.board_size, [row[:] for row in self.board], self.current_player)
       game.status, game.winner = self.status, self.winner
       return game

def print_board(board: list[list[int]]) -> None:
    offset = 0
    n = len(board)
    for i in range(n):
        print(" " * offset, end="")
        for j in range(n):
            print(board[i][j], end=" ")
        print()
        offset += 2

def empty_board(size: int) -> list[list[int]]:
    return [[0] * size for _ in range(size)]

def neighbors(row, col, size):
    result = []
    for dr, dc in NEIGHBOR_DIRECTIONS:
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size:
            result.append((nr, nc))
    return result


if __name__ == "__main__":
    game = HexGame(3)
    game.play(0, 0) # player 1
    game.play(0, 1) # player -1
    game.play(1, 0) # player 1
    game.play(1, 1) # player -1
    game.play(2, 0) # player 1, column 0 is complete: top to bottom
    print_board(game.board)
    print(game.winner, game.status)