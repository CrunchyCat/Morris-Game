# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project
# MorrisGame - The Main Logic for Calculating the Best Move by MiniMax/Alpha-Beta Pruning

import sys
from dataclasses import dataclass, field

class Morris:
    '''Configures the Game Board & Makes Optimal Moves'''
    states_reached = 0                          # Number of States Reached
    
    def __init__(self, max_depth: int, ab_pruning: bool, is_improved: bool, is_opening: bool, is_white=True):
        '''Configures the Game Parameters
        @param max_depth:   Maximum Depth of the Search
        @param ab_pruning:  True: MiniMax Algorithm, False: Alpha-Beta Pruning
        @param is_improved: True: Improved,          False: Standard
        @param is_opening:  True: Opening,           False: Endgame/Midgame
        @param is_white:    True: Player is White,   False: Player is Black'''
        self.MAX_DEPTH = max_depth
        self.IS_OPENING = is_opening
        self.pieces = Morris.Pieces() if is_white else Morris.Pieces('B', 'W')

        self.play = self.__alpha_beta if ab_pruning else self.__minimax
        self.move = self.__generate_add if is_opening else self.__generate_move
        self.static_estimation = self.__static_estimation_improved if is_improved else self.__static_estimation
    
    @dataclass
    class Pieces:
        '''Data Class to Store the Pieces'''
        player: str = 'W'
        opponent: str = 'B'
        EMPTY: str = 'x'
        # def swap(self):
        #     self.player, self.opponent = self.opponent, self.player

    @dataclass
    class Evaluator:
        '''Data Class to Store a Board & its Evaluation'''
        board: list[str] = field(default_factory=lambda: []) # Board
        evaluation: int = 0                     # Evaluation of the Board
    
    def __minimax(self, b: list[str], is_player_1=True, depth=0) -> Evaluator:
        '''MiniMax Algorithm
        @param b:           Board
        @param is_player_1: True: Player 1, False: Player 2
        @param depth:       Current Depth of the Search
        @return: Evaluation of the Board'''
        if depth >= self.MAX_DEPTH:
            Morris.states_reached += 1
            return Morris.Evaluator(b, self.static_estimation(b))
        if is_player_1:
            eval_best = Morris.Evaluator(evaluation=-sys.maxsize - 1)
            for move in self.move(b):
                eval_temp = self.__minimax(move, False, depth + 1).evaluation
                if eval_best.evaluation < eval_temp:
                    eval_best = Morris.Evaluator(move, eval_temp)
        else: # If Player #2
            eval_best = Morris.Evaluator(evaluation=sys.maxsize)
            for move in self.move(self.__invert_board(b)):
                eval_temp = self.__minimax(self.__invert_board(move), True, depth + 1).evaluation
                if eval_best.evaluation > eval_temp:
                    eval_best = Morris.Evaluator(move, eval_temp)
        return eval_best
    
    def __alpha_beta(self, b: list[str], is_player_1=True, depth=0, alpha=-sys.maxsize-1, beta=sys.maxsize) -> Evaluator:
        '''Alpha-Beta Pruning Algorithm
        @param b:           Board
        @param is_player_1: True: Player 1, False: Player 2
        @param depth:       Current Depth of the Search
        @param alpha:       Current Alpha Value
        @param beta:        Current Beta Value
        @return: Evaluation of the Board'''
        if depth >= self.MAX_DEPTH:
            Morris.states_reached += 1
            return Morris.Evaluator(b, self.static_estimation(b))
        if is_player_1:
            eval_best = Morris.Evaluator(evaluation=-sys.maxsize - 1)
            for move in self.move(b):
                eval_temp = self.__alpha_beta(move, False, depth + 1, max(alpha, eval_best.evaluation), beta).evaluation
                if eval_best.evaluation < eval_temp:
                    eval_best = Morris.Evaluator(move, eval_temp)
                if eval_best.evaluation >= beta:
                    return eval_best
        else: # If Player #2
            eval_best = Morris.Evaluator(evaluation=sys.maxsize)
            for move in self.move(self.__invert_board(b)):
                eval_temp = self.__alpha_beta(self.__invert_board(move), True, depth + 1, alpha, min(beta, eval_best.evaluation)).evaluation
                if eval_best.evaluation > eval_temp:
                    eval_best = Morris.Evaluator(move, eval_temp)
                if eval_best.evaluation <= alpha:
                    return eval_best
        return eval_best
    
    def __invert_board(self, b: list[str]):
        '''Inverts the Board (player <-> opponent)
        @param b: Board
        @return: Inverted Board'''
        return [self.pieces.opponent if i == self.pieces.player else self.pieces.player if i != self.pieces.EMPTY else i for i in b]
    
    def __generate_add(self, b: list[str]) -> list[list[str]]:
        '''Generates all Possible Moves that Add a Piece on the Board
        @param b: Board
        @return: List of Possible Moves'''
        L = []
        for b_temp, i in [([*b[:i], self.pieces.player, *b[i+1:]], i) for i in range(len(b)) if b[i] == self.pieces.EMPTY]:
            L += self.__generate_remove(b_temp) if Morris.__will_close_mill(b_temp, i) else [b_temp]
        return L

    def __generate_move(self, b: list[str]) -> list[list[str]]:
        '''Generates all Possible Moves that Move a Piece on the Board
        @param b: Board
        @return: List of Possible Moves'''
        L = []
        for loc1 in [i for i in range(len(b)) if b[i] == self.pieces.player]:
            for loc2 in [i for i in (range(len(b)) if b.count(self.pieces.player) == 3 else Morris.__neighbors(loc1)) if b[i] == self.pieces.EMPTY]:
                b_temp = b[:]
                b_temp[loc1] = self.pieces.EMPTY
                b_temp[loc2] = self.pieces.player
                L += self.__generate_remove(b_temp) if Morris.__will_close_mill(b_temp, loc2) else [b_temp]
        return L
    
    def __generate_remove(self, b: list[str]):
        '''Generates all Possible Moves that Remove a Piece from the Board
        @param b: Board
        @return: List of Possible Moves'''
        return [[*b[:i], self.pieces.EMPTY, *b[i+1:]] for i in range(len(b)) if b[i] == self.pieces.opponent and not Morris.__will_close_mill(b, i)]

    def __static_estimation(self, b: list[str]):
        '''Static Estimation of the Board
        @param b: Board
        @return: Evaluation of the Board'''
        num_player = b.count(self.pieces.player)
        num_opponent = b.count(self.pieces.opponent)
        if self.IS_OPENING:
            return num_player - num_opponent
        if num_opponent <= 2:
            return 10000
        if num_player <= 2:
            return -10000
        num_moves_opponent = len(self.__generate_move(self.__invert_board(b)))
        if num_moves_opponent == 0:
            return 10000
        return 1000 * (num_player - num_opponent) - num_moves_opponent
    
    def __static_estimation_improved(self, b: list[str]):
        '''Static Estimation of the Board (Improved)
        @param b: Board
        @return: Evaluation of the Board'''
        num_player = b.count(self.pieces.player)
        num_opponent = b.count(self.pieces.opponent)
        num_moves_opponent = 0 if self.IS_OPENING else len(self.__generate_move(self.__invert_board(b)))
        if not self.IS_OPENING:
            if num_opponent <= 2 or num_moves_opponent == 0:
                return sys.maxsize
            if num_player <= 2:
                return -sys.maxsize - 1

        return (175 * len(self.__pieces_in_premill(b)) * (1 if num_player < 4 else 2)   # x2 Value if in Endgame
            + 125 * len(self.__pieces_blocking_mill(b)) * (2 if num_player < 4 else 1)  # x2 Value if in Midgame
            - (10 * num_moves_opponent)             # Penalty for Opponent Having Choices
            + 200 * (num_player - num_opponent))    # Value for Having More Pieces

    @staticmethod
    def __will_close_mill(b: list[str], loc: int, piece=None):
        '''Returns whether the Piece at Location loc will Close a Mill
        @param b:     The Board
        @param loc:   The Location of the Piece
        @param piece: The Piece at the Location
        @return: True if the Piece at Location loc will Close a Mill, False Otherwise'''
        C = b[loc] if piece == None else piece
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

    @staticmethod
    def __neighbors(loc: int):
        '''Returns the List of the neighbors for a Location
        @param loc: Location
        @return: List of Locations'''
        return {
            0: [1, 2, 6],           1: [0, 3, 11],          2: [0, 3, 4, 7],
            3: [1, 2, 5, 10],       4: [2, 5, 8],           5: [3, 4, 9],
            6: [0, 7, 18],          7: [2, 6, 8, 15],       8: [4, 7, 12],
            9: [5, 10, 14],         10: [3, 9, 11, 17],     11: [1, 10, 20],
            12: [8, 13, 15],        13: [12, 14, 16],       14: [9, 13, 17],
            15: [7, 12, 16, 18],    16: [13, 15, 17, 19],   17: [10, 14, 16, 20],
            18: [6, 15, 19],        19: [16, 18, 20],       20: [11, 17, 19]
        }[loc]
    
    def __pieces_in_premill(self, b: list[str]):
        '''Calculates a List of Locations Where a Mill would Form if a Piece is Placed at a Location
        @param b: Board
        @return: List of Locations'''
        return [i for i in range(len(b)) if b[i] == self.pieces.EMPTY and Morris.__will_close_mill(b, i, self.pieces.player)]

    def __pieces_blocking_mill(self, b: list[str]):
        '''Calculates a List of Player Pieces Blocking a Mill
        @param b: Board
        @return: List of Player Pieces blocking a Mill'''
        return [a for i in range(len(b)) if b[i] == self.pieces.opponent for a in Morris.__neighbors(i) if b[a] == self.pieces.player and
        [i for i in Morris.__neighbors(a) if b[i] == self.pieces.player and not Morris.__will_close_mill(b, a, self.pieces.player)]]

