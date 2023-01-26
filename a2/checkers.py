import sys
import os
from copy import copy, deepcopy
import time

# Global variables

# Int <-> Char
TileToCharMap = {
  -2: 'B',
  -1: 'b',
   0: '.',
   1: 'r',
   2: 'R' 
}

# Char <-> Int
CharToTileMap = {
  'B': -2,
  'b': -1,
  '.': 0,
  'r': 1,
  'R': 2
}

# Debugging Variables
DebugMode = False
DumpStats = False
DumpBoard = False
CheckNumSuccessors = False
DumpIterativeDeepening = True
DumpTime = False

def DebugPrint(Str, Control):
  if Control:
    print(Str)


# Global Game Variables
BlackTurnG = -1
RedTurnG = 1
GameEndValG = 327319 # This is a magic number to indicate game end.
UsingAlphaBetaPruning = True
SearchDepthLimitG = 8
MinG = -10000000
MaxG = 10000000
UsingHeuristicG = False
UsingIterativeDeepeningG = True

# Global Timer
StartTimeG = 0
TimeLimit = 295.0

def TimerInit():
  global StartTimeG
  StartTimeG = time.time()

def TimeOut():
  global StartTimeG
  Period = time.time() - StartTimeG
  if Period > TimeLimit:
    return True
  return False

def ReportTotalTime():
  global StartTimeG
  Period = time.time() - StartTimeG
  DebugPrint("\nTime used in sec: {}".format(Period), DumpTime)


# Helper functiosn for I/O
def ErrLog(Str):
  # Logging for errors.
  sys.stderr.write(Str)
  exit()


def ReadFile(InputFileName):
  InputFile = open(InputFileName, "r")
  Board = []
  Row = 0
  for Line in InputFile:
    Board.append([])
    for c in Line:
      if c == '\n':
        continue
      Board[Row].append(CharToTileMap[c])
    if len(Board[Row]) != 8:
      ErrLog("Error: wrong # input cols. Line: {}; Size: {}\n". \
        format(Line, len(Board[Row])))
    Row += 1
  if len(Board) != 8:
    ErrLog("Error: wrong # input rows.")
  return Board


def WriteFile(OutputFileName, StrBoard):
  F = open(OutputFileName, "w")
  F.write(StrBoard)


# Game Helper
def InBound(Row, Col):
  return Row < 8 and Row >= 0 and Col < 8 and Col >= 0


# Get number: used to calculate the number of successors for the current player.
# Get number of jumps
def GetNumNextJumps(Board, Row, Col, dRow, isKing):
  Target1 = dRow        # Opponent's tile
  Target2 = dRow * 2    # Opponent's king 
  FoundJump = False
  Result = 0

  Row1 = Row + dRow
  Col1 = Col + 1
  Row2 = Row1 + dRow
  Col2 = Col1 + 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
    InBound(Row2, Col2) and Board[Row2][Col2] == 0:
    Result += 1

  Row1 = Row + dRow
  Col1 = Col - 1
  Row2 = Row1 + dRow
  Col2 = Col1 - 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
    InBound(Row2, Col2) and Board[Row2][Col2] == 0:
    Result += 1

  if not isKing:
    return Result

  Row1 = Row - dRow
  Col1 = Col + 1
  Row2 = Row1 - dRow
  Col2 = Col1 + 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
    InBound(Row2, Col2) and Board[Row2][Col2] == 0:
    Result += 1

  Row1 = Row - dRow
  Col1 = Col - 1
  Row2 = Row1 - dRow
  Col2 = Col1 - 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
    InBound(Row2, Col2) and Board[Row2][Col2] == 0:
    Result += 1

  return Result


# Get number of normal moves
def GetNumNextMoves(Board, Row, Col, dRow, isKing):
  Result = 0

  Row1 = Row + dRow
  Col1 = Col + 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    Result += 1

  Row1 = Row + dRow
  Col1 = Col - 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    Result += 1
  
  if not isKing:
    return Result
  
  Row1 = Row - dRow
  Col1 = Col + 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    Result += 1

  Row1 = Row - dRow
  Col1 = Col - 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    Result += 1

  return Result


