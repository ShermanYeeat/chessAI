import pygame as pyg
from pygame import gfxdraw
import ChessBoard
import sys 
sys.setrecursionlimit(5000) 

WIDTH = HEIGHT = 600
DIMENSION = 8
MAX_FPS = 60
SQUARE_SIZE = 75
IMAGES = {}
CLICK = False

# Main driver of the chess engine
def main(window, clock, versusPlayer):
    if versusPlayer:
        pyg.display.set_caption('vs Player')
    else:
        pyg.display.set_caption('vs AI')
    game = ChessBoard.Board() # creating the 2D list representation of the chess board
    validMoves = game.getValidMoves()
    moveMade = False # Boolean when a move is made so validMoves does not prematurely makes the appropriate moves
    create_chess_pieces() 
    running = True
    squareSelected = () # Will keep track of the last click of the user
    playerClicks = [] # Keep track of player clicks in (row, col) format i.e. [(1, 2), (1, 4)]
    gameOver = False
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            elif event.type == pyg.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pyg.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if squareSelected == (row, col): # If user clicked same square twice, reset 
                        squareSelected = () 
                        playerClicks = [] 
                    else: # Add it to player clicks if a different square was clicked
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2: # Player clicked two different squares
                        move = ChessBoard.Move(playerClicks[0], playerClicks[1], game.board)
                        # print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                game.makeMove(validMoves[i])
                                # game.computeScore()
                                moveMade = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade: # Invalid second click/Move i.e (second click on friendly piece)
                            playerClicks = [squareSelected]
            elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_u: # Undo when u is pressed
                    game.undoMove()
                    moveMade = True
                if event.key == pyg.K_r: # Reset game when r is pressed 
                    game = ChessBoard.Board()
                    validMoves = game.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                if event.key == pyg.K_ESCAPE:
                    running = False

            
        if moveMade:
            validMoves = game.getValidMoves()
            moveMade = False

        if not gameOver:
            draw_game(window, game, validMoves, squareSelected, game.movesLog)
        

        if game.checkMate:
            gameOver = True
            if game.whitesMove:
                draw_text(window, 'Black Wins By Checkmate')
            else:
                draw_text(window, 'White Wins By Checkmate')
        elif game.staleMate:
            gameOver = True
            draw_text(window, 'Stalemate')

        if not versusPlayer and not game.whitesMove:
            game.aiMove()
            moveMade = True

        clock.tick(MAX_FPS)
        pyg.display.flip()


def main_menu():
    pyg.init()
    window = pyg.display.set_mode((WIDTH, HEIGHT))
    clock = pyg.time.Clock()
    running = True
    font = pyg.font.SysFont('Arial', 25)
    pyg.display.set_caption('Main Menu')
    while running:       
        window.fill((0, 0, 0))
        mx, my = pyg.mouse.get_pos()
        button_1 = pyg.Rect(235, 200, 125, 50)
        button_2 = pyg.Rect(235, 300, 125, 50)
        if button_1.collidepoint((mx, my)):
            if CLICK:
                main(window, clock, True)
        if button_2.collidepoint((mx, my)):
            if CLICK:  
                main(window, clock, False)
        pyg.draw.rect(window, (255, 255 , 255), button_1)
        pyg.draw.rect(window, (255, 255 , 255), button_2)
        window.blit(font.render("vs Player", True, (0, 0, 0)), (260, 210))
        window.blit(font.render("vs AI", True, (0, 0, 0)), (260, 310))
        CLICK = False
        for event in pyg.event.get():
            if event.type == pyg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    CLICK = True
            if event.type == pyg.QUIT:
                running = False   
        pyg.display.update()
        clock.tick(MAX_FPS)


                
    
# Highlight king if in check
def highlight_king(screen, game):
    if game.inCheck():
        if game.whitesMove:
            row, col = game.whiteKingLocation
        else: 
            row, col = game.blackKingLocation
        s = pyg.Surface((SQUARE_SIZE, SQUARE_SIZE)) # Highlight square
        s.set_alpha(125) # Transparency value (0 - 255)
        s.fill(pyg.Color('red'))
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Highlight moves for piece selected
def highlight_squares(screen, game, validMoves, squareSelected, movesLog):
    
    squares = pyg.Surface((SQUARE_SIZE, SQUARE_SIZE)) # Highlight square
    squares.set_alpha(100) # Transparency value (0 - 255)

    # Highlight last move
    if len(movesLog) > 0:
        squares.fill(pyg.Color('yellow'))
        last_move = movesLog.pop()
        screen.blit(squares, (SQUARE_SIZE * last_move.startCol, SQUARE_SIZE * last_move.startRow))
        screen.blit(squares, (SQUARE_SIZE * last_move.endCol, SQUARE_SIZE * last_move.endRow))
        movesLog.append(last_move)

    if squareSelected != ():
        row, col = squareSelected
        if game.board[row][col][0] == ('w' if game.whitesMove else 'b'): # Square selected is a piece we can move
            squares.fill(pyg.Color('blue'))
            screen.blit(squares, (col * SQUARE_SIZE, row * SQUARE_SIZE))
             # squares.fill(pyg.Color('dark green')) # Highlight moves from that square
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    squares.fill(pyg.Color('red'))
                    squares.set_alpha(150)
                    if game.whitesMove:
                        if game.board[move.endRow][move.endCol][0] == 'b':
                            screen.blit(squares, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))
                        elif game.board[move.endRow][move.endCol] == '--':
                            draw_circle(screen, SQUARE_SIZE * move.endCol + (75 // 2),
                                       SQUARE_SIZE * move.endRow + (75 // 2), 8, (0, 85, 0, 175))
                    else:
                        if game.board[move.endRow][move.endCol][0] == 'w':
                            screen.blit(squares, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))
                        elif game.board[move.endRow][move.endCol] == '--':
                            draw_circle(screen, SQUARE_SIZE * move.endCol + (75 // 2),
                                       SQUARE_SIZE * move.endRow + (75 // 2), 8, (0, 85, 0, 175))
                    # screen.blit(squares, (SQUARE_SIZE * move.endCol, SQUARE_SIZE * move.endRow))
                    



# Fitting chess piece images to the correct size relative to the chess board
def create_chess_pieces():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP", "bR", "bN", "bB", "bQ", "bK", "bP"]
    for piece in pieces:
        IMAGES[piece] = pyg.transform.scale(pyg.image.load('images/' + piece + '.png'), (SQUARE_SIZE, SQUARE_SIZE))
    
def draw_circle(surface, x, y, radius, color):
    pyg.gfxdraw.aacircle(surface, x, y, radius, color)
    pyg.gfxdraw.filled_circle(surface, x, y, radius, color)

def draw_game(window, game, validMoves, squareSelected, movesLog):
    chess_board = pyg.transform.scale(pyg.image.load('images/board.png'), (WIDTH, HEIGHT))
    window.blit(chess_board, (0, 0))
    highlight_king(window, game)
    highlight_squares(window, game, validMoves, squareSelected, movesLog)
    draw_pieces(window, game)
    pyg.display.update()
    
def draw_pieces(window, game):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = game.board[row][col]
            if piece != '--':
                window.blit(IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_text(screen, text):
    font = pyg.font.SysFont('Helvetica', 32, True, False)
    textObject = font.render(text, 0, pyg.Color('Black'))
    textLocation = pyg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)





#if __name__ == "__main__":
#    main()
main_menu()


