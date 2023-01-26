import os
import sys
################################################################################
# Debug controls
IsDumpTokenList = False
IsDumpTags = False

def PrintErr(Str):
  print(Str)
  exit(-1)
################################################################################
# Global Variables
TagIdxMap = {}
WordIdxMap = {}
TagList = []
WordList = []
TerminatorDic = {}

TagNum = 0
WordNum = 0

I = []
M = []
T = []
################################################################################
def DumpTokenList(TokenList):
  i = 0
  Len = len(TokenList)
  while i < Len:
    print("{} : {}".format(WordList[TokenList[i]], TagList[TokenList[i + 1]]))
    i += 2
  print("Total number of tags: {}".format(TagNum))
  print("Total number of words: {}".format(WordNum))


def DumpTags():
  TagDict = {}
  for Tag in TagList:
    print(Tag)
    if not Tag in TagDict:
      TagDict[Tag] = 1
    else:
      PrintErr("Duplicated Tag: {}".format(Tag))


def StatSentence(SentenceBuffer):
  global I
  global M
  global T
  Len = len(SentenceBuffer)
  assert Len % 2 == 0
  # TokenLen = Len // 2
  if Len == 0:
    return
  I[SentenceBuffer[1]] += 1
  M[SentenceBuffer[1]][SentenceBuffer[0]] += 1
  for Idx in range(2, Len, 2):
    M[SentenceBuffer[Idx + 1]][SentenceBuffer[Idx]] += 1
    T[SentenceBuffer[Idx - 1]][SentenceBuffer[Idx + 1]] += 1


def Training(TrainingList):
  # TokenList should only contain numbers.
  # The even idx should store the word idx
  # The odd idx should store the tag idx
  TokenList = []

  global TagIdxMap
  global WordIdxMap
  global TagList
  global WordList
  global TagNum 
  global WordNum
  for FileName in TrainingList:
    F = open(FileName, "r")
    for Line in F:
      Tokens = Line.split(" : ")
      assert len(Tokens) == 2
      if Tokens[1].endswith("\n"):
        Tokens[1] = Tokens[1][:-1]
      Word = Tokens[0]
      Tag = Tokens[1]
      # Checking for the words:
      if not Word in WordIdxMap:
        WordIdxMap[Word] = WordNum
        WordList.append(Word)
        TokenList.append(WordNum)
        WordNum += 1
      else:
        TokenList.append(WordIdxMap[Word])

      # Checking for the tags:
      if not Tag in TagIdxMap:
        TagIdxMap[Tag] = TagNum
        TagList.append(Tag)
        TokenList.append(TagNum)
        TagNum += 1
      else:
        TokenList.append(TagIdxMap[Tag])

  assert len(TokenList) % 2 == 0

  if IsDumpTokenList:
    DumpTokenList(TokenList)
  if IsDumpTags:
    DumpTags()

  # Preprocess the matrix
  global I
  global M
  global T
  I = [0 for _ in range(TagNum)]
  T = [[0 for _ in range(TagNum)] for _ in range(TagNum)]
  M = [[0 for _ in range(WordNum)] for _ in range(TagNum)]
  # print("{}, {}".format(len(T), len(T[0])))
  # print("{}, {}".format(len(M), len(M[0])))

  global TerminatorDic
  TerminatorDic = {}
  if "." in WordIdxMap:
    TerminatorDic["."] = WordIdxMap["."]
  if "?" in WordIdxMap:
    TerminatorDic["?"] = WordIdxMap["?"]
  if "!" in WordIdxMap:
    TerminatorDic["!"] = WordIdxMap["!"]

  TokenIdx = 0
  TokenListLen = len(TokenList)
  SentenceBuffer = []
  while TokenIdx < TokenListLen:
    Word = TokenList[TokenIdx]
    Tag = TokenList[TokenIdx + 1]
    SentenceBuffer.append(Word)
    SentenceBuffer.append(Tag)
    if WordList[Word] in TerminatorDic:
      StatSentence(SentenceBuffer)
      SentenceBuffer.clear()
    TokenIdx += 2
  # Process the rest
  if len(SentenceBuffer) != 0:
    StatSentence(SentenceBuffer)

  # Normalize matrices
  Sentence = 0
  for i in range(TagNum):
    Sentence += I[i]
  assert Sentence != 0
  for i in range(TagNum):
    I[i] /= Sentence

  for i in range(TagNum):
    Sum = 0
    for j in range(TagNum):
      Sum += T[i][j]
    if Sum == 0:
      continue
    for j in range(TagNum):
      T[i][j] /= Sum
  
  for i in range(TagNum):
    Sum = 0
    for j in range(WordNum):
      Sum += M[i][j]
    if Sum == 0:
      ## Should probably return an error
      continue
    for j in range(WordNum):
      M[i][j] /= Sum

  # print("Training Ends.")


