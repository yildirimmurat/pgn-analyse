#!/usr/bin/python3
import sys
import re
import cs50
from helpers import *
from analyseSingleMove import analyseMove, findCellByRowLocation, findCellByColLocation
import numpy as np


# TODO --> en passant for pawns
# TODO --> for Ne2, Bxe2 emptyCell didnt work
# TODO --> for Nf6, other knight disappears




def main():
    printBoard()
    putPiecesIntoDefaultPosition()
    printBoard()

    #readSingleGameFromDB()
    gameId = readSingleGameGromDB()

    #readMovesFromGame()
    moveList = readMovesFromGame(gameId)

    playGame(board, moveList)

# play a simple game by given move list
def playGame(board, moveList):
    color = colors['BLACK']
    for i in range(len(moveList)):
        color = switchColor(color)
        print('color is: ', color)
        print('move is: ', moveList[i])
        move = moveList[i]

        output = analyseMove(board, move, color)

        if len(output['piece']) == 2:
            castle(color, output)

        elif (isinstance(output['previousCell'], list)):
            possibleFirstPawnMove(color, output, board)
            
        elif(output['previousCell'] == 'previousCell'):
            makeMoveFromSavedLocation(color, output, board)

        else:
            makeMoveByGivenLocation(color, output, board)

        if output['promotion'] != '':
            promote(output['nextCell'], color, output['promotion'])

        printBoard()

    return

# make move when there is only one possible piece to move there
def makeMoveByGivenLocation(color, output, board):
    piece=color+output['piece']
    previousCell=output['previousCell']
    nextCell=output['nextCell']
    captureCell(piece, previousCell, nextCell)

    return

# when there is more than one possibility move from the appropriate  piece which is saved on a location
def makeMoveFromSavedLocation(color, output, board):
    piece=color+output['piece']
    nextCell=output['nextCell']

    previousCell=findSavedCellLocation(piece)
    if (len(previousCell) == 1):
        previousCell = previousCell[0]
    else:
        previousCell = getPreviousCellByPieceMove(piece, previousCell, nextCell)

    captureCell(piece, previousCell, nextCell)

    return

# helper function for makeMoveFromSavedLocation
def getPreviousCellByPieceMove(piece, previousCell, nextCell):
    numOfPieces = len(previousCell)
    for i in range(numOfPieces):
        capture = canCapture(piece[1], previousCell[i], nextCell)
        if capture:
            previousCell = previousCell[0]
            break
    return previousCell

# make possible first move
def possibleFirstPawnMove(color, output, board):
    # e.g for e4 move previous cell could be both e3 or e2
    # TODO problem when both e3 and e2 are occupied by a pawn
    
    piece=color+output['piece']
    for i in range(len(output['previousCell'])):
        cell = output['previousCell'][i]
        index = mapCellToIndex(cell)
        if (board[index[0]][index[1]] != '--'):
            previousCell = cell
            break
    nextCell=output['nextCell']
    captureCell(piece, previousCell, nextCell)

    return

# make castle
def castle(color, output):
    # Castling
    for i in range(2):
        piece=color+output['piece'][i]
        previousCell=output['previousCell'][i]
        nextCell=output['nextCell'][i]
        captureCell(piece, previousCell, nextCell)

    return

# promote a cell by given type
def promote(cell, color, promotionType):
    index = mapCellToIndex(cell)
    piece = color+promotionType
    fillCell(cell, piece)

    return

# capture a cell by piece
def captureCell(piece, previousCell, nextCell):
    print('previousCell:', previousCell)
    print('nextCell: ', nextCell)
    print('piecess-..', piece)
    emptyCell(previousCell)
    fillCell(nextCell, piece)

    return

