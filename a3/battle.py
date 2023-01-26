import sys
import os
from copy import copy, deepcopy
import time

sys.setrecursionlimit(80000)

# Debugging Variables
DumpIc = False
DumpInitState = False
DumpSolution = False

def DebugPrint(Str, Control):
  if Control:
    print(Str)


def WriteFile(OutputFileName, StrBoard):
  F = open(OutputFileName, "w")
  F.write(StrBoard)


# Global Variables
"""
For IC:
   0: no constrain
   1: water
   2: submarine
   3: left
   4: right
   5: top
   6: bot
   7: mid
"""
Ic = []   # Initial constrians
RowC = [] # Row constrains
ColC = [] # Col constrains
ng = 0    # n, the dimension of the initial board
Ng = 0     # N = n + 2, which is the size of the padding board
ShipList = []
NumC = -1
IcMap = [' ', 'W', 'S', 'L', 'R', 'T', 'B', 'M']
IcDic = {
  '0': 0,
  'W': 1, 
  'S': 2, 
  'L': 3, 
  'R': 4, 
  'T': 5, 
  'B': 6, 
  'M': 7
}
Unused = IcDic['0']
Water = IcDic['W']
Submarine = IcDic['S']
Top = IcDic['T']
Bot = IcDic['B']
Left = IcDic['L']
Right = IcDic['R']
Mid = IcDic['M']


# Print Ic Board
def PrintState(State):
  print("\nState:")
  for i in range(Ng):
    Buffer = ""
    for j in range(Ng):
      Buffer += IcMap[State[i][j]]
    print(Buffer)