# Get the actual jumps. Return a list of all possible moves. 
# Recursively process multi-jump.
def GetNextJumps(Board, Row, Col, dRow, isKing, Result):
  Val = Board[Row][Col] # The current val
  Target1 = dRow        # Opponent's tile
  Target2 = dRow * 2    # Opponent's king 
  FoundJump = False

  Row1 = Row + dRow
  Col1 = Col + 1
  Row2 = Row1 + dRow
  Col2 = Col1 + 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
     InBound(Row2, Col2) and Board[Row2][Col2] == 0:
     FoundJump = True
     NewBoard = deepcopy(Board)
     NewBoard[Row][Col] = 0
     NewBoard[Row1][Col1] = 0
     if (not isKing) and \
        ((dRow == -1 and Row2 == 0) or (dRow == 1 and Row2 == 7)):
      # King Promotion
      NewBoard[Row2][Col2] = Val * 2
      Result.append(NewBoard)
     else:
      NewBoard[Row2][Col2] = Val
      FoundLaterJump = GetNextJumps(NewBoard, Row2, Col2, dRow, isKing, Result)
      if not FoundLaterJump:
        Result.append(NewBoard)
  
  Row1 = Row + dRow
  Col1 = Col - 1
  Row2 = Row1 + dRow
  Col2 = Col1 - 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
     InBound(Row2, Col2) and Board[Row2][Col2] == 0:
     FoundJump = True
     NewBoard = deepcopy(Board)
     NewBoard[Row][Col] = 0
     NewBoard[Row1][Col1] = 0
     if (not isKing) and \
        ((dRow == -1 and Row2 == 0) or (dRow == 1 and Row2 == 7)):
      # King Promotion
      NewBoard[Row2][Col2] = Val * 2
      Result.append(NewBoard)
     else:
      NewBoard[Row2][Col2] = Val
      FoundLaterJump = GetNextJumps(NewBoard, Row2, Col2, dRow, isKing, Result)
      if not FoundLaterJump:
        Result.append(NewBoard)

  if (not isKing):
    return FoundJump
  
  # King's jump:
  Row1 = Row - dRow
  Col1 = Col + 1
  Row2 = Row1 - dRow
  Col2 = Col1 + 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
     InBound(Row2, Col2) and Board[Row2][Col2] == 0:
     FoundJump = True
     NewBoard = deepcopy(Board)
     NewBoard[Row][Col] = 0
     NewBoard[Row1][Col1] = 0
     NewBoard[Row2][Col2] = Val
     FoundLaterJump = GetNextJumps(NewBoard, Row2, Col2, dRow, isKing, Result)
     if not FoundLaterJump:
       Result.append(NewBoard)
  
  Row1 = Row - dRow
  Col1 = Col - 1
  Row2 = Row1 - dRow
  Col2 = Col1 - 1
  if InBound(Row1, Col1) and \
     (Board[Row1][Col1] == Target1 or Board[Row1][Col1] == Target2) and \
     InBound(Row2, Col2) and Board[Row2][Col2] == 0:
     FoundJump = True
     NewBoard = deepcopy(Board)
     NewBoard[Row][Col] = 0
     NewBoard[Row1][Col1] = 0
     NewBoard[Row2][Col2] = Val
     FoundLaterJump = GetNextJumps(NewBoard, Row2, Col2, dRow, isKing, Result)
     if not FoundLaterJump:
       Result.append(NewBoard)
  
  return FoundJump


