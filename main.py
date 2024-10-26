# Main Driver file. User input and displaying GameState Object

import pygame as p
import ChessEngine

p.init()  # Located here instead of main in case other methods need this.
max_fps = 30  # Might change later.
width = height = 512  # Can do 400
dimension = 8
sq_size = height // dimension   # to make sure it is an int. //
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
    valid_moves = gamestate.get_valid_moves()
    move_made = False # Flag variable for move.

    load_images()
    playing = True
    selected_sq = ()    # tuple: (row, col)
    player_clicks = []  # two tuples: using (row, col)
    start = True

    while playing:
        for e in p.event.get():
            if e.type == p.QUIT:
                playing = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location for mouse
                col = location[0] // sq_size
                row = location[1] // sq_size
                current_color = 'w' if gamestate.white_to_move else 'b'

                if selected_sq == (row, col):   # if user click same square, will undo.
                    selected_sq = ()
                    player_clicks = []
                else:                           # Selected square
                    selected_sq = (row, col)
                    player_clicks.append(selected_sq)
                if len(player_clicks) == 2:     # after 2nd click
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gamestate.board)
                    print(move.get_chess_notation())
                    for i in range(len(valid_moves)):
                        # Pawn promotion is here instead of engine because I am inefficient and 'fake check' moves.
                        if move == valid_moves[i]:
                            gamestate.make_move(valid_moves[i])
                            move_made = True

                            # reset
                            selected_sq = ()
                            player_clicks = []
                            gamestate.move_redo_stack = []
                    if not move_made:
                        player_clicks = [selected_sq]
                        create_game_state(screen, gamestate)
                        if gamestate.in_check():
                            if gamestate.white_to_move:
                                p.draw.rect(screen, p.Color("Orange"),
                                            p.Rect(gamestate.white_king_loc[1] * sq_size,
                                                   gamestate.white_king_loc[0] * sq_size,
                                                   sq_size, sq_size))
                            else:
                                p.draw.rect(screen, p.Color("Orange"),
                                            p.Rect(gamestate.black_king_loc[1] * sq_size,
                                                   gamestate.black_king_loc[0] * sq_size,
                                                   sq_size, sq_size))
                if gamestate.board[row][col][0] == current_color and len(player_clicks) == 1:    # highlight selection
                    p.draw.rect(screen, p.Color("Red"), p.Rect(col * sq_size, row * sq_size, sq_size, sq_size))
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # Undo when u is pressed
                    move_made = True
                    gamestate.undo_move(move_made)
                if e.key == p.K_r:  # redo when r is pressed
                    move_made = True
                    gamestate.redo_move()
        if move_made:
            valid_moves = gamestate.get_valid_moves()
            move_made = False
            create_game_state(screen, gamestate)
            if gamestate.in_check():
                if gamestate.white_to_move:
                    p.draw.rect(screen, p.Color("Orange"),
                                p.Rect(gamestate.white_king_loc[1] * sq_size, gamestate.white_king_loc[0] * sq_size,
                                       sq_size, sq_size))
                else:
                    p.draw.rect(screen, p.Color("Orange"),
                                p.Rect(gamestate.black_king_loc[1] * sq_size, gamestate.black_king_loc[0] * sq_size,
                                       sq_size, sq_size))
        elif start:
            create_game_state(screen, gamestate)
            start = False
        else:
            create_piece(screen, gamestate.board)
        clock.tick(max_fps)
        p.display.flip()




def create_game_state(screen, gamestate):
    create_board(screen, gamestate.board)  # draw squares then drawing pieces. Board should come first
    create_piece(screen, gamestate.board)


def create_board(screen, board):
    colors = [p.Color("white"), p.Color("forestgreen")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]  # (0 = white, 1 = not white)
            p.draw.rect(screen, color, p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))


def create_piece(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]

            if piece != "--":
                screen.blit(images[piece], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))


if __name__ == "__main__":  # This is done because it only runs when this python file is called. Typical practice
    main()
