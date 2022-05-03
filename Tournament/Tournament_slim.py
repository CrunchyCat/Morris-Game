# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project (Tournament Slim Version)
# Modified Version to Decrease Memory Usage & Increase Speed (See Submission/MorrisGame.py)

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
    def __init__(self, num_pieces: int, empty: str, player: str, opponent: str, max_depth: int):
        self.NUM_PIECES = num_pieces        # Number of Player Pieces to Play During Opening Game
        self.EMPTY = empty                  # Symbol for Empty Space
        self.PLAYER = player                # Symbol for the Player
        self.OPPONENT = opponent            # Symbol for the Opponent
        self.MAX_DEPTH = max_depth          # Maximum Depth of the Search
        self.moves_made = 0                 # N-1 Moves Made (Used to Determine if in Opening Game)

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
            return (self.__static_estimation(b, self.moves_made + depth // 2 <= self.NUM_PIECES), b)
        move_best: str = "RESIGN"
        if depth % 2 == 0: # If player #1
            eval_best = MIN_SIZE
            for move in self.move_player(b, self.moves_made + depth // 2 <= self.NUM_PIECES):
                eval_temp = self.__ab(move, depth + 1, max(alpha, eval_best), beta)[0]
                if eval_temp > eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best >= beta:
                    return (eval_best, move_best)
        else: # If Player #2
            eval_best = MAX_SIZE
            for move in self.move_opponent(b, self.moves_made + depth // 2 <= self.NUM_PIECES):
                eval_temp = self.__ab(move, depth + 1, alpha, min(beta, eval_best))[0]
                if eval_temp < eval_best:
                    eval_best = eval_temp
                    move_best = move
                if eval_best <= alpha:
                    return (eval_best, move_best)
        return (eval_best, move_best)

    # Generates all Moving Moves for Player
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: List of Possible Moves
    def move_player(self, b: str, is_opening: bool) -> list[str]:
        L = []
        if is_opening:
            for i in [i for i in range(len(b)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.PLAYER + b[i+1:]
                L += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range(len(b_temp)) if b_temp[i] == self.OPPONENT and not will_close_mill(b_temp, i, self.OPPONENT)] if will_close_mill(b, i, self.PLAYER) else [b_temp]
            return L
        for o in [i for i in range(len(b)) if b[i] == self.PLAYER]:
            for i in [i for i in (range(len(b)) if b.count(self.PLAYER) == 3 else neighbors(o)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.PLAYER + b[i+1:]          # Add a Piece to Board at Location i
                b_temp = b_temp[:o] + self.EMPTY + b_temp[o+1:] # Remove Piece from Origin Location o
                L += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range(len(b_temp)) if b_temp[i] == self.OPPONENT and not will_close_mill(b_temp, i, self.OPPONENT)] if will_close_mill(b, i, self.PLAYER) else [b_temp]
        return L

    # Generates all Moving Moves for Opponent
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: List of Possible Moves
    def move_opponent(self, b: str, is_opening: bool) -> list[str]:
        L = []
        if is_opening:
            for i in [i for i in range(len(b)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.OPPONENT + b[i+1:]
                L += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range(len(b_temp)) if b_temp[i] == self.PLAYER and not will_close_mill(b_temp, i, self.PLAYER)] if will_close_mill(b, i, self.OPPONENT) else [b_temp]
            return L
        for o in [i for i in range(len(b)) if b[i] == self.OPPONENT]:
            for i in [i for i in (range(len(b)) if b.count(self.OPPONENT) == 3 else neighbors(o)) if b[i] == self.EMPTY]:
                b_temp = b[:i] + self.OPPONENT + b[i+1:]        # Add a Piece to Board at Location i
                b_temp = b_temp[:o] + self.EMPTY + b_temp[o+1:] # Remove Piece from Origin Location o
                L += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range(len(b_temp)) if b_temp[i] == self.PLAYER and not will_close_mill(b_temp, i, self.PLAYER)] if will_close_mill(b, i, self.OPPONENT) else [b_temp]
        return L

    # Generates all Removal Moves
    # @param b: Board
    # @return: List of Possible Moves
    # def __count_sub_moves(self, b: str) -> int: # OPTIMIZATION 1: Don't Count # of Moves, Just Check that there are Moves
    #     return sum(1 for i in range(len(b)) if b[i] == self.OPPONENT and not will_close_mill(b, i, self.OPPONENT))
    
    # Static Estimation of the Board
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: Evaluation of the Board 
    def __static_estimation(self, b: str, is_opening: bool) -> int:
        num_pieces_opponent = b.count(self.OPPONENT)
        num_pieces_player = b.count(self.PLAYER)
        is_endgame = num_pieces_player == 3
        is_midgame = not is_opening and not is_endgame
        # num_moves_player = 0 # OPTIMIZATION 1: Don't Count # of Moves, Just Check that there are Moves
        # num_moves_opponent = 0 # OPTIMIZATION 1: Don't Count # of Moves, Just Check that there are Moves
        num_pieces_mill_player = 0
        num_pieces_mill_opponent = 0
        num_pieces_blocked_player = 0
        num_pieces_blocked_opponent = 0
        num_pieces_premill_player = 0
        num_pieces_premill_opponent = 0
        num_pieces_double_premill_player = 0
        num_pieces_double_premill_opponent = 0
        # num_double_mill_player = 0 #TODO: Calculate These Features
        # num_double_mill_opponent = 0
        
        # Feature Calculation
        for pos in range(len(b)):
            if b[pos] == self.PLAYER:
                if will_close_mill(b, pos, self.PLAYER):
                    num_pieces_mill_player += 1
                elif not is_midgame and sum(1 for j in neighbors(pos) if b[j] == self.PLAYER) > 1:
                    num_pieces_double_premill_player += 1
                if not [j for j in neighbors(pos) if b[j] == self.EMPTY]:
                    num_pieces_blocked_player += 1
                # if not is_opening: # OPTIMIZATION 1: Don't Count # of Moves, Just Check that there are Moves
                #     for i in [i for i in (range(len(b)) if is_endgame else neighbors(pos)) if b[i] == self.EMPTY]:
                #         b_temp = b[:pos] + self.EMPTY + b[pos+1:]
                #         num_moves_player += self.__count_sub_moves(b_temp[:i] + self.PLAYER + b_temp[i+1:]) if will_close_mill(b, i, self.PLAYER) else 1
            elif b[pos] == self.OPPONENT:
                if will_close_mill(b, pos, self.OPPONENT):
                    num_pieces_mill_opponent += 1
                elif not is_midgame and sum(1 for j in neighbors(pos) if b[j] == self.OPPONENT) > 1:
                    num_pieces_double_premill_opponent += 1
                if not [j for j in neighbors(pos) if b[j] == self.EMPTY]:
                    num_pieces_blocked_opponent += 1
                # if not is_opening: # OPTIMIZATION 1: Don't Count # of Moves, Just Check that there are Moves
                #     for i in [i for i in (range(len(b)) if is_endgame else neighbors(pos)) if b[i] == self.EMPTY]:
                #         b_temp = b[:pos] + self.EMPTY + b[pos+1:]
                #         num_moves_opponent += self.__count_sub_moves(b_temp[:i] + self.OPPONENT + b_temp[i+1:]) if will_close_mill(b, i, self.OPPONENT) else 1
            else: # Empty Space
                if will_close_mill(b, pos, self.PLAYER):
                    num_pieces_premill_player += 1
                if will_close_mill(b, pos, self.OPPONENT):
                    num_pieces_premill_opponent += 1
                # if is_opening: # OPTIMIZATION 2: Don't Consider # of Possible Moves for Opening
                #     num_moves_player += self.__count_sub_moves(b[:pos] + self.PLAYER + b[pos+1:]) if will_close_mill(b, pos, self.PLAYER) else 1
                #     num_moves_opponent += self.__count_sub_moves(b[:pos] + self.OPPONENT + b[pos+1:]) if will_close_mill(b, pos, self.OPPONENT) else 1

        if is_opening:
            return (    # Opening Estimation
                9 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 1 * (num_pieces_blocked_opponent - num_pieces_blocked_player)
                + 9 * (num_pieces_player - num_pieces_opponent)
                + 4 * (num_pieces_premill_player - num_pieces_premill_opponent)
                + 3 * (num_pieces_double_premill_player - num_pieces_double_premill_opponent)
            )
        # is_win = num_moves_opponent == 0 or num_pieces_opponent < 3 # OPTIMIZATION 1: Don't Considering # of Possible Moves for Opening
        # is_loss = num_moves_player == 0 or num_pieces_player < 3    # OPTIMIZATION 1: Don't Considering # of Possible Moves for Opening
        is_win = num_pieces_blocked_opponent >= num_pieces_opponent or num_pieces_opponent < 3  # OPTIMIZATION 1: Not all are blocked?
        is_loss = num_pieces_blocked_player >= num_pieces_player or num_pieces_player < 3       # OPTIMIZATION 1: Not all are blocked?
        if is_endgame:
            return (    # Endgame Estimation
                3 * (num_pieces_premill_player - num_pieces_premill_opponent)
                + 1 * (num_pieces_double_premill_player - num_pieces_double_premill_opponent)
                + 1190 * (1 if is_win == 0 else -1 if is_loss == 0 else 0)
            )
        return (        # Midgame Estimation
                14 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 10 * (num_pieces_blocked_opponent - num_pieces_blocked_player)
                + 11 * (num_pieces_player - num_pieces_opponent)
                #TODO: + 8 * # of Double Mills
                + 1086 * (1 if is_win else -1 if is_loss == 0 else 0)
        )

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

# Main: Play a Tournament Game
if __name__=="__main__":
    # Input Parameters
    NUM_PIECES = 8
    IS_WHITE = True

    player = Morris(NUM_PIECES, 'x', *(('W', 'B') if IS_WHITE else ('B', 'W')), 6)
    import time #TODO: REMOVE TIMER
    while True:
        board = input('INPUT: ')
        t1: float = time.time() #TODO: REMOVE TIMER START
        board_state = player.play(board)
        print("BOARD: ", *board_state[1], sep='')
        print("Time Taken: %.8fs" % (time.time()-t1)) #TODO: REMOVE TIMER END