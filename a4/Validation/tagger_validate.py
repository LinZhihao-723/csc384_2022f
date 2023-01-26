"""This file contains the validation program for CSC384 Assignment 4.
The validation assumes that the following files are in the same directory as the tagger_validate.py file:
  - training1.txt  --> file of tagged words used to train the HMM tagger
  - test1.txt      --> file of untagged words to be tagged by the HMM
  - solution1.txt  --> file with correct tags for autotest words
This auto grader generates a file called results.txt that records the test results.
"""
import os

if __name__ == '__main__':

    for idx in range(7):
      # Invoke the shell command to train and test the HMM tagger
      print("Training on training{}.txt, running tests on test{}.txt. "
            "Output --> output{}.txt".format(idx, idx, idx))
      os.system("time python3 tagger.py -d training{}.txt -t test{}.txt -o output{}.txt".format(idx, idx, idx))

      # Compare the contents of the HMM tagger output with the reference solution.
      # Store the missed cases and overall stats in results.txt
      with open("output{}.txt".format(idx), "r") as output_file, \
           open("solution{}.txt".format(idx), "r") as solution_file, \
           open("results{}.txt".format(idx), "w") as results_file:
          # Each word is on a separate line in each file.
          output = output_file.readlines()
          solution = solution_file.readlines()
          total_matches = 0

          # generate the report
          for index in range(len(output)):
              if output[index] != solution[index]:
                  results_file.write(f"Line {index + 1}: "
                                     f"expected <{output[index].strip()}> "
                                     f"but got <{solution[index].strip()}>\n")
              else:
                  total_matches = total_matches + 1

          # Add stats at the end of the results file.
          results_file.write(f"Total words seen: {len(output)}.\n")
          results_file.write(f"Total matches: {total_matches}.\n")