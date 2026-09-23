import math
import tkinter as tk

from status import Status  # adjust to your package layout

# Player colors: 1 connects top <-> bottom, -1 connects left <-> right
COLORS = {0: "#ECEAE4", 1: "#D9463E", -1: "#2F6FB5"}
NAMES = {1: "Red", -1: "Blue"}
OUTLINE = "#8A877F"
HEX_RADIUS = 28   # center to corner, in pixels
MARGIN = 50


class HexUI:
    def __init__(self, root: tk.Tk, controller, size: int):
        self.root = root
        self.controller = controller
        self.size = size
        self.cell_ids = {}   # (row, col) -> canvas polygon id

        w = math.sqrt(3) * HEX_RADIUS
        width = 2 * MARGIN + w * size + w * (size - 1) / 2
        height = 2 * MARGIN + 1.5 * HEX_RADIUS * (size - 1) + 2 * HEX_RADIUS

        self.canvas = tk.Canvas(root, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.status_label = tk.Label(root, font=("Helvetica", 14), pady=10)
        self.status_label.pack()

        self._draw_edges()
        self._draw_cells()

    # ---- geometry -------------------------------------------------------

    def _center(self, row: int, col: int) -> tuple[float, float]:
        w = math.sqrt(3) * HEX_RADIUS
        x = MARGIN + w / 2 + col * w + row * w / 2   # the half-cell shift per row
        y = MARGIN + HEX_RADIUS + row * 1.5 * HEX_RADIUS
        return x, y

    def _corners(self, x: float, y: float) -> list[float]:
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)   # pointy-top hexagon
            points += [x + HEX_RADIUS * math.cos(angle), y + HEX_RADIUS * math.sin(angle)]
        return points

    # ---- drawing --------------------------------------------------------

    def _draw_cells(self):
        for row in range(self.size):
            for col in range(self.size):
                x, y = self._center(row, col)
                cell_id = self.canvas.create_polygon(
                    self._corners(x, y), fill=COLORS[0], outline=OUTLINE, width=1
                )
                # the "React-style" click handler: each hexagon knows its (row, col)
                self.canvas.tag_bind(
                    cell_id, "<Button-1>",
                    lambda e, r=row, c=col: self.controller.on_hex_clicked(r, c)
                )
                self.cell_ids[(row, col)] = cell_id

    def _draw_edges(self):
        """Colored bars showing which edges each player must connect."""
        n, gap, thick = self.size - 1, HEX_RADIUS + 10, 6
        (x0, y0), (x1, _) = self._center(0, 0), self._center(0, n)
        (x2, y2), (x3, _) = self._center(n, 0), self._center(n, n)
        w = math.sqrt(3) * HEX_RADIUS / 2 + 10

        self.canvas.create_line(x0, y0 - gap, x1, y0 - gap, fill=COLORS[1], width=thick)   # top
        self.canvas.create_line(x2, y2 + gap, x3, y2 + gap, fill=COLORS[1], width=thick)   # bottom
        self.canvas.create_line(x0 - w, y0, x2 - w, y2, fill=COLORS[-1], width=thick)      # left
        self.canvas.create_line(x1 + w, y0, x3 + w, y2, fill=COLORS[-1], width=thick)      # right

    # ---- called by the controller --------------------------------------

    def redraw(self, game):
        for (row, col), cell_id in self.cell_ids.items():
            self.canvas.itemconfig(cell_id, fill=COLORS[game.board[row][col]])

        if game.status == Status.FINISHED:
            self.status_label.config(text=f"{NAMES[game.winner]} wins")
        else:
            self.status_label.config(text=f"{NAMES[game.current_player]}'s turn")

    def schedule(self, delay_ms: int, callback):
        self.root.after(delay_ms, callback)