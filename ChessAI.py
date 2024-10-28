import random
from decimal import Decimal

piece_score = {"K": Decimal(0), "Q": Decimal('9.5'), "R": Decimal(5), "B": Decimal('3.3'), "N": Decimal(3),
               "P": Decimal(1)}
checkmate = 100
stalemate = 0
DEPTH = 3
next_move = None
recursion_count = 0

# This is denoting point value for pawns in certain positions. Value in terms of white in my view
pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [7, 7, 7, 7, 7, 7, 7, 7],
            [4, 4, 4, 4, 4, 4, 4, 4],
            [Decimal('1.5'), Decimal('1.5'), 2, 2, 2, 2, Decimal('1.5'), Decimal('1.5')],
            [0, 0, Decimal('0.5'), 2, 2, Decimal('0.5'), 0, 0],
            [Decimal('0.5'), 0, 0, 1, 1, 0, 0, Decimal('0.5')],
            [Decimal('0.5'), Decimal('0.5'), 1, 1, 1, 1, Decimal('0.5'), Decimal('0.5')],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

knight_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, Decimal('0.5'), 1, 2, 2, 1, Decimal('0.5'), 0],
        [0, 0, 1, 2, 2, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

test = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0]
    ]


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]        # returns number between a and b including a and b


# Non-recursive
def find_best_move(gamestate, valid_moves):
    turn_value = 1 if gamestate.white_to_move else -1
    minimax_score = checkmate
    best_move = None
    random.shuffle(valid_moves)                     # Randomly shuffle moves.
    for player_move in valid_moves:
        gamestate.make_move(player_move)
        opponent_moves = gamestate.get_valid_moves()    # making move already switches turn order
        if gamestate.stalemate:
            opponent_max_score = stalemate
        elif gamestate.checkmate:
            opponent_max_score = -checkmate
        else:
            opponent_max_score = -checkmate
            for opponent_move in opponent_moves:
                gamestate.make_move(opponent_move)
                gamestate.get_valid_moves()
                # Have to generate valid moves to see if there is a checkmate. This now also lags it really hard.
                if gamestate.checkmate:
                    score = checkmate  # Everything is - now because two moves ahead
                elif gamestate.stalemate:
                    score = stalemate
                else:
                    # Black's view. Wants to minimize.
                    # White's view. Wants to maximize.
                    score = -turn_value * score_board(gamestate)
                    opponent_max_score = max(opponent_max_score, score)
                gamestate.undo_move(False)
        if minimax_score > opponent_max_score:
            minimax_score = opponent_max_score
            best_move = player_move
        elif minimax_score == opponent_max_score:   # Randomly change move if they have same value
            if random.randint(0,9) < 3:
                best_move = player_move
        gamestate.undo_move(False)
    return best_move


def find_best_move_minimax(gamestate, valid_moves):
    global next_move, recursion_count
    next_move = None
    recursion_count = 0             # for debugging
    random.shuffle(valid_moves)
    # minimax_move(gamestate, valid_moves, DEPTH, gamestate.white_to_move)
    negamax_move(gamestate, valid_moves, DEPTH, 1 if gamestate.white_to_move else -1)
    print(recursion_count)
    return next_move


def minimax_move(gamestate, valid_moves, depth, white_to_move, alpha=-1000, beta=1000):
    global next_move
    if depth == 0:
        return score_board(gamestate)
    search = 0
    min_move_search = 5
    # This is so it will check at least a couple as not ordered therefore can exist a better move

    if white_to_move:
        max_score = -checkmate  # worst score possible
        for move in valid_moves:
            gamestate.make_move(move)
            new_valid_moves = gamestate.get_valid_moves()
            # switch beta and alpha because we are looking in the opponent view
            score = minimax_move(gamestate, new_valid_moves, depth - 1, False, beta, alpha)
            alpha = max(alpha, score)
            search += 1
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            elif score == max_score:  # Randomly change move if they have same value
                if random.randint(0, 9) < 3:
                    if depth == DEPTH:
                        next_move = move
            if alpha >= beta and search >= min_move_search:  # if max is > minimum, no more reason to look in this tree.
                gamestate.undo_move(False)
                break

            gamestate.undo_move(False)
        return max_score
    else:
        min_score = checkmate
        for move in valid_moves:
            gamestate.make_move(move)
            new_valid_moves = gamestate.get_valid_moves()
            # switch beta and alpha because we are looking in the opponent view
            score = minimax_move(gamestate, new_valid_moves, depth - 1, True, beta, alpha)
            beta = min(beta, score)
            search += 1
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            elif score == min_score:  # Randomly consider changing move if they have same value
                if random.randint(0, 9) < 3:
                    if depth == DEPTH:
                        next_move = move
            if alpha <= beta and search >= min_move_search:  # if min is > maximum, no more reason to look in this tree.
                gamestate.undo_move(False)
                break

            gamestate.undo_move(False)
        return min_score