# return true if type of a piece can capture the cell from a prev. cell
def canCapture(piece, previousCell, nextCell):
    if piece == 'R':

        sameRow = checkOnSameRow(previousCell, nextCell)
        sameCol = checkOnSameCol(previousCell, nextCell)


        if sameRow:
            if not checkPieceInRow(previousCell, nextCell):
                return True
            return False
        elif sameCol:
            if not checkPieceInCol(previousCell, nextCell):
                return True
            return False
        else:
            return False

    elif piece=='Q':
        # if has on same diagonal or same row or same col
        sameDiagonal = checkOnSameDiagonal(previousCell, nextCell)
        sameRow = checkOnSameRow(previousCell, nextCell)
        sameCol = checkOnSameCol(previousCell, nextCell)

        if sameRow:
            if not checkPieceInRow(previousCell, nextCell):
                return True
            return False
        elif sameCol:
            if not checkPieceInCol(previousCell, nextCell):
                return True
            return False
        elif sameDiagonal:
            if not checkPieceInDiagonal(previousCell, nextCell):
                return True
            return False
        else:
            return False

    elif piece == 'N':
        print('in here')
        prevCellCol = map[previousCell[0]]
        prevCellRow = int(previousCell[1])

        nextCellCol = map[nextCell[0]]
        nextCellRow = int(nextCell[1])

        colDiff = abs(prevCellCol - nextCellCol)
        rowDiff = abs(prevCellRow - nextCellRow)

        print('col', colDiff)
        print('row', rowDiff)

        if (colDiff == 1 and rowDiff == 2) or (colDiff == 2 and rowDiff == 1):
            return True
        return False

    elif piece == 'B':
        prevColor = getCellColor(previousCell)
        nextColor = getCellColor(nextCell)
        if prevColor == nextColor:
            return True
        return False

# returns False if there is no piece between cells which are on same row
def checkPieceInRow(previousCell, nextCell):

    row = int(previousCell[1]) - 1

    prevCol = map[previousCell[0]]
    nextCol = map[nextCell[0]]

    if (prevCol > nextCol):
        prevCol, nextCol = nextCol, prevCol

    # CHECK IF adjacent cells
    if(nextCol - prevCol == 1):
        return False
    else:
        for i in range(prevCol + 1, nextCol):
            searchIndex = [row, i]
            cell = mapIndexToCell(searchIndex)
            val = getCellValue(board, cell)
            if (val != '--'):
                return True
        return False

# returns False if there is no piece between cells which are on same col
def checkPieceInCol(previousCell, nextCell):
    
    col = map[previousCell[0]]

    prevRow = int(previousCell[1]) - 1
    nextRow = int(nextCell[1]) - 1

    if (prevRow > nextRow):
        prevRow, nextRow = nextRow, prevRow

    # CHECK IF adjacent cells
    if(nextRow - prevRow == 1):
        return False
    else:
        for i in range(prevRow + 1, nextRow):
            searchIndex = [i, col]
            cell = mapIndexToCell(searchIndex)
            val = getCellValue(board, cell)
            if (val != '--'):
                return True
        return False           

# returns False if there is no piece between cells which are on same diagonal
def checkPieceInDiagonal(previousCell, nextCell):
    
    prevRow = int(previousCell[1]) - 1
    nextRow = int(nextCell[1]) - 1

    prevCol = map[previousCell[0]]
    nextCol = map[nextCell[0]]

    toUp = 1
    if (prevRow > nextRow):
        prevRow, nextRow = nextRow, prevRow
        prevCol, nextCol = nextCol, prevCol
    if(prevCol > nextCol):
        # if previous cell is on the upper part of the board, then go downwards while searching
        toUp = -1

    # CHECK IF adjacent cells
    if(nextRow - prevRow == 1):
        return False
    else: 
        col = prevCol
        for i in range(prevRow + 1, nextRow):
            col = col + toUp
            searchIndex = [i, col]
            cell = mapIndexToCell(searchIndex)
            val = getCellValue(board, cell)
            if (val != '--'):
                return True
        return False

# puts a piece into a desired location on the board
def putPieceIntoBoard(piece, location):
    global board

    index=mapCellToIndex(location)
    row=index[0]
    col=index[1]
    board[row][col] = piece

    return  

