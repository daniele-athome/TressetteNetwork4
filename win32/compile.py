#!/usr/bin/env python
# Compile all python files in .. and ../netframework

import compileall

compileall.compile_dir("..",force=1)
