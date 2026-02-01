import random
import sys

import pygame

CELL = 30
COLS = 10
ROWS = 20
PANEL_COLS = 6
PANEL_W = CELL * PANEL_COLS
W = CELL * COLS + PANEL_W
H = CELL * ROWS
FPS = 60
MINES_INITIAL = 6
MINES_PER_5_LINES = 1
MINE_COLOR = (120, 120, 120)

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


def collide(board, piece, mines=None):
    for x, y in piece.blocks():
        if x < 0 or x >= COLS or y >= ROWS:
            return True
        if y >= 0 and board[y][x]:
            return True
        if mines and y >= 0 and (x, y) in mines:
            return True
    return False


def lock_piece(board, piece):
    for x, y in piece.blocks():
        if y >= 0:
            board[y][x] = piece.kind


def clear_lines(board):
    kept_rows = []
    cleared_rows = []
    for idx, row in enumerate(board):
        if all(cell != "" for cell in row):
            cleared_rows.append(idx)
        else:
            kept_rows.append(row)
    new_board = kept_rows
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [""] * COLS)
    return new_board, cleared, cleared_rows


def shift_mines_after_clear(mines, cleared_rows):
    if not cleared_rows:
        return mines
    cleared_set = set(cleared_rows)
    new_mines = set()
    for x, y in mines:
        if y in cleared_set:
            continue
        shift = sum(1 for r in cleared_rows if r < y)
        new_mines.add((x, y - shift))
    return new_mines


def spawn_mines(mines, board, count):
    empty = [
        (x, y)
        for y in range(2, ROWS)
        for x in range(COLS)
        if board[y][x] == "" and (x, y) not in mines
    ]
    random.shuffle(empty)
    for pos in empty[:count]:
        mines.add(pos)


def draw_board(screen, board, mines):
    screen.fill(BG)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(PANEL_W + x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, GRID, rect, 1)
            if board[y][x]:
                color = COLORS[board[y][x]]
                pygame.draw.rect(screen, color, rect.inflate(-2, -2))
            elif (x, y) in mines:
                pygame.draw.rect(screen, MINE_COLOR, rect.inflate(-4, -4))
                pygame.draw.line(
                    screen,
                    (30, 30, 30),
                    (rect.left + 6, rect.top + 6),
                    (rect.right - 6, rect.bottom - 6),
                    2,
                )
                pygame.draw.line(
                    screen,
                    (30, 30, 30),
                    (rect.left + 6, rect.bottom - 6),
                    (rect.right - 6, rect.top + 6),
                    2,
                )


def draw_piece(screen, piece):
    for x, y in piece.blocks():
        if y >= 0:
            rect = pygame.Rect(PANEL_W + x * CELL, y * CELL, CELL, CELL)
            pygame.draw.rect(screen, COLORS[piece.kind], rect.inflate(-2, -2))


def draw_next(screen, piece, font):
    label = font.render("Next", True, (220, 220, 220))
    screen.blit(label, (10, 10))
    # Center the 4x4 preview in the left panel
    start_x = (PANEL_W - 4 * CELL) // 2
    start_y = 40
    for r in range(4):
        for c in range(4):
            if piece.shape[r][c] == "#":
                rect = pygame.Rect(start_x + c * CELL, start_y + r * CELL, CELL, CELL)
                pygame.draw.rect(screen, COLORS[piece.kind], rect.inflate(-2, -2))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    board = [[""] * COLS for _ in range(ROWS)]
    mines = set()
    spawn_mines(mines, board, MINES_INITIAL)
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
                    if collide(board, current, mines):
                        current.x += 1
                if event.key == pygame.K_RIGHT:
                    current.x += 1
                    if collide(board, current, mines):
                        current.x -= 1
                if event.key == pygame.K_DOWN:
                    current.y += 1
                    if collide(board, current, mines):
                        current.y -= 1
                if event.key == pygame.K_UP:
                    rotated = rotate(current.shape)
                    old = current.shape
                    current.shape = rotated
                    if collide(board, current, mines):
                        current.shape = old
                if event.key == pygame.K_SPACE:
                    while not collide(board, current, mines):
                        current.y += 1
                    current.y -= 1

        if fall_timer >= drop_ms:
            fall_timer = 0
            current.y += 1
            if collide(board, current, mines):
                current.y -= 1
                # Mine hit destroys the current piece instead of locking it.
                hit = [(x, y) for x, y in current.blocks() if (x, y + 1) in mines]
                if hit:
                    for x, y in hit:
                        mines.discard((x, y + 1))
                else:
                    lock_piece(board, current)
                board, cleared, cleared_rows = clear_lines(board)
                mines = shift_mines_after_clear(mines, cleared_rows)
                if cleared:
                    lines_total += cleared
                    score += [0, 40, 100, 300, 1200][cleared] * level
                    level = max(1, 1 + lines_total // 10)
                    drop_ms = max(100, 700 - (level - 1) * 50)
                    if lines_total % 5 == 0:
                        spawn_mines(mines, board, MINES_PER_5_LINES)
                current = next_piece
                if not bag:
                    bag = new_bag()
                next_piece = Piece(bag.pop())
                if collide(board, current, mines):
                    running = False

        draw_board(screen, board, mines)
        draw_piece(screen, current)

        # UI
        draw_next(screen, next_piece, font)
        info = font.render(f"Score: {score}", True, (220, 220, 220))
        level_txt = font.render(f"Level: {level}", True, (220, 220, 220))
        screen.blit(info, (10, 200))
        screen.blit(level_txt, (10, 225))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
