#!/usr/bin/env python
# Retrieve TressetteNetwork4 version.

import sys
sys.path.append("..")

import main

if len(sys.argv) > 1:
	f = open(sys.argv[1],"w+")
	f.write(main.VERSION)
	f.close()
else:
	print main.VERSION
