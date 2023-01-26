import copy
import random
import time
import queue
import sys
import os

# Validation script:
# Test case 0 to 5 are given by course instructors.
# 0 & 1: easy
# 2 & 3: hard
# 4 & 6: mid

if __name__ == '__main__':
  n = 19
  passed_num = 0
  for i in range(n):
    print("\n------------Case {}------------".format(i))
    print("Input file: {}.in, output file: {}.out".format(i, i))

    start = time.time()
    os.system("python3 battle.py {}.in {}.out".format(i, i))
    end = time.time()
    time_used = end - start
    print("Time in sec:", time_used)

    output_read = open("{}.out".format(i), "r")
    solution_read = open("{}ref.out".format(i), "r")

    output_lines = output_read.readlines()
    solution_lines = solution_read.readlines()
    passed = True

    for index in range(1, len(output_lines)):
      if output_lines[index].strip() != solution_lines[index].strip():
        print(f"Line {index + 1}: "
                              f"Expected <{output_lines[index].strip()}> "
                              f"Encountered <{solution_lines[index].strip()}>\n")
        passed = False
        break

    if passed:
      print("Battleship output matches solution file.")
      os.system("rm {}.out".format(i))
      passed_num += 1

  print("\n----------------------------------------------------------------")
  print("Case Passed: {}/{}".format(passed_num, n))

  
