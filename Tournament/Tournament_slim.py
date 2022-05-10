# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project (Tournament Slim/Fast Version)
# Modified Version to Increase Speed (See Submission/MorrisGame.py)

from functools import lru_cache

# Configuration
PIECES = ('W', 'B', 'x')        # Pieces (Primary, Secondary, Empty)
NUM_PIECES = 8                  # Number of Pieces Each Player Has
CACHE_EST = 225_000             # Size of Estimations Cache (37,450: ~1GB, 0: No Caching)
READ_CACHE = True               # Load Moves from Moves Cache File
WRITE_CACHE = True              # Write Moves to Moves Cache File
FILE_CACHE = "moves_cache.pkl"  # Filename of Moves Cache File

# Constants
BOARD_EMPTY = PIECES[2] * 21    # Starting Board: "xxxxxxxxxxxxxxxxxxxxx"
MIN_SIZE, MAX_SIZE = -2147483647, 2147483647
NEIGHBORS = {   0: [1, 2, 6],           1: [0, 3, 11],          2: [0, 3, 4, 7],
                3: [1, 2, 5, 10],       4: [2, 5, 8],           5: [3, 4, 9],
                6: [0, 7, 18],          7: [2, 6, 8, 15],       8: [4, 7, 12],
                9: [5, 10, 14],         10: [3, 9, 11, 17],     11: [1, 10, 20],
                12: [8, 13, 15],        13: [12, 14, 16],       14: [9, 13, 17],
                15: [7, 12, 16, 18],    16: [13, 15, 17, 19],   17: [10, 14, 16, 20],
                18: [6, 15, 19],        19: [16, 18, 20],       20: [11, 17, 19] }
NEIGHBORS_LONG = {  0: [2, 6],              1: [3, 11],             2: [0, 4, 7],
                    3: [1, 5, 10],          4: [2, 8],              5: [3, 9],
                    6: [0, 7, 18],          7: [2, 6, 8, 15],       8: [4, 7, 12],
                    9: [5, 10, 14],         10: [3, 9, 11, 17],     11: [1, 10, 20],
                    12: [8, 13, 15],        13: [12, 14, 16],       14: [9, 13, 17],
                    15: [7, 12, 16, 18],    16: [13, 15, 17, 19],   17: [10, 14, 16, 20],
                    18: [6, 15, 19],        19: [16, 18, 20],       20: [11, 17, 19] }