# General Flow: Continue until depth 0, find best possible score to the first response to a player's move
# EX: 3. Black -> 2. White -> 1. Black Search all moves and find best answer to White's move
# At 2nd White Responses, if white can 'beat' this number, as >= is worst for black so no need to check others
# It will then use these values to find white's possible best response to Black's initial move, repeating.
def negamax_move(gamestate, valid_moves, depth, turn_multiplier, alpha=-1000, beta=1000):
    global next_move, recursion_count
    search = 0
    min_move_search = 7
    # This is here because my sorting is terrible so quite a likely chance for better move to exist
    recursion_count += 1    # for debugging
    if depth == 0:
        return turn_multiplier * score_board(gamestate)
    max_score = -checkmate
    for move in valid_moves:
        gamestate.make_move(move)
        new_valid_moves = gamestate.get_valid_moves()
        # it will always search from top left to bottom right piece of a color's pieces
        random.shuffle(new_valid_moves)
        # switch beta and alpha because we are looking in the opponent view
        score = -negamax_move(gamestate, new_valid_moves, depth - 1, -turn_multiplier, -beta, -alpha)
        alpha = max(alpha, score)       # Maximum of all moves
        search += 1
        if score >= max_score:
            max_score = score
            if depth == DEPTH:
                if score > max_score:
                    next_move = move
                else:
                    if random.randint(0, 9) < 3:    # Randomly consider changing move if they have same value
                        next_move = move
        # if max is > minimum, no more reason to look in this tree.
        if alpha >= beta and search >= min_move_search:
            gamestate.undo_move(False)
            break

        gamestate.undo_move(False)
    return max_score


# this will track importance of location instead of just material.
def score_board(gamestate):
    if gamestate.checkmate:
        if gamestate.white_to_move:
            return -checkmate   # black wins
        else:
            return checkmate    # white wins
    elif gamestate.stalemate:
        return stalemate
    score = 0

    for row in range(len(gamestate.board)):
        for square in range(len(gamestate.board)):
            if gamestate.board[row][square][0] == 'w':  # White is advantage at positive
                score += piece_score[gamestate.board[row][square][1]]
                if gamestate.board[row][square][1] == 'P':
                    score += pawn_table[row][square]
                if gamestate.board[row][square][1] == 'N':
                    score += knight_table[row][square]
            elif gamestate.board[row][square][0] == 'b':  # Black is advantage at negative
                score -= piece_score[gamestate.board[row][square][1]]
                if gamestate.board[row][square][1] == 'P':
                    score -= pawn_table[::-1][row][square]
                if gamestate.board[row][square][1] == 'N':
                    score -= knight_table[::-1][row][square]
    return score


def score_material(board):
    score = 0

    for row in range(len(board)):
        for square in range(len(board)):
            if board[row][square][0] == 'w':  # White is advantage at positive
                score += piece_score[board[row][square][1]]
            elif board[row][square][0] == 'b':  # Black is advantage at negative
                score -= piece_score[board[row][square][1]]
    return score


def basic_test(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':  # White is advantage at positive
                score += piece_score[square[1]]
            elif square[0] == 'b':  # Black is advantage at negative
                score -= piece_score[square[1]]
    return score
