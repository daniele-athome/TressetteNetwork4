#!/usr/bin/env python
# Distutils script for TressetteNetwork4

from distutils.core import setup
import main

setup(	name		= main.PACKAGE,
		version		= main.VERSION,
		description	= main.NAME,
		author		= main.AUTHORS[0]['name'],
		author_email= main.AUTHORS[0]['email'],
		url			= 'http://gna.org/projects/tsnet4',
		packages	= ['','netframework'],
		scripts		= ['tressettenetwork4', 'ts4launcher'],
		license		= 'GNU GPL v2',
		requires	= ['wx'],
		package_data= { '': ['cards/piacentine*.jpg'] }
)
