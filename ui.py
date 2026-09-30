import math
import tkinter as tk
from tkinter import ttk

from game import HexGame
from controller import Controller

from agents.random_agent import RandomAgent
from agents.shortest_path_agent import ShortestPathAgent
from agents.minimax_agent import MinimaxAgent
from agents.alpha_beta_agent import AlphaBetaAgent
from agents.mcts_agent import MCTSAgent

COLORS = {0: "#ECEAE4", 1: "#D9463E", -1: "#2F6FB5"}
NAMES = {1: "Red", -1: "Blue"}
OUTLINE = "#8A877F"
MUTED = "#6B6860"
MARGIN = 45

BOARD_SIZES = [5, 7, 9, 11]
PLAYER_TYPES = ["User", "Random", "Shortest path", "Minimax", "Alpha-beta", "MCTS"]

MAX_DEPTH = {
    "Minimax":    {5: 2, 7: 1, 9: 1, 11: 1},
    "Alpha-beta": {5: 3, 7: 3, 9: 2, 11: 1},
}
MCTS_ITERATIONS = [500, 1000, 2000, 5000, 10000]
DEFAULT_ITERATIONS = "2000"


def make_agent(kind: str, param):
    if kind == "User":
        return None
    if kind == "Random":
        return RandomAgent()
    if kind == "Shortest path":
        return ShortestPathAgent()
    if kind == "Minimax":
        return MinimaxAgent(param)
    if kind == "Alpha-beta":
        return AlphaBetaAgent(param)
    if kind == "MCTS":
        return MCTSAgent(param)
    raise ValueError(f"unknown player type: {kind}")


def describe(kind: str, param) -> str:
    if kind in MAX_DEPTH:
        return f"{kind}, depth {param}"
    if kind == "MCTS":
        return f"MCTS, {param} iterations"
    return kind


