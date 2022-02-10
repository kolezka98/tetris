import pygame
import random

# window and board
BLOCK_SIZE = 30
ROW_NUM = 20
COL_NUM = 10
BOARD_CORNER_X = 2
BOARD_CORNER_Y = 2

# colors
BLUE = (3, 65, 174)
GREEN = (114, 203, 59)
YELLOW = (254, 213, 0)
ORANGE = (255, 151, 28)
RED = (255, 50, 19)
PURPLE = (128, 0, 128)
GREY = (127, 127, 127)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# shapes
SHAPES = ("L", "S", "T", "Z", "J", "O", "I")
S_COLOR = {
    "L": ORANGE,
    "S": GREEN,
    "T": PURPLE,
    "Z": RED,
    "J": BLUE,
    "O": YELLOW,
    "I": CYAN,
}

S_ROT = {
    "L": (
        ((-1, 0), (-1, 1), (1, 0)),
        ((0, -1), (-1, -1), (0, 1)),
        ((1, 0), (1, -1), (-1, 0)),
        ((0, 1), (1, 1), (0, -1)),
    ),
    "S": (
        ((1, 0), (0, 1), (-1, 1)),
        ((0, 1), (-1, 0), (-1, -1)),
        ((-1, 0), (0, -1), (1, -1)),
        ((0, -1), (1, 0), (1, 1)),
    ),
    "T": (
        ((-1, 0), (0, 1), (1, 0)),
        ((0, -1), (-1, 0), (0, 1)),
        ((1, 0), (0, -1), (-1, 0)),
        ((0, 1), (1, 0), (0, -1)),
    ),
    "Z": (
        ((-1, 0), (0, 1), (1, 1)),
        ((0, -1), (-1, 0), (-1, 1)),
        ((1, 0), (0, -1), (-1, -1)),
        ((0, 1), (1, 0), (1, -1)),
    ),
    "J": (
        ((-1, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 1), (-1, 1)),
        ((1, 0), (-1, 0), (-1, -1)),
        ((0, 1), (0, -1), (1, -1)),
    ),
    "O": (
        ((-1, 0), (-1, 1), (0, 1)),
        ((-1, 0), (-1, 1), (0, 1)),
        ((-1, 0), (-1, 1), (0, 1)),
        ((-1, 0), (-1, 1), (0, 1)),
    ),
    "I": (
        ((-1, 0), (1, 0), (2, 0)),
        ((0, 1), (0, -1), (0, -2)),
        ((-1, 0), (1, 0), (2, 0)),
        ((0, 1), (0, -1), (0, -2)),
    ),
}


class Cube:
    def __init__(self, cord, color):
        assert (
            0 <= cord[0] <= COL_NUM - 1
        ), f"First coordinate (x) is out of range (0  - {COL_NUM-1})"
        assert (
            0 <= cord[1] <= ROW_NUM - 1
        ), f"Second coordinate (y) is out of range (0  - {ROW_NUM-1})"
        assert (
            color in S_COLOR.values()
        ), f'Provided type: "{color}" is not in valid colors: {S_COLOR.values()}'

        self.x, self.y = cord[0], cord[1]
        self.color = color


class Frozen_Pieces:
    def __init__(self):
        self.cubes = []
        self.cube_dict = {}
        self.full_row = []
        self.deleted_rows = 0
        for i in range(ROW_NUM):
            self.cube_dict[str(i)] = []

    def check_full_row(self):
        self.create_cube_dict()
        for key, arr in self.cube_dict.items():
            s = set(arr)
            if s == {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}:
                self.full_row.append(int(key))
                return True
        return False

    def create_cube_dict(self):
        for i in range(ROW_NUM):
            self.cube_dict[str(i)] = []
        for c in self.cubes:
            self.cube_dict[str(c.y)].append(c.x)

    def remove_full_rows(self):
        removing = self.check_full_row()
        removed_rows = 0
        while removing:
            # remove row
            removed_rows += 1
            self.cubes = list(filter((lambda c: c.y != self.full_row[0]), self.cubes))
            self.cube_dict[str(self.full_row[0])] = []
            # lower all rows above removed row
            for c in self.cubes:
                if c.y < self.full_row[0]:
                    c.y = c.y + 1
            self.full_row = []
            removing = self.check_full_row()
        if removed_rows == 1:
            return 50
        if removed_rows == 2:
            return 100
        if removed_rows == 3:
            return 300
        if removed_rows > 3:
            return 1000
        else:
            return 0

    def add_pieces(self, new_cubes):
        self.cubes.extend(new_cubes)


