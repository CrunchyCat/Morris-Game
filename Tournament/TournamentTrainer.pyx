# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project (Tournament Version)
# MorrisGame - The Main Logic for Calculating the Best Move by MiniMax/Alpha-Beta Pruning
# This File has been Modified to Decrease Memory Usage & Increase Speed (See MorrisGame.py)

from typing import List, Tuple
import cython

# Variable Declaration
cdef int ITERATIONS
cdef int MAX_MOVES
cdef int NUM_PIECES
cdef int MAX_SIZE
cdef int MIN_SIZE
cdef int i_game
cdef int i_move

# Input Parameters
BOARD_NAME = "boards/board_empty.txt"   # Starting Board to Use
ITERATIONS = 3                          # Number of Games to Play (Should be Odd #, Start First 1/2 the Time)
MAX_MOVES = 1_000                       # Maximum # of Moves to Make Per Game
NUM_PIECES = 16                         # Total Pieces to Play before Midgame Phase (2 x # Pieces per Player)

# Constants
MAX_SIZE = 2147483647
MIN_SIZE = -2147483647

# Configures the Game Board & Makes Optimal Moves
class Morris:
    # Configures the Game Parameters
    # @param max_depth:   Maximum Depth of the Search
    # @param is_improved: True: Improved,          False: Standard
    # @param is_white:    True: Player is White,   False: Player is Black
    def __init__(self, max_depth: int, is_improved: bool, is_white=True):
        self.MAX_DEPTH = max_depth
        self.EMPTY = 'x'
        if is_white:
            self.PLAYER = 'W'
            self.OPPONENT = 'B'
        else:
            self.PLAYER = 'B'
            self.OPPONENT = 'W'
        self.static_estimation = self.__static_estimation_improved if is_improved else self.__static_estimation

    # Alpha-Beta Pruning Algorithm
    # @param b:           Board
    # @param is_opening   True: Opening, False: Not Opening
    # @param depth:       Current Depth of the Search
    # @param alpha:       Current Alpha Value
    # @param beta:        Current Beta Value
    # @return: Evaluation of the Board
    def play(self, b: List[str], is_opening: bool, depth: int=0, alpha=MIN_SIZE, beta=MAX_SIZE) -> Tuple[int, List[str]]:
        if depth >= self.MAX_DEPTH:
            return (self.static_estimation(b, is_opening), b)
        move_best: List[str] = ["RESIGN"] # Resign if No Possible Moves
        if depth % 2 == 0: # If player #1
            eval_best = MIN_SIZE
            for move in self.move(b, is_opening):
                eval_temp = self.play(move, is_opening, depth + 1, max(alpha, eval_best), beta)[0]
                if eval_temp > eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best >= beta:
                    return (eval_best, move_best)
        else: # If Player #2
            eval_best = MAX_SIZE
            for move in self.move(self.__invert_board(b), is_opening):
                eval_temp = self.play(self.__invert_board(move), is_opening, depth + 1, alpha, min(beta, eval_best))[0]
                if eval_temp < eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best <= alpha:
                    return (eval_best, move_best)
        return (eval_best, move_best)

    # Generates all Moving Moves
    # @param b: Board
    # @return: List of Possible Moves
    def move(self, b: List[str], is_opening: bool) -> List[List[str]]:
        L = []
        if is_opening:
            for i in [i for i in range(len(b)) if b[i] == self.EMPTY]:
                b_temp = [*b[:i], self.PLAYER, *b[i+1:]]     # Add Piece to Board at Location i
                L += self.__generate_remove(b_temp) if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
            return L
        for o in [i for i in range(len(b)) if b[i] == self.PLAYER]:
            for i in [i for i in (range(len(b)) if b.count(self.PLAYER) == 3 else neighbors(o)) if b[i] == self.EMPTY]:
                b_temp = [*b[:i], self.PLAYER, *b[i+1:]] # Add a Piece to Board at Location i
                b_temp[o] = self.EMPTY                   # Remove Piece from Origin Location o
                L += self.__generate_remove(b_temp) if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
        return L

    # Generates all Removal Moves
    # @param b: Board
    # @return: List of Possible Moves
    def __generate_remove(self, b: List[str]):
        return [[*b[:i], self.EMPTY, *b[i+1:]] for i in range(len(b)) if b[i] == self.OPPONENT and not will_close_mill(b, i)]

    # Static Estimation of the Board
    # @param b: Board
    # @return: Evaluation of the Board
    def __static_estimation(self, b: List[str], is_opening: bool) -> int:
        num_player = b.count(self.PLAYER)
        num_opponent = b.count(self.OPPONENT)
        if is_opening:
            return num_player - num_opponent
        if num_opponent <= 2:
            return 10000
        if num_player <= 2:
            return -10000
        num_moves_opponent = len(self.move(self.__invert_board(b), is_opening))
        if num_moves_opponent == 0:
            return 10000
        return 1000 * (num_player - num_opponent) - num_moves_opponent

    # Static Estimation of the Board (Improved)
    # @param b: Board
    # @return: Evaluation of the Board
    def __static_estimation_improved(self, b: List[str], is_opening: bool) -> int:
        num_player = b.count(self.PLAYER)
        num_opponent = b.count(self.OPPONENT)
        num_moves_opponent = 0 if is_opening else len(self.move(self.__invert_board(b), is_opening))
        if not is_opening:
            if num_opponent < 3:
                return MAX_SIZE
            if num_player < 3:
                return MIN_SIZE

        return (100 * len(self.__pieces_in_premill(b)) * (1 if num_player < 4 else 2)   # x2 Value if in Endgame
            + 100 * len(self.__pieces_in_double_mill(b)) * (2 if num_player < 4 else 1)  # x2 Value if in Midgame
            - (1 * num_moves_opponent)             # Penalty for Opponent Having Choices
            + 1000 * (num_player - num_opponent))    # Value for Having More Pieces
    
    # Inverts the Board (player <-> opponent)
    # @param b: Board
    # @return: Inverted Board
    def __invert_board(self, b: List[str]):
        return [self.OPPONENT if i == self.PLAYER else self.PLAYER if i != self.EMPTY else i for i in b]

    # Calculates a List of Locations Where a Mill would Form if a Piece is Placed at a Location
    # @param b: Board
    # @return: List of Locations
    def __pieces_in_premill(self, b: List[str]):
        return [i for i in range(len(b)) if b[i] == self.EMPTY and will_close_mill(b, i, self.PLAYER)]

    # Calculates a List of Player Pieces in a Double Mill
    # @param b: Board
    # @return: List of Player Pieces in a Double Mill
    def __pieces_in_double_mill(self, b: List[str]):
        return [a for i in range(len(b)) if b[i] == self.OPPONENT for a in neighbors(i) if b[a] == self.PLAYER and
        [i for i in neighbors(a) if b[i] == self.PLAYER and not will_close_mill(b, a, self.PLAYER)]]

