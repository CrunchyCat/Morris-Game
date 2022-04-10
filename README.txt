CS 6364.501 Artificial Intelligence - Project
Caleb Hoff (crh170230)
31 March 2022

Tournament Improvements
Code is cut down & modified for greater efficiency.
The faster the code can run, the more depth can be considered during the tournament.
Also, a compiled version of the program using Cython (increasing speed by 43.5% on my machine) is included

Files Included (for Submission)
1)  README.txt                - This README File
2)  MiniMaxOpening.py         - Makes a Move for White with MiniMax Algorithm in Opening Phase of Morris Game
3)  MiniMaxOpeningBlack.py    - Makes a Move for Black with MiniMax Algorithm in Opening Phase of Morris Game
4)  MiniMaxOpeningImproved.py - Makes a Move for White with MiniMax Algorithm in Opening Phase of Morris Game (Improved)
5)  MiniMaxGame.py            - Makes a Move for White with MiniMax Algorithm in Midgame/Endgame Phase of Morris Game
6)  MiniMaxGameBlack.py       - Makes a Move for Black with MiniMax Algorithm in Midgame/Endgame Phase of Morris Game
7)  MiniMaxGameImproved.py    - Makes a Move for White with MiniMax Algorithm in Midgame/Endgame Phase of Morris Game (Improved)
8)  ABOpening.py              - Makes a Move for White with Alpha-Beta Algorithm in Opening Phase of Morris Game
9)  ABGame.py                 - Makes a Move for White with Alpha-Beta Algorithm in Midgame/Endgame Phase of Morris Game
10) MorrisGame.py             - The Project Logic, Required for the Other Programs

Instructions
1) Choose a Program to Run (Files 2-9)
2) Execute with: `python3 <File: Input Board> <File: Output Board> <Depth>
    - Files contain text in the form: 'xxxxxxxxxxxxxxxxxxxxx' where x can be {x, W, B}
    - A Depth of 5 is typical

Description
    This project demonstrates using the MiniMax Algorithm (with and without Alpha-Beta Pruning) to play a variant of the game,
Morris Game. The program accepts a text file representing the board positions, and outputs a new text file including its move,
in addition to printing out the estimation of the advantage on the board & the number of states reached by the algorithm.

Example Output
_______________________________________________________________________________________________________________________________
|  #  |         Input         |     MiniMax White     |     MiniMax Black     |MiniMax White Improved |   Alpha-Beta White    |
|  1  | xxxxxxWWWxWWxBBBBxxxx | xxxxxxWWWxxWxBBBBWxxx | xxxxxxWWWxWWBxBBBxxxx | xxxxxxWWxxWWWBBBBxxxx | xxxxxxxxxxxxxxxxxxxxx |
|     |                       | pos=152779     est=-4 | pos=112665    est=-10 | pos=152779    est=660 | pos=9946       est=-4 |
_______________________________________________________________________________________________________________________________
|  2  | BWWxWxBWxBWBBBWBWBWWB | BWWxxWBWxBWBBBWBWBWWB | BWWxWBBWxxWBBBWBWBWWB | BWWxxWBWxBWBBBWBWBWWB | BWWxxWBWxBWBBBWBWBWWB |
|     |                       | pos=17579    est=1993 | pos=6140       est=-5 | pos=17679    est=2145 | pos=1169     est=1993 |
_______________________________________________________________________________________________________________________________
|  3  | WWBxxxxWxxxxxxBxxxxxx | xWBWxxxWxxxxxxBxxxxxx | WWxBxxxWxxxxxxBxxxxxx | xWBWxxxWxxxxxxBxxxxxx | xWBWxxxWxxxxxxBxxxxxx |
|     |                       | pos=3464377 est=10000 | pos=387013 est=-10000 | pos=3464377   est=Inf | pos=112867  est=10000 |
_______________________________________________________________________________________________________________________________
|  4  | xWWxxxxxxxxWxxxBBBxxW | WxWxxxxxxxxWxxxBBBxxW | BWWxxxxxxxxWxxxxBBxxW | xWWxxxxxxxxWxxxBBBxxW | WxWxxxxxxxxWxxxBBBxxW |
|     |                       | pos=1491120   est=-45 | pos=6427753  est=-45  | pos=1491120   est=350 | pos=23306     est=-45 |
_______________________________________________________________________________________________________________________________
- In all 4 cases above, Alpha-Beta pruning results in far fewer states being reached & the result being calculated much faster.
- In cases #1 & #4, the improved static estimation function results in a different move being made than the standard one would.
- These results were collected using a depth of 5 for each

Improved Static Estimation Function
    As you can see in the table above, the improved static estimation function does sometimes inform different choices than the
standard static estimation function provided by the professor. I believe my new function to result in much better choices,
particularly when depth is not extremely huge. This is because of a few specific improvements. Firstly, the new
function is able to take into account the number of pieces in a formation that nearly makes a mill (i.e. 2/3 pieces in a row).
Secondly, the new function can take into account how many pieces are blocking an opponents potential mill, thus preventing
easy movements by limiting adjacents spaces. Finally, the new function has tweaked weighting that takes into account if the
game is in Midgame or Endgame. All of this results in more informed decisions for the algorithm.