def ProcessTest(TestFile):
  # print("Test File Name: {}".format(TestFile))
  F = open(TestFile, "r")
  Words = []
  StringWord = []
  for Line in F:
    Word = Line
    if Line.endswith("\n"):
      Word = Word[:-1]
    StringWord.append(Word)
    if not Word in WordIdxMap:
      Words.append(-1)
    else:
      Words.append(WordIdxMap[Word])
  
  TagOutputs = []
  Sentence = []
  # print("Words len: {}".format(len(Words)))
  Num = 0
  for Word in Words:
    Sentence.append(Word)
    if WordList[Word] in TerminatorDic:
      TagOutputs = TagSentence(Sentence, TagOutputs)
      Sentence.clear()
    Num += 1
    #if Num % 1000 == 0:
    #  print("Words processed: {}".format(Num))
  if len(Sentence) != 0:
    TagOutputs = TagSentence(Sentence, TagOutputs)

  # print("Len <Words, Tags>: {}, {}".format(len(Words), len(TagOutputs)))
  assert len(Words) == len(TagOutputs)
  return StringWord, TagOutputs


def TagSentence(Sentence, TagOutputs):
  # print("Start Tagging")

  SentenceLen = len(Sentence)
  Probability = [[0 for _ in range(TagNum)] for _ in range(SentenceLen)]
  PreviousIdx = [[0 for _ in range(TagNum)] for _ in range(SentenceLen)]

  for i in range(TagNum):
    Probability[0][i] = I[i] * M[i][Sentence[0]]
    PreviousIdx[0][i] = None

  for WordIdx in range(1, SentenceLen):
    for TagIdxCurr in range(TagNum):
      BestTagIdxPre = -1
      BestProbability = -1
      for TagIdxPre in range(TagNum):
        WordTranProb = 1
        if Sentence[WordIdx] != -1:
          WordTranProb = M[TagIdxCurr][Sentence[WordIdx]]
        P = Probability[WordIdx - 1][TagIdxPre] * \
            T[TagIdxPre][TagIdxCurr] * \
            WordTranProb
        if P > BestProbability:
          BestProbability = P
          BestTagIdxPre = TagIdxPre
      assert BestTagIdxPre != -1
      Probability[WordIdx][TagIdxCurr] = BestProbability
      PreviousIdx[WordIdx][TagIdxCurr] = BestTagIdxPre
  
  GeneratedTags = []
  WordIdx = SentenceLen - 1
  BackTrackIdx = -1
  BestProbability = -1
  # Find the largest idx given all the words in the sentence.
  for TagIdx in range(TagNum):
    if Probability[WordIdx][TagIdx] > BestProbability:
      BestProbability = Probability[WordIdx][TagIdx]
      BackTrackIdx = TagIdx
  assert BackTrackIdx != -1
  
  while BackTrackIdx != None:
    GeneratedTags.append(TagList[BackTrackIdx])
    BackTrackIdx = PreviousIdx[WordIdx][BackTrackIdx]
    WordIdx -= 1

  GeneratedTags.reverse()
  return TagOutputs + GeneratedTags

  # print("End Tagging: {}".format(len(TagOutputs)))


def WriteOutput(OutputFile, WordList, TagOutputs):
  F = open(OutputFile, "w")
  for Idx in range(0, len(WordList)):
    F.write("{} : {}\n".format(WordList[Idx], TagOutputs[Idx]))


def tag(TrainingList, TestFile, OutputFile):
  # print("Tagging the file.")
  Training(TrainingList)
  Words, TagOutputs = ProcessTest(TestFile)
  WriteOutput(OutputFile, Words, TagOutputs)


if __name__ == '__main__':
  # Run the tagger function.
  print("Starting the tagging process.") 
  # Tagger expects the input call: 
  # "python3 tagger.py -d <training files> -t <test file> -o <output file>"
  parameters = sys.argv
  training_list = parameters[parameters.index("-d")+1:parameters.index("-t")]
  test_file = parameters[parameters.index("-t")+1]
  output_file = parameters[parameters.index("-o")+1]
  # print("Training files: " + str(training_list))
  # print("Test file: " + test_file)
  # print("Output file: " + output_file) 
  # Start the training and tagging operation.
  tag(training_list, test_file, output_file)