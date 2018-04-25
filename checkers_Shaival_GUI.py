#!/home/shaival/anaconda3/bin/python3.5

###########################################
#  Name:          Shaival Dalal           #
#  Course:        Artificial Intelligence #
#  Course Number: CS6613                  #
#  Project:       Checkers Game           #
###########################################

"""""
TODO:
1. Ask the human player if they want to go first or second [DONE]
2. Prefer jumps over normal moves [DONE]
3. Generate stats: - Max depth of the tree [DONE],
                   - No. of nodes generated, [DONE]
                   - Pruning in max_value [DONE],
                   - Pruning in min_value [DONE]
4. Set a 15 seconds cutoff [DONE]
"""



### IMPORTING LIBRARIES ###
import numpy as np
from copy import deepcopy
import sys
import time
import pygame
from pygame.locals import *



### DECLARING GLOBAL VARIABLES ###
MOVE=1
BEST_ALPHA=()
PERM_DEPTH=200
MAX_DEPTH=0
START_TIME=0
MAX_PRUN=0
MIN_PRUN=0
NODES=0
DIFFICULTY=0
TURN=0
WINDOW_SIZE=(522,522)
TITLE='Checkers Game'
BACKGROUND_IMAGE= './board.png'
FPS=10



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
                            ['- ','C2','- ','C4','- ','C6'],
                            ['C1','- ','C3','- ','C5','- '],
                            ['- ','0 ','- ','0 ','- ','0 '],
                            ['0 ','- ','0 ','- ','0 ','- '],
                            ['- ','H2','- ','H4','- ','H6'],
                            ['H1','- ','H3','- ','H5','- ']])




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
            return (Cscore*100)-(Hscore*100) # Return a higher score for every piece saved by amplifying the gain
        elif Cscore==Hscore:
            return 0 # Return a zero score for a draw
        elif Hscore>Cscore:
            if Hscore==6:
                return -1000
            return (-Hscore*100)+(Cscore*100) # Return a lower score for every Human piece remaining and introduce heavy penalties



