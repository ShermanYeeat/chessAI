import pygame as pyg
import ChessBoard


WIDTH = HEIGHT = 600
DIMENSION = 8
MAX_FPS = 30
SQUARE_SIZE = 75
IMAGES = {}

def load_chess_pieces():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP", "bR", "bN", "bB", "bQ", "bK", "bP"]
    for piece in pieces:
        IMAGES[piece] = pyg.transform.scale(pyg.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    pyg.init()
    window = pyg.display.set_mode((WIDTH, HEIGHT))
    board = pyg.transform.scale(pyg.image.load("images/board.png"), (WIDTH, HEIGHT))
    clock = pyg.time.Clock()
    game = ChessBoard.ChessBoard()
    load_chess_pieces()
    running = True
    squareSelected = () # initially, no square is selected, but will keep track of the last click of the user
    playerClicks = [] # keep track of player clicks i.e. [(1, 2), (1, 4)]
    while running:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            elif event.type == pyg.MOUSEBUTTONDOWN:
                location = pyg.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if squareSelected == (row, col): # user clicked same square twice, do nothing
                    squareSelected = () 
                    playerClicks = [] 
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                if len(playerClicks) == 2: # if player clicked twice
                    move = ChessBoard.Move(playerClicks[0], playerClicks[1], game.board)
                    print(move.getChessNotation())
                    game.makeMove(move)
                    squareSelected = ()
                    playerClicks = []

        draw_game(window, game, board)
        clock.tick(MAX_FPS)
        pyg.display.flip()


def draw_game(window, game, board):
    window.blit(board, (0, 0))
    draw_pieces(window, game)
    pyg.display.update()
    
    

def draw_pieces(window, game):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = game.board[row][col]
            if piece != "--":
                window.blit(IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


if __name__ == "__main__":
    main()



