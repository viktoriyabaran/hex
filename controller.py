from agents.agent import IAgent
from status import Status


class Controller:
    AGENT_DELAY_MS = 300

    def __init__(self, game, agents: dict[int: IAgent()]):
        self.game = game
        self.agents = agents
        self.view = None

    def start(self):
        self.next_turn()

    def next_turn(self):
        if self.game.status != Status.FINISHED and self.agents[self.game.current_player] is not None:
            self.view.schedule(self.AGENT_DELAY_MS, self.agent_move)

    def on_hex_clicked(self, row, col):
        if self.game.status == Status.FINISHED:
            return
        
        if self.agents[self.game.current_player] is not None:
            return
        
        if self.game.board[row][col] != 0:
            return
        
        self.game.play(row, col)
        self.after_move()

    def after_move(self):
        self.view.redraw(self.game)
        self.next_turn()

    def agent_move(self):
        row, col = self.agents[self.game.current_player].choose_next_move(self.game)
        self.game.play(row, col)
        self.after_move()