# Configures the Game Board & Makes Optimal Moves
class Morris:
    # Configures the Game Parameters
    # @param num_pieces:  # of Pieces to Play During Opening Game
    # @param empty:       Symbol for Empty Space
    # @param player:      Symbol for the Player
    # @param opponent:    Symbol for the Opponent
    # @param max_depth:   Maximum Depth of the Search
    def __init__(self, pieces: tuple[str, str, str], num_pieces: int, max_depth: int):
        self.PLAYER, self.OPPONENT, self.EMPTY, self.NUM_PIECES, self.MAX_DEPTH = *pieces, num_pieces, max_depth
        self.moves_made = 0                 # # of Moves Made (Used to Determine if in Opening Game)
        self.invert_board = lambda b: ''.join([self.OPPONENT if i == self.PLAYER else self.PLAYER if i != self.EMPTY else i for i in b])

    # Makes Optimal Move by Calling Alpha-Beta Pruning Algorithm
    # @param b:           Board
    # @param cache:       Dictionary of Cached Moves
    # @return: Tuple of (Board after Move, Static Evaluation of the Board)
    def play(self, b: str, cache: dict[tuple[int, str]]={}, use_cache=True) -> tuple[int, str]:
        key = ('O' if self.moves_made < 8 else 'M') + (b if self.PLAYER == PIECES[0] else self.invert_board(b))
        self.moves_made += 1
        if key in cache and use_cache:  # If Move is Cached, Retrieve
            return cache[key] if self.PLAYER == PIECES[0] else (cache[key][0], self.invert_board(cache[key][1]))
        result = self.__ab(b)           # Else, Generate Move
        cache[key] = result if self.PLAYER == PIECES[0] else (result[0], self.invert_board(result[1]))
        return result                   # Return Move

    # Alpha-Beta Pruning Algorithm
    # @param b:           Board
    # @param depth:       Current Depth of the Search
    # @param alpha:       Current Alpha Value
    # @param beta:        Current Beta Value
    # @return: Tuple of (Board after Move, Static Evaluation of the Board)
    def __ab(self, b: str, depth: int=0, alpha=MIN_SIZE, beta=MAX_SIZE) -> tuple[int, str]:
        global NEIGHBORS, MIN_SIZE, MAX_SIZE
        move_best: str = "" # Empty String: No Best Move
        moves_possible: list[str] = []
        if depth % 2 == 0: # If player #1
            range_asc = range(len(b)) # Backwards Faster, but Moves were Cached for Forward ¯\_(ツ)_/¯
            if self.moves_made + depth // 2 <= self.NUM_PIECES:
                for i in [i for i in range_asc if b[i] == self.EMPTY]:
                    b_temp = b[:i] + self.PLAYER + b[i+1:]
                    moves_possible += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range_asc if b_temp[i] == self.OPPONENT and not will_close_mill(b_temp, i, self.OPPONENT)] if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
            else:
                is_endgame = b.count(self.PLAYER) == 3
                for o in [i for i in range_asc if b[i] == self.PLAYER]:
                    for i in [i for i in (range_asc if is_endgame else NEIGHBORS[o]) if b[i] == self.EMPTY]:
                        b_temp = b[:i] + self.PLAYER + b[i+1:]          # Add a Piece to Board at Location i
                        b_temp = b_temp[:o] + self.EMPTY + b_temp[o+1:] # Remove Piece from Origin Location o
                        moves_possible += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range_asc if b_temp[i] == self.OPPONENT and not will_close_mill(b_temp, i, self.OPPONENT)] if will_close_mill(b_temp, i, self.PLAYER) else [b_temp]
            eval_best = MIN_SIZE
            depth += 1
            for move in moves_possible:
                eval = self.__static_estimation(b, self.moves_made + depth // 2 <= self.NUM_PIECES) if depth == self.MAX_DEPTH else self.__ab(move, depth, max(alpha, eval_best), beta)[0]
                if eval > eval_best:
                    if eval >= beta:
                        return (eval, move)
                    eval_best = eval
                    move_best = move
        else: # If Player #2
            range_dsc = range(len(b) - 1, -1, -1) # Backwards, Allows More Pruning, Bottom of Board is Bad
            if self.moves_made + depth // 2 <= self.NUM_PIECES:
                for i in [i for i in range_dsc if b[i] == self.EMPTY]:
                    b_temp = b[:i] + self.OPPONENT + b[i+1:]
                    moves_possible += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range_dsc if b_temp[i] == self.PLAYER and not will_close_mill(b_temp, i, self.PLAYER)] if will_close_mill(b_temp, i, self.OPPONENT) else [b_temp]
            else:
                is_endgame = b.count(self.OPPONENT) == 3
                for o in [i for i in range_dsc if b[i] == self.OPPONENT]:
                    for i in [i for i in (range_dsc if is_endgame else NEIGHBORS[o]) if b[i] == self.EMPTY]:
                        b_temp = b[:i] + self.OPPONENT + b[i+1:]        # Add a Piece to Board at Location i
                        b_temp = b_temp[:o] + self.EMPTY + b_temp[o+1:] # Remove Piece from Origin Location o
                        moves_possible += [b_temp[:i] + self.EMPTY + b_temp[i+1:] for i in range_dsc if b_temp[i] == self.PLAYER and not will_close_mill(b_temp, i, self.PLAYER)] if will_close_mill(b_temp, i, self.OPPONENT) else [b_temp]
            eval_best = MAX_SIZE
            depth += 1
            for move in moves_possible:
                eval = self.__static_estimation(b, self.moves_made + depth // 2 <= self.NUM_PIECES) if depth == self.MAX_DEPTH else self.__ab(move, depth, alpha, min(beta, eval_best))[0]
                if eval < eval_best:
                    if eval <= alpha:
                        return (eval, move)
                    eval_best = eval
                    move_best = move
        return (eval_best, move_best)

    # Static Estimation of the Board
    # @param b: Board
    # @param is_opening   True: Opening, False: Not Opening
    # @return: Evaluation of the Board
    @lru_cache(maxsize=CACHE_EST)
    def __static_estimation(self, b: str, is_opening: bool) -> int:
        global NEIGHBORS, NEIGHBORS_LONG
        num_pieces_player = b.count(self.PLAYER)
        num_pieces_opponent = b.count(self.OPPONENT)
        num_pieces_blocked_player = 0
        num_pieces_blocked_opponent = 0

        # Opening Game Calculation
        if is_opening:
            num_pieces_mill_player = 0
            num_pieces_mill_opponent = 0
            num_pieces_premill_player = 0
            num_pieces_premill_opponent = 0
            num_pieces_double_premill_player = 0
            num_pieces_double_premill_opponent = 0

            # Feature Calculation
            for pos in range(len(b)):
                if b[pos] == self.PLAYER:
                    if will_close_mill(b, pos, self.PLAYER):
                        num_pieces_mill_player += 1
                    elif sum(1 for j in NEIGHBORS_LONG[pos] if b[j] == self.PLAYER) > 1:
                        num_pieces_double_premill_player += 1
                    if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                        num_pieces_blocked_player += 1
                elif b[pos] == self.OPPONENT:
                    if will_close_mill(b, pos, self.OPPONENT):
                        num_pieces_mill_opponent += 1
                    elif sum(1 for j in NEIGHBORS_LONG[pos] if b[j] == self.OPPONENT) > 1:
                        num_pieces_double_premill_opponent += 1
                    if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                        num_pieces_blocked_opponent += 1
                else: # Empty Space
                    if will_close_mill(b, pos, self.PLAYER):
                        num_pieces_premill_player += 1
                    if will_close_mill(b, pos, self.OPPONENT):
                        num_pieces_premill_opponent += 1
            return (
                9 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 1 * (num_pieces_blocked_opponent - num_pieces_blocked_player)
                + 9 * (num_pieces_player - num_pieces_opponent)
                + 4 * (num_pieces_premill_player - num_pieces_premill_opponent)
                + 3 * (num_pieces_double_premill_player - num_pieces_double_premill_opponent)
            )
        # Midgame Calculation
        if num_pieces_player != 3:
            num_pieces_mill_player = 0
            num_pieces_mill_opponent = 0
            num_double_mill_player = 0
            num_double_mill_opponent = 0

            # Feature Calculation
            for pos in range(len(b)):
                if b[pos] == self.PLAYER:
                    if will_close_mill(b, pos, self.PLAYER):
                        num_pieces_mill_player += 1
                        if will_close_double_mill(b, pos, self.PLAYER):
                            num_double_mill_player += 1
                    if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                        num_pieces_blocked_player += 1
                elif b[pos] == self.OPPONENT:
                    if will_close_mill(b, pos, self.OPPONENT):
                        num_pieces_mill_opponent += 1
                        if will_close_double_mill(b, pos, self.OPPONENT):
                            num_double_mill_opponent += 1
                    if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                        num_pieces_blocked_opponent += 1
            return (
                14 * (num_pieces_mill_player - num_pieces_mill_opponent)
                + 10 * (num_pieces_blocked_opponent - num_pieces_blocked_player)
                + 11 * (num_pieces_player - num_pieces_opponent)
                + 8 * (num_double_mill_player - num_double_mill_opponent)
                + 1086 * (1 if num_pieces_blocked_opponent >= num_pieces_opponent or num_pieces_opponent < 3 else -1
                            if num_pieces_blocked_player >= num_pieces_player or num_pieces_player < 3 == 0 else 0)
            )
        # Endgame Calculation
        num_pieces_premill_player = 0
        num_pieces_premill_opponent = 0
        num_pieces_double_premill_player = 0
        num_pieces_double_premill_opponent = 0

        # Feature Calculation
        for pos in range(len(b)):
            if b[pos] == self.PLAYER:
                if not will_close_mill(b, pos, self.PLAYER) and sum(1 for j in NEIGHBORS_LONG[pos] if b[j] == self.PLAYER) > 1:
                    num_pieces_double_premill_player += 1
                if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                    num_pieces_blocked_player += 1
            elif b[pos] == self.OPPONENT:
                if not will_close_mill(b, pos, self.OPPONENT) and sum(1 for j in NEIGHBORS_LONG[pos] if b[j] == self.OPPONENT) > 1:
                    num_pieces_double_premill_opponent += 1
                if not [j for j in NEIGHBORS[pos] if b[j] == self.EMPTY]:
                    num_pieces_blocked_opponent += 1
            else: # Empty Space
                if will_close_mill(b, pos, self.PLAYER):
                    num_pieces_premill_player += 1
                if will_close_mill(b, pos, self.OPPONENT):
                    num_pieces_premill_opponent += 1
        return (
            3 * (num_pieces_premill_player - num_pieces_premill_opponent)
            + 1 * (num_pieces_double_premill_player - num_pieces_double_premill_opponent)
            + 1190 * (1 if num_pieces_blocked_opponent >= num_pieces_opponent or num_pieces_opponent < 3 else -1
                        if num_pieces_blocked_player >= num_pieces_player or num_pieces_player < 3 else 0)
        )

# Returns whether a Piece at Location loc will Close a Mill
# @param b:     The Board
# @param loc:   The Location of the Piece
# @param p:     The Hypothetical Piece at the Location
# @return: True if the Piece at Location loc will Close a Mill, False Otherwise
def will_close_mill(b: str, loc: int, p: str) -> bool:
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

# Returns whether a Piece at Location loc will Close a Double Mill
# @param b:     The Board
# @param loc:   The Location of the Piece
# @param p:     The Hypothetical Piece at the Location
# @return: True if the Piece at Location loc will Close a Double Mill, False Otherwise
def will_close_double_mill(b: str, loc: int, p: str) -> bool:
    return {
        0: b[2] == b[4] == b[6] == b[18] == p,
        1: b[3] == b[5] == b[11] == b[20] == p,
        2: b[0] == b[4] == b[7] == b[15] == p,
        3: b[1] == b[5] == b[10] == b[17] == p,
        4: b[0] == b[2] == b[8] == b[12] == p,
        5: b[1] == b[3] == b[9] == b[14] == p,
        6: b[0] == b[18] == b[7] == b[8] == p,
        7: b[2] == b[15] == b[6] == b[8] == p,
        8: b[4] == b[12] == b[6] == b[7] == p,
        9: b[5] == b[14] == b[10] == b[11] == p,
        10: b[3] == b[17] == b[9] == b[11] == p,
        11: b[1] == b[20] == b[9] == b[10] == p,
        12: (b[4] == b[8] == b[13] == b[14] == p) or (b[13] == b[14] == b[15] == b[18] == p),
        13: b[12] == b[14] == b[16] == b[19] == p,
        14: (b[5] == b[9] == b[12] == b[13] == p) or (b[12] == b[13] == b[17] == b[20] == p),
        15: (b[2] == b[7] == b[12] == b[18] == p) or (b[12] == b[18] == b[16] == b[17] == p),
        16: b[13] == b[19] == b[15] == b[17] == p,
        17: (b[3] == b[10] == b[14] == b[20] == p) or (b[14] == b[20] == b[15] == b[16] == p),
        18: (b[0] == b[6] == b[12] == b[15] == p) or (b[12] == b[15] == b[19] == b[20] == p),
        19: (b[13] == b[16] == p) or (b[18] == b[20] == p),
        20: (b[1] == b[11] == b[14] == b[17] == p) or (b[14] == b[17] == b[18] == b[19] == p)
    }[loc]

# Builds Moves Cache
# @param max_moves: Moves Before Considering a Draw
def build_cache(max_moves: int):
    # Register Signal Handler (Ctrl + C to Save/Exit)
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize Players
    white = Morris(PIECES, NUM_PIECES, 7)                               # White Player
    black = Morris((PIECES[1], PIECES[0], PIECES[2]), NUM_PIECES, 7)    # Black Player

    # Make List of Starting Boards
    boards_starting = [BOARD_EMPTY]
    for i in range(len(BOARD_EMPTY) - 1):
        for j in range(i + 1, len(BOARD_EMPTY)):
            boards_starting += [BOARD_EMPTY[:i] + PIECES[0] + BOARD_EMPTY[i+1:j] + PIECES[1] + BOARD_EMPTY[j+1:],
                                BOARD_EMPTY[:i] + PIECES[1] + BOARD_EMPTY[i+1:j] + PIECES[0] + BOARD_EMPTY[j+1:]]

    # Play Games
    for i_game, board_start in enumerate(boards_starting):
        white.moves_made = black.moves_made = 0 if i_game == 0 else 1
        board_state = (0, board_start)
        print("{0:s}Game #{1:<4d}{0:s}\n   0) Start: {2:s}".format("-----------------------------------", i_game, board_start))
        for i_move in range(max_moves):
            time_start = time.time()
            player = black if i_move % 2 else white
            board_before_1st_try = board_state[1]
            board_state = player.play(board_state[1], cache_moves) # Play Move

            elapsed = time.time() - time_start
            depth_extra = 0 if elapsed > 42 or elapsed < 0.03 else 1 if elapsed > 19 else 2 if elapsed > 3 else 3
            print("%4d) %s: %s Time: %.8fs (+%d)" % (i_move + 1, "White" if player is white else "Black", board_state[1], elapsed, depth_extra))

            # Increase Depth if Calculation was Really Fast (JANKY)
            # if depth_extra:
            #     player.MAX_DEPTH += depth_extra
            #     player.moves_made -= 1
            #     board_state = player.play(board_before_1st_try, cache_moves, use_cache=False) # Play Move
            #     player.MAX_DEPTH -= depth_extra
            #     print("%4d) %s: %s Time: %.8fs (REDO)" % (i_move + 1, "White" if player is white else "Black", board_state[1], time.time() - time_start - elapsed))

            if board_state[0] <= MIN_SIZE: # or board_state[0] >= MAX_SIZE
                print(f"-----------> {'BLACK' if player is white else 'WHITE'} WINS!")
                break
        else:
            print("-----------> MOVE LIMIT REACHED!")

# Challenge Another Player in Tournament
# @param is_white: Whether the Player is White, or Black
def challenge(is_white: bool):
    player = Morris(PIECES if is_white else (PIECES[1], PIECES[0], PIECES[2]), NUM_PIECES, 8)
    while True:
        board = input('INPUT: ')

        # Accept Commands "exit", "save" & "x"
        if board == "exit":
            break
        if board == 'save':
            with open(FILE_CACHE, 'wb') as f:
                pickle.dump(cache_moves, f, protocol=pickle.HIGHEST_PROTOCOL)
            continue
        if board == 'x':
            board = BOARD_EMPTY

        # Play Move & Print Board
        time_start = time.time()
        board_state = player.play(board, cache_moves) # Play Move (Using Cache if Available)
        print("BOARD: {0:s}\nTime Taken: {1:.8f}s".format(board_state[1], time.time() - time_start))

# Handles Signal (Ctrl + C)
def signal_handler(signum, frame):
    if WRITE_CACHE:
        with open(FILE_CACHE, 'wb') as f:
            pickle.dump(cache_moves, f, protocol=pickle.HIGHEST_PROTOCOL)
    if input(("Saved Cache to Disk. " if WRITE_CACHE else "") + "Quit? ")[0].lower() == "y":
        exit("Quitting...")

# Main: Play a Tournament Game or Build Cache
if __name__=="__main__":
    # Imports for Caching & Timing
    import pickle
    from os.path import exists
    import signal
    import time

    # Load Moves Cache
    if READ_CACHE and exists(FILE_CACHE):
        with open(FILE_CACHE, 'rb') as f:
            cache_moves: dict[tuple[int, str]] = pickle.load(f)
    else:
        cache_moves = {}

    challenge(True)
    #build_cache(25)