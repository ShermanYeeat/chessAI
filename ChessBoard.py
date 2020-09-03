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
        self.whitesMove = True
        self.movesLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movesLog.append(move)
        self.whitesMove = not self.whitesMove
        # Update king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation(move.endRow, move.endCol)
        elif move.pieceMoves == 'bK':
            self.blackKingLocation(move.endRow, move.endCol)

    def undoMove(self):
        if len(self.movesLog) != 0:
            move = self.movesLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whitesMove = not self.whitesMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation(move.startRow, move.startCol)
            elif move.pieceMoves == 'bK':
                self.blackKingLocation(move.startRow, move.startCol)
    
    # Considers checks on the King
    def getValidMoves(self):
        return self.getAllPossibleMoves()

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




class Move():

    rankToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    rowsToRanks = {v: k for k, v in rankToRows.items()}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
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