### DEFINING THE PLAYER CLASS ###
class Player:
    def __init__(self):
        self.TYPE="H"



    ## The getMove function fetches moves from the user, calls a validating function and also calls the newBoard function.
    ## Inputs: Board (object)
    ## Output: Piece Information (list: Contains source and destination)
    def getMove(self,board,pos):
        global MOVE
        global SELECTED  # use global variables

        while self.TYPE=="H":
            try:
                piecex, piecey= int(pos[0] / (WINDOW_SIZE[0] / board_size)),int(pos[1] / (WINDOW_SIZE[1] / board_size))

                if not board[piecex][piecey].startswith('H'): # If the player enters an illegal piece, raise an error
                    return

                # Convert string input to integer
                destx,desty=input("Where would you like to move it? E.g. 4,1: ").split(',')
                destx=int(destx)
                desty=int(desty)

                # If the player enters coordinates outside the scope of the board, raise an error
                if (destx>7 or desty>7) or (destx<1 or desty<1):
                    raise ValueError

                # Check for the validity of the move
                movetype = self.checkMove(pieceInfo=[[piecex,piecey],[destx,desty]],board=board.initialBoard,TYPE=self.TYPE)
                if movetype is not None:
                    MOVE=1-MOVE
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

        if depth>MAX_DEPTH:
            MAX_DEPTH=depth

        possiblemoves=self.endMove(board,local_type) #Calculate if we have any moves possible for the current player

        if possiblemoves=="Terminate" or possiblemoves=="Switch": #Terminate if no possible moves or if the current depth is more than or equal to the max depth
            return board.winCheck()

        end=[]
        if len(possiblemoves)>1:
            for allmoves in possiblemoves:
                if allmoves[4]>1:
                    end.append(allmoves)

        if len(end)==0:
            end=possiblemoves


        #Maximizer
        if local_type=="C":
            for i in np.arange(len(end)):
                if time.time()-START_TIME >= DIFFICULTY or depth>PERM_DEPTH:
                    return alpha

                tempboard=deepcopy(board)
                x,y,destx,desty=end[i][0],end[i][1],end[i][2],end[i][3]
                movetype=self.checkMove(pieceInfo=[[x,y],[destx,desty]],board=tempboard.initialBoard,TYPE="C")
                if movetype:
                    NODES += 1
                    tempboard.newBoard([[x,y],[destx,desty]],movetype,"C")
                    local_type="H"
                    scoreCount=self.AlphaBeta(local_type,tempboard,depth+1,alpha,beta)
                    if scoreCount>alpha:
                        if depth == 0:
                            BEST_ALPHA=(x,y,destx,desty)
                        alpha=scoreCount
                    if alpha>=beta:
                        MAX_PRUN+=1
                        return alpha
            return alpha

        #Minimizer
        elif local_type=="H":
            for i in np.arange(len(end)):
                if time.time()-START_TIME >= DIFFICULTY or depth>PERM_DEPTH:
                    return beta

                tempboard=deepcopy(board)
                x, y, destx, desty = end[i][0],end[i][1],end[i][2],end[i][3]
                movetype=self.checkMove(pieceInfo=[[x,y],[destx,desty]],board=tempboard.initialBoard,TYPE="H")
                if movetype:
                    NODES+=1
                    tempboard.newBoard([[x,y],[destx,desty]],movetype,"H")
                    local_type = "C"
                    scoreCount = self.AlphaBeta(local_type,tempboard,depth+1,alpha,beta)
                    if scoreCount<beta:
                        beta=scoreCount
                    if alpha>=beta:
                        MIN_PRUN+=1
                        return beta
            return beta



    ## The checkAI function is responsible for initiating moves for the computer
    ## Inputs: board (object)
    ## Output: score (integer)
    def checkAI(self,board):
        global BEST_ALPHA
        global MOVE
        global START_TIME

        START_TIME=time.time()
        print("The Computer Is Thinking...")
        alpha=self.AlphaBeta(local_type="C",board=board,depth=0,alpha=-10000,beta=10000)
        if alpha==-10000:
            return board.winCheck()
        movetype=self.checkMove(pieceInfo=[[BEST_ALPHA[0],BEST_ALPHA[1]],[BEST_ALPHA[2],BEST_ALPHA[3]]],board=board.initialBoard,TYPE="C")
        if movetype:
            board.newBoard([[BEST_ALPHA[0],BEST_ALPHA[1]],[BEST_ALPHA[2],BEST_ALPHA[3]]],movetype,"C")
            print("Best Move: {0}".format(BEST_ALPHA))
        MOVE=1-MOVE



    ## The moveGenerator function is responsible for generating moves on behalf of the human and the computer player.
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

                    if len(moves)==0:
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

                if len(moves)==0:
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



    ## The endMove function is a wrapper responsible for checking if the player has any moves left.
    ## Inputs: remaining_pieces (list), board (object), TYPE (character)
    ## Output: moves (list: Contains possible moves for every piece)
    def endMove(self, board, TYPE):
        global MOVE

        if TYPE=="H":
            opponent="C"
        else:
            opponent="H"

        remainingPiecesO = np.argwhere(np.char.find(board.initialBoard, opponent) == 0)
        remainingPieces = np.argwhere(np.char.find(board.initialBoard, TYPE) == 0)

        if len(remainingPieces) == 0 and len(remainingPiecesO) == 0:
            return "Terminate"

        else:
            movesO=self.moveGenerator(remainingPiecesO, board.initialBoard,opponent)
            moves=self.moveGenerator(remainingPieces, board.initialBoard, TYPE)

            if len(moves)==0 and len(movesO)==0:
                return "Terminate"

            elif (moves is None or len(moves)==0) and (movesO is not None and len(movesO)!=0):
                MOVE=1-MOVE
                return "Switch"

            else:
                return moves



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

            if diff_level==1:
                DIFFICULTY = int(5) # Set the seconds cutoff to 5 if the user selects easy
            elif diff_level==2:
                DIFFICULTY = int(10) # Set the seconds cutoff to 10 if the user selects moderrate
            else:
                DIFFICULTY = int(15) # Set the seconds cutoff to 15 if the user selects difficult

            endfunc=1

        except ValueError:
            print("Not a valid integer value. Please try again.")
        except IndexError:
            print("Please enter an integer from the above choices.")

def turnSelect():
    global TURN

    endfunc=0
    while endfunc==0:
        try:
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


### GUI Functions ###
#-----------------------------------------------------------------------------------------------------------------------
# function that will draw a piece on the board
def draw_piece(board,pieceInfo):
    column=pieceInfo[1]
    row=pieceInfo[0]
    # find the center pixel for the piece
    posX = int(((WINDOW_SIZE[0] / 6) * column) - (WINDOW_SIZE[0] / 6) / 2)
    posY = int(((WINDOW_SIZE[1] / 6) * row) - (WINDOW_SIZE[1] / 6) / 2)

    # set color for piece
    if board[row][column].startswith('H'):
        border_color = (255, 255, 255)
        inner_color = (0, 0, 0)
        pygame.draw.circle(screen, border_color, (posX, posY), 12)  # draw piece border
        pygame.draw.circle(screen, inner_color, (posX, posY), 10)  # draw piece
    elif board[row][column].startswith('C'):
        border_color = (0, 0, 0)
        inner_color = (255, 255, 255)
        pygame.draw.circle(screen, border_color, (posX, posY), 12)  # draw piece border

    # pygame.draw.circle(screen, border_color, (posX, posY), 12)  # draw piece border
    # pygame.draw.circle(screen, inner_color, (posX, posY), 10)  # draw piece

# show message for user on screen
def show_message(message):
    text = pygame.font.Font.render(' ' + message + ' ', True, (255, 255, 255), (120, 195, 46))  # create message
    textRect = text.get_rect()  # create a rectangle
    textRect.centerx = screen.get_rect().centerx  # center the rectangle
    textRect.centery = screen.get_rect().centery
    screen.blit(text, textRect)  # blit the text


