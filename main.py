import tkinter as tk

from agents.alpha_beta_agent import AlphaBetaAgent
from controller import Controller
from game import HexGame
from ui import HexUI

BOARD_SIZE = 7

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hex")

    game = HexGame(BOARD_SIZE)
    controller = Controller(game, {1: AlphaBetaAgent(3), -1: AlphaBetaAgent(4)})
    ui = HexUI(root, controller, BOARD_SIZE)
    controller.view = ui

    ui.redraw(game)
    controller.start()
    root.mainloop()