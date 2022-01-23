import json
from xiangqi_game.game import Game
from xiangqi_game.data import alg_games as ag
from xiangqi_game.user_io.single_move import convert_alg_move_list

with open('../data/game_start.json') as game_info:
    game_config = json.load(game_info)

moves_d = convert_alg_move_list(ag.game_d)
game_d = Game(game_config, auto_moves=moves_d)
game_d.play_auto_moves()