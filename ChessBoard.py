class Board():

    def __init__(self):  

        # Chess Board representation as a 2D list
        #    First character in the string represents the color (b for Black, w for White)
        #    Second character is the piece (R for Rook, N for Knight)
        #    -- represents no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "wP", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "bP", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],    
        ]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.movesLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movesLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.movesLog) != 0:
            move = self.movesLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
    
    # Considers checks on the King
    def getValidMoves(self):
        return self.getAllPossibleMoves()

    # Does not consider checks on the King
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) # Call appropriate move funciton based on piece type
        return moves
                    
    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:
            if self.board[row - 1][col] == "--": # One square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": # Two square pawn advance if first move
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0: # Make sure within the board
                if self.board[row - 1][col - 1][0] == 'b': # Capture on left
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7: 
                if self.board[row - 1][col + 1][0] == 'b': # Capture on right
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if self.board[row + 1][col] == "--": # One square pawn advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--": # Two square pawn advance if first move
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0: # Make sure within the board
                if self.board[row + 1][col - 1][0] == 'w': # Capture on left
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7: 
                if self.board[row + 1][col + 1][0] == 'w': # Capture on right
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

    def getRookMoves(self, row, col, moves):
        pass

    def getKnightMoves(self, row, col, moves):
        pass

    def getBishopMoves(self, row, col, moves):
        pass

    def getQueenMoves(self, row, col, moves):
        pass

    def getKingMoves(self, row, col, moves):
        pass




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

