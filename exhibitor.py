from dlgo.gotypes import Point
from dlgo.gotypes import Player

from dlgo import gotypes
from dlgo.gotypes import Point
from dlgo.goboard_slow import Move
from dlgo.agent import helpers


class Exhibitor:
    def __init__(self, board_size, block_size, mode):
        # self.game = game

        self.block_size = block_size
        # 地图长宽各多少格
        self.board_size = board_size
        # 窗口中世界的大小
        self.world_win_size = (self.block_size * self.board_size, self.block_size * self.board_size)
        # 窗口大小（加上状态栏）
        self.win_size = (
            self.world_win_size[1] + 2 * self.block_size + self.world_win_size[0] / 5,
            self.world_win_size[0] + 2 * self.block_size + self.world_win_size[0] / 5)
        self.__init_exhibitor()
        self.gate = True

        # 定义颜色
        self.bg_color = (255, 255, 255)
        self.board_color = (225, 255, 255)

        # 模式
        self.mode = mode

    # 初始化展示器
    def __init_exhibitor(self):
        # 初始化框架
        import pygame

        self.pygame = pygame

        # 初始化
        pygame.init()

        # 规定大小 生成窗口
        self.window = pygame.display.set_mode(self.win_size)

        # 设置标题
        pygame.display.set_caption("Smart Cirno")

        # 设定时间频率
        self.clock = pygame.time.Clock()

        # 定义点类
        class Position:
            def __init__(self, exhibitor, row, col, interspace=5):
                # 在第几行
                self.row = row
                # 在第几列
                self.col = col
                self.mid_interspace = interspace
                self.exhibitor = exhibitor
                # 屏幕宽度除以横向有几个格
                self.cell_width = exhibitor.world_win_size[1] / exhibitor.board_size
                # 屏幕长度除以纵向有几个格
                self.cell_height = exhibitor.world_win_size[0] / exhibitor.board_size
                # 求本格的位置
                self.left = self.col * self.cell_width
                self.top = self.row * self.cell_height

            def draw_point(self):
                pygame.draw.rect(self.exhibitor.window, self.exhibitor.board_color,
                                 (self.left, self.top, self.cell_width - 1, self.cell_height - 1))

            def draw_stone(self, faction):
                if faction == Player.black:
                    pygame.draw.circle(self.exhibitor.window, (0, 0, 0),
                                       (self.left + (self.cell_width - 1) / 2, self.top + (self.cell_width - 1) / 2),
                                       (self.cell_width - 1) / 2, width=int(self.cell_width) // 10)
                elif faction == Player.white:
                    pygame.draw.line(self.exhibitor.window, (0, 0, 0),
                                     start_pos=(self.left + self.cell_width / 10,
                                                self.top + self.cell_width / 10),
                                     end_pos=(self.left + self.cell_width - self.cell_width / 10,
                                              self.top + self.cell_width - self.cell_width / 10),
                                     width=int(self.cell_width) // 10)

                    pygame.draw.line(self.exhibitor.window, (0, 0, 0),
                                     start_pos=(self.left + self.cell_width / 10,
                                                self.top + self.cell_width - self.cell_width / 10),
                                     end_pos=(self.left + self.cell_width - self.cell_width / 10,
                                              self.top + self.cell_width / 10),
                                     width=int(self.cell_width) // 10)

        self.Position = Position

    """
        展示的框架
    """

    def display(self, game, stone):
        # 绘图内容
        pass

        # win_event = True

        """
            画方格世界
        """
        self.draw_game(game)

        """
            画状态栏
        """
        # 让渡控制权
        self.pygame.display.flip()

        # 设置帧率
        self.clock.tick(60)

        player_cmd = None
        # 读取玩家操作
        if self.mode == "h v b":
            if stone == gotypes.Player.black:
                player_cmd = self.detect_player_input(game)

        elif self.mode == "b v h":
            if stone == gotypes.Player.white:
                player_cmd = self.detect_player_input(game)

        elif self.mode == "h v h":
            player_cmd = self.detect_player_input(game)

        return player_cmd

    def draw_game(self, game):
        """
            定义绘图函数
        """

        # 画棋盘
        def draw_board():
            board_size = game.board.num_cols
            for row in range(board_size):
                for col in range(board_size):
                    self.Position(self, row=row + 1, col=col + 1).draw_point()

        # 画棋子
        def draw_stone():
            board_size = game.board.num_cols
            for row in range(board_size):
                for col in range(board_size):
                    stone = game.board.get(Point(row=row + 1, col=col + 1))
                    # print(stone)
                    if stone is not None:
                        self.Position(self, row=row + 1, col=col + 1).draw_stone(stone)

        """
            画图执行
        """

        # 渲染
        # 画背景
        self.pygame.draw.rect(self.window, self.bg_color, (0, 0, self.win_size[0], self.win_size[1]))
        self.pygame.draw.rect \
            (self.window, self.board_color,
             (0, 0, self.world_win_size[0] + 2 * self.block_size, self.world_win_size[1] + 2 * self.block_size))
        self.pygame.draw. \
            rect(self.window, (0, 0, 0),
                 (self.block_size - 1, self.block_size - 1, self.world_win_size[0] + 1,
                  self.world_win_size[1] + 1))

        # 画棋盘
        draw_board()

        # 画棋子
        draw_stone()

    def detect_player_input(self, game):
        door = True
        while door and self.gate:
            # 处理事件
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.pygame.quit()
                    return False
                # keys = self.pygame.key.get_pressed()

                if event.type == self.pygame.MOUSEBUTTONDOWN:
                    if self.legal_position(event.pos):
                        point_position = self.shift_screen_position_to_move(event.pos)
                        point = Point(row=point_position[1] + 1, col=point_position[0] + 1)
                        if game.is_valid_move(Move.play(point)):
                            door = False
                            return point

                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_SPACE:
                        door = False
                        return "pass"

    def legal_position(self, position):
        return self.board_size * self.block_size + self.block_size > position[0] > self.block_size and \
               self.board_size * self.block_size + self.block_size > position[1] > self.block_size

    def shift_screen_position_to_move(self, screen_position):
        return (screen_position[0] // self.block_size) - 1, \
               (screen_position[1] // self.block_size) - 1

    def no_repetitive_stone(self, screen_position, game):
        move_position = self.shift_screen_position_to_move(screen_position)
        return game.board.repetitive_stone(Point(row=move_position[1] + 1, col=move_position[0] + 1))
