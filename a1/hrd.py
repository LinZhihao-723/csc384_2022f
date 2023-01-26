import sys
import os
from copy import copy, deepcopy
import heapq

sys.setrecursionlimit(50000)
UsingManhattanDistance = True

T = [0, 1, 3, 5, 7]
PieceRenamingMap = []

# Class to define a block, which will be used to store different blocks.
class BlockType:
  def __init__(self):
    self.Top = 100
    self.Left = 100
    self.Bot = -1
    self.Right = -1

  def Height(self):
    return self.Bot - self.Top + 1

  def Width(self):
    return self.Right - self.Left + 1

  def Print(self):
    print("TL: [{}, {}], BR: [{}, {}]".format( \
      self.Top, \
      self.Left, \
      self.Bot, \
      self.Right))

  def Update(self, Row, Col):
    if (Row < self.Top):
      self.Top = Row
    if (Row > self.Bot):
      self.Bot = Row
    if (Col < self.Left):
      self.Left = Col
    if (Col > self.Right):
      self.Right = Col

  def ValidUp(self, Board):
    Row = self.Top - 1
    if Row < 0:
      return False;
    for Col in range(self.Left, self.Right + 1):
      if Board[Row][Col] != 0:
        return False
    return True
  
  def ValidDown(self, Board):
    Row = self.Bot + 1
    if Row > 4:
      return False;
    for Col in range(self.Left, self.Right + 1):
      if Board[Row][Col] != 0:
        return False
    return True
  
  def ValidLeft(self, Board):
    Col = self.Left - 1
    if Col < 0:
      return False;
    for Row in range(self.Top, self.Bot + 1):
      if Board[Row][Col] != 0:
        return False
    return True

  def ValidRight(self, Board):
    Col = self.Right + 1
    if Col > 3:
      return False;
    for Row in range(self.Top, self.Bot + 1):
      if Board[Row][Col] != 0:
        return False
    return True

  def MoveUp(self, Board):
    Tile = Board[self.Top][self.Left]
    Row = self.Top - 1
    for Col in range(self.Left, self.Right + 1):
      Board[Row][Col] = Tile
      Board[self.Bot][Col] = 0
    self.Top -= 1
    self.Bot -= 1

  def MoveDown(self, Board):
    Tile = Board[self.Top][self.Left]
    Row = self.Bot + 1
    for Col in range(self.Left, self.Right + 1):
      Board[Row][Col] = Tile
      Board[self.Top][Col] = 0
    self.Top += 1
    self.Bot += 1

  def MoveLeft(self, Board):
    Tile = Board[self.Top][self.Left]
    Col = self.Left - 1
    for Row in range(self.Top, self.Bot + 1):
      Board[Row][Col] = Tile
      Board[Row][self.Right] = 0
    self.Left -= 1
    self.Right -= 1

  def MoveRight(self, Board):
    Tile = Board[self.Top][self.Left]
    Col = self.Right + 1
    for Row in range(self.Top, self.Bot + 1):
      Board[Row][Col] = Tile
      Board[Row][self.Left] = 0
    self.Left += 1
    self.Right += 1


# Class to store the board.
# To avoid shallow copy, always create the object using a given board.
class StateType:
  # Constructor
  def __init__(self, Board):
    Counter = 7
    self.CurrMove = 0
    self.BlockList = []
    self.BoardArray = deepcopy(Board)
    for i in range(11):
      self.BlockList.append(BlockType())
    for row in range(5):
      for col in range(4):
        Curr = Board[row][col]
        if Curr == 0:
          continue;
        elif Curr == 7:
          self.BlockList[Counter].Update(row, col)
          Counter += 1
        else:
          self.BlockList[Curr].Update(row, col)
    self.EncodedBoard = ""
    self.Encoding()
    self.Encoded = True
    global PieceRenamingMap
    if len(PieceRenamingMap) == 0:
      PieceRenamingMap.append("0") # For 0
      PieceRenamingMap.append("1") # For CaoCao
      for i in range(2, 7):
        if self.BlockList[i].Height() > self.BlockList[i].Width():
          PieceRenamingMap.append("3")
        else:
          PieceRenamingMap.append("2")
      PieceRenamingMap.append("4")

  def Encoding(self):
    self.EncodedBoard = ""
    for row in range(5):
      for col in range(4):
        self.EncodedBoard += str(self.BoardArray[row][col])
    self.Encoded = True
  
  def EncodeBoard(self):
    self.EncodedBoard = ""
    for row in range(5):
      for col in range(4):
        self.EncodedBoard += PieceRenamingMap[self.BoardArray[row][col]]
    return self.EncodedBoard

  def MakeCpy(self):
    NewState = deepcopy(self)
    NewState.CurrMove += 1
    return NewState

  # Print the board
  def Print(self):
    BlockIdx = 0
    for Blocks in self.BlockList:
      if BlockIdx == 0:
        BlockIdx += 1
        continue
      print("Block {}:".format(BlockIdx))
      BlockIdx += 1
      for Block in Blocks:
        Block.Print()

  # Print digital board
  def PrintDigit(self):
    for Row in self.BoardArray:
      print(Row)

  # Determine if we reach the end state.
  def ReachedGoalState(self):
    return self.BoardArray[3][1] == 1 and self.BoardArray[4][2] == 1

  # Get available moves
  def GetNextMoves(self):
    NextMoveList = []
    BlockIdx = 0
    for BlockIdx in range(10, 0, -1):
      if self.BlockList[BlockIdx].ValidUp(self.BoardArray):
        NewBoard = self.MakeCpy()
        NewBoard.BlockList[BlockIdx].MoveUp(NewBoard.BoardArray)
        NextMoveList.append(NewBoard)
      if self.BlockList[BlockIdx].ValidDown(self.BoardArray):
        NewBoard = self.MakeCpy()
        NewBoard.BlockList[BlockIdx].MoveDown(NewBoard.BoardArray)
        NextMoveList.append(NewBoard)
      if self.BlockList[BlockIdx].ValidLeft(self.BoardArray):
        NewBoard = self.MakeCpy()
        NewBoard.BlockList[BlockIdx].MoveLeft(NewBoard.BoardArray)
        NextMoveList.append(NewBoard)
      if self.BlockList[BlockIdx].ValidRight(self.BoardArray):
        NewBoard = self.MakeCpy()
        NewBoard.BlockList[BlockIdx].MoveRight(NewBoard.BoardArray)
        NextMoveList.append(NewBoard)
    return NextMoveList

  # Heuristic value function
  def GetCost(self):
    VirticalDist = abs(self.BlockList[1].Left - 1)
    HorizonDist = abs(self.BlockList[1].Top - 3)
    ManhattanDist = VirticalDist + HorizonDist 
    # This will be Manhattan distance
    if UsingManhattanDistance:
       return self.CurrMove + ManhattanDist
    Cost = self.CurrMove + T[ManhattanDist]
    return Cost

  def __lt__(self, other):
    return self.GetCost() < other.GetCost()