def test(argv: list[str], ab_pruning: bool, is_improved: bool, is_opening: bool, is_white=True):
    '''Tests the Program with the Given Parameters & Prints Results
        @param argv:        List of Command-Line Arguments (input, output, max-depth)
        @param ab_pruning:  True: MiniMax Algorithm, False: Alpha-Beta Pruning
        @param is_improved: True: Improved,          False: Standard
        @param is_opening:  True: Opening,           False: Endgame/Midgame
        @param is_white:    True: Player is White,   False: Player is Black'''
    # Check Input Arguments
    if len(argv) < 4:                           # Check for Missing Arguments
        print("Missing Command-Line Arguments\n" +
        "Usage: python3 Program_name.py <File: Input Board> <File: Output Board> <Depth>")
        sys.exit("Exiting...")
    if len(argv) > 4:                           # Check for Extra Arguments
        print("Extra Command-Line Arguments\n" +
        "Usage: python3 Program_name.py <File: Input Board> <File: Output Board> <Depth>")

    # Read Input Board, Play Board, & Write Output Board
    input = [i for i in open(argv[1], "r").read().strip()]  # Input: File to Board
    output = Morris(int(argv[3]), ab_pruning, is_improved, is_opening, is_white).play(input)
    open(argv[2], "w").write(''.join(output.board)) # Output: Board to File

    # Print Results
    print("   Board Input: ", *input, sep = "")
    print("Board Position: ", *output.board, sep = "")
    print("Positions evaluated by static estimation:", Morris.states_reached)
    print("ALPHA-BETA estimate" if ab_pruning else "MINIMAX estimate:", output.evaluation)