# show countdown on screen
# def show_countdown(i):
#     while i >= 0:
#         tim = font_big.render(' ' + repr(i) + ' ', True, (255, 255, 255), (20, 160, 210))  # create message
#         timRect = tim.get_rect()  # create a rectangle
#         timRect.centerx = screen.get_rect().centerx  # center the rectangle
#         timRect.centery = screen.get_rect().centery + 50
#         screen.blit(tim, timRect)  # blit the text
#         pygame.display.flip()  # display scene from buffer
#         i -= 1
#         pygame.time.wait(1000)  # pause game for a second


# will display the winner and do a countdown to a new game
def show_winner(score):
    if score>0:
        show_message("The Computer Won!")
    elif score==0:
        show_message("It's a draw!")
    else:
        show_message("You Won!")
    pygame.display.flip()  # display scene from buffer

# function displaying position of clicked square
def mouse_click(pos):
    global SELECTED  # use global variables

    # only go ahead if we can actually play :)
    if (turn != 'black' and white.type != 'cpu') or (turn != 'white' and black.type != 'cpu'):
        column = int(pos[0] / (window_size[0] / board_size))
        row = int(pos[1] / (window_size[1] / board_size))

        if board[row][column] != 0 and board[row][column].color == turn:
        selected = row, column  # 'select' a piece
    else:
        moves = avail_moves(board, turn)  # get available moves for that player
        for i in range(len(moves)):
            if selected[0] == moves[i][0] and selected[1] == moves[i][1]:
                if row == moves[i][2] and column == moves[i][3]:
                    make_move(selected, (row, column), board)  # make the move
                    move_limit[1] += 1  # add to move limit
                    end_turn()  # end turn


######################## START OF GAME ########################

pygame.init()  # initialize pygame

screen = pygame.display.set_mode(WINDOW_SIZE)  # set window size
pygame.display.set_caption(TITLE)  # set title of the window
clock = pygame.time.Clock()  # create clock so that game doesn't refresh that often

background = pygame.image.load(BACKGROUND_IMAGE).convert()  # load background







while True:  # main game loop
    for event in pygame.event.get():  # the event loop
        if event.type == QUIT:
            exit()  # quit game
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
            mouse_click(event.pos)  # mouse click

    screen.blit(background, (0, 0))  # keep the background at the same spot

    # let user know what's happening (whose turn it is)
    # create antialiased font, color, background
    if TURN==1:
        show_message('YOUR TURN')
    else:
        show_message('CPU THINKING...')

    # draw pieces on board
    for m in range(6):
        for n in range(6):
            if board[m][n] != 0:
                draw_piece(m + 1, n + 1, board[m][n].color, board[m][n].king)

    # show intro
    if start == True:
        show_message('Welcome to ' + title)
        show_countdown(pause)
        start = False

    # check state of game
    end = end_game(board)
    if end[1] == 0:
        show_winner("black")
    elif end[0] == 0:
        show_winner("white")

    # check if we breached the threshold for number of moves
    elif move_limit[0] == move_limit[1]:
        show_winner("draw")

    else:
        pygame.display.flip()  # display scene from buffer

    # cpu play
    if turn != 'black' and white.type == 'cpu':
        cpu_play(white)  # white cpu turn
    elif turn != 'white' and black.type == 'cpu':
        cpu_play(black)  # black cpu turn

    clock.tick(fps)  # saves cpu time




#-----------------------------------------------------------------------------------------------------------------------

def main():
    global MOVE
    global DIFFICULTY
    global TURN

    b=Board()
    b.printBoard()
    turnSelect()
    selectDifficulty()
    human=Player()
    computer=Player()
    computer.TYPE="C"
    while MOVE!=2:
        if TURN==1:
            hstate = human.endMove(b,"H")
            if hstate == "Terminate":
                MOVE=2
                break
            elif hstate !="Switch":
                human.getMove(b)

            cstate = computer.endMove(b,"C")
            if cstate == "Terminate":
                MOVE=2
                break
            elif cstate != "Switch":
                computer.checkAI(b)

        elif TURN==2:
            cstate = computer.endMove(b,"C")
            if cstate == "Terminate":
                break
            elif cstate != "Switch":
                computer.checkAI(b)

            b.printBoard()
            hstate = human.endMove(b, "H")
            if hstate == "Terminate":
                break
            elif hstate != "Switch":
                human.getMove(b)
        b.printBoard()

    score=b.winCheck()
    if score>0:
        print("\nThe Computer Won!")
    elif score==0:
        print("\nIt's A Tie!")
    else:
        print("\nYou Won!")
    print("\nGame Statistics:\nMaximum Depth Attained: {0}\nNodes Expanded: {1}\nMax Pruning: {2}\nMin Pruning: {3}".format(MAX_DEPTH,NODES,MAX_PRUN,MIN_PRUN))

main()