# Read the input into the global variables
def LoadInput(InputFileName):
  InputFile = open(InputFileName, "r")
  global Ic
  global ng
  global Ng
  global RowC
  global ColC
  global ShipList
  global NumC
  
  StrRowC = ""
  StrColC = ""
  StrShipList = ""
  StrBoard = []

  LineNum = 0
  for Line in InputFile:
    if LineNum == 0:
      StrRowC = Line
      ng = len(StrRowC) - 1
    elif LineNum == 1:
      StrColC = Line
      # assert ng == len(StrColC)
    elif LineNum == 2:
      StrShipList = Line
    else:
      # assert len(Line) == ng
      StrBoard.append(Line)
    LineNum += 1
  # assert ng == len(StrBoard)
  
  Ng = ng + 2
  Ic = [[0 for i in range(Ng)] for j in range(Ng)]
  RowC = [0 for i in range(Ng)]
  ColC = [0 for i in range(Ng)]

  # Load row/col constrain
  for i in range(ng):
    Idx = i + 1
    RowC[Idx] = int(StrRowC[i])
    ColC[Idx] = int(StrColC[i])
  
  # Load ship list
  ShipList = [0 for i in range(5)] # 0, 1, 2, 3, 4
  for i in range(len(StrShipList) - 1):
    ShipList[i + 1] = int(StrShipList[i])
  
  # Load explicit constrains:
  for i in range(ng):
    for j in range(ng):
      Tile = StrBoard[i][j]
      if Tile == '0':
        continue
      Row = i + 1
      Col = j + 1
      Ic[Row][Col] = IcDic[Tile]
      if Tile == 'S':
        # submarine
        # To-do: fix a bug here. Should update RowC and ColC!
        RowC[Row] -= 1;
        ColC[Col] -= 1;
        ShipList[1] -= 1
        assert ShipList[1] >= 0
  
  # Load implicit constrains:
  # All row with 0 bit should be water
  # All col with 0 bit should be water
  for i in range(Ng):
    if RowC[i] == 0:
      for j in range(Ng):
        if Ic[i][j] == Unused:
          Ic[i][j] = Water
    if ColC[i] == 0:
      for j in range(Ng):
        if Ic[j][i] == Unused:
          Ic[j][i] = Water
  
  # Provided tile could indicate water
  # At this stage we assume that it is always valid
  NumC = 0
  for i in range(ng):
    for j in range(ng):
      Row = i + 1
      Col = j + 1
      Val = Ic[Row][Col]
      if Val == 0 or Val == 1:
        # Unused or water:
        continue
      Type = IcMap[Val]
      if Type == 'S':
        # We already handled this
        Ic[Row - 1][Col - 1] = Water # Top Left
        Ic[Row - 1][Col] = Water     # Top
        Ic[Row - 1][Col + 1] = Water # Top Right
        Ic[Row][Col - 1] = Water     # Left
        Ic[Row][Col + 1] = Water     # Right
        Ic[Row + 1][Col - 1] = Water # Bot Left
        Ic[Row + 1][Col] = Water     # Bot
        Ic[Row + 1][Col + 1] = Water # Bot Right
      else:
        NumC += 1
        if Type == 'L':
          Ic[Row - 1][Col - 1] = Water # Top Left
          Ic[Row - 1][Col] = Water     # Top
          Ic[Row - 1][Col + 1] = Water # Top Right
          Ic[Row][Col - 1] = Water     # Left
          Ic[Row + 1][Col - 1] = Water # Bot Left
          Ic[Row + 1][Col] = Water     # Bot
          Ic[Row + 1][Col + 1] = Water # Bot Right
          Ic[Row - 1][Col + 2] = Water # Top Right + 1
          Ic[Row + 1][Col + 2] = Water # Bot Right + 1
        elif Type == 'R':
          Ic[Row - 1][Col - 1] = Water # Top Left
          Ic[Row - 1][Col] = Water     # Top
          Ic[Row - 1][Col + 1] = Water # Top Right
          Ic[Row][Col + 1] = Water     # Right
          Ic[Row + 1][Col - 1] = Water # Bot Left
          Ic[Row + 1][Col] = Water     # Bot
          Ic[Row + 1][Col + 1] = Water # Bot Right
          Ic[Row - 1][Col - 2] = Water # Top Left - 2
          Ic[Row + 1][Col - 2] = Water # Bot Left - 2
        elif Type == 'T':
          Ic[Row - 1][Col - 1] = Water # Top Left
          Ic[Row - 1][Col] = Water     # Top
          Ic[Row - 1][Col + 1] = Water # Top Right
          Ic[Row][Col - 1] = Water     # Left
          Ic[Row][Col + 1] = Water     # Right
          Ic[Row + 1][Col - 1] = Water # Bot Left
          Ic[Row + 1][Col + 1] = Water # Bot Right
          Ic[Row + 2][Col - 1] = Water # Bot + 1 Left  
          Ic[Row + 2][Col + 1] = Water # Bot + 1 Right 
        elif Type == 'B':
          Ic[Row - 1][Col - 1] = Water # Top Left
          Ic[Row - 1][Col + 1] = Water # Top Right
          Ic[Row][Col - 1] = Water     # Left
          Ic[Row][Col + 1] = Water     # Right
          Ic[Row + 1][Col - 1] = Water # Bot Left
          Ic[Row + 1][Col] = Water     # Bot
          Ic[Row + 1][Col + 1] = Water # Bot Right
          Ic[Row - 2][Col - 1] = Water # Top - 1 Left
          Ic[Row - 2][Col + 1] = Water # Top - 1 Right
        elif Type == 'M':
          Ic[Row - 1][Col - 1] = Water # Top Left
          Ic[Row - 1][Col + 1] = Water # Top Right
          Ic[Row + 1][Col - 1] = Water # Bot Left
          Ic[Row + 1][Col + 1] = Water # Bot Right

  # Get initial state
  T = deepcopy(Ic)
  # Set to Unused
  for i in range(Ng):
    for j in range(Ng):
      if T[i][j] > Submarine:
        T[i][j] = Unused

  return StateType(T, RowC, ColC)


