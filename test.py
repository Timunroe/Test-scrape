#!/usr/local/bin/python3

import sys

if len(sys.argv) == 2:
    print("The argument is: ")
    print(sys.argv[1])
elif len(sys.argv) == 1:
    print("No argument given")
else:
    print("Too many arguments")
