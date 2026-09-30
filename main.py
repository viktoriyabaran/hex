import tkinter as tk

from agents.shortest_path_agent import ShortestPathAgent
from controller import Controller
from game import HexGame
from ui import HexUI

BOARD_SIZE = 11

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hex")

    game = HexGame(BOARD_SIZE)
    controller = Controller(game, {1: None, -1: ShortestPathAgent()})
    ui = HexUI(root, controller, BOARD_SIZE)
    controller.view = ui

    ui.redraw(game)
    controller.start()
    root.mainloop()