# puts multiple pieces into board
def putPieceIntoBoardByArray(arr):
    for i in range(len(arr)):
        piece=arr[i][0]
        location=arr[i][1]
        putPieceIntoBoard(piece, location)
    
    return

# put pieces into default location in the beginning of the game
def putPiecesIntoDefaultPosition():
    # default position
    # first letter is whether it is (W)hite or (B)lack
    # second letter is about type of piece (Q):Queen etc.    putPieceIntoBoard('BR', 'a8')
    putPieceIntoBoardByArray([['BR', 'a8'], ['BN', 'b8'], ['BB', 'c8'], ['BQ', 'd8'], ['BK', 'e8'], ['BB', 'f8'], ['BN', 'g8'], ['BR', 'h8']])
    putPieceIntoBoardByArray([['Bp', 'a7'], ['Bp', 'b7'], ['Bp', 'c7'], ['Bp', 'd7'], ['Bp', 'e7'], ['Bp', 'f7'], ['Bp', 'g7'], ['Bp', 'h7']])
    putPieceIntoBoardByArray([['Wp', 'a2'], ['Wp', 'b2'], ['Wp', 'c2'], ['Wp', 'd2'], ['Wp', 'e2'], ['Wp', 'f2'], ['Wp', 'g2'], ['Wp', 'h2']])
    putPieceIntoBoardByArray([['WR', 'a1'], ['WN', 'b1'], ['WB', 'c1'], ['WQ', 'd1'], ['WK', 'e1'], ['WB', 'f1'], ['WN', 'g1'], ['WR', 'h1']])
    
    savedLocations['BR']=['a8', 'h8']
    savedLocations['BN']=['b8', 'g8']
    savedLocations['BB']=['c8', 'f8']
    savedLocations['BQ']=['d8'] # saved as an array because afterwards pawns could promote
    savedLocations['BK']=['e8']
    savedLocations['Bp']=['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7']

    savedLocations['WR']=['a1', 'h1']
    savedLocations['WN']=['b1', 'g1']
    savedLocations['WB']=['c1', 'f1']
    savedLocations['WQ']=['d1'] # saved as an array because afterwards pawns could promote
    savedLocations['WK']=['e1']
    savedLocations['Wp']=['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2']

    return

# print the board row by row
def printBoard():
    print("=================================")
    for i in range(8):
        print(board[8-i-1])
    print("=================================")

# show indexes of the piece on the board
def showLocation(piece):#todo searchIn -- whole board or just white-black squares, how many piece there are currently
    locationArr=[]
    for i in range(8):
        for j in range(8):
            if(board[i][j]==piece):
                index=[i, j]
                cell=mapIndexToCell(index)
                locationArr.append(cell)

    return locationArr

# returns gameId of a game on games table
def readSingleGameGromDB():
    print("reading single game from database")
    return int('4')

def readMovesFromGame(gameId):
    print("reading moves from game")
    # moveList=['e4', 'e5', 'Nf3', 'Nc6', 'd4', 'd5', 'Nxe5', 'Nxd4', 'a8=Q', 'b1=N', 'Rb1', 'Bd7', 'Qxd8+', 'b6', 'Ngxf3', 'gxh1=R']
    moveList = ['e4', 'c6', 'd4', 'd5', 'exd5', 'cxd5', 'Bd3', 'Nf6', 'c3', 'Bg4', 'Qb3', 'Qc7', 'Ne2', 'Bxe2', 'Bxe2', 'Nc6']
# 9.O-O e6 10.Be3 Bd6 11.f4 O-O 12.Qd1 Qb6 13.b4 Ne4 14.Bd3 f5 15.Rf3 a5 16.b5 Ne7
# 17.c4 dxc4 18.Bxc4 Rf6 19.Qb3 a4 20.Bxe6+ Kh8 21.Qc4 Bxf4 22.Bxf4 Rxe6 23.Na3 Rc8
# 24.Qxa4 Nc3 25.Qb4 Ned5 26.Rxc3 Nxc3 27.Kh1 Nd5 28.Qd6
    return moveList




main()