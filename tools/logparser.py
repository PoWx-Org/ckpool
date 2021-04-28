import os

from parse import *

logPath = "../logs/ckpool.log"



if os.path.isfile(logPath):
    print(f"path {logPath} is a file, everyhting ok")
else:
    print(f"paht {logPath} is not a file!")
    exit(0)

def found_block(line):
    print("Block found, doing something usefull")
    block_number = parse("[{time:ti}] Solved and confirmed block {height:d} {}", line)
    print(block_number)



with open(logPath,'r') as infile:
    lines = infile.readlines()
    while True:
        lines = infile.readlines()
        if len(lines) > 0:
            for line in lines:
                print( line.rstrip())
                if 'Solved and confirmed block' in line:
                    found_block(line)