# Returns whether a Piece at Location loc will Close a Mill (Optional, check with Hypothetical Piece)
# @param b:     The Board
# @param loc:   The Location of the Piece
# @param piece: A Hypothetical Piece at the Location [OPTIONAL]
# @return: True if the Piece at Location loc will Close a Mill, False Otherwise
@cython.cfunc
def will_close_mill(b: List[str], loc: int, piece: str=None):
    C = piece or b[loc]
    return {
        0: (b[2] == b[4] == C)    or (b[6] == b[18] == C),
        1: (b[3] == b[5] == C)    or (b[11] == b[20] == C),
        2: (b[0] == b[4] == C)    or (b[7] == b[15] == C),
        3: (b[1] == b[5] == C)    or (b[10] == b[17] == C),
        4: (b[0] == b[2] == C)    or (b[8] == b[12] == C),
        5: (b[1] == b[3] == C)    or (b[9] == b[14] == C),
        6: (b[0] == b[18] == C)   or (b[7] == b[8] == C),
        7: (b[2] == b[15] == C)   or (b[6] == b[8] == C),
        8: (b[4] == b[12] == C)   or (b[6] == b[7] == C),
        9: (b[5] == b[14] == C)   or (b[10] == b[11] == C),
        10: (b[3] == b[17] == C)  or (b[9] == b[11] == C),
        11: (b[1] == b[20] == C)  or (b[9] == b[10] == C),
        12: (b[4] == b[8] == C)   or (b[13] == b[14] == C)  or (b[15] == b[18] == C),
        13: (b[12] == b[14] == C) or (b[16] == b[19] == C),
        14: (b[5] == b[9] == C)   or (b[12] == b[13] == C)  or (b[17] == b[20] == C),
        15: (b[2] == b[7] == C)   or (b[12] == b[18] == C)  or (b[16] == b[17] == C),
        16: (b[13] == b[19] == C) or (b[15] == b[17] == C),
        17: (b[3] == b[10] == C)  or (b[14] == b[20] == C)  or (b[15] == b[16] == C),
        18: (b[0] == b[6] == C)   or (b[12] == b[15] == C)  or (b[19] == b[20] == C),
        19: (b[13] == b[16] == C) or (b[18] == b[20] == C),
        20: (b[1] == b[11] == C)  or (b[14] == b[17] == C)  or (b[18] == b[19] == C)
    }[loc]

