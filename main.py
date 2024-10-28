# Main Driver file. User input and displaying GameState Object

import pygame as p
import ChessEngine
import ChessAI
import time

global colors
p.init()  # Located here instead of main in case other methods need this.
max_fps = 30  # Might change later.
width = height = 512  # Can do 400
dimension = 8
sq_size = height // dimension   # to make sure it is an int. //
images = {}
"""
Future to do list
- Change game state creation so it only updates moves that has changed 
    so it does not need to update entire board each time
- Fix undo causing out of range error. I believe this has to do with the process of how log is saved not the fake moves
- Try making the play state asynch. Aka thread and make the ui unresponsive if AI is taking turn
"""


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
    move_made = False   # Flag variable for move.
    animate = False     # Flag variable for move. Also future potential for options

    load_images()
    playing = True
    selected_sq = ()    # tuple: (row, col)
    player_clicks = []  # two tuples: using (row, col)
    game_over = False
    player_one = False   # If a human is playing, then this will be true, if AI, False.
    player_two = False  # Same as above but for black

    while playing:
        human_turn = (gamestate.white_to_move and player_one) or (not gamestate.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                playing = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:               # If game over, do not allow more moves / selections
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
                                animate = True

                                # reset
                                selected_sq = ()
                                player_clicks = []
                                gamestate.move_redo_stack = []
                        if not move_made:
                            player_clicks = [selected_sq]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # Undo when u is pressed
                    move_made = True
                    gamestate.undo_move(move_made)
                    animate = False
                    game_over = False
                    if gamestate.stalemate:
                        gamestate.stalemate = False
                if e.key == p.K_r:  # redo when r is pressed
                    move_made = True
                    gamestate.redo_move()
                    animate = False
                if e.key == p.K_MINUS:  # reset when - is pressed
                    gamestate = ChessEngine.GameState()
                    valid_moves = gamestate.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    game_over = False
                    move_made = False
                    animate = False

        # AI move finder
        if not game_over and not human_turn:
            print("Current Board Score:", ChessAI.score_board(gamestate))
            print("Material: ", ChessAI.score_material(gamestate.board))
            AI_move = ChessAI.find_best_move_minimax(gamestate, valid_moves) if gamestate.white_to_move else (
                ChessAI.find_best_move(gamestate, valid_moves))
            if AI_move is not None:
                print("The Move:", AI_move.get_chess_notation())
            time.sleep(0.22)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
            gamestate.make_move(AI_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animations(gamestate.move_log[-1], screen, gamestate.board, clock)
            valid_moves = gamestate.get_valid_moves()
            move_made = False
            animate = False

        create_game_state(screen, gamestate, valid_moves, selected_sq)

        if gamestate.checkmate:
            game_over = True
            if gamestate.white_to_move:
                create_text(screen, "Black wins by checkmate", "Black")
            else:
                create_text(screen, "White wins by checkmate", "White")
        elif gamestate.stalemate:
            game_over = True
            if gamestate.stalemate_by_repeat:
                create_text(screen, "Stalemate by repeat", "Aqua")
            else:
                create_text(screen, "Stalemate", "Aqua")
        clock.tick(max_fps)
        p.display.flip()


# highlight when in check
def highlight_in_check(game_state, screen):
    if game_state.in_check():
        if game_state.white_to_move:
            p.draw.rect(screen, p.Color("Red"),
                    p.Rect(game_state.white_king_loc[1] * sq_size,
                           game_state.white_king_loc[0] * sq_size,
                           sq_size, sq_size))
        else:
            p.draw.rect(screen, p.Color("Red"),
                    p.Rect(game_state.black_king_loc[1] * sq_size,
                           game_state.black_king_loc[0] * sq_size,
                           sq_size, sq_size))


# highlight selected square and show possible moves
def highlight_squares(gamestate, screen, valid_moves, selected_sq):
    if selected_sq != ():
        r, c = selected_sq
        # highlighting selected square
        if gamestate.board[r][c][0] == ('w' if gamestate.white_to_move else 'b'):
            # highlight selected square
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100)        # transparency value
            s.fill(p.Color("Aqua"))
            screen.blit(s, (c * sq_size, r * sq_size))
            # highlight moves from that square
            s.set_alpha(200)
            s.fill(p.Color("Orchid"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * sq_size, move.end_row * sq_size))


def create_game_state(screen, gamestate, valid_moves, selected_sq):
    create_board(screen)  # draw squares then drawing pieces. Board should come first
    highlight_squares(gamestate, screen, valid_moves, selected_sq)
    highlight_in_check(gamestate, screen)
    create_piece(screen, gamestate.board)


def create_board(screen):
    global colors

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


def animations(move, screen, board, clock):
    global colors

    delta_row = move.end_row - move.start_row
    delta_column = move.end_col - move.start_col
    frames_per_square = 5          # Frames for one square
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + delta_row * frame/frame_count, move.start_col + delta_column * frame/frame_count)
        create_board(screen)
        create_piece(screen, board)
        # erase piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * sq_size, move.end_row * sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, end_square)
        # draw piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(images[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(images[move.piece_moved], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)


def create_text(screen, text, color):
    font = p.font.SysFont('Ariel', 32, True, False)
    text_object = font.render(text, 0, p.Color('Aqua'))     # text in back
    text_location = p.Rect(0, 0, width, height).move(width/2 - text_object.get_width()/2,
                                                     height/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color(color))    # Text in front to create a little 3d effect
    screen.blit(text_object, text_location.move(1, 1))


if __name__ == "__main__":  # This is done because it only runs when this python file is called. Typical practice
    main()
