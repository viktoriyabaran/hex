from agents.agent import IAgent
from status import Status


class Controller:
    def __init__(self, game, agents: dict[int: IAgent()]):
        self.game = game
        self.agents = agents

    def on_hex_clicked(self, row, col):
        if self.agents[self.game.current_player] is not None:
            return
        self.game.play(row, col)
        self.after_move()

    def after_move(self):
        if self.game.status == Status.FINISHED:
            return
        
        agent = self.agents[self.game.current_player]
        if agent is not None:
            row, col = agent.choose_move(self.game)
            self.game.play(row, col)
            self.after_move()