# Get the actual moves. Return a list of all possible moves.
def GetNextMoves(Board, Row, Col, dRow, isKing, Result):
  Val = Board[Row][Col] # The current val

  Row1 = Row + dRow
  Col1 = Col + 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    NewBoard = deepcopy(Board)
    if (not isKing) and \
        ((dRow == -1 and Row1 == 0) or (dRow == 1 and Row1 == 7)):
      NewBoard[Row1][Col1] = Val * 2
    else:
      NewBoard[Row1][Col1] = Val
    NewBoard[Row][Col] = 0
    Result.append(NewBoard)

  Row1 = Row + dRow
  Col1 = Col - 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    NewBoard = deepcopy(Board)
    if (not isKing) and \
        ((dRow == -1 and Row1 == 0) or (dRow == 1 and Row1 == 7)):
      NewBoard[Row1][Col1] = Val * 2
    else:
      NewBoard[Row1][Col1] = Val
    NewBoard[Row][Col] = 0
    Result.append(NewBoard)
  
  if not isKing:
    return
  
  Row1 = Row - dRow
  Col1 = Col + 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    NewBoard = deepcopy(Board)
    NewBoard[Row1][Col1] = Val
    NewBoard[Row][Col] = 0
    Result.append(NewBoard)

  Row1 = Row - dRow
  Col1 = Col - 1
  if InBound(Row1, Col1) and Board[Row1][Col1] == 0:
    NewBoard = deepcopy(Board)
    NewBoard[Row1][Col1] = Val
    NewBoard[Row][Col] = 0
    Result.append(NewBoard)


# Stringlize the board.
def GetStrBoard(Board):
  StrBuffer = ""
  for Row in range(8):
    for Col in range(8):
      StrBuffer += TileToCharMap[Board[Row][Col]]
    StrBuffer += "\n"
  return StrBuffer


MidMap = [
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 1, 1, 1, 1, 0, 0],
  [0, 0, 1, 1, 1, 1, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0]
]

# Heuristic Function to evaluate the board.
def GetHeuristic(Board):
  NumTile = 0
  NumKing = 0
  NumBack = 0
  NumMid = 0
  NumSafe = 0
  
  for Row in range(8):
    for Col in range(8):
      Val = Board[Row][Col]
      if Val == 0:
        continue

      Side = 1 # Red
      if Val < 0: 
        Side = -1 # Black

      # Determine if it's a king or normal tile.
      if abs(Val) == 1:
        NumTile += Side
      else:
        NumKing += Side

      # Determine if it's in the back row.
      if (Side == 1 and Row == 7) or (Side == -1 and Row == 0):
        NumBack += Side

      # Determine if the tile is in the middle box.
      if MidMap[Row][Col] == 1:
        NumMid += Side

      # Determine if the tile is safe.
      if Side == 1:
        # Processing for red
        if Row == 7:
          NumSafe += 1
        elif Col == 0 or Col == 7:
          NumSafe += 1
        else:
          RightDown = Board[Row + 1][Col + 1]
          LeftDown = Board[Row + 1][Col - 1]
          if (RightDown > 0 or RightDown == -1) and \
             (LeftDown > 0 or LeftDown == -1):
            NumSafe += 1
      else:
        # Processing for black
        if Row == 0:
          NumSafe -= 1
        elif Col == 0 or Col == 7:
          NumSafe -= 1
        else:
          RightTop = Board[Row - 1][Col + 1]
          LeftTop = Board[Row - 1][Col - 1]
          if (RightTop < 0 or RightTop == 1) and \
             (LeftTop < 0 or LeftTop == 1):
            NumSafe -= 1
  
  Val = \
    NumTile * 5 + \
    NumKing * 10 + \
    NumBack * 4 + \
    NumMid * 1 + \
    NumSafe * 3
  return Val

      
