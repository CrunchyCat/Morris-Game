# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project (Tournament Version)
# Modified Version to Decrease Memory Usage & Increase Speed (See Submission/MorrisGame.py)

# Input Parameters
BOARD_NAME = "boards/board_empty.txt"   # Starting Board to Use
ITERATIONS = 3                          # N+1 Games to Play (Should be Odd #, Start 1st Every Other Game)
MAX_MOVES = 200                         # Maximum # of Moves to Make Per Game
NUM_PIECES = 8                          # Pieces Each Player has to Play During Opening Phase

# Constants
MAX_SIZE = 2147483647
MIN_SIZE = -2147483647

# Configures the Game Board & Makes Optimal Moves
class Morris:
    # Configures the Game Parameters
    # @param num_pieces:  # of Pieces to Play During Opening Game
    # @param empty:       Symbol for Empty Space 
    # @param player:      Symbol for the Player
    # @param opponent:    Symbol for the Opponent
    # @param max_depth:   Maximum Depth of the Search
    # @param is_improved: True: Improved,          False: Standard
    def __init__(self, num_pieces: int, empty: str, player: str, opponent: str, max_depth: int, is_improved: bool):
        self.NUM_PIECES = num_pieces        # Number of Player Pieces to Play During Opening Game
        self.moves_made = 0                 # N-1 Moves Made (Used to Determine if in Opening Game)
        self.EMPTY = empty                  # Symbol for Empty Space
        self.PLAYER = player                # Symbol for the Player
        self.OPPONENT = opponent            # Symbol for the Opponent
        self.MAX_DEPTH = max_depth          # Maximum Depth of the Search
        self.static_estimation = self.__static_estimation_improved if is_improved else self.__static_estimation

    # Makes Optimal Move by Calling Alpha-Beta Pruning Algorithm
    # @param b:           Board
    # @return: Tuple of (Board after Move, Static Evaluation of the Board)
    def play(self, b: str) -> tuple[int, str]:
        self.moves_made += 1
        return self.__ab(b)
    
    # Alpha-Beta Pruning Algorithm
    # @param b:           Board
    # @param depth:       Current Depth of the Search
    # @param alpha:       Current Alpha Value
    # @param beta:        Current Beta Value
    # @return: Tuple of (Board after Move, Static Evaluation of the Board)
    def __ab(self, b: str, depth: int=0, alpha=MIN_SIZE, beta=MAX_SIZE) -> tuple[int, str]:
        if depth >= self.MAX_DEPTH:
            return (self.static_estimation(b, self.moves_made + int(depth / 2) <= self.NUM_PIECES), b)
        move_best: str = "RESIGN"
        if depth % 2 == 0: # If player #1
            eval_best = MIN_SIZE
            for move in self.move(b, self.moves_made + int(depth / 2) <= self.NUM_PIECES):
                eval_temp = self.__ab(move, depth + 1, max(alpha, eval_best), beta)[0]
                if eval_temp > eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best >= beta:
                    return (eval_best, move_best)
        else: # If Player #2
            eval_best = MAX_SIZE
            for move in self.move(self.__invert_board(b), self.moves_made + int(depth / 2) <= self.NUM_PIECES):
                eval_temp = self.__ab(self.__invert_board(move), depth + 1, alpha, min(beta, eval_best))[0]
                if eval_temp < eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best <= alpha:
                    return (eval_best, move_best)
        return (eval_best, move_best)

    # Generates all Moving Moves
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: List of Possible Moves
    def move(self, b: str, is_opening: bool) -> list[str]:
        L = []
        if is_opening:
            for i in [i for i in range(len(b)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.PLAYER + b[i+1:]
                L += self.__generate_remove(b_temp) if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
            return L
        for o in [i for i in range(len(b)) if b[i] == self.PLAYER]:
            for i in [i for i in (range(len(b)) if b.count(self.PLAYER) == 3 else neighbors(o)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.PLAYER + b[i+1:]          # Add a Piece to Board at Location i
                b_temp = b_temp[:o] + self.EMPTY + b_temp[o+1:] # Remove Piece from Origin Location o
                L += self.__generate_remove(b_temp) if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
        return L

    # Generates all Removal Moves
    # @param b: Board
    # @return: List of Possible Moves
    def __generate_remove(self, b: str) -> list[str]:
        return [b[:i] + self.EMPTY + b[i+1:] for i in range(len(b)) if b[i] == self.OPPONENT and not will_close_mill(b, i, self.OPPONENT)]

    # Static Estimation of the Board
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: Evaluation of the Board
    def __static_estimation(self, b: str, is_opening: bool) -> int:
        num_player = b.count(self.PLAYER)
        num_opponent = b.count(self.OPPONENT)
        if is_opening:
            return num_player - num_opponent
        num_moves_opponent = len(self.move(self.__invert_board(b), is_opening))
        if num_opponent < 3:
            return 10000
        if num_player < 3:
            return -10000
        if num_moves_opponent == 0:
            return 10000
        return 1000 * (num_player - num_opponent) - num_moves_opponent

    # Static Estimation of the Board (Improved, Slow)
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: Evaluation of the Board
    def __static_estimation_OLD(self, b: str, is_opening: bool) -> int:
        num_player = b.count(self.PLAYER)
        num_opponent = b.count(self.OPPONENT)
        if is_opening: # Opening Estimation
            return (
                # +18 if Mill is Closed, -18 if Opponent Mill Closed
                18 * (self.__num_mills(b, self.PLAYER) - self.__num_mills(b, self.OPPONENT))
                + 1 * (self.__num_pieces_blocked(b , self.OPPONENT) - self.__num_pieces_blocked(b, self.PLAYER))
                + 1 * (num_player - num_opponent)
                + 5 * (len(self.__pieces_in_premill(b, self.PLAYER)) - len(self.__pieces_in_premill(b, self.OPPONENT)))
                # + 7 * # of Difference in Double Premills
            )
        if num_opponent < 3:
            return MAX_SIZE
        if num_player < 3:
            return MIN_SIZE
        if len(self.move(self.__invert_board(b), is_opening)) == 0:
            return MAX_SIZE
        is_win = num_opponent < 3 or len(self.move(self.__invert_board(b), is_opening)) == 0
        is_loss = num_player < 3 or len(self.move(b, is_opening)) == 0
        if num_player == 3: # Endgame Estimation
            return (
                # +16 if Mill is Closed, -16 if Opponent Mill Closed
                8 * (len(self.__pieces_in_premill(b, self.PLAYER)) - len(self.__pieces_in_premill(b, self.OPPONENT)))
                # + 1 * # of Difference in Double Premills
                + 95 * (1 if is_win else -1 if is_loss else 0)
            )
        return ( # Midgame Estimation
                # +14 if Mill is Closed, -14 if Opponent Mill Closed
                14 * (self.__num_mills(b, self.PLAYER) - self.__num_mills(b, self.OPPONENT))
                + 10 * (self.__num_pieces_blocked(b , self.OPPONENT) - self.__num_pieces_blocked(b, self.PLAYER))
                + 17 * (num_player - num_opponent)
                # + 8 * # of Double Mills
                + 1728 * (1 if is_win else -1 if is_loss else 0)
        )   # Value for Having More Pieces
    
    # Static Estimation of the Board (Improved, Fast)
    # #TODO: Make Faster by Separating Game Phases & Not Using __generate_remove
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: Evaluation of the Board 
    def __static_estimation_improved(self, b: str, is_opening: bool) -> int:
        # Features to Calculate
        num_pieces_opponent = b.count(self.OPPONENT)
        num_pieces_player = b.count(self.PLAYER)
        # if not is_opening:
        #     if num_pieces_opponent < 3: return MAX_SIZE # Stop if Player Won
        #     if num_pieces_player < 3: return MIN_SIZE   # Stop if Player Lost
        num_moves_player = 0
        num_moves_opponent = 0
        num_pieces_mill_player = 0
        num_pieces_mill_opponent = 0
        num_pieces_blocked_player = 0
        num_pieces_blocked_opponent = 0
        num_pieces_premill_player = 0
        num_pieces_premill_opponent = 0
        num_double_premill_player = 0
        num_double_premill_opponent = 0
        # num_double_mill_player = 0 #TODO: Calculate These Features
        # num_double_mill_opponent = 0
        
        # Feature Calculation
        for pos in range(len(b)):
            if b[pos] == self.PLAYER:
                if will_close_mill(b, pos, self.PLAYER):
                    num_pieces_mill_player += 1
                elif len([j for j in neighbors(pos) if b[j] == self.PLAYER]) > 1:
                    num_double_premill_player += 1
                if not [j for j in neighbors(pos) if b[j] == self.EMPTY]:
                    num_pieces_blocked_player += 1
                if not is_opening:
                    for i in [i for i in (range(len(b)) if num_pieces_player == 3 else neighbors(pos)) if b[i] == self.EMPTY]:
                        b_temp = b[:pos] + self.EMPTY + b[pos+1:]
                        num_moves_player += len(self.__generate_remove(b_temp[:i] + self.PLAYER + b_temp[i+1:])) if will_close_mill(b, i, self.PLAYER) else 1
            elif b[pos] == self.OPPONENT:
                if will_close_mill(b, pos, self.OPPONENT):
                    num_pieces_mill_opponent += 1
                elif len([j for j in neighbors(pos) if b[j] == self.OPPONENT]) > 1:
                    num_double_premill_opponent += 1
                if not [j for j in neighbors(pos) if b[j] == self.EMPTY]:
                    num_pieces_blocked_opponent += 1
                if not is_opening:
                    for i in [i for i in (range(len(b)) if num_pieces_opponent == 3 else neighbors(pos)) if b[i] == self.EMPTY]:
                        b_temp = b[:pos] + self.EMPTY + b[pos+1:]
                        num_moves_opponent += len(self.__generate_remove(b_temp[:i] + self.OPPONENT + b_temp[i+1:])) if will_close_mill(b, i, self.OPPONENT) else 1
            elif b[pos] == self.EMPTY:
                if will_close_mill(b, pos, self.PLAYER):
                    num_pieces_premill_player += 1
                elif will_close_mill(b, pos, self.OPPONENT):
                    num_pieces_premill_opponent += 1
                if is_opening:
                    num_moves_player += len(self.__generate_remove(b[:pos] + self.PLAYER + b[pos+1:])) if will_close_mill(b, pos, self.PLAYER) else 1
                    num_moves_opponent += len(self.__generate_remove(b[:pos] + self.OPPONENT + b[pos+1:])) if will_close_mill(b, pos, self.OPPONENT) else 1

        # Static Estimation Features
        if is_opening: # Opening Estimation
            return (
                9 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 1 * (num_pieces_opponent - num_pieces_opponent)
                + 9 * (num_pieces_player - num_pieces_opponent)
                + 4 * (num_pieces_premill_player - num_pieces_premill_opponent)
                + 3 * (num_double_premill_player - num_double_premill_opponent)
            )
        is_win = num_moves_opponent == 0 or num_pieces_opponent < 3
        is_loss = num_moves_player == 0 or num_pieces_player < 3
        if num_pieces_player == 3:
            return ( # Endgame Estimation
                3 * (num_pieces_premill_player - num_pieces_premill_opponent)
                + 1 * (num_double_premill_player - num_double_premill_opponent)
                + 1190 * (1 if is_win == 0 else -1 if is_loss == 0 else 0)
            )
        return ( # Midgame Estimation
                14 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 10 * (num_pieces_blocked_opponent - num_pieces_blocked_player)
                + 11 * (num_pieces_player - num_pieces_opponent)
                #TODO: + 8 * # of Double Mills
                + 1086 * (1 if is_win else -1 if is_loss == 0 else 0)
        )
    
    # Inverts the Board (player <-> opponent)
    # @param b: Board
    # @return: Inverted Board
    def __invert_board(self, b: str) -> str:
        return ''.join([self.OPPONENT if i == self.PLAYER else self.PLAYER if i != self.EMPTY else i for i in b])

    # Returns the # of Mills for the Piece
    # @param b: Board
    # @param p: Piece
    # @return: # of Mills for the Piece
    def __num_mills(self, b: str, p: str) -> str:
        if b.count(p) < 3:
            return 0
        pieces = len([i for i in range(len(b)) if b[i] == p and will_close_mill(b, i, p)])
        return 3 if pieces > 6 else 2 if pieces > 4 else 1 if pieces > 2 else 0

    # Returns # of Pieces Blocked
    # @param b: Board
    # @param p: Piece
    # @return: # of Pieces Blocked
    def __num_pieces_blocked(self, b: str, p: str) -> int:
        return b.count(p) - len(set(
            [i for i in range(len(b)) if b[i] == p for j in neighbors(i) if b[j] == self.EMPTY]
        ))

    # Calculates a List of Locations that would Complete a Mill
    # @param b: Board
    # @return: List of Locations that would Complete a Mill
    def __pieces_in_premill(self, b: str, p: str) -> list[int]:
        return [i for i in range(len(b)) if b[i] == self.EMPTY and will_close_mill(b, i, p)]
    
    #TODO: Implement: Pieces in Double Mill def __pieces_in_double(self, b: str) -> list[int]:

# Returns whether a Piece at Location loc will Close a Mill (Optional, check with Hypothetical Piece)
# @param b:     The Board
# @param loc:   The Location of the Piece
# @param p:     The Hypothetical Piece at the Location
# @return: True if the Piece at Location loc will Close a Mill, False Otherwise
def will_close_mill(b: str, loc: int, p: str=None) -> bool:
    return {
        0: (b[2] == b[4] == p)    or (b[6] == b[18] == p),
        1: (b[3] == b[5] == p)    or (b[11] == b[20] == p),
        2: (b[0] == b[4] == p)    or (b[7] == b[15] == p),
        3: (b[1] == b[5] == p)    or (b[10] == b[17] == p),
        4: (b[0] == b[2] == p)    or (b[8] == b[12] == p),
        5: (b[1] == b[3] == p)    or (b[9] == b[14] == p),
        6: (b[0] == b[18] == p)   or (b[7] == b[8] == p),
        7: (b[2] == b[15] == p)   or (b[6] == b[8] == p),
        8: (b[4] == b[12] == p)   or (b[6] == b[7] == p),
        9: (b[5] == b[14] == p)   or (b[10] == b[11] == p),
        10: (b[3] == b[17] == p)  or (b[9] == b[11] == p),
        11: (b[1] == b[20] == p)  or (b[9] == b[10] == p),
        12: (b[4] == b[8] == p)   or (b[13] == b[14] == p)  or (b[15] == b[18] == p),
        13: (b[12] == b[14] == p) or (b[16] == b[19] == p),
        14: (b[5] == b[9] == p)   or (b[12] == b[13] == p)  or (b[17] == b[20] == p),
        15: (b[2] == b[7] == p)   or (b[12] == b[18] == p)  or (b[16] == b[17] == p),
        16: (b[13] == b[19] == p) or (b[15] == b[17] == p),
        17: (b[3] == b[10] == p)  or (b[14] == b[20] == p)  or (b[15] == b[16] == p),
        18: (b[0] == b[6] == p)   or (b[12] == b[15] == p)  or (b[19] == b[20] == p),
        19: (b[13] == b[16] == p) or (b[18] == b[20] == p),
        20: (b[1] == b[11] == p)  or (b[14] == b[17] == p)  or (b[18] == b[19] == p)
    }[loc]

# Returns the List of the neighbors for a Location
# @param loc: Location
# @return: List of Locations
def neighbors(loc: int) -> list[int]:
    return {
        0: [1, 2, 6],           1: [0, 3, 11],          2: [0, 3, 4, 7],
        3: [1, 2, 5, 10],       4: [2, 5, 8],           5: [3, 4, 9],
        6: [0, 7, 18],          7: [2, 6, 8, 15],       8: [4, 7, 12],
        9: [5, 10, 14],         10: [3, 9, 11, 17],     11: [1, 10, 20],
        12: [8, 13, 15],        13: [12, 14, 16],       14: [9, 13, 17],
        15: [7, 12, 16, 18],    16: [13, 15, 17, 19],   17: [10, 14, 16, 20],
        18: [6, 15, 19],        19: [16, 18, 20],       20: [11, 17, 19]
    }[loc]

# Challenge Another Player in Tournament
# @param is_white: Whether the Player is White, or Black
def challenge(is_white: bool):
    player = Morris(NUM_PIECES, 'x', *(('W', 'B') if is_white else ('B', 'W')), 6, True)
    while True:
        board_state = player.play(input('BOARD: '))
        print("BOARD: ", *board_state[1], sep='')

# Quickly Plays A Game between AI & AI (Improved)
# Useful for Determining weights
def train():
    import time #TODO: REMOVE TIMER
    t1: float = time.time() #TODO: REMOVE TIMER START

    # Initialize White & Black Players
    white = Morris(NUM_PIECES, 'x', 'W', 'B', 3, True)   # White Player
    black = Morris(NUM_PIECES, 'x', 'B', 'W', 3, False)  # Black Player

    # Store Win Counts
    wins_white: int = 0
    wins_black: int = 0

    # Read Board from File
    board_start = open(BOARD_NAME, "r").read().strip()

    # Play Games
    for i_game in range(1, ITERATIONS):
        white.moves_made = -1
        black.moves_made = -1
        board_state = (0, board_start)
        print("{0:s}Game #{1:<4d}{0:s}\n   0) Start: {2:s}".format("-----------------------------------", i_game, board_start))
        for i_move in range(MAX_MOVES):
            turn_white = (i_game + i_move) % 2 == 1  # Alternate Starting Player
            board_state = (white if turn_white else black).play(board_state[1]) # Play Move
            print("{0:4d}) {1:s}: {3:s} Eval: {2:d}".format(i_move + 1, "White" if turn_white else "Black", *board_state))
            if turn_white and board_state[0] >= MAX_SIZE or not turn_white and board_state[0] <= MIN_SIZE:
                print("-----------> WHITE WINS!")
                wins_white += 1
                break
            if turn_white and board_state[0] <= MIN_SIZE or not turn_white and board_state[0] >= MAX_SIZE:
                print("-----------> BLACK WINS!")
                wins_black += 1
                break
        else:
            print("-----------> MOVE LIMIT REACHED!")

    # Print Aggregated Final Results
    print("{0:s}Final Results {0:s}\nWhite Wins:{1:d}\nBlack Wins:{2:d}".format("---------------------------------", wins_white, wins_black))
    print("Time Taken: %.8fs" % (time.time()-t1)) #TODO: REMOVE TIMER END

# Main: Play a Tournament Game or Train
if __name__=="__main__":
    #challenge(True)
    train()