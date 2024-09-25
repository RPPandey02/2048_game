import pygame
import numpy as np
import random
import time

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 4
TILE_SIZE = 100
TILE_MARGIN = 10
ANIMATION_SPEED = 30  # Speed of tile movement
WIDTH = HEIGHT = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * TILE_MARGIN
FONT_SIZE = 40
FONT = pygame.font.Font(None, FONT_SIZE)

# Colors
BG_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
    16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97), 512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46),
}

# Initialize game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('2048 Game')


# Initialize the game board
def init_board():
    board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    add_random_tile(board)
    add_random_tile(board)
    return board


# Add a new random tile to the board
def add_random_tile(board):
    empty_tiles = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if board[i][j] == 0]
    if empty_tiles:
        i, j = random.choice(empty_tiles)
        board[i][j] = 2 if random.random() < 0.9 else 4


# Slide and merge row logic
def slide_row_left(row):
    row = [i for i in row if i != 0]  # Remove zeros
    for i in range(len(row) - 1):
        if row[i] == row[i + 1]:  # Merge tiles
            row[i] *= 2
            row[i + 1] = 0
    row = [i for i in row if i != 0]  # Remove merged zero spots
    return row + [0] * (GRID_SIZE - len(row))  # Pad with zeros to the right


# Move logic
def move_left(board):
    return np.array([slide_row_left(row) for row in board])


def move_right(board):
    return np.array([slide_row_left(row[::-1])[::-1] for row in board])


def move_up(board):
    return move_left(board.T).T


def move_down(board):
    return move_right(board.T).T


# Make a move based on the direction
def make_move(board, direction):
    if direction == "left":
        return move_left(board)
    elif direction == "right":
        return move_right(board)
    elif direction == "up":
        return move_up(board)
    elif direction == "down":
        return move_down(board)
    return board


# Check if any moves are possible
def can_move(board):
    if 0 in board:
        return True
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE - 1):
            if board[i][j] == board[i][j + 1] or board[j][i] == board[j + 1][i]:
                return True
    return False


# Draw the game board
def draw_board(board, animations=None):
    screen.fill(BG_COLOR)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            tile_value = board[row][col]
            rect_x = col * TILE_SIZE + (col + 1) * TILE_MARGIN
            rect_y = row * TILE_SIZE + (row + 1) * TILE_MARGIN

            if animations and (row, col) in animations:
                rect_x += animations[(row, col)][0]
                rect_y += animations[(row, col)][1]

            rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, TILE_COLORS.get(tile_value, EMPTY_TILE_COLOR), rect, 0)

            if tile_value != 0:
                text_surface = FONT.render(f"{tile_value}", True, (119, 110, 101))
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)

    pygame.display.update()


# Animate the swipe movement
def animate_swipe(board, new_board, direction):
    # Map of directions to movement offsets
    direction_offsets = {
        "left": (-1, 0), "right": (1, 0),
        "up": (0, -1), "down": (0, 1)
    }
    offset = direction_offsets[direction]

    # Create animation dictionary to store positions
    animations = {}
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != 0 and new_board[row][col] == 0:
                animations[(row, col)] = (0, 0)

    # Animate movement in small steps
    steps = TILE_SIZE // ANIMATION_SPEED
    for step in range(steps):
        for (row, col), (dx, dy) in animations.items():
            animations[(row, col)] = (dx + offset[0] * ANIMATION_SPEED, dy + offset[1] * ANIMATION_SPEED)
        draw_board(board, animations)
        pygame.time.delay(30)


# Main game loop
def main():
    board = init_board()
    running = True

    while running:
        draw_board(board)

        if 2048 in board:
            print("Congratulations! You reached 2048!")
            running = False

        if not can_move(board):
            print("Game Over! No more moves possible.")
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                new_board = None
                if event.key == pygame.K_LEFT:
                    new_board = make_move(board, "left")
                    direction = "left"
                elif event.key == pygame.K_RIGHT:
                    new_board = make_move(board, "right")
                    direction = "right"
                elif event.key == pygame.K_UP:
                    new_board = make_move(board, "up")
                    direction = "up"
                elif event.key == pygame.K_DOWN:
                    new_board = make_move(board, "down")
                    direction = "down"

                if new_board is not None and not np.array_equal(board, new_board):
                    animate_swipe(board, new_board, direction)
                    board = new_board
                    add_random_tile(board)

    pygame.quit()


if __name__ == "__main__":
    main()