class Piece:
    def __init__(self, rand=True, shape=None):
        if rand:
            self.shape = random.choice(SHAPES)
        else:
            self.shape = shape
        self.rot = 0
        self.main_cube = Cube([5, 0], S_COLOR[self.shape])
        self.cubes = [self.main_cube]
        for i in S_ROT[self.shape][self.rot]:
            c = Cube(
                (self.main_cube.x + i[0], self.main_cube.y + i[1]), S_COLOR[self.shape]
            )
            self.cubes.append(c)

    def update_cubes(self):
        self.cubes[0].x = self.main_cube.x
        self.cubes[0].y = self.main_cube.y
        for idx, cord in enumerate(S_ROT[self.shape][self.rot]):
            self.cubes[idx + 1].x = self.main_cube.x + cord[0]
            self.cubes[idx + 1].y = self.main_cube.y + cord[1]

    def check_collision(self, frozen_cubes: list):
        # border  collision
        for c in self.cubes:
            if c.x < 0 or c.x >= COL_NUM or c.y > ROW_NUM - 1 or c.y < 0:
                return True
        # cube collision
        for c in self.cubes:
            for f_c in frozen_cubes:
                if [c.x, c.y] == [f_c.x, f_c.y]:
                    return True

        return False

    def check_freeze(self, frozen_cubes: list):
        for c in self.cubes:
            # check bottom border
            if c.y > ROW_NUM - 1:
                return True
            # check frozen cubes
            for f_c in frozen_cubes:
                if [c.x, c.y] == [f_c.x, f_c.y]:
                    return True

        return False

    def rotate(self, frozen_pieces):
        self.rot += 1
        if self.rot > 3:
            self.rot = 0
        self.update_cubes()
        if self.check_collision(frozen_pieces.cubes):
            self.rot -= 1
            if self.rot < 0:
                self.rot = 3
            self.update_cubes()


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(
            (
                COL_NUM * BLOCK_SIZE + 6 * BOARD_CORNER_X * BLOCK_SIZE,
                ROW_NUM * BLOCK_SIZE + 2 * BOARD_CORNER_Y * BLOCK_SIZE,
            )
        )
        pygame.display.set_caption("Tetris")
        pygame.display.set_icon(pygame.image.load("data\\tetris_icon.png"))
        self.font = pygame.font.Font("data\\Chicken_Cripsy.ttf", 24)
        self.GO_font = pygame.font.Font("data\\Chicken_Cripsy.ttf", 64)
        self.current_piece = Piece()
        self.next_piece = Piece()
        self.piece_to_draw = Piece(False, self.next_piece.shape)
        self.piece_to_draw.main_cube.x = COL_NUM + 4
        self.piece_to_draw.main_cube.y = 4
        self.piece_to_draw.update_cubes()
        self.frozen_pieces = Frozen_Pieces()
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 0.27
        self.score = 0
        self.game_over = True
        self.first_run = True
        pygame.mixer.music.load("data\\tetris_theme.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

    def change_pieces(self):
        self.current_piece = self.next_piece
        self.next_piece = Piece()
        self.piece_to_draw = Piece(False, self.next_piece.shape)
        self.piece_to_draw.main_cube.x = COL_NUM + 4
        self.piece_to_draw.main_cube.y = 4
        self.piece_to_draw.update_cubes()

    def check_game_over(self):
        if self.current_piece.main_cube.y == 0 and self.current_piece.check_collision(
            self.frozen_pieces.cubes
        ):
            return True

    def draw_grid(self):
        self.surface.fill(BLACK)
        for i in range(COL_NUM):
            pygame.draw.line(
                self.surface,
                WHITE,
                (
                    BOARD_CORNER_X * BLOCK_SIZE + i * BLOCK_SIZE,
                    BOARD_CORNER_Y * BLOCK_SIZE,
                ),
                (
                    BOARD_CORNER_X * BLOCK_SIZE + i * BLOCK_SIZE,
                    BOARD_CORNER_Y * BLOCK_SIZE + ROW_NUM * BLOCK_SIZE - 2,
                ),
            )

        for i in range(ROW_NUM):
            pygame.draw.line(
                self.surface,
                WHITE,
                (
                    BOARD_CORNER_X * BLOCK_SIZE,
                    BOARD_CORNER_Y * BLOCK_SIZE + i * BLOCK_SIZE,
                ),
                (
                    BOARD_CORNER_X * BLOCK_SIZE + COL_NUM * BLOCK_SIZE - 2,
                    BOARD_CORNER_Y * BLOCK_SIZE + i * BLOCK_SIZE,
                ),
            )

    def draw_border(self):
        border = pygame.rect.Rect(
            BOARD_CORNER_X * BLOCK_SIZE,
            BOARD_CORNER_Y * BLOCK_SIZE,
            COL_NUM * BLOCK_SIZE,
            ROW_NUM * BLOCK_SIZE,
        )
        pygame.draw.rect(self.surface, WHITE, border, width=3)

    def draw_cube(self, cube: Cube):
        r = pygame.rect.Rect(
            BOARD_CORNER_X * BLOCK_SIZE + cube.x * BLOCK_SIZE,
            BOARD_CORNER_Y * BLOCK_SIZE + cube.y * BLOCK_SIZE,
            BLOCK_SIZE + 1,
            BLOCK_SIZE + 1,
        )
        pygame.draw.rect(self.surface, cube.color, r)
        pygame.draw.rect(self.surface, GREY, r, width=3)

    def draw_current_piece(self):
        for c in self.current_piece.cubes:
            self.draw_cube(c)

    def draw_frozen_pieces(self):
        for c in self.frozen_pieces.cubes:
            self.draw_cube(c)

    def draw_next_piece(self):
        for c in self.piece_to_draw.cubes:
            self.draw_cube(c)

    def draw_writings(self):
        text = self.font.render("NEXT PIECE:", True, WHITE)
        self.surface.blit(text, (COL_NUM * BLOCK_SIZE + 130, 130))
        text = self.font.render(f"SCORE:   {self.score}", True, WHITE)
        self.surface.blit(text, (COL_NUM * BLOCK_SIZE + 120, 280))
        if self.game_over:
            text = self.font.render(f"Press SPACE", True, WHITE)
            self.surface.blit(text, (COL_NUM * BLOCK_SIZE + 120, 380))
            text = self.font.render(f"to play", True, WHITE)
            self.surface.blit(text, (COL_NUM * BLOCK_SIZE + 145, 410))
            if not self.first_run:
                text = self.GO_font.render(f"GAME OVER", True, WHITE)
                self.surface.blit(text, (30, 240))

    def draw_all(self):
        self.draw_grid()
        self.draw_current_piece()
        self.draw_next_piece()
        self.draw_frozen_pieces()
        self.draw_border()
        self.draw_writings()
        pygame.display.update()

    def restart_game(self):
        self.current_piece = Piece()
        self.next_piece = Piece()
        self.piece_to_draw = Piece(False, self.next_piece.shape)
        self.piece_to_draw.main_cube.x = COL_NUM + 4
        self.piece_to_draw.main_cube.y = 4
        self.piece_to_draw.update_cubes()
        self.frozen_pieces = Frozen_Pieces()
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 0.27
        self.score = 0

    def run(self):

        k_up_pressed = False
        level_time = 0
        last_speed = self.fall_speed

        while not self.game_over:

            # incresing speed
            level_time += self.clock.get_rawtime()
            if level_time > 15000:
                level_time = 0
                if last_speed > 0.11:
                    last_speed -= 0.01
                    if not k_up_pressed:
                        self.fall_speed = last_speed

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.current_piece.main_cube.x -= 1
                        self.current_piece.update_cubes()
                        if self.current_piece.check_collision(self.frozen_pieces.cubes):
                            self.current_piece.main_cube.x += 1
                            self.current_piece.update_cubes()

                    if event.key == pygame.K_RIGHT:
                        self.current_piece.main_cube.x += 1
                        self.current_piece.update_cubes()
                        if self.current_piece.check_collision(self.frozen_pieces.cubes):
                            self.current_piece.main_cube.x -= 1
                            self.current_piece.update_cubes()

                    if event.key == pygame.K_DOWN:
                        self.fall_speed = 0.05
                        k_up_pressed = True

                    if event.key == pygame.K_UP:
                        self.current_piece.rotate(self.frozen_pieces)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.fall_speed = last_speed
                        k_up_pressed = False

            # piece falling
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()

            if self.fall_time >= self.fall_speed * 1000:
                self.fall_time = 0
                self.current_piece.main_cube.y += 1
                self.current_piece.update_cubes()
                if self.current_piece.check_freeze(self.frozen_pieces.cubes):
                    self.current_piece.main_cube.y -= 1
                    self.current_piece.update_cubes()
                    self.frozen_pieces.add_pieces(self.current_piece.cubes)
                    # add score and remove rows
                    self.score = self.score + self.frozen_pieces.remove_full_rows()
                    self.change_pieces()
                    if self.check_game_over():
                        self.game_over = True

            self.draw_all()

    def main(self):

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_over = False
                        self.restart_game()
                        self.first_run = False

            if not self.game_over:
                game.run()

            self.draw_all()


if __name__ == "__main__":
    game = Game()
    game.main()
