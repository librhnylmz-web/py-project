import random
import sys

import pygame

CELL = 30
COLS = 10
ROWS = 20
W = CELL * COLS
H = CELL * ROWS
FPS = 60

# Tetromino shapes (4x4)
SHAPES = {
    "I": [
        "....",
        "####",
        "....",
        "....",
    ],
    "O": [
        ".##.",
        ".##.",
        "....",
        "....",
    ],
    "T": [
        ".#..",
        "###.",
        "....",
        "....",
    ],
    "S": [
        ".##.",
        "##..",
        "....",
        "....",
    ],
    "Z": [
        "##..",
        ".##.",
        "....",
        "....",
    ],
    "J": [
        "#...",
        "###.",
        "....",
        "....",
    ],
    "L": [
        "..#.",
        "###.",
        "....",
        "....",
    ],
}

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}

BG = (20, 20, 26)
GRID = (45, 45, 60)


def rotate(shape):
    return ["".join(row[i] for row in reversed(shape)) for i in range(4)]


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.shape = SHAPES[kind]
        self.x = COLS // 2 - 2
        self.y = 0

    def blocks(self):
        for r in range(4):
            for c in range(4):
                if self.shape[r][c] == "#":
                    yield self.x + c, self.y + r


def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag


def collide(board, piece):
    for x, y in piece.blocks():
        if x < 0 or x >= COLS or y >= ROWS:
            return True
        if y >= 0 and board[y][x]:
            return True
    return False


def lock_piece(board, piece):
    for x, y in piece.blocks():
        if y >= 0:
            board[y][x] = piece.kind


def clear_lines(board):
    new_board = [row for row in board if any(cell == "" for cell in row)]
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [""] * COLS)
    return new_board, cleared


def draw_board(screen, board):
    screen.fill(BG)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, GRID, rect, 1)
            if board[y][x]:
                color = COLORS[board[y][x]]
                pygame.draw.rect(screen, color, rect.inflate(-2, -2))


def draw_piece(screen, piece):
    for x, y in piece.blocks():
        if y >= 0:
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, COLORS[piece.kind], rect.inflate(-2, -2))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    board = [[""] * COLS for _ in range(ROWS)]
    bag = new_bag()
    current = Piece(bag.pop())
    next_piece = Piece(bag.pop())

    drop_ms = 700
    fall_timer = 0
    score = 0
    level = 1
    lines_total = 0
    running = True

    while running:
        dt = clock.tick(FPS)
        fall_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LEFT:
                    current.x -= 1
                    if collide(board, current):
                        current.x += 1
                if event.key == pygame.K_RIGHT:
                    current.x += 1
                    if collide(board, current):
                        current.x -= 1
                if event.key == pygame.K_DOWN:
                    current.y += 1
                    if collide(board, current):
                        current.y -= 1
                if event.key == pygame.K_UP:
                    rotated = rotate(current.shape)
                    old = current.shape
                    current.shape = rotated
                    if collide(board, current):
                        current.shape = old
                if event.key == pygame.K_SPACE:
                    while not collide(board, current):
                        current.y += 1
                    current.y -= 1

        if fall_timer >= drop_ms:
            fall_timer = 0
            current.y += 1
            if collide(board, current):
                current.y -= 1
                lock_piece(board, current)
                board, cleared = clear_lines(board)
                if cleared:
                    lines_total += cleared
                    score += [0, 40, 100, 300, 1200][cleared] * level
                    level = max(1, 1 + lines_total // 10)
                    drop_ms = max(100, 700 - (level - 1) * 50)
                current = next_piece
                if not bag:
                    bag = new_bag()
                next_piece = Piece(bag.pop())
                if collide(board, current):
                    running = False

        draw_board(screen, board)
        draw_piece(screen, current)

        # UI
        info = font.render(f"Score: {score}  Level: {level}", True, (220, 220, 220))
        screen.blit(info, (6, 6))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