def ResultGenerator(FileName, Path, FoundSolution):
  F = open(FileName, "w")
  if not FoundSolution:
    F.write("No solution Found!\n")
    return
  F.write("Cost of the solution: {}\n".format(len(Path) - 1))
  for State in Path:
    Buffer = ""
    for Row in range(5):
      for Col in range(4):
        Buffer += PieceRenamingMap[State.BoardArray[Row][Col]]
      Buffer += "\n"
    Buffer += "\n"
    F.write(Buffer)


# A star driver
def DriverAStar(InitState, AstartFileName):
  AStarPath = []
  VisitedCache = {} 
  VisitedCache[InitState.EncodeBoard()] = None
  PQ = []
  heapq.heappush(PQ, InitState)
  EndState = None
  FoundSolution = False

  while len(PQ) != 0:
    CurrState = heapq.heappop(PQ)
    if CurrState.ReachedGoalState():
      EndState = CurrState
      FoundSolution = True
      break
    NextStates = CurrState.GetNextMoves()
    for NextState in NextStates:
      HashedBoard = NextState.EncodeBoard()
      if HashedBoard in VisitedCache:
        # visited
        continue
      else:
        VisitedCache[HashedBoard] = CurrState
        heapq.heappush(PQ, NextState)
  
  if EndState != None:
    CurrState = EndState
    while CurrState != None:
      AStarPath.append(CurrState)
      CurrState = VisitedCache[CurrState.EncodeBoard()]
  
  AStarPath.reverse()
  ResultGenerator(AstartFileName, AStarPath, FoundSolution)

    
# DFS
def DriverDFS(InitState, DFSFFileName):
  DFSPath = []
  VisitedCache = {} 
  VisitedCache[InitState.EncodeBoard()] = None
  WorkingStack = []
  WorkingStack.append(InitState)
  EndState = None
  FoundSolution = False

  while len(WorkingStack) != 0:
    CurrState = WorkingStack.pop()
    if CurrState.ReachedGoalState():
      EndState = CurrState
      FoundSolution = True
      break
    NextStates = CurrState.GetNextMoves()
    for NextState in NextStates:
      HashedBoard = NextState.EncodeBoard()
      if HashedBoard in VisitedCache:
        # visited
        continue
      else:
        VisitedCache[HashedBoard] = CurrState
        WorkingStack.append(NextState)

  if EndState != None:
    CurrState = EndState
    while CurrState != None:
      DFSPath.append(CurrState)
      CurrState = VisitedCache[CurrState.EncodeBoard()]
      
  DFSPath.reverse()
  ResultGenerator(DFSFFileName, DFSPath, FoundSolution)


# To read the input file and store it into an int array.
def ReadConfig(InputFileName, Board):
  InputFile = open(InputFileName, "r")
  Row = 0
  for Line in InputFile:
    # notice that the new line character is included.
    for Col in range(4):
      Board[Row][Col] = int(Line[Col])
    Row += 1

if __name__ == "__main__":
  Argc = len(sys.argv)
  if Argc != 4:
    print("Error: wrong command line arguments!")
    exit()
  
  InputFileName = sys.argv[1]
  DFSFFileName = sys.argv[2]
  AstartFileName = sys.argv[3]

  InitBoard = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ]
  
  ReadConfig(InputFileName, InitBoard)

  InitState = StateType(InitBoard)
  DriverAStar(InitState, AstartFileName)
  DriverDFS(InitState, DFSFFileName)
  