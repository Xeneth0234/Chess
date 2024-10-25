# Main Driver file. User input and displaying GameState Object

import pygame as p
import ChessEngine

p.init()  # Located here instead of main in case other methods need this.
max_fps = 30  # Might change later.
width = height = 512  # Can do 400
dimension = 8
sq_size = height / dimension
images = {}


# Initialize global directory of images
def load_images():
    pieces = ['bP', 'bQ', 'bN', 'bK', 'bR', 'bB', 'wP', 'wQ', 'wN', 'wK', 'wR', 'wB']
    for piece in pieces:
        images[piece] = p.image.load("images/" + piece + ".png")
    # EX Usage: image['wP']


def main():
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gamestate = ChessEngine.GameState()
    load_images()
    playing = True

    while playing:
        for e in p.event.get():
            if e.type == p.QUIT:
                playing = False
        create_game_state(screen, gamestate)
        clock.tick(max_fps)
        p.display.flip()


def create_game_state(screen, gamestate):
    create_board(screen, gamestate.board)  # draw squares then drawing pieces. Board should come first


def create_board(screen, board):
    colors = [p.Color("white"), p.Color("forestgreen")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]  # (0 = white, 1 = not white)
            p.draw.rect(screen, color, p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))

            piece = board[r][c]  # I may separate these later
            if piece != "--":  # Not empty
                screen.blit(images[piece], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))


if __name__ == "__main__":  # This is done because it only runs when this python file is called. Typical practice
    main()
