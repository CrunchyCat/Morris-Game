# Caleb Hoff (crh170230)
# CS 6364.501 Artificial Intelligence - Project
# TournamentTraining - Plays against itself to determine optimal weights for board features

from MorrisGame import Morris

if __name__ == "__main__":
    # Input Parameters
    BOARD_NAME = "boards/board_midgame_1.txt"   # Starting Board to Use
    ITERATIONS = 2                              # Number of Games to Play (Should be Even #, Start First 1/2 the Time)
    MAX_MOVES = 1_000                           # Maximum # of Moves to Make Per Game

    # Initialize White & Black Players
    white = Morris(4, True, True, True, True)   # White Player Midgame
    black = Morris(4, True, True, True, False)  # Black Player Midgame

    # Initialize List to Store Game Results
    white_win_boards = []
    black_win_boards = []

    # Read Board from File
    board_start = [i for i in open(BOARD_NAME, "r").read().strip()]

    # Play Games
    for i_game in range (1, ITERATIONS + 1):
        board_state = Morris.Evaluator(board=board_start)
        turn_white = start_white = i_game % 2 == 0  # Alternate Starting Player
        print("-----------------------------------{0:10s}-----------------------------------".format("Game #" + str(i_game)))
        print(("   0) Start: "), *board_start, sep="")
        for i_move in range(MAX_MOVES):
            turn_white = not turn_white
            board_state = white.play(board_state.board) if turn_white else black.play(board_state.board)
            print(("{0:4d}) " + ("White" if turn_white else "Black") + ": ").format(i_move + 1), *board_state.board, sep="")
            if board_state.eval > 2147483646:
                print("-----------> " + ("WHITE" if turn_white else "BLACK") + " WINS!")
                white_win_boards.append(board_state.board) if turn_white else black_win_boards.append(board_state.board)
                break
            if board_state.eval < -2147483647:
                print("-----------> " + ("BLACK" if turn_white else "WHITE") + " WINS!")
                black_win_boards.append(board_state.board) if turn_white else white_win_boards.append(board_state.board)
                break
        else:
            print("-----------> MOVE LIMIT REACHED!")

    # Print Aggregated Final Results
    print("---------------------------------Final Results ---------------------------------")
    print('White Wins:', len(white_win_boards))
    print('Black Wins:', len(black_win_boards))