class StateType():
  def __init__(self, T, RowC_, ColC_):
    self.T = T
    self.RowCount = deepcopy(RowC_)
    self.ColCount = deepcopy(ColC_)
  def Dump(self):
    print("\nRowC:")
    print(self.RowCount)
    print("\nColC:")
    print(self.ColCount)
    PrintState(self.T)
  def GetResult(self):
    Buffer = ""
    for i in range(1, 1 + ng):
      for j in range(1, 1 + ng):
        Buffer += IcMap[self.T[i][j]]
      Buffer += "\n"
    return Buffer
    

def PrintIc():
  print("\n")
  print("n: {}\nN: {}".format(ng, Ng))
  print("NumC: {}".format(NumC))
  print("\nRowC:")
  print(RowC)
  print("\nColC:")
  print(ColC)
  print("\nShip List:")
  print(ShipList)
  PrintState(Ic)


# Place with k size, starting from [i,j], in horizon
def PlaceHorizon(CurrState, i, j, k):
  # Check if placeable
  if CurrState.RowCount[i] < k:
    return None
  # Check if in-bound
  LeftBound = j - 1
  RightBound = j + k
  if RightBound > ng + 1:
    return None
  
  NewState = deepcopy(CurrState)

  # Place the ship
  Count = 0
  for Col in range(j, RightBound):
    Count += 1
    # This cell must be empty
    if NewState.T[i][Col] != Unused:
      return None
    # This col should have at least one bit
    if NewState.ColCount[Col] == 0:
      return None
    NewState.ColCount[Col] -= 1
    Val = 0
    if Count == 1:
      Val = Left
    elif Count == k:
      Val = Right
    else:
      Val = Mid
    if Ic[i][Col] != Unused and Ic[i][Col] != Val:
      return None
    NewState.T[i][Col] = Val
  NewState.RowCount[i] -= k

  # Check Top Row
  TopRow = i - 1
  for Col in range(LeftBound, RightBound + 1):
    if NewState.T[TopRow][Col] == Water:
      continue
    if NewState.T[TopRow][Col] != Unused or Ic[TopRow][Col] != Unused:
      return None
    NewState.T[TopRow][Col] = Water
  # Check Bot Row
  BotRow = i + 1
  for Col in range(LeftBound, RightBound + 1):
    if NewState.T[BotRow][Col] == Water:
      continue
    if NewState.T[BotRow][Col] != Unused or Ic[BotRow][Col] != Unused:
      return None
    NewState.T[BotRow][Col] = Water
  # Check Left:
  if NewState.T[i][LeftBound] != Water:
    if NewState.T[i][LeftBound] != Unused or Ic[i][LeftBound] != Unused:
      return None
    NewState.T[i][LeftBound] = Water
  # Check Right:
  if NewState.T[i][RightBound] != Water:
    if NewState.T[i][RightBound] != Unused or Ic[i][RightBound] != Unused:
      return None
    NewState.T[i][RightBound] = Water
  
  return NewState


def PlaceVertical(CurrState, i, j, k):
  # Check if placeable
  if CurrState.ColCount[j] < k:
    return None
  # Check if in-bound
  TopBound = i - 1
  BotBound = i + k
  if BotBound > ng + 1:
    return None
  
  NewState = deepcopy(CurrState)

  # Place the ship
  Count = 0
  for Row in range(i, BotBound):
    Count += 1
    # This cell must be empty
    if NewState.T[Row][j] != Unused:
      return None
    # This row should at least have one bit
    if NewState.RowCount[Row] == 0:
      return None
    NewState.RowCount[Row] -= 1
    Val = 0
    if Count == 1:
      Val = Top
    elif Count == k:
      Val = Bot
    else:
      Val = Mid
    if Ic[Row][j] != Unused and Ic[Row][j] != Val:
      return None
    NewState.T[Row][j] = Val
  NewState.ColCount[j] -= k

  # Check Left Col
  LeftCol = j - 1
  for Row in range(TopBound, BotBound + 1):
    if NewState.T[Row][LeftCol] == Water:
      continue
    if NewState.T[Row][LeftCol] != Unused or Ic[Row][LeftCol] != Unused:
      return None
    NewState.T[Row][LeftCol] = Water
  # Check Right Col
  RightCol = j + 1
  for Row in range(TopBound, BotBound + 1):
    if NewState.T[Row][RightCol] == Water:
      continue
    if NewState.T[Row][RightCol] != Unused or Ic[Row][RightCol] != Unused:
      return None
    NewState.T[Row][RightCol] = Water
  # Check Top:
  if NewState.T[TopBound][j] != Water:
    if NewState.T[TopBound][j] != Unused or Ic[TopBound][j] != Unused:
      return None
    NewState.T[TopBound][j] = Water
  # Check Bot:
  if NewState.T[BotBound][j] != Water:
    if NewState.T[BotBound][j] != Unused or Ic[BotBound][j] != Unused:
      return None
    NewState.T[BotBound][j] = Water
  
  return NewState