# Class for the board, defining some helpers.
class BoardType:
  def __init__(self, Board, Turn):
    self.Board = Board
    self.Turn = Turn

    # Count tiles
    self.NumBlackTile = 0
    self.NumBlackKing = 0
    self.NumRedTile = 0
    self.NumRedKing = 0
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == CharToTileMap['B']:
          self.NumBlackKing += 1
        elif self.Board[Row][Col] == CharToTileMap['b']:
          self.NumBlackTile += 1
        elif self.Board[Row][Col] == CharToTileMap['R']:
          self.NumRedKing += 1
        elif self.Board[Row][Col] == CharToTileMap['r']:
          self.NumRedTile += 1

    # Val is the default utility, it will also be used as the heuristic for 
    # move ordering.
    self.Val = 0
    self.Val += self.NumRedKing * 2
    self.Val += self.NumRedTile
    self.Val -= self.NumBlackKing * 2
    self.Val -= self.NumBlackTile
    # Set legal moves to -1.
    self.NumLegalMove = -1


  # Used for move sorting
  def __lt__(self, other):
    if self.Turn == 1:
      # Parent turn is black, expand from small to large.
      return self.Val < other.Val
    else:
      return self.Val > other.Val


  # Used to recount the number of tiles.
  def Count(self):
    self.NumBlackTile = 0
    self.NumBlackKing = 0
    self.NumRedTile = 0
    self.NumRedKing = 0
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == CharToTileMap['B']:
          self.NumBlackKing += 1
        elif self.Board[Row][Col] == CharToTileMap['b']:
          self.NumBlackTile += 1
        elif self.Board[Row][Col] == CharToTileMap['R']:
          self.NumRedKing += 1
        elif self.Board[Row][Col] == CharToTileMap['r']:
          self.NumRedTile += 1


  def Dump(self, Depth = 0):
    StrBuffer = "\n"
    StrBuffer += GetStrBoard(self.Board)
    StrBuffer += "# b: {}\n".format(self.NumBlackTile)
    StrBuffer += "# B: {}\n".format(self.NumBlackKing)
    StrBuffer += "# r: {}\n".format(self.NumRedTile)
    StrBuffer += "# R: {}\n".format(self.NumRedKing)
    if Depth == 0:
      StrBuffer += "Depth: {}\n".format(Depth)
      StrBuffer += "Value: {}\n".format(self.GetUtility())
    return StrBuffer


  def Output(self):
    return GetStrBoard(self.Board)


  def DumpValue(self, Depth):
    StrBuffer = "\n"
    StrBuffer += "Depth: {}\n".format(Depth)
    StrBuffer += "Value: {}\n".format(self.GetUtility())
    return StrBuffer


  def GetUtility(self):
    # Default utility.
    NumSucc = 0
    if self.NumLegalMove != -1:
      NumSucc = self.NumLegalMove
    else:
      NumSucc = self.GetNumSuccessors()
    if NumSucc == 0:
      # Game End
      return -1 * GameEndValG * self.Turn
    if UsingHeuristicG:
      return GetHeuristic(self.Board)
    else:
      return self.Val


  def GetNumSuccessors(self):
    King = 0
    dRow = 0
    Tile = 0
    if self.Turn == 1:
      # Red
      dRow = -1
      King = CharToTileMap["R"]
      Tile = CharToTileMap["r"]
    elif self.Turn == -1:
      dRow = 1
      King = CharToTileMap["B"]
      Tile = CharToTileMap["b"]
    else:
      ErrLog("Wrong Turn...")

    Num = 0
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == King:
          Num += GetNumNextJumps(self.Board, Row, Col, dRow, True)
        elif self.Board[Row][Col] == Tile:
          Num += GetNumNextJumps(self.Board, Row, Col, dRow, False)

    if Num != 0:
      # Forced capture
      return Num

    Num = 0
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == King:
          Num += GetNumNextMoves(self.Board, Row, Col, dRow, True)
        elif self.Board[Row][Col] == Tile:
          Num += GetNumNextMoves(self.Board, Row, Col, dRow, False)

    return Num


  def GetSuccessors(self):
    King = 0
    dRow = 0
    Tile = 0
    if self.Turn == 1:
      # Red
      dRow = -1
      King = CharToTileMap["R"]
      Tile = CharToTileMap["r"]
    elif self.Turn == -1:
      dRow = 1
      King = CharToTileMap["B"]
      Tile = CharToTileMap["b"]
    else:
      ErrLog("Wrong Turn...")

    NextJumps = []
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == King:
          GetNextJumps(self.Board, Row, Col, dRow, True, NextJumps)
        elif self.Board[Row][Col] == Tile:
          GetNextJumps(self.Board, Row, Col, dRow, False, NextJumps)

    if len(NextJumps) != 0:
      # We found all the jumps.
      # Note: we may need to cache founded board.
      Result = []
      NextTurn = -1 * self.Turn
      for BoardArray in NextJumps:
        Result.append(BoardType(BoardArray, NextTurn))
      self.NumLegalMove = len(Result)
      # Path ordering
      Result.sort()
      return Result
    
    # If control flow reaches here, there is no legal captures.
    NextMoves = []
    for Row in range(8):
      for Col in range(8):
        if self.Board[Row][Col] == King:
          GetNextMoves(self.Board, Row, Col, dRow, True, NextMoves)
        elif self.Board[Row][Col] == Tile:
          GetNextMoves(self.Board, Row, Col, dRow, False, NextMoves)

    Result = []
    NextTurn = -1 * self.Turn
    for BoardArray in NextMoves:
      Result.append(BoardType(BoardArray, NextTurn))
    self.NumLegalMove = len(Result)
    # if CheckNumSuccessors:
    #   if len(Result) != self.GetNumSuccessors():
    #     ErrLog("Inconsistent Num Successors!\n")
    #   else:
    #     print("Good!\n")
    return Result


