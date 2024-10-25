# File responsible for current state of game and determining current valid moves.

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_list = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves
                          , 'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        # This is just to make code look more clean.

        # 8x8 2d list. Labeled "colorPiece"
        self.white_to_move = True
        self.move_log = []
        self.move_redo_stack = []
        self.current_move = []

    def make_move(self, move):  # Assuming move is valid and NOT special moves like castling, promotion & en-passant
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log move so we can undo it later
        self.white_to_move = not self.white_to_move  # swap players. Not negates current boolean (flips)
        self.move_redo_stack.clear()    # to keep track of what has been undone

    def undo_move(self):
        if len(self.move_log) != 0:     # if a move can not be undone
            move = self.move_log.pop()
            self.move_redo_stack.append(move)

            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    def redo_move(self):
        if self.move_redo_stack:
            move = self.move_redo_stack.pop()
            self.move_log.append(move)      # re-append to move log.

            self.board[move.end_row][move.end_col] = move.piece_moved
            self.board[move.start_row][move.start_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    def get_valid_moves(self):  # for things like pins and checks
        return self.get_possible_moves()    # Temporarily not caring for checks

    def get_possible_moves(self):   # for legal moves.
        # In the future, try making it so it only checks on pieces you click maybe
        moves = [Move((6, 4), (4, 4), self.board)]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = self.board[r][c][0]
                if (color == "w" and self.white_to_move) or (color == 'b' and not self.white_to_move):  # if their turn
                    piece = self.board[r][c][1]
                    self.move_list[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c + 1 <= 7:                # Right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
            if c - 1 >= 0:                # Left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))

        else:                               # Black
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c + 1 <= 7:                # Right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            if c - 1 >= 0:                # Left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))

    def get_rook_moves(self, r, c, moves):
        movement = {(-1, 0), (0, -1), (1,0), (0, 1)}    # up, left, down, right
        opposite_color = 'b' if self.white_to_move else 'w'
        for m in movement:
            for i in range(1, 8):
                dest_row = r + (m[0] * i)       # row + direction increment.
                dest_col = c + (m[1] * i)       # column + direction increment.
                if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:   # in bounds
                    dest = self.board[dest_row][dest_col]
                    if dest == "--":
                        moves.append(Move((r, c), (dest_row, dest_col), self.board))
                    elif dest[0] == opposite_color:            # If opposite color, can capture then stop
                        moves.append(Move((r, c), (dest_row, dest_col), self.board))
                        break
                    else:                                   # if same color, stop
                        break
                else:                           # counting out of bounds
                    break

    def get_knight_moves(self, r, c, moves):
        movement = {(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2)}  # Knight 8 spots
        color = 'w' if self.white_to_move else 'b'
        for m in movement:
            dest_row = r + m[0]  # row + direction increment.
            dest_col = c + m[1]  # column + direction increment.
            if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:  # in bounds
                dest = self.board[dest_row][dest_col]
                if dest[0] != color:
                    moves.append(Move((r, c), (dest_row, dest_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        movement = {(-1, -1), (-1, 1), (1, 1), (1, -1)}  # SW, SE, NE, NW
        opposite_color = 'b' if self.white_to_move else 'w'
        for m in movement:
            for i in range(1, 8):
                dest_row = r + (m[0] * i)  # row + direction increment.
                dest_col = c + (m[1] * i)  # column + direction increment.
                if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:  # in bounds
                    dest = self.board[dest_row][dest_col]
                    if dest == "--":
                        moves.append(Move((r, c), (dest_row, dest_col), self.board))
                    elif dest[0] == opposite_color:  # If opposite color, can capture then stop
                        moves.append(Move((r, c), (dest_row, dest_col), self.board))
                        break
                    else:  # if same color, stop
                        break
                else:  # counting out of bounds
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        movement = {(-1, -1), (-1, 1), (1, 1), (1, -1), (-1, 0), (0, 1), (1, 0), (0, -1)}  # SW, SE, NE, NW, S, E, N, W
        color = 'w' if self.white_to_move else 'b'
        for m in movement:
            dest_row = r + m[0]  # row + direction increment.
            dest_col = c + m[1]  # column + direction increment.
            if 0 <= dest_row <= 7 and 0 <= dest_col <= 7:  # in bounds
                dest = self.board[dest_row][dest_col]
                if dest[0] != color:
                    moves.append(Move((r, c), (dest_row, dest_col), self.board))


class Move():
    # changing values to match chess board
    ranks_to_row = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_rank = {v: k for k, v in ranks_to_row.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    # Reformatting using items. Goes from dict_items([('a', 0,  ('b', 1), ...)] to {0: a, 1: b, ...}
    def __init__(self, start, end, board):  # start square, end square.
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

    def __eq__(self, other):
        if isinstance(other, Move):     # Making sure they are both objects of the class. Going to compare chess notation
            return self.get_chess_notation() == other.get_chess_notation()
        return False

    # Overriding equal methods to allow an object to compare to another object since I am using class objects
    # instead of directly using numbers for the moves

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_rank[r]