def PlaceSubmarine(CurrState, i, j):
  # It should always in bound
  NewState = deepcopy(CurrState)

  if NewState.T[i][j] != Unused:
    # This should be redundant
    return None
  if NewState.RowCount[i] == 0:
    return None
  if NewState.ColCount[j] == 0:
    return None
  if Ic[i][j] != Unused:
    return None
  NewState.RowCount[i] -= 1
  NewState.ColCount[j] -= 1
  NewState.T[i][j] = Submarine
  
  # Check Top Row
  TopRow = i - 1
  for Col in range(j - 1, j + 2):
    if NewState.T[TopRow][Col] == Water:
      continue
    if NewState.T[TopRow][Col] != Unused or Ic[TopRow][Col] != Unused:
      return None
    NewState.T[TopRow][Col] = Water
  # Check Bot Row
  BotRow = i + 1
  for Col in range(j - 1, j + 2):
    if NewState.T[BotRow][Col] == Water:
      continue
    if NewState.T[BotRow][Col] != Unused or Ic[BotRow][Col] != Unused:
      return None
    NewState.T[BotRow][Col] = Water
  # Check Left
  if NewState.T[i][j - 1] != Water:
    if NewState.T[i][j - 1] != Unused or Ic[i][j - 1] != Unused:
      return None
    NewState.T[i][j - 1] = Water
  # Check Right
  if NewState.T[i][j + 1] != Water:
    if NewState.T[i][j + 1] != Unused or Ic[i][j + 1] != Unused:
      return None
    NewState.T[i][j + 1] = Water
  
  return NewState


def MoveNext(State, i, j):
  # Check early exit
  if i == ng:
    # The col is filled.
    if State.ColCount[j] != 0:
      return None
  if j == ng:
    # The row is filled.
    if State.RowCount[i] != 0:
      return None
  
  # Increment
  j += 1
  GameEnd = False
  if j == ng + 1:
    NextRow = 0;
    for i in range(0, len(State.RowCount)):
      if State.RowCount[i] == 0:
        continue
      if NextRow == 0 or State.RowCount[i] < State.RowCount[NextRow]:
        NextRow = i
    if NextRow != 0:
      i = NextRow
      j = 1
    else:
      GameEnd = True
    
  # Check terminate state
  if GameEnd:
    # Terminate
    Count = 0
    for idx in range(1, 5):
      if ShipList[idx] != 0:
        return None
    return State # We found the solution!
  
  return Search(State, i, j)