# A driver to test 
def FindMoveDrive(Board, InputFileName):
  Moves = Board.GetSuccessors()
  Out = open(InputFileName + ".out", "w")
  for Move in Moves:
    Str = Move.Dump()
    Out.write(Str)


# This is a debug version, with naive MinMax provided.
def AphaBetaMinMax(Board, MyTurn, Depth, Alpha, Beta):
  # if DebugMode:
  #   if DumpBoard:
  #     print(Board.Dump(Depth))
  #   else:
  #     print("Reaching Bot: Value = {}".format(Depth, Val))

  # Base case 1: Reaching the end.
  if Depth == 0:
    Val = Board.GetUtility()
    if DebugMode:
      # print(Board.Dump(Depth))
      print("Reaching Bot: Value = {}".format(Val))
    return Board, Val

  Successors = Board.GetSuccessors()

  # Base Case 2: No further moves, Game End.
  if len(Successors) == 0:
    RetVal = GameEndValG
    if Board.Turn == MyTurn:
      RetVal *= -1
    if DebugMode:
      print("Reaching NoMove: Value = {}".format(RetVal))
    return Board, RetVal

  Maximizer = True
  if Board.Turn != MyTurn:
    Maximizer = False
  BestSucc = None

  if Maximizer:
    Val = MinG
    for Successor in Successors:
      _, CurrVal = AphaBetaMinMax(Successor, MyTurn, Depth - 1, Alpha, Beta)
      if CurrVal == None:
        return None, None
      if CurrVal > Val:
        Val = CurrVal
        BestSucc = Successor
        if UsingAlphaBetaPruning:
          if Val >= Beta:
            break;
          if Val > Alpha:
            Alpha = Val
    if BestSucc == None:
      ErrLog("Error: maximizer found no result.\n")
    if DebugMode:
      print("Maximizer Depth {}: Value = {}".format(Depth, Val))
      if Val == 24:
        print(" Successor len: {}".format(len(Successors)))
        for Successor in Successors:
          print(Successor.Output())
    return BestSucc, Val
  else:
    Val = MaxG
    for Successor in Successors:
      _, CurrVal = AphaBetaMinMax(Successor, MyTurn, Depth - 1, Alpha, Beta)
      if CurrVal == None:
        return None, None
      if CurrVal < Val:
        Val = CurrVal
        BestSucc = Successor
        if UsingAlphaBetaPruning:
          if Val <= Alpha:
            break;
          if Val < Beta:
            Beta = Val
    if BestSucc == None:
      ErrLog("Error: minimizer found no result.\n")
    if DebugMode:
      print("Minimizer Depth {}: Value = {}".format(Depth, Val))
      if Val == 24:
        print(" Successor len: {}".format(len(Successors)))
        for Successor in Successors:
          print(Successor.Output())
          # Successor.Dump()
    return BestSucc, Val


