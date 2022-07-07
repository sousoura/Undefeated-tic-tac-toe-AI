# tag::randombotimports[]
import random
from dlgo.agent.base import Agent
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point
# end::randombotimports[]


# 该py文件仅出口RandomBot这一个元素
__all__ = ['RandomBot']


# 随机机器人
# tag::random_bot[]
class RandomBot(Agent):
    # 随机机器人没有记忆 其唯一的方法就是输入一个棋盘状态 然后它返回一个动作（move落子点或pass）作为方案
    def select_move(self, game_state):
        """Choose a random valid move that preserves our own eyes."""
        # 候选者落子点数组
        candidates = []
        # 遍历棋盘的每一个点
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                # 该点的point数据结构
                candidate = Point(row=r, col=c)
                # 判断该落子点对于该阵营是否合法
                if game_state.is_valid_move(Move.play(candidate)):
                    # 若合法 则假如到数组中
                    candidates.append(candidate)
        # 若不存在一个合法的落子点 即候选数组为空
        if not candidates:
            # 返回pass
            return Move.pass_turn()
        # 若不不存在一个合法的落子点 则从合法的落子点中随机选择一个
        return Move.play(random.choice(candidates))
# end::random_bot[]