class PlayerPanel(ttk.Frame):
    """Player type + its parameter (depth or iterations) for one side."""

    def __init__(self, parent, player: int, board_size: tk.IntVar):
        super().__init__(parent, padding=(0, 8, 24, 8))
        self.board_size = board_size

        tk.Label(self, text=NAMES[player], fg=COLORS[player],
                 font=("Helvetica", 17, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        goal = "Connects top and bottom" if player == 1 else "Connects left and right"
        tk.Label(self, text=goal, fg=MUTED).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(self, text="Player").grid(row=2, column=0, sticky="w")
        self.kind = tk.StringVar(value="User" if player == 1 else "MCTS")
        ttk.Combobox(self, textvariable=self.kind, values=PLAYER_TYPES,
                     state="readonly", width=14).grid(row=2, column=1, sticky="ew", padx=(10, 0))

        self.param_label = ttk.Label(self)
        self.param_label.grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.param = tk.StringVar()
        self.param_box = ttk.Combobox(self, textvariable=self.param, state="readonly", width=14)
        self.param_box.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(8, 0))

        self.kind.trace_add("write", lambda *_: self.refresh())
        board_size.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def refresh(self):
        kind = self.kind.get()
        if kind in MAX_DEPTH:
            max_depth = MAX_DEPTH[kind][self.board_size.get()]
            options = [str(d) for d in range(1, max_depth + 1)]
            default = options[-1]
            self.param_label.config(text="Depth")
        elif kind == "MCTS":
            options = [str(i) for i in MCTS_ITERATIONS]
            default = DEFAULT_ITERATIONS
            self.param_label.config(text="Iterations")
        else:
            self.param_label.grid_remove()
            self.param_box.grid_remove()
            return

        self.param_label.grid()
        self.param_box.grid()
        self.param_box.config(values=options)
        if self.param.get() not in options:   # e.g. depth too big for new board size
            self.param.set(default)

    def value(self) -> tuple[str, int | None]:
        kind = self.kind.get()
        param = int(self.param.get()) if kind in MAX_DEPTH or kind == "MCTS" else None
        return kind, param


class SetupScreen(ttk.Frame):
    def __init__(self, parent, on_start):
        super().__init__(parent, padding=28)
        self.on_start = on_start

        tk.Label(self, text="Hex", font=("Helvetica", 30, "bold")).pack(anchor="w")
        tk.Label(self, text="Choose who plays each side.", fg=MUTED).pack(anchor="w", pady=(0, 16))

        row = ttk.Frame(self)
        row.pack(anchor="w", pady=(0, 8))
        ttk.Label(row, text="Board size").pack(side="left")
        self.size = tk.IntVar(value=7)
        ttk.Combobox(row, textvariable=self.size, values=BOARD_SIZES,
                     state="readonly", width=5).pack(side="left", padx=10)

        sides = ttk.Frame(self)
        sides.pack(anchor="w", pady=8)
        self.panels = {p: PlayerPanel(sides, p, self.size) for p in (1, -1)}
        self.panels[1].pack(side="left", anchor="n")
        self.panels[-1].pack(side="left", anchor="n")

        tk.Label(self, text="Red moves first.", fg=MUTED).pack(anchor="w", pady=(8, 0))
        ttk.Button(self, text="Start game", command=self._start).pack(anchor="e", pady=(16, 0))

    def _start(self):
        self.on_start({
            "size": self.size.get(),
            "players": {p: panel.value() for p, panel in self.panels.items()},
        })

class GameScreen(ttk.Frame):
    """Draws the board. Implements the view interface: redraw(game), schedule(ms, fn)."""

    def __init__(self, parent, controller, size, labels, is_agent, on_game_over):
        super().__init__(parent, padding=(16, 12))
        self.controller = controller
        self.size = size
        self.is_agent = is_agent
        self.on_game_over = on_game_over
        self.radius = max(18, min(30, 200 // size))   # smaller hexagons on bigger boards
        self.cell_ids = {}
        self.pending = set()
        self.game_over_reported = False

        header = ttk.Frame(self)
        header.pack(pady=(0, 4))
        tk.Label(header, text=f"Red: {labels[1]}", fg=COLORS[1]).pack(side="left", padx=10)
        tk.Label(header, text=f"Blue: {labels[-1]}", fg=COLORS[-1]).pack(side="left", padx=10)

        w = math.sqrt(3) * self.radius
        width = 2 * MARGIN + w * size + w * (size - 1) / 2
        height = 2 * MARGIN + 1.5 * self.radius * (size - 1) + 2 * self.radius
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.status = tk.Label(self, font=("Helvetica", 15), pady=8)
        self.status.pack()

        self._draw_edges()
        self._draw_cells()

    # ---- geometry -------------------------------------------------------

    def _center(self, row, col):
        w = math.sqrt(3) * self.radius
        return (MARGIN + w / 2 + col * w + row * w / 2,
                MARGIN + self.radius + row * 1.5 * self.radius)

    def _corners(self, x, y):
        points = []
        for i in range(6):
            a = math.radians(60 * i - 30)
            points += [x + self.radius * math.cos(a), y + self.radius * math.sin(a)]
        return points

    # ---- drawing --------------------------------------------------------

    def _draw_cells(self):
        for row in range(self.size):
            for col in range(self.size):
                cell = self.canvas.create_polygon(
                    self._corners(*self._center(row, col)), fill=COLORS[0], outline=OUTLINE)
                self.canvas.tag_bind(cell, "<Button-1>",
                                     lambda e, r=row, c=col: self.controller.on_hex_clicked(r, c))
                self.cell_ids[(row, col)] = cell

    def _draw_edges(self):
        n, gap, thick = self.size - 1, self.radius + 10, 6
        (x0, y0), (x1, _) = self._center(0, 0), self._center(0, n)
        (x2, y2), (x3, _) = self._center(n, 0), self._center(n, n)
        side = math.sqrt(3) * self.radius / 2 + 10
        self.canvas.create_line(x0, y0 - gap, x1, y0 - gap, fill=COLORS[1], width=thick)
        self.canvas.create_line(x2, y2 + gap, x3, y2 + gap, fill=COLORS[1], width=thick)
        self.canvas.create_line(x0 - side, y0, x2 - side, y2, fill=COLORS[-1], width=thick)
        self.canvas.create_line(x1 + side, y0, x3 + side, y2, fill=COLORS[-1], width=thick)

    def redraw(self, game):
        for (row, col), cell in self.cell_ids.items():
            self.canvas.itemconfig(cell, fill=COLORS[game.board[row][col]])

        if game.winner != 0:
            self.status.config(text=f"{NAMES[game.winner]} wins")
            if not self.game_over_reported:
                self.game_over_reported = True
                self.schedule(400, lambda: self.on_game_over(game.winner))  # let the last move show
        elif self.is_agent[game.current_player]:
            self.status.config(text=f"{NAMES[game.current_player]} is thinking…")
        else:
            self.status.config(text=f"{NAMES[game.current_player]}'s turn")
        self.update_idletasks()

    def schedule(self, delay_ms, callback):
        def run():
            self.pending.discard(job)
            callback()
        job = self.after(delay_ms, run)
        self.pending.add(job)

    def destroy(self):
        for job in self.pending:
            self.after_cancel(job)
        self.pending.clear()
        super().destroy()


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Hex")
        root.resizable(False, False)
        self.settings = None
        self.game_screen = None
        self.setup = SetupScreen(root, self.start_game)
        self.show_setup()

    def show_setup(self):
        self._close_game()
        self.setup.pack()

    def start_game(self, settings=None):
        if settings is not None:
            self.settings = settings
        self._close_game()
        self.setup.pack_forget()

        size, players = self.settings["size"], self.settings["players"]
        game = HexGame(size)
        agents = {p: make_agent(*players[p]) for p in (1, -1)}
        controller = Controller(game, agents)

        self.game_screen = GameScreen(
            self.root, controller, size,
            labels={p: describe(*players[p]) for p in (1, -1)},
            is_agent={p: agents[p] is not None for p in (1, -1)},
            on_game_over=self.show_result,
        )
        self.game_screen.pack()
        controller.view = self.game_screen
        self.game_screen.redraw(game)
        controller.start()

    def _close_game(self):
        if self.game_screen is not None:
            self.game_screen.destroy()
            self.game_screen = None

    def show_result(self, winner: int):
        modal = tk.Toplevel(self.root)
        modal.title("Game over")
        modal.transient(self.root)
        modal.resizable(False, False)

        body = ttk.Frame(modal, padding=28)
        body.pack()
        tk.Label(body, text=f"{NAMES[winner]} wins", fg=COLORS[winner],
                 font=("Helvetica", 24, "bold")).pack()
        tk.Label(body, text=describe(*self.settings["players"][winner]), fg=MUTED).pack(pady=(4, 20))

        def close_then(action):
            modal.grab_release()
            modal.destroy()
            action()

        buttons = ttk.Frame(body)
        buttons.pack()
        ttk.Button(buttons, text="Try again",
                   command=lambda: close_then(self.start_game)).pack(side="left", padx=4)
        ttk.Button(buttons, text="Change players",
                   command=lambda: close_then(self.show_setup)).pack(side="left", padx=4)
        modal.protocol("WM_DELETE_WINDOW", lambda: close_then(self.show_setup))

        modal.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - modal.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - modal.winfo_height()) // 3
        modal.geometry(f"+{x}+{y}")
        try:
            modal.grab_set()
        except tk.TclError:
            pass