# Returns the List of the neighbors for a Location
# @param loc: Location
# @return: List of Locations
@cython.cfunc
def neighbors(loc: int):
    return {
        0: [1, 2, 6],           1: [0, 3, 11],          2: [0, 3, 4, 7],
        3: [1, 2, 5, 10],       4: [2, 5, 8],           5: [3, 4, 9],
        6: [0, 7, 18],          7: [2, 6, 8, 15],       8: [4, 7, 12],
        9: [5, 10, 14],         10: [3, 9, 11, 17],     11: [1, 10, 20],
        12: [8, 13, 15],        13: [12, 14, 16],       14: [9, 13, 17],
        15: [7, 12, 16, 18],    16: [13, 15, 17, 19],   17: [10, 14, 16, 20],
        18: [6, 15, 19],        19: [16, 18, 20],       20: [11, 17, 19]
    }[loc]

import time # TODO: REMOVE TIMER

if __name__ == "__main__":
    t1 = time.time() # TODO: REMOVE TIMER START

    # Initialize White & Black Players
    white = Morris(4, True, True)   # White Player Full Game
    black = Morris(4, False, False) # Black Player Full Game

    # Initialize List to Store Game Results
    white_win_boards = []
    black_win_boards = []

    # Read Board from File
    board_start = [i for i in open(BOARD_NAME, "r").read().strip()]

    # Play Games
    for i_game in range(1, ITERATIONS):
        board_state = (0, board_start)
        turn_white = start_white = i_game % 2 == 0  # Alternate Starting Player
        print("-----------------------------------{0:10s}-----------------------------------".format("Game #" + str(i_game)))
        print(("   0) Start: "), *board_start, sep="")
        for i_move in range(MAX_MOVES):
            turn_white = not turn_white
            is_opening = i_move < NUM_PIECES
            board_state = white.play(board_state[1], is_opening) if turn_white else black.play(board_state[1], is_opening)
            print(("{0:4d}) " + ("White" if turn_white else "Black") + ": ").format(i_move + 1), *board_state[1], ' Eval: ', board_state[0], sep="")
            if board_state[0] >= MAX_SIZE:
                print("-----------> " + ("WHITE" if turn_white else "BLACK") + " WINS!")
                white_win_boards.append(board_state[1]) if turn_white else black_win_boards.append(board_state[1])
                break
            if board_state[0] <= MIN_SIZE:
                print("-----------> " + ("BLACK" if turn_white else "WHITE") + " WINS!")
                black_win_boards.append(board_state[1]) if turn_white else white_win_boards.append(board_state[1])
                break
        else:
            print("-----------> MOVE LIMIT REACHED!")

    # Print Aggregated Final Results
    print("---------------------------------Final Results ---------------------------------")
    print('White Wins:', len(white_win_boards))
    print('Black Wins:', len(black_win_boards))

    t2 = time.time()    #TODO: REMOVE TIMER END
    print("Time Taken: %.8fs" % (t2-t1)) #TODO: REMOVE TIMER END