def IterativeDeepening(OriginBoard, Turn):
  CurrDepth = 1
  BestBoard = None
  BestVal = None
  Depth = None
  while True:
    DebugPrint("Current Depth: {}".format(CurrDepth), DumpIterativeDeepening)
    Board, V = AlphaBetaSearch(OriginBoard, Turn, CurrDepth, MinG, MaxG)
    if Board == None:
      # Times Out or No valid solution.
      return BestBoard, BestVal, Depth
    DebugPrint("Best Value: {}".format(V), DumpIterativeDeepening)
    # Update global best board and best val.
    BestBoard = Board
    BestVal = V
    Depth = CurrDepth
    CurrDepth += 1
    if abs(BestVal) == GameEndValG:
      # The current move will lead to the end of the game.
      # No need to search further 
      return BestBoard, BestVal, Depth


def AlphaBetaSearch(Board, MyTurn, Depth, Alpha, Beta):
  # If Timeout, directly return.
  if TimeOut():
    return None, None

  # Base case 1: Reaching the end.
  if Depth == 0:
    return Board, Board.GetUtility()
  
  Successors = Board.GetSuccessors()

  # Base case 2: No further moves, game ends.
  if len(Successors) == 0:
    RetVal = GameEndValG
    if Board.Turn == MyTurn:
      RetVal *= -1
    return Board, RetVal

  # AlphaBeta starts.
  BestSucc = None
  
  # Break into Alpha and Beta for better performance.
  if Board.Turn == MyTurn:
    # maximizer
    Val = MinG
    for Successor in Successors:
      _, CurrVal = AlphaBetaSearch(Successor, MyTurn, Depth - 1, Alpha, Beta)
      if CurrVal == None:
        # Out of time.
        return None, None
      if CurrVal > Val:
        # We will update val first.
        Val = CurrVal
        BestSucc = Successor
        if Val >= Beta:
          # Cutoff
          break
        if Val > Alpha:
          Alpha = Val
    # Processing:
    if BestSucc == None:
      ErrLog("Error: Maximizer failed to find moves.\n")
    return BestSucc, Val
  else:
    # minimizer
    Val = MaxG
    for Successor in Successors:
      _, CurrVal = AlphaBetaSearch(Successor, MyTurn, Depth - 1, Alpha, Beta)
      if CurrVal == None:
        # Out of time.
        return None, None
      if CurrVal < Val:
        # We will update val first.
        Val = CurrVal
        BestSucc = Successor
        if Val <= Alpha:
          # Cutoff
          break
        if Val < Beta:
          Beta = Val
    # Processing:
    if BestSucc == None:
      ErrLog("Error: Minimizer failed to find moves.\n")
    return BestSucc, Val


# Start of the main entry.
if __name__ == "__main__":
  TimerInit()

  Argc = len(sys.argv)
  if Argc != 3:
    ErrLog("Error: Wrong # arguments: {}\n".format(Argc))
    exit()
  
  InputFileName = sys.argv[1]
  OutputFileName = sys.argv[2]

  BoardArray = ReadFile(InputFileName)
  Board = BoardType(BoardArray, RedTurnG)
  if Board.NumBlackTile == 0 and Board.NumBlackKing == 0:
    # End.
    WriteFile(OutputFileName, Board.Output())
    exit()
  if Board.NumRedTile == 0 and Board.NumRedKing == 0:
    # End.
    WriteFile(OutputFileName, Board.Output())
    exit()

  BoardMove = None
  V = None
  D = None

  if UsingIterativeDeepeningG:
    BestMove, V, D = IterativeDeepening(Board, RedTurnG)
    if DumpStats:
      print("\nValue returned: {}\nDepth: {}".format(V, D))
  else:
    BestMove, V = AlphaBetaSearch(Board, RedTurnG, SearchDepthLimitG, MinG, MaxG)

  if BestMove == None:
    print("No Valid Moves!")
    WriteFile(OutputFileName, Board.Output())
  else:
    WriteFile(OutputFileName, BestMove.Output())
  
  ReportTotalTime()