# -*- coding: utf-8 -*-
from player import Player
from direct.showbase.ShowBase import ShowBase

class Main(ShowBase):
    def __init__(self):
        # self.player = Player(0, 1)
        
        #
        # initialize game content
        #
        self.player = Player(1, 1, "p1")
        self.player2 = Player(2, 2, "p2")

        # self.player.start((0, 8, -0.5))
    
    def enterGame(self):
        # main game code should be called here
        self.player.start((-1, 8, -0.5))
        self.player2.start((1, 8, -0.5))


app = Main()
app.run()