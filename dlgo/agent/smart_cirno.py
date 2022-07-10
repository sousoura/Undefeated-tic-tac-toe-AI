"""
    程序最重要的是完成select_move函数
    该函数读入一个状态 并根据状态返回一个认为最佳的move
"""

import random
from dlgo.agent.base import Agent
from dlgo.goboard_slow import Move
from dlgo.gotypes import Point
from dlgo.scoring import evaluate_win
from dlgo.gotypes import Player


class Smart_Cirno(Agent):
    # 琪露诺的完美井字棋教室
    def select_move(self, game_state):
        candidates = self.find_candidate_action(game_state)
        # 若不存在一个合法的落子点 即候选数组为空
        if not candidates:
            # 返回pass
            return Move.pass_turn(), None

        action, estimation = self.thinking_action(game_state, game_state.next_player, None)
        return action, estimation

    # 若存在一个合法的落子点 则开始琪露诺的完美井字棋推理
    # return Move.play(random.choice(candidates))
    @classmethod
    def find_candidate_action(cls, game_state):
        # 候选者落子点数组
        candidates = []
        # 遍历棋盘的每一个点 找到所有合法落子点
        for r in range(1, game_state.board.num_rows + 1):
            for c in range(1, game_state.board.num_cols + 1):
                # 该点的point数据结构
                candidate = Point(row=r, col=c)
                # 判断该落子点对于该阵营是否合法
                if game_state.is_valid_move(Move.play(candidate)):
                    # 若合法 则加入到数组中
                    candidates.append(candidate)
        return candidates

    @classmethod
    def action_consequence(cls, game_state, move):
        return game_state.apply_move(move)

    def thinking_action(self, game_state, faction, mother_estimation):
        now_estimation = None

        candidates = self.find_candidate_action(game_state)
        if len(candidates) == 0:
            candidates = self.find_candidate_action(game_state)

        win_actions = []
        tie_actions = []
        lose_actions = []

        for point in candidates:

            move = Move.play(point)
            new_state = self.action_consequence(game_state, move)
            winner = evaluate_win(new_state.board)
            # 未完成的情况
            if winner is None and len(candidates) - 1 > 0:
                action, winner = self.thinking_action(new_state, change_faction(faction), now_estimation)

                """
                    α-β剪枝
                """
                # if now_estimation is None:
                #     now_estimation = winner
                # else:
                #     if judge_estimation_better(now_estimation, winner, faction):
                #         now_estimation = winner
                #
                # if mother_estimation is not None:
                #     # 母亲节点是否比本节点更【好】（对母亲节点而言的好）
                #     # 如果不比母亲节点更好 相等乃至更烂 则不再继续
                #     if not judge_estimation_better(mother_estimation, now_estimation, change_faction(faction)):
                #         return move, faction
                """
                    α-β剪枝
                """

                if winner == faction:
                    return move, winner
                elif winner == change_faction(faction):
                    lose_actions.append(move)
                elif winner is False:
                    tie_actions.append(move)
                elif winner is None:
                    print("warning: there is a bug here. code:001")
                else:
                    print("warning: there is a bug here. code:003")
            # 平局的情况
            elif winner is None and len(candidates) - 1 == 0:
                tie_actions.append(move)
            # 胜负的情况
            else:
                if winner == faction:
                    # print("必胜手")
                    return move, winner
                elif winner == change_faction(faction):
                    lose_actions.append(move)
                elif winner is False:
                    tie_actions.append(move)
                else:
                    print("warning: there is a bug here. code:002")
        if len(candidates) == 9:
            print(win_actions, tie_actions, lose_actions, sep="\n")
        if win_actions:
            return random.choice(win_actions), faction
        elif tie_actions:

            return random.choice(tie_actions), False
        elif lose_actions:

            return random.choice(lose_actions), change_faction(faction)
        else:
            print("warning: there is a bug here. code:006")


def change_faction(faction):
    if faction == Player.white:
        return Player.black
    elif faction == Player.black:
        return Player.white


def judge_estimation_better(now_estimation, winner, faction):
    if now_estimation is None:
        return False

    def get_mark(now_faction, self_faction):
        if now_faction == self_faction:
            return 1
        elif now_faction == change_faction(self_faction):
            return -1
        elif now_faction is False:
            return 0
        else:
            print("warning: there is a bug here. code:005")

    now_mark = get_mark(now_estimation, faction)
    new_mark = get_mark(winner, faction)

    return new_mark > now_mark
