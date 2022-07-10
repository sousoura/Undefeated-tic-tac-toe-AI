from __future__ import print_function
# tag::play_against_your_bot[]
from dlgo import agent
from dlgo import goboard_slow as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move, point_from_coords
from six.moves import input
from dlgo.agent.naive import RandomBot
from dlgo.agent.smart_cirno import Smart_Cirno
from exhibitor import Exhibitor

from dlgo.gotypes import Point
from dlgo.goboard_slow import Move

"""
    解读：
        game对应棋盘
            其是一个GameState对象
            由GameState的类方法new_game()生成
            其储存
                一个棋盘 board
                落子者 next_player
                移动 last_move
            其存在以下方法：
                is_over(): 返回bool值 用于棋局是否结束
                apply_move(): 输入一个move变量 使棋盘引用move的变化
        程序运作逻辑
            程序通过给予move值 game运用move值的方式推进
            给予move值的可以是bot对象 也可以是人类的键盘输入
        move是一个动作 其可以是pass 落子 或 认输
"""


def main():
    # 人对机器 还是 机器对机器
    mode = "b v h"

    # 初始化 定义棋盘大小
    board_size = 3
    # 生成对应大小的棋盘 使用类内的方法生成
    game = goboard.GameState.new_game(board_size)

    """
        测试用
    """
    # game = game.apply_move(Move(Point(row=1, col=1)))
    # game = game.apply_move(Move(Point(row=1, col=2)))
    # game = game.apply_move(Move(Point(row=2, col=2)))
    # game = game.apply_move(Move(Point(row=3, col=2)))
    # game = game.apply_move(Move(Point(row=2, col=3)))
    # game = game.apply_move(Move(Point(row=2, col=1)))
    """
        测试用
    """

    # 前端展示器类
    exhibitor = Exhibitor(board_size, 50, mode)
    # 生成bot对象 可以接收一个棋盘作为输入 输出一个落子方案
    bot = Smart_Cirno()

    # 判断游戏是否结束 否则一直进行轮流落子
    while not game.is_over():
        move = None

        # 判断这一步由谁下
        if game.next_player == gotypes.Player.black:
            if mode == "h v b" or mode == "h v h":
                # 若由黑棋下 则人类玩家决定这一步下在哪
                # 人类玩家输入落子点 数据结构是两个字符
                point = exhibitor.display(game, gotypes.Player.black)
                if point == "pass":
                    move = Move(is_pass=True)
                else:
                    move = Move.play(point)
            elif mode == "b v b" or mode == "b v h":
                # 让机器人下这一步
                move, estimation = bot.select_move(game)
                exhibitor.display(game, gotypes.Player.black)
        else:
            if mode == "b v b" or mode == "h v b":
                # 给bot棋盘 bot生成一个动作
                move, estimation = bot.select_move(game)
                exhibitor.display(game, gotypes.Player.white)
            elif mode == "b v h" or mode == "h v h":
                # 人类玩家输入落子点 数据结构是两个字符
                point = exhibitor.display(game, gotypes.Player.white)
                if point == "pass":
                    move = Move(is_pass=True)
                else:
                    move = Move.play(point)
        # 打印 谁 下了哪步（或干了别的什么）
        print_move(game.next_player, move)
        # 将move交给game 应用变化
        game = game.apply_move(move)

    print(game.winner(), "win this game")


if __name__ == '__main__':
    main()
# end::play_against_your_bot[]
