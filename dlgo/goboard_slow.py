import numpy as np
# tag::imports[]
import copy
from dlgo.gotypes import Player
# end::imports[]
from dlgo.gotypes import Point
from dlgo.scoring import compute_game_result
from dlgo.scoring import evaluate_win

__all__ = [
    'Board',
    'GameState',
    'Move',
]

"""
    解读：
        定义了三个类的数据结构
            GameState是游戏本身 也即游戏的管理者和统筹者
                其储存一个棋盘Board对象 作为棋盘状况
                    棋盘维护一个字典
                        键-棋子位置：值-所属棋块
                每回合其接收一个Move作为行动 以更新棋盘
        其中 GoString用于构成棋盘
            棋盘由一个个子组成
                每个子都被标记了属于特定棋块
                这样或许方便ai进行分析
                所属棋块相当于身份 同一棋块的子会被统一对待
            棋块储存
                阵营
                所有子的位置
                气的数量和位置
        棋块和棋盘的棋子字典是冗余的
            旧的棋块依然存在
            棋盘字典才是棋盘状况的根本依据
"""


class IllegalMoveError(Exception):
    pass


# 棋块的数据结构 棋块具有阵营属性 棋块中包含有很多子
# tag::strings[]
class GoString():  # <1>
    def __init__(self, color, stones, liberties):
        # 棋块颜色
        self.color = color
        # 棋子集（一堆point）
        self.stones = set(stones)
        # 气的数量和位置
        self.liberties = set(liberties)

    # 被紧一口气 将气的位置去掉
    def remove_liberty(self, point):
        self.liberties.remove(point)

    # 添一口气 应该是被提子了
    def add_liberty(self, point):
        self.liberties.add(point)

    # 相连棋块合并
    def merged_with(self, go_string):  # <2>
        # 检查双方是否是同一阵营
        assert go_string.color == self.color
        # 集合取并集
        combined_stones = self.stones | go_string.stones
        # 返回一个船新的棋块 旧的依然存在（可能这就是冗余的原因 处理棋块很潇洒 没必要删了旧的）
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

    # 计算还有几口气
    @property
    def num_liberties(self):
        return len(self.liberties)

    # 棋块相等判断接口 一旦各个参数吻合 则相同
    def __eq__(self, other):
        return isinstance(other, GoString) and \
               self.color == other.color and \
               self.stones == other.stones and \
               self.liberties == other.liberties


# <1> Go strings are stones that are linked by a chain of connected stones of the same color.
# <2> Return a new Go string containing all stones in both strings.
# end::strings[]


# 棋盘 数据结构对象 储存了棋盘的大小和一个不知道干嘛用和怎么用的_grid
# tag::board_init[]
class Board():  # <1>
    def __init__(self, num_rows, num_cols):
        # 基本参数 行列
        self.num_rows = num_rows
        self.num_cols = num_cols
        # 棋块的集合 键是棋块中的每个点 值是棋块对象
        self._grid = {}

    # <1> A board is initialized as empty grid with the specified number of rows and columns.
    # end::board_init[]

    # 更新棋盘用的 输入阵营和落子点 在那个点上加上那个字 然后刷新棋块状态
    # 棋块方法的理解入口
    # tag::board_place_0[]
    def place_stone(self, player, point):
        # assert用于错误检查 若变量为False则报错
        # 此处显然是在判断point是否在棋盘内 是否合法
        assert self.is_on_grid(point)
        # 此处显然是在point的点上是不是已经有子了 如果已经有子了 则不能在此处落子
        assert self.get(point) is None

        self._grid[point] = player

    # 判断一个落子点是否出界
    # tag::board_utils[]
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
               1 <= point.col <= self.num_cols

    # 判断一个落子点上是否有子 若有 是什么阵营的
    def get(self, point):  # <1>
        stone = self._grid.get(point)
        return stone

    # <1> Returns the content of a point on the board:  a Player if there is a stone on that point or else None.
    # <2> Returns the entire string of stones at a point: a GoString if there is a stone on that point or else None.
    # end::board_utils[]

    # 判断一个棋块是不是和另一个一样
    def __eq__(self, other):
        return isinstance(other, Board) and \
               self.num_rows == other.num_rows and \
               self.num_cols == other.num_cols and \
               self._grid == other._grid


# 数据结构 动作 交给棋盘处理的数据结构 具有落子 pass 和 认输 三个互斥状态
# tag::moves[]
class Move():  # <1>
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # 用于得到落子动作的数据结构 输入一个point数据结构 输出一个point状态的move
    @classmethod
    def play(cls, point):  # <2>
        return Move(point=point)

    # 用于得到pass动作的数据结构
    @classmethod
    def pass_turn(cls):  # <3>
        return Move(is_pass=True)

    # 用于得到认输动作的数据结构
    @classmethod
    def resign(cls):  # <4>
        return Move(is_resign=True)


# <1> Any action a player can play on a turn, either is_play, is_pass or is_resign will be set.
# <2> This move places a stone on the board.
# <3> This move passes.
# <4> This move resigns the current game
# end::moves[]


# 棋盘 储存棋盘状态 储存落子顺序 处理move和更新棋盘
# tag::game_state[]
class GameState():
    def __init__(self, board, next_player, previous, move):
        # 棋盘状态
        self.board = board
        # 落子顺序
        self.next_player = next_player
        # 储存前一状态 用链的形式储存棋谱（状态） 也就是上一个自己
        self.previous_state = previous
        # 储存上一move
        self.last_move = move

    # 以move更新棋盘
    def apply_move(self, move):  # <1>
        # 创建一个next_board变量 作为下一个状态的棋盘
        if move.is_play:
            # 如果落子了 就把落子点加上
            # 深复制棋盘 加上新子
            next_board = copy.deepcopy(self.board)
            # 注意place_stone这个方法 落子更新棋块 使得棋盘变成船新的棋盘
            next_board.place_stone(self.next_player, move.point)
        else:
            # 如果没落子 就棋盘原封不动
            next_board = self.board
        # 返回下一个状态 注意返回了一个新的GameState对象
        return GameState(next_board, self.next_player.other, self, move)

    # 生成一个初始状态 自己生成自己的类方法
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    @property
    def situation(self):
        return (self.next_player, self.board)

    # end::is_ko[]

    # 判断一个落子点是否合法
    # tag::is_valid_move[]
    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return self.board.get(move.point) is None

    # end::is_valid_move[]
    # 如果连续两次pass 则结束
    # tag::is_over[]
    def is_over(self):
        # 如果处于刚开始的时候 就没结束
        if self.last_move is None:
            return False
        # 如果上一步是一个人认输 就结束
        if self.last_move.is_resign:
            return True
        # 取上上一步
        second_last_move = self.previous_state.last_move
        # 如果处于刚开始的时候 就没结束
        if second_last_move is None:
            return False
        if evaluate_win(self.board) is not None:
            return True
        # 如果连续两次pass 则结束
        return self.last_move.is_pass and second_last_move.is_pass

    # 返回所有合法落子点的move
    # end::is_over[]
    def legal_moves(self):
        moves = []

        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    # 判断谁是赢家
    def winner(self):
        # 如果游戏没有结束 就还没有赢家
        if not self.is_over():
            return None
        # 如果上一步有人投降 则下一步的是赢家
        if self.last_move.is_resign:
            return self.next_player
        # 算点
        game_result = compute_game_result(self)
        return game_result
