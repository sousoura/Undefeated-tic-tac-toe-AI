# tag::scoring_imports[]
from __future__ import absolute_import
from collections import namedtuple

from dlgo.gotypes import Player, Point
# end::scoring_imports[]


# tag::scoring_game_result[]
class GameResult(namedtuple('GameResult', 'winner')):
    @property
    def get_winner(self):
        return self.winner

    def __str__(self):
        name = ""
        if self.winner == Player.black:
            name = "black"
        elif self.winner == Player.white:
            name = "white"
        else:
            name = "nobody"
        return name + " is winner"
# end::scoring_game_result[]


""" evaluate_territory:
Map a board into territory and dame.

Any points that are completely surrounded by a single color are
counted as territory; it makes no attempt to identify even
trivially dead groups.
"""


#
# tag::scoring_evaluate_territory[]
# 计算胜负
def evaluate_win(board):
    winner = None

    # 每行是不是连起来
    for r in range(1, board.num_rows + 1):
        is_link = True
        for c in range(2, board.num_cols + 1):
            if board.get(Point(row=r, col=c)) is None:
                is_link = False
            if board.get(Point(row=r, col=c)) != board.get(Point(row=r, col=c - 1)):
                is_link = False
        if is_link:
            winner = board.get(Point(row=r, col=1))
            return winner

    # 每列是不是连起来
    for c in range(1, board.num_cols + 1):
        is_link = True
        for r in range(2, board.num_rows + 1):
            if board.get(Point(row=r, col=c)) is None:
                is_link = False
            if board.get(Point(row=r, col=c)) != board.get(Point(row=r - 1, col=c)):
                is_link = False
        if is_link:
            winner = board.get(Point(row=1, col=c))
            return winner

    # 撇是不是连起来
    is_link = True
    for c in range(2, board.num_cols + 1):
        if board.get(Point(row=c, col=c)) is None:
            is_link = False
        if board.get(Point(row=c, col=c)) != board.get(Point(row=c - 1, col=c - 1)):
            is_link = False
    if is_link:
        winner = board.get(Point(row=1, col=1))
        return winner

    # 捺是不是连起来
    is_link = True
    for c in range(2, board.num_cols + 1):
        if board.get(Point(row=c, col=board.num_rows + 1 - c)) is None:
            is_link = False
        if board.get(Point(row=c, col=board.num_rows + 1 - c)) != board.get(Point(row=c - 1, col=board.num_rows - c + 2)):
            is_link = False
    if is_link:
        winner = board.get(Point(row=1, col=board.num_rows))
        return winner

    return winner


# 计算赢家
# tag::scoring_compute_game_result[]
def compute_game_result(game_state):
    # 判断有没有连星
    winner = evaluate_win(game_state.board)
    return GameResult(winner)
# end::scoring_compute_game_result[]
