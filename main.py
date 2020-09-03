import pygame as pyg
import ChessBoard


WIDTH = HEIGHT = 600
DIMENSION = 8
MAX_FPS = 30
SQUARE_SIZE = 75
IMAGES = {}

# Main driver of the chess engine
def main():
    pyg.init()
    window = pyg.display.set_mode((WIDTH, HEIGHT))
    clock = pyg.time.Clock()
    game = ChessBoard.Board() # creating the 2D list representation of the chess board
    validMoves = game.getValidMoves()
    moveMade = False # Boolean when a move is made so validMoves does not prematurely makes the appropriate moves
    create_chess_pieces() 
    running = True
    squareSelected = () # Will keep track of the last click of the user
    playerClicks = [] # Keep track of player clicks in (row, col) format i.e. [(1, 2), (1, 4)]
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            elif event.type == pyg.MOUSEBUTTONDOWN:
                location = pyg.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if squareSelected == (row, col): # User clicked same square twice, do nothing
                    squareSelected = () 
                    playerClicks = [] 
                else: # Add it to player clicks if a different square was clicked
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                if len(playerClicks) == 2: # Player clicked two different squares
                    move = ChessBoard.Move(playerClicks[0], playerClicks[1], game.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        game.makeMove(move)
                        moveMade = True
                        squareSelected = ()
                        playerClicks = []
                    else: # invalid second click / Move i.e (second click on friendly piece)
                        playerClicks = [squareSelected]
            elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_u: # Undo when u is pressed
                    game.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = game.getValidMoves()
            moveMade = False

        draw_game(window, game)
        clock.tick(MAX_FPS)
        pyg.display.flip()

# Fitting chess piece images to the correct size relative to the chess board
def create_chess_pieces():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP", "bR", "bN", "bB", "bQ", "bK", "bP"]
    for piece in pieces:
        IMAGES[piece] = pyg.transform.scale(pyg.image.load('images/' + piece + '.png'), (SQUARE_SIZE, SQUARE_SIZE))

def draw_game(window, game):
    chess_board = pyg.transform.scale(pyg.image.load('images/board.png'), (WIDTH, HEIGHT))
    window.blit(chess_board, (0, 0))
    draw_pieces(window, game)
    pyg.display.update()
    
def draw_pieces(window, game):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = game.board[row][col]
            if piece != '--':
                window.blit(IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

if __name__ == "__main__":
    main()



