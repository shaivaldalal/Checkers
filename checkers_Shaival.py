#!/home/shaival/anaconda3/bin/python3.5

###########################################
#  Name:          Shaival Dalal           #
#                                         #
#  Project:       Checkers Game           #
###########################################


### IMPORTING LIBRARIES ###
import numpy as np
from copy import deepcopy
import datetime
import random



### DECLARING GLOBAL VARIABLES ###
MOVE=1 # Indicates whether a player can move or not
BEST_ALPHA=() # The best move indicated by alpha
PERM_DEPTH=60 # Cutoff depth for AI before backtracking
MAX_DEPTH=0 # The maximum depth reached by the AI
START_TIME=0 # AI start time
MAX_PRUN=0 # Pruning at Maximizer node
MIN_PRUN=0 # Pruning at Minimizer node
NODES=0 # The number of nodes created by the AI
DIFFICULTY=0 # Difficulty in number of seconds
TURN=0 # User's turn



### DEFINING THE BOARD CLASS ###
class Board:
    def __init__(self):


        """""
        Initialising our game board statically to make computations easier to manage and reducing the usage of "for" loops
        0 indicates an empty legal location on the board
        "H" pieces are owned by the human player
        "C" pieces are owned by the computer
        """

        self.initialBoard = np.array([
                            ['/','1','2','3','4','5','6'],
                            ['1','- ','C2','- ','C4','- ','C6'],
                            ['2','C1','- ','C3','- ','C5','- '],
                            ['3','- ','0 ','- ','0 ','- ','0 '],
                            ['4','0 ','- ','0 ','- ','0 ','- '],
                            ['5','- ','H2','- ','H4','- ','H6'],
                            ['6','H1','- ','H3','- ','H5','- ']])




    ## The printBoard function is responsible for printing the current state of the board
    ## Inputs: None
    ## Output: None    
    def printBoard(self):
        print("\n")
        for i in np.arange(1,8):
            for j in np.arange(1,8):
                print("{0:s} | ".format(self.initialBoard[i-1][j-1]), end="\t")
            print()



    ## The newBoard function makes the moves on the existing board and generates a new board
    ## Inputs: moves (list), movetype (character), type (character)
    ## Output: None
    def newBoard(self,moves,movetype,TYPE):
        x,y=moves[0][0],moves[0][1]
        dx,dy=moves[1][0],moves[1][1]

        ## For human moves
        if TYPE=="H":
            # movetype description
            # 1: Normal Move
            # 2: Jump left
            # 3: Jump right
            if movetype=="1":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
            if movetype=="2":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
                self.initialBoard[x-1][y-1]="0 " # Replace the jumped piece with 0
            elif movetype=="3":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
                self.initialBoard[x-1][y+1]="0 " # Replace the jumped piece with 0

        ## For computer's moves
        if TYPE=="C":
            # movetype description
            # 1: Normal Move
            # 2: Jump left
            # 3: Jump right         
            if movetype=="1":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
            if movetype=="2":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
                self.initialBoard[x+1][y-1]="0 " # Replace the jumped piece with 0
            elif movetype=="3":
                self.initialBoard[dx][dy]=self.initialBoard[x][y]
                self.initialBoard[x][y]="0 "
                self.initialBoard[x+1][y+1]="0 " # Replace the jumped piece with 0



    ## The winCheck function is the evaluation function to calculate the score
    ## Inputs: None
    ## Output: Score (signed integer)
    def winCheck(self):
        # Find all pieces for the human player and the computer
        Hscore=(len(np.where(np.char.find(self.initialBoard, "H")==0)[0]))
        Cscore=(len(np.where(np.char.find(self.initialBoard, "C")==0)[0]))

        if Cscore>Hscore:
            if Cscore==6:
                return 1000
            return (Cscore*100)-(Hscore*100)+400 # Return a higher score for every piece saved by amplifying the gain
        elif Cscore==Hscore:
            return 0 # Return a zero score for a draw
        elif Hscore>Cscore:
            if Hscore==6:
                return -1000
            return (-Hscore*100)+(Cscore*100)-400 # Return a lower score for every Human piece remaining and introduce heavy penalties



