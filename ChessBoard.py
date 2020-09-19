import sys 
import time
sys.setrecursionlimit(5000) 
TIMEOUT = 30
start = None
end = None
class Board():

    def __init__(self):  

        # Chess Board representation as a 2D list
        #    First character in the string represents the color (b for Black, w for White)
        #    Second character is the piece (R for Rook, N for Knight)
        #    -- represents no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],    
        ]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whitePieces = {'P': 8, 'R': 2, 'N': 2, 'B': 2, 'Q': 1, 'K': 1}
        self.blackPieces = {'P': 8, 'R': 2, 'N': 2, 'B': 2, 'Q': 1, 'K': 1}
        self.whitesMove = True
        self.movesLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.currentCastlingRight = CastleRights(True, True, True, True)
        # Update log correctly with the actual values
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs )]
        self.INTIAL_DEPTH = 2
        self.currentDepth = 0
        self.globalBestMove = None
        self.bestMove = None
        self.timedOut = None
           
    def makeMove(self, move):
        if move.pieceCaptured[0] == 'w':
            self.whitePieces[move.pieceCaptured[1]] -= 1
        elif move.pieceCaptured[0] == 'b':
            self.blackPieces[move.pieceCaptured[1]] -= 1
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movesLog.append(move)
        self.whitesMove = not self.whitesMove

        # Update king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion (only for QUEEN)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # Kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # Moves rook into new square
                self.board[move.endRow][move.endCol + 1] = '--' # Erase old rook
            else: # Queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # Moves rook into new square
                self.board[move.endRow][move.endCol - 2] = '--' # Erase old rook

        # Update castling rights whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
            

    def undoMove(self):
        if len(self.movesLog) != 0:
            move = self.movesLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whitesMove = not self.whitesMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo castling rights
            self.castleRightsLog.pop() # Get rid of new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1] 
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) # Update castle rights
            # Undo castling 
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] == '--'
                else: # Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] == '--'

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.bks = False
    
    # Considers checks on the King
    def getValidMoves(self):
        # Hold because when we makeMove(moves[i]), it can change self.currentCastlingRight
        tempCasteRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves() # Generate all possible moves
        if self.whitesMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # Then for each move, make the move (go through list backwards b/c if remove a move, then you could skip if you did it forward)
        for i in range(len(moves) -1, -1, -1):
            self.makeMove(moves[i]) # Swap turn
            opponentMoves = self.getAllPossibleMoves() # Generate all opponents move
            # For each of those moves, see if it attacks king
            # If it does, it is not a valid move
            self.whitesMove = not self.whitesMove # Swap turn, self.MakeMove changes turn
            if self.inCheck():
                moves.remove(moves[i]) 
            self.whitesMove = not self.whitesMove # Swap turn
            self.undoMove() # Swap turn
        if len(moves) == 0: # Checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.currentCastlingRight = tempCasteRights
        return moves


    # Determine if current player is in check
    def inCheck(self):
        if self.whitesMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Determine if the enemy can attack the square (row, col)
    def squareUnderAttack(self, row, col):
        self.whitesMove = not self.whitesMove  # Switch to opponent's turn to figure out all of their possible moves
        opponentMoves = self.getAllPossibleMoves()
        self.whitesMove = not self.whitesMove # Switch turn's back 
        for move in opponentMoves:
            if move.endRow == row and move.endCol == col: # Square is under attack
                return True
        return False


    # Does not consider checks on the King
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whitesMove) or (turn == 'b' and not self.whitesMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) # Call appropriate move function based on piece type
        return moves
                    
    def getPawnMoves(self, row, col, moves):
        if self.whitesMove:
            if row - 1 >= 0: # Make sure within the board
                if self.board[row - 1][col] == '--': # One square pawn advance
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == '--': # Two square pawn advance if first move
                        moves.append(Move((row, col), (row - 2, col), self.board))
                if col - 1 >= 0: # Make sure within the board
                    if self.board[row - 1][col - 1][0] == 'b': # Capture on left
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                if col + 1 <= 7: 
                    if self.board[row - 1][col + 1][0] == 'b': # Capture on right
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if row + 1 <= 7: # Make sure within the board
                if self.board[row + 1][col] == '--': # One square pawn advance
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == '--': # Two square pawn advance if first move
                        moves.append(Move((row, col), (row + 2, col), self.board))
                if col - 1 >= 0: # Make sure within the board
                    if self.board[row + 1][col - 1][0] == 'w': # Capture on left
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                if col + 1 <= 7: 
                    if self.board[row + 1][col + 1][0] == 'w': # Capture on right
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))

    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1)) # up, right, down, left
        enemyColor = 'b' if self.whitesMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((row, col), (endRow, endCol), self.board)) 
                    elif endPiece[0] == enemyColor: # Enemy Piece, take
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break # Break to get out of inner loop, Rook cannot get go further as piece is in way
                    else: # Friendly piece, same reason as previous line comment
                        break
                else: # Off board
                    break

    def getKnightMoves(self, row, col, moves):
        directions = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
        enemyColor = 'b' if self.whitesMove else 'w'
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == '--':
                    moves.append(Move((row, col), (endRow, endCol), self.board)) 


    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # top right, top left, bottom right, bottom left
        enemyColor = 'b' if self.whitesMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((row, col), (endRow, endCol), self.board)) 
                    elif endPiece[0] == enemyColor: # Enemy Piece, take
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break # Break to get out of inner loop, Rook cannot get go further as piece is in way
                    else: # Friendly piece, same reason as previous line comment
                        break
                else: # Off board
                    break

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        directions = ((-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1))
        enemyColor = 'b' if self.whitesMove else 'w'
        for i in range(8):
            endRow = row + directions[i][0]
            endCol = col + directions[i][1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == '--':
                    moves.append(Move((row, col), (endRow, endCol), self.board)) 

    # Generate all valid castle moves for the king at (row, col) and add them to the list of moves
    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return # Can't castle while in check
        if (self.whitesMove and self.currentCastlingRight.wks) or (not self.whitesMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whitesMove and self.currentCastlingRight.wqs) or (not self.whitesMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)
        
        
    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove = True))


    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove = True))

    # Pieces are assigned values
    # Determine the score of white and black based on the current board
    def computeScore(self):
        pieceValues = {"P": 1, "B": 3, "N": 3, "R": 5, "Q": 9 , "K": 99}
        # blackPieces = []
        # whitePieces = []
        blackScore = 0
        whiteScore = 0
        for key, value in self.whitePieces.items():
            whiteScore += pieceValues[key] * value
        for key, value in self.blackPieces.items():
            blackScore += pieceValues[key] * value
        if self.whitesMove:
            return whiteScore - blackScore
        return blackScore - whiteScore
        """
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                color = self.board[row][col][0]
                piece = self.board[row][col]
                if color == 'w':
                    whitePieces.append(piece)
                elif color == 'b':
                    blackPieces.append(piece)
        for bPiece in blackPieces:
            blackScore += pieceValues[bPiece[1]]
        for wPiece in whitePieces:
            whiteScore += pieceValues[wPiece[1]]
        # print("White's score: " + str(whiteScore))
        # print("Black's score: " + str(blackScore))
        if self.whitesMove:
            return whiteScore - blackScore
        return blackScore - whiteScore
        """

    def undoMovee(self, move):
        if move.pieceCaptured[0] == 'w':
            self.whitePieces[move.pieceCaptured[1]] += 1
        elif move.pieceCaptured[0] == 'b':
            self.blackPieces[move.pieceCaptured[1]] += 1
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured
        self.whitesMove = not self.whitesMove
    

    def aiMove(self):
        self.makeMove(self.findBestMove())

    def findBestMove(self):
        self.timedOut = False
        start = time.time()
        for d in range(6):
            if d > 0:
                self.globalBestMove = self.bestMove
                print("Completed search with depth: " + str(self.currentDepth))
            self.currentDepth = self.INTIAL_DEPTH + d
            # self.maximizer(self.currentDepth, -10000, 10000, start)
            self.negamax(self.currentDepth, float("-inf"), float("inf"), start, self.whitesMove)
            if self.timedOut:
                return self.globalBestMove
        return self.globalBestMove

    def negamax(self, depth, alpha, beta, start, whitesMove):
        value = float("-inf")
        end = time.time()
        if end - start > TIMEOUT:
            self.timedOut = True
            return value
        if depth == 0:
            return self.computeScore()  
        moves = self.giveValuesToMoves(self.getValidMoves())
        orderedMoves = sorted(moves, key=lambda list: list[0], reverse=True)
        for val, move in orderedMoves:
            self.makeMove(move)
            value = max(value, - self.negamax(depth - 1, -beta, -alpha, start, not whitesMove))
            self.undoMovee(move)
            if value > alpha:
                alpha = value
                if depth == self.currentDepth:
                    self.bestMove = move
            if alpha >= beta:
                return alpha
        return value


    def giveValuesToMoves(self, moves):
        newMoves = []
        for move in moves:
            self.makeMove(move)
            score = self.computeScore()
            newMoves.append([score, move])
            self.undoMovee(move)
        return newMoves


    def maximizer(self, depth, alpha, beta, start):
        end = time.time()
        if (end - start > TIMEOUT):
            self.timedOut = True
            return alpha
        if depth == 0:
            return self.computeScore()
        moves = self.getValidMoves()
        for move in moves:
            self.makeMove(move)
            score = self.minimizer(depth - 1, alpha, beta, start)
            self.undoMovee(move)
            if score > alpha:
                alpha = score
                if depth == self.currentDepth:
                    # print(move)
                    self.bestMove = move
            if alpha >= beta:
                return alpha
        return alpha
        
    def minimizer(self, depth, alpha, beta, start):
        if depth == 0:
            return self.computeScore()
        moves = self.getValidMoves()
        for move in moves:
            self.makeMove(move)
            score = self.maximizer(depth - 1, alpha, beta, start)
            self.undoMovee(move)
            if score <= beta:
                beta = score
            if alpha >= beta:
                return beta
        return beta
        
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs): # WhiteQueensSide, BlackQueenSide, ...
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    rankToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    rowsToRanks = {v: k for k, v in rankToRows.items()}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isCastleMove = False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        self.isCastleMove = isCastleMove
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7): # Made it to end
            self.isPawnPromotion = True
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # moveID's are unique
        # 1323 means piece moving from (1,3) to (2,3)


    def getChessNotation(self):
        return self.getRankAndFile(self.startRow, self.startCol) + self.getRankAndFile(self.endRow, self.endCol)

    def getRankAndFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

    # Override equals function as 
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