def Search(CurrState, i, j):
  if CurrState.T[i][j] != Unused:
    return MoveNext(CurrState, i, j)

  # T[i][j] will must be unused!

  CurrRowCount = CurrState.RowCount[i]
  CurrColCount = CurrState.ColCount[j]

  global ShipList

  # If we've running out of bits, it can only be Water
  if CurrRowCount == 0 or CurrColCount == 0:
    if Ic[i][j] > Water:
      # It is reserved
      return None
    CurrState.T[i][j] = Water
    return MoveNext(CurrState, i, j)

  # Trying to place 4, 3, and 2. They have directions.
  for offset in range(3):
    k = 4 - offset
    if ShipList[k] == 0:
      # Placed all.
      continue
    
    NextState = PlaceHorizon(CurrState, i, j, k)
    if NextState != None:
      ShipList[k] -= 1 # Place
      Result = MoveNext(NextState, i, j)
      if Result != None:
        return Result
      ShipList[k] += 1 # Restore

    NextState = PlaceVertical(CurrState, i, j, k)
    if NextState != None:
      ShipList[k] -= 1 # Place
      Result = MoveNext(NextState, i, j)
      if Result != None:
        return Result
      ShipList[k] += 1 # Restore

  # Try to place the submarine
  if ShipList[1] != 0:
    NextState = PlaceSubmarine(CurrState, i, j)
    if NextState != None:
      ShipList[1] -= 1 # Place
      Result = MoveNext(NextState, i, j)
      if Result != None:
        return Result
      ShipList[1] += 1 # Restore
  
  # We can only fill out with 0
  if Ic[i][j] > Water:
    # It is reserved
    return None
  CurrState.T[i][j] = Water
  return MoveNext(CurrState, i, j)
    

# Start of the main entry.
if __name__ == "__main__":
  Argc = len(sys.argv)
  assert Argc == 3, "#arguments not matching. 3 is required."

  InputFileName = sys.argv[1]
  OutputFileName = sys.argv[2]

  InitState = LoadInput(InputFileName)

  if DumpInitState:
    InitState.Dump()
  if DumpIc:
    PrintIc()

  # HorizonTest(InitState)
  # VerticalTest(InitState)
  # TestSubmarine(InitState)

  FinalState = Search(InitState, 0, ng)
  Result = FinalState.GetResult()
  WriteFile(OutputFileName, Result)
  if DumpSolution:
    print("\n---------------------Solution-----------------------")
    print(Result)


"""
Testing Driver
"""
def TestSubmarine(State):
  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 2, 2)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 9, 9)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 2, 9)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 9, 2)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 7, 4)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 5, 5)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  State.RowCount[5] = 0
  State.ColCount[5] = 0

  print("\n--------------------------------------------")
  NextState = PlaceSubmarine(State, 5, 5)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  State.Dump()


# Horizon test
def VerticalTest(State):
  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 1, 1, 2)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 2, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 2, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 2, 4)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  State.ColCount[1] -= 2

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 1, 4)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 1, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  State.RowCount[3] -= 5
  
  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 1, 2, 3)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 1, 2, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()
  
  State.ColCount[1] = 5
  State.RowCount[3] = 5

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 2, 8, 2)
  if NextState == None:
    print("Not valid") ## 
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 2, 8, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 4, 7, 2)
  if NextState == None:
    print("Not valid") ## 
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 4, 7, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 4, 10, 2)
  if NextState == None:
    print("Not valid") ## 
  else:
    NextState.Dump()

  Temp = NextState

  print("\n--------------------------------------------")
  NextState = PlaceVertical(Temp, 7, 10, 4)
  if NextState == None:
    print("Not valid") ## 
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(Temp, 7, 10, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 9, 10, 3)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceVertical(State, 9, 10, 2)
  if NextState == None:
    print("Not valid") ##
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  State.Dump()


# Horizon test
def HorizonTest(State):
  State.RowCount[10] -= 1
  State.ColCount[1] -= 1

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 2, 7, 4)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 4, 5, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 4, 5, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(NextState, 6, 6, 4)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 9, 1, 4)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 10, 8, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 8, 9, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 1, 1, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 1, 2, 2)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 1, 2, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 1, 2, 4)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()

  print("\n--------------------------------------------")
  NextState = PlaceHorizon(State, 2, 2, 3)
  if NextState == None:
    print("Not valid")
  else:
    NextState.Dump()
  
  print("\n--------------------------------------------")
  State.Dump()