### DEFINING THE PLAYER CLASS ###
class Player:
    def __init__(self):
        self.TYPE="H"



    ## The getMove function fetches moves from the user, calls a validating function and also calls the newBoard function.
    ## Inputs: Board (object)
    ## Output: Piece Information (list: Contains source and destination)
    def getMove(self,board):
        global MOVE

        while self.TYPE=="H":
            try:
                piece=input("Please select the piece you want to move. E.g.: {0}1: ".format(self.TYPE)).upper()

                if not piece.startswith('H'): # If the player enters an illegal piece, raise an error
                    raise IndexError

                # Convert string input to integer
                piecex,piecey=np.argwhere(board.initialBoard==piece)[0]
                destx,desty=input("Where would you like to move it? E.g. 4,1: ").split(',')
                destx=int(destx)
                desty=int(desty)

                # If the player enters coordinates outside the scope of the board, raise an error
                if (destx>7 or desty>7) or (destx<1 or desty<1):
                    raise ValueError

                # Check for the validity of the move
                movetype = self.checkMove(pieceInfo=[[piecex,piecey],[destx,desty]],board=board.initialBoard,TYPE=self.TYPE)
                if movetype is not None:
                    MOVE=1-MOVE # Switch move
                    board.newBoard([[piecex,piecey],[destx,desty]],movetype,self.TYPE) # If the entered move is valid, execute the move
                    return [[piecex,piecey],[destx,desty]]
                else:
                    raise ValueError
            except ValueError:
                print("Please enter valid coordinates.")
            except IndexError:
                print("No such piece found.")



    ## The checkMove function validates the moves passed to conform to game rules.
    ## Inputs: pieceInfo (list: Contains source and destination), board (object), TYPE (character)
    ## Output: movetype (character) 
    def checkMove(self,pieceInfo,board,TYPE):
        x,y=pieceInfo[0][0],pieceInfo[0][1]
        dx,dy=pieceInfo[1][0],pieceInfo[1][1]

        # For human moves
        if TYPE=="H":
            if board.shape==(7,7):
                # Check for jumps
                if ((dx-x==-2 and dy-y==-2) and (board[dx][dy]=="0 ") and (board[x-1][y-1].startswith('C'))): # Check for a left jump
                    return "2"

                elif ((dx-x==-2 and dy-y==2) and (board[dx][dy]=="0 ") and (board[x-1][y+1]).startswith('C')): # Check for a right jump
                    return "3"

                elif ((dx-x==-1 and dy-y==1) or (dx-x==-1 and dy-y==-1)) and board[dx][dy]=="0 ": # Check for regular moves
                    return "1"

                else:
                    return None # Return None if the move is not legal

        # For computer moves
        if TYPE=="C":
            if board.shape==(7,7):
                #Check for jumps
                if ((dx-x==2 and dy-y==-2) and (board[dx][dy]=="0 ") and (board[x+1][y-1].startswith('H'))): # Check for a left jump
                    return "2"
                elif ((dx-x==2 and dy-y==2) and (board[dx][dy]=="0 ") and (board[x+1][y+1]).startswith('H')): # Check for a right jump
                    return "3"

                elif ((dx-x==1 and dy-y==1) or (dx-x==1 and dy-y==-1)) and board[dx][dy]=="0 ":
                    return "1"

                else:
                    return None # return None if the move is not legal



    ## The AlphaBeta function is responsible for making moves on behalf of the computer. It calculates moves on behalf of the user and the computer.
    ## Inputs: local_type (character), board (object), depth (integer), alpha (integer), beta (integer)
    ## Output: score (integer)  
    def AlphaBeta(self,local_type,board,depth,alpha,beta):
        global PERM_DEPTH
        global MAX_DEPTH
        global BEST_ALPHA
        global MAX_PRUN
        global MIN_PRUN
        global NODES
        global DIFFICULTY

        if depth>MAX_DEPTH: # Record the maximum depth attained
            MAX_DEPTH=depth

        possiblemoves=self.endMove(board,local_type) #Calculate if we have any moves possible for the current player

        if possiblemoves=="Terminate": #Terminate if no possible moves or if the current depth is more than or equal to the max depth
            return board.winCheck()

        elif possiblemoves=="Switch": # If the current user is out of moves, switch to the opponent
            if local_type=="H":
                local_type="C"
            else:
                local_type="H"
            possiblemoves=self.endMove(board,local_type) # Generate opponent's moves
            if possiblemoves=="Terminate":
                return board.winCheck()
            else:
                end=[]
                if len(possiblemoves) > 1: # For more than one move in the move list
                    for allmoves in possiblemoves:
                        if allmoves[4] > 1: # If the move identifier belongs to jumps, append to end or else discard
                            end.append(allmoves)
                else:
                    end = deepcopy(possiblemoves) # If only normal moves possible execute this
        else:
            end=[]
            if len(possiblemoves)>1:
                for allmoves in possiblemoves:
                    if allmoves[4]>1:
                        end.append(allmoves)
                if len(end)==0:
                    end=deepcopy(possiblemoves)
            else:
                end=deepcopy(possiblemoves)

        #Maximizer
        if local_type=="C":
            for i in np.arange(len(end)):
                if (datetime.datetime.now() - START_TIME).seconds >= DIFFICULTY: # Check for cutoff time (Difficulty)
                    # print("Cutoff ",datetime.datetime.now()-START_TIME)
                    return board.winCheck()

                if (depth>=PERM_DEPTH): # Cutoff depth
                    # print("Depth Cutoff: ",depth)
                    return board.winCheck()

                tempboard=deepcopy(board) # Create a new node to calculate possible moves
                NODES+=1
                x,y,destx,desty=end[i][0],end[i][1],end[i][2],end[i][3]
                movetype=self.checkMove(pieceInfo=[[x,y],[destx,desty]],board=tempboard.initialBoard,TYPE="C") # Check move validity
                if movetype: # If there exists a valid move
                    tempboard.newBoard([[x,y],[destx,desty]],movetype,"C") # Make the move
                    local_type="H" # Set the opponent type to "Human"
                    scoreCount=self.AlphaBeta(local_type,tempboard,depth+1,alpha,beta) # Recursively call AlphaBeta
                    if scoreCount>alpha:
                        if depth == 0:
                            BEST_ALPHA=(x,y,destx,desty)
                        alpha=scoreCount
                    if alpha>=beta:
                        MAX_PRUN+=1 # Prune maximizer nodes
                        return board.winCheck()
            return board.winCheck()

        #Minimizer
        elif local_type=="H":
            for i in np.arange(len(end)):
                if (datetime.datetime.now() - START_TIME).seconds >= DIFFICULTY: # Check for cutoff time (Difficulty)
                    # print("Cutoff ",datetime.datetime.now()-START_TIME)
                    return board.winCheck()

                if (depth>=PERM_DEPTH): # Cutoff depth
                    # print("Depth Cutoff: ",depth)
                    return board.winCheck()

                tempboard=deepcopy(board)
                NODES+=1
                x, y, destx, desty = end[i][0],end[i][1],end[i][2],end[i][3]
                movetype=self.checkMove(pieceInfo=[[x,y],[destx,desty]],board=tempboard.initialBoard,TYPE="H")
                if movetype:
                    tempboard.newBoard([[x,y],[destx,desty]],movetype,"H")
                    local_type = "C"
                    scoreCount = self.AlphaBeta(local_type,tempboard,depth+1,alpha,beta)
                    if scoreCount<beta:
                        beta=scoreCount
                    if alpha>=beta:
                        MIN_PRUN+=1 # Prune minimizer node
                        return board.winCheck()
            return board.winCheck()



    ## The checkAI function is responsible for initiating moves for the computer
    ## Inputs: board (object)
    ## Output: score (integer)  
    def checkAI(self,board):
        global BEST_ALPHA
        global MOVE
        global START_TIME

        START_TIME=datetime.datetime.now() # Start the counter for the computer
        print("The Computer Is Thinking...")
        alpha=self.AlphaBeta(local_type="C",board=board,depth=0,alpha=-10000,beta=10000) # Initial call to Alpha Beta
        if alpha==-10000:
            return board.winCheck()
        movetype=self.checkMove(pieceInfo=[[BEST_ALPHA[0],BEST_ALPHA[1]],[BEST_ALPHA[2],BEST_ALPHA[3]]],board=board.initialBoard,TYPE="C") # Check move validity
        if movetype: # If movetype is valid
            board.newBoard([[BEST_ALPHA[0],BEST_ALPHA[1]],[BEST_ALPHA[2],BEST_ALPHA[3]]],movetype,"C")

            # Print statistics related to the game after every move
            # print("Best Move: {0}".format(BEST_ALPHA))
            # print("Min Pruning: ",MIN_PRUN)
            # print("Max Pruning: ",MAX_PRUN)
            # print("Nodes: ",NODES)
        MOVE=1-MOVE # Switch move



    ## The moveGenerator function is responsible for generating moves on behalf of the human and the computer player.
    ## Inputs: remaining_pieces (list), board (object), TYPE (character)
    ## Output: moves (list: Contains possible moves for every piece)    
    def endMove(self, board, TYPE):
        global MOVE

        if TYPE=="H": # Set opponent type
            opponent="C"
        else:
            opponent="H"

        # Find all the remaining pieces of the computer and the human
        remainingPiecesO = np.argwhere(np.char.find(board.initialBoard, opponent) == 0)
        remainingPieces = np.argwhere(np.char.find(board.initialBoard, TYPE) == 0)

        if len(remainingPieces) == 0 and len(remainingPiecesO) == 0: # If no remaining pieces, return "Terminate"
            return "Terminate"

        else:
            movesO=self.moveGenerator(remainingPiecesO, board.initialBoard,opponent) # Generate moves for the opponent
            moves=self.moveGenerator(remainingPieces, board.initialBoard, TYPE) # Generate moves for the player

            if len(moves)==0 and len(movesO)==0:
                return "Terminate"

            elif (moves is None or len(moves)==0) and (movesO is not None and len(movesO)!=0): # Switch turns if no possible moves for the current player but possible for the opponent
                MOVE=1-MOVE
                return "Switch"

            else:
                return moves



    ## The endMove function is a wrapper responsible for checking if the player has any moves left.
    ## Inputs: remaining_pieces (list), board (object), TYPE (character)
    ## Output: moves (list: Contains possible moves for every piece)
    def moveGenerator(self,remainingPieces,board,TYPE):
        moves=[]
        if TYPE=="C": # For Computer's moves
            for element in np.arange(len(remainingPieces)):
                    x=remainingPieces[element][0]
                    y=remainingPieces[element][1]

                    # Jumps
                    # Generate jumps with a distance of 2 blocks
                    if x<5: dx2=x+2
                    else: dx2=None

                    # Conditions for a right jump
                    if dx2 and y<5 and board[dx2][y+2]=="0 " and board[x+1][y+1].startswith("H"): dy2=y+2
                    else: dy2=None
                    if dx2 and dy2: moves.append([x,y,dx2,dy2,2])

                    # Conditions for a left jump
                    if dx2 and y>2 and board[dx2][y-2]=="0 " and board[x+1][y-1].startswith("H"): dy3=y-2
                    else: dy3=None
                    if dx2 and dy3: moves.append([x,y,dx2,dy3,3])

                    # Regular Move
                    # Generate moves within a distance of 1 block (X represents rows and Y, columns)
                    if x<6: dx1=x+1
                    else: dx1=None
                    if dx1 and y>1 and board[dx1][y-1]=="0 ": dy1=y-1
                    else: dy1=None

                    if dx1 and dy1: moves.append([x,y,dx1,dy1,1])
                    if dx1 and y<6 and board[dx1][y+1]=="0 ": dy2=y+1
                    else: dy2=None
                    if dx1 and dy2: moves.append([x,y,dx1,dy2,1])


        elif TYPE=="H":  # For human player's moves
            for element in np.arange(len(remainingPieces)):
                x=remainingPieces[element][0]
                y=remainingPieces[element][1]

                # Jumps
                # Generate jumps with a distance of 2 blocks
                if x>2: dx2=x-2
                else: dx2=None

                # Conditions for a right jump
                if dx2 and y<5 and board[dx2][y+2]=="0 " and board[x-1][y+1].startswith("C"): dy2=y+2
                else: dy2=None
                if dx2 and dy2: moves.append([x,y,dx2,dy2,2])

                # Conditions for a left jump
                if dx2 and y>2 and board[dx2][y-2]=="0 " and board[x-1][y-1].startswith("C") : dy3=y-2
                else: dy3=None
                if dx2 and dy3: moves.append([x,y,dx2,dy3,3])

                # Regular Move
                # Generate moves within a distance of 1 block (X represents rows and Y, columns)
                if x>1: dx1=x-1
                else: dx1=None
                if dx1 and y>1 and board[dx1][y-1]=="0 ": dy1=y-1
                else: dy1=None

                if dx1 and dy1: moves.append([x,y,dx1,dy1,1])
                if dx1 and y<6 and board[dx1][y+1]=="0 ": dy2=y+1
                else: dy2=None
                if dx1 and dy2: moves.append([x,y,dx1,dy2,1])

        return moves  # Returns a list of possible moves containing the source X and Y, and the destination X and Y



