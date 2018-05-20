# Author
**Name**: Shaival Dalal
**Contact**: sd3462 [at] nyu [dot] edu


### INTRODUCTION
The game uses artificial intelligence to make moves and compete against a human
player.

__Features:__
  1. Command Line Interface
  2. Alpha Beta based AI algorithm
  3. Ability to select the first player
  4. No King piece
  
  
### COMPILATION INSTRUCTION

|  Dependencies 	|  Version 	|
|---	|---	|
|  Anaconda 	|  5.1 	|
|  Python 	|   3.5.4	|
|  Numpy 	|   Python Library 1.14.2	|
|  Datetime 	|  Inbuilt 	|
|  Random 	|  Inbuilt 	|
|  Copy  |  Inbuilt  |

The operating system used for code compilation was Ubuntu 16.04 with Linux kernel
4.4+

**Shell command**
> python checkers_Shaival.py

**Running the game**
1. Run the shell command
2. Select if you would like to go first or second
3. Select the level of difficulty
4. When your turn comes, select the piece you wish to move
5. Enter where you would like to move the piece
6. The computer will make a move subsequently
7. If the game ends, the computer will calculate the score and declare the winner

### DESIGN
General flow of control:
1. The player selects whether they wish to go first or not (**turnSelect()**)
2. The player chooses the difficulty level (**selectDifficulty()**)
3. Based on the user input, a particular execution flow is followed. Functions involved are:<br>
  a. **endMove()** which checks for moves possible for the user or the computer<br>
      &nbsp;&nbsp;&nbsp;i. Calls **moveGenerator()** to generate legal moves <br>
  b. **checkAI()** is a wrapper function which implements the Alpha Beta pruning in the code<br>
        &nbsp;&nbsp;&nbsp;i. Calls the **AlphaBeta()** function which recursively expands the nodes and explores possible moves<br>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Calls the **winCheck()** function to calculate the score <br>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Calls the **newBoard()** function to update the temporary board with new moves<br>
   c. **getMove()** is a function to fetch moves from the user. It enforces basic rules to minimise function calls<br>
      &nbsp;&nbsp;&nbsp;i. Calls the **checkMove()** function to enforce extended rules to ensure the legality of moves<br>
      &nbsp;&nbsp;&nbsp;ii. Calls the **newBoard()** function to update the board<br>

4. The score function (**winCheck()**) is called to calculate the score and return the results
5. The program prints the statistics calculated at every step of the game


### STATE INFORMATION
The computer is the Maximiser and the human is the Minimiser.
The score/ utility range is from [-1000,1000] where the negative value represents a human win (Minimiser) and the positive value indicates a computer win (Maximiser)
Terminal States and their utility values:
  - User wins the game (Minimiser) [-1000,-1]
  - Computer wins the game (Maximiser) [1,1000]
  - The user and the computer get tied [0]


### EVALUATION FUNCTION
The evaluation function calculates the number of remaining pieces of the user and the computer at any possible state. It thus calculates the number of captures made by the computer and the user.<br>

If the user or the computer save all their pieces, they get the highest score in the
evaluation function i.e. -1000 or +1000 respectively.<br>

Every capture move results in a change in the score which is calculated by this function:
> (No. of Computer Pieces) - (No. of Human Pieces) ± 400*
<br><br>_400 is used for completeness of the equation and uniformity in score generation. Check the
code to refer to the commented implementation_


### DIFFICULTY LEVELS
The user can select the level of difficulty that he/she prefers. Each difficulty level is associated with a cutoff measured in the number of seconds taken by the computer to generate a move.
  - Easy level has a cutoff between 0 and 5 seconds
  - Moderate has a cutoff between 6 and 10 seconds
  - Difficult has a cutoff between 11 and 15 seconds
<br>We randomly select a cutoff value for user’s level selection in order to generate a fresh new game despite repeating the same moves
<br>We also use a Depth cutoff level in order to ensure that the algorithm expands other nodes quicker and discover the best move possible