## The selectDifficulty function is used to ask the user about the difficulty level.
## Inputs: None
## Output: None
def selectDifficulty():
    global DIFFICULTY

    endfunc=0
    while endfunc==0:
        try:
            diff_level=int(input("Please select the difficulty level of the game:\n1. Easy\n2. Moderate\n3. Difficult\nEnter the number of the selected choice: "))
            if diff_level<1 or diff_level>3:
                raise IndexError

            # We use random integers to select the difficulty level in order to generate a fresh game
            if diff_level==1:
                DIFFICULTY = random.randint(0,5) # Set the seconds cutoff between 0 and 5 if the user selects easy
            elif diff_level==2:
                DIFFICULTY = random.randint(6,10) # Set the seconds cutoff between 6 and 10 if the user selects moderate
            else:
                DIFFICULTY = random.randint(11,15) # Set the seconds cutoff between 11 and 15 if the user selects difficult

            endfunc=1

        except ValueError:
            print("Not a valid integer value. Please try again.")
        except IndexError:
            print("Please enter an integer from the above choices.")

## The turnSelect function is used to ask the user about the start order preference.
## Inputs: None
## Output: None
def turnSelect():
    global TURN

    endfunc=0
    while endfunc==0:
        try:
            # Take user preference
            turn=int(input("Please select your choice:\n1. Play First\n2. Play Second\nEnter the number of the selected choice: "))
            if turn<1 or turn>2:
                raise IndexError

            if turn==1 or turn==2:
                TURN = turn
            endfunc=1

        except ValueError:
            print("Not a valid integer. Please try again.")
        except IndexError:
            print("Please select an integer from the above choices.")

## The main function is used to initialise our variables and set the sequence for game execution
## Inputs: None
## Output: None
def main():
    global MOVE
    global DIFFICULTY
    global TURN

    b=Board() # Initialise the Board class
    b.printBoard() # Print our initial board
    turnSelect() # User wants to go first or second
    selectDifficulty() # Select the game difficulty
    human=Player() # Initialise the Player object (Human)
    computer=Player() # Initialise the Player object (Computer)
    computer.TYPE="C"
    while MOVE!=2:
        if TURN==1:
            hstate = human.endMove(b,"H")  # Check if the user can make moves
            if hstate == "Terminate": # If no remaining pieces, terminate the game
                MOVE=2
                break
            elif hstate !="Switch": # If the current player has moves left
                human.getMove(b)

            cstate = computer.endMove(b,"C") # Check if the computer can make moves
            if cstate == "Terminate":
                MOVE=2
                break
            elif cstate != "Switch":
                computer.checkAI(b) # Generate, evaluate and make moves on behalf of the computer

        elif TURN==2: # If  the user wishes to go second
            cstate = computer.endMove(b,"C")
            if cstate == "Terminate":
                break
            elif cstate != "Switch":
                computer.checkAI(b)

            b.printBoard() # Print board to update computer's moves
            hstate = human.endMove(b, "H")
            if hstate == "Terminate":
                break
            elif hstate != "Switch":
                human.getMove(b)
        b.printBoard() # Print board to update computer's moves

    # Display the winner
    score=b.winCheck()
    if score>0:
        print("\nThe Computer Won!")
    elif score==0:
        print("\nIt's A Tie!")
    else:
        print("\nYou Won!")

    # Print game statistics
    print("\nGame Statistics:\nMaximum Depth Attained: {0}\nNodes Expanded: {1}\nMax Pruning: {2}\nMin Pruning: {3}".format(MAX_DEPTH,NODES,MAX_PRUN,MIN_PRUN))

main()
