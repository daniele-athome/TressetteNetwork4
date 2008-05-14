# -*- coding: utf-8 -*-
'''File di avvio per TressetteNetwork4.'''
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
#    TressetteNetwork4 - copyright (C) daniele_athome
#
#    TressetteNetwork4 is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    TressetteNetwork4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TressetteNetwork4; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

import sys,os,traceback,socket,time
from threading import Thread
import netframework

PACKAGE="TressetteNetwork4"
VERSION="0.0.1"
PORT=8154
SIZE=800,600

# codici di uscita
# < 0: segnali
EXIT_SUCCESS=netframework.EXIT_SUCCESS				# uscita normale
EXIT_CONN_CLOSED=netframework.EXIT_CONN_CLOSED		# connessione chiusa (durante la connessione)
EXIT_CONN_REFUSED=netframework.EXIT_CONN_REFUSED	# connessione rifiutata
EXIT_CONN_ERROR=netframework.EXIT_CONN_ERROR		# errore di connessione (anche host non risolto)
EXIT_SYS_ERROR=netframework.EXIT_SYS_ERROR			# errore di sistema/python exception
EXIT_ARGV=5											# errore parsing argomenti

class TS4App:
	def __init__(self):
		# argomenti predefiniti
		self.size = SIZE

		# se siamo su windows, prendi hostname come nome
		if os.name == "nt":
			self.name = socket.gethostname()

		# unix/linux, mac os x
		elif os.name == "posix":

			try:
				self.name = os.getlogin()

			except:
				self.name = os.getenv("USER")

		# prova altre cose
		try:
			if len(self.name) == 0: self.name = socket.gethostname()
			if len(self.name) == 0: self.name = "Giocatore"

		except:
			self.name = "Giocatore"

		self.standalone = False

	def run(self,argv):
		# parsa argv
		for arg in argv[1:]:
			if arg.startswith('size='):

				try:
					sz = arg.split('=')[1].split(',')
					if sz[0].isdigit() and sz[1].isdigit():
						if int(sz[0]) >= SIZE[0] and int(sz[1]) >= SIZE[1]:
							self.size = (int(sz[0]),int(sz[1]))

				except:
					self.size = SIZE

			elif arg.startswith('server=') or arg.startswith('bind='):

				if arg.startswith('server='):
					self.client = True
				else:
					self.client = False

				try:
					svr = arg.split('=')[1].split(':')
					if len(svr) == 2:
						port = int(svr[1])
						if port < 1 or port > 65536: raise ValueError("invalid port value")

						# ok, server accepted
						self.server = (svr[0],port)

						continue

					else:
						if svr[0].isdigit():
							self.server = ('', int(svr[0]))
						else:
							self.server = (svr[0],PORT)

				except:
					traceback.print_exc()
					print "Invalid server= argument, format is server=host:port"
					return EXIT_ARGV

			elif arg.startswith('name='):
				name = arg.split('=')
				if len(name[1]) > 0: self.name = name[1]

			elif arg == 'standalone':
				self.standalone = True

			elif arg == 'help':
				self.print_version()
				self.print_help(argv)
				return EXIT_SUCCESS

		self.print_version()

		if 'version' in argv[1:]:
			return EXIT_SUCCESS

		if not hasattr(self,'client'):
			self.server = ('',PORT)
			self.client = False

		# thread per flushare lo standard output (madonna...)
		FlushThread(sys.stdout,sys.stderr).start()

		# determina se dobbiamo essere client o server
		if not self.client:
			# in ogni caso fai partire il server
			import server
			self.ts4server = server.TS4Server(self,self.name,self.server)

			if self.standalone:
				# dobbiamo stare da soli
				try:
					return self.ts4server.start_blocking()
				except:
					traceback.print_exc()
					return EXIT_SYS_ERROR

			else:
				# insieme al client, quindi thread separato
				self.ts4server.start()

			self.server = ('127.0.0.1',self.server[1])

		r = EXIT_SUCCESS
		try:
			# il client si connettera' al giusto server...
			import client
			self.manager = client.TS4Client(self,self.name,self.server,self.size)
			r = self.manager.run()

		except:
			traceback.print_exc()
			r = EXIT_SYS_ERROR

		if not self.client:
			# stoppa tutte le connessioni se siamo server
			self.ts4server.conn.stop_all()

		return r

	def print_help(self,argv):
		print "Usage: "+PACKAGE.lower()+" [OPTIONS...]"

		print "\nServer options:"
		print "\tstandalone\t\tStart a standalone server"
		print "\tbind=host:port\t\tBind the server to the specified address"

		print "\nClient options:"
		print "\tname=name\t\tSet player name"
		print "\tsize=width,height\tCustom client window size (min "+str(SIZE[0])+","+str(SIZE[1])+")"
		print "\tserver=host:port\tConnect to the specified server"
		print "\nWithout any server= option, a server will be started along the client."

		print "\nOther options:"
		print "\tversion\t\t\tShow version information and exit"
		print "\thelp\t\t\tShow this help screen"

	def print_version(self):
		print PACKAGE+" version "+VERSION

		try:
			import pygame
			print "Pygame version",pygame.version.ver
		except:
			print "Pygame not installed."

class FlushThread(Thread):
	def __init__(self,*fd):
		Thread.__init__(self)
		self.fd = fd

	def run(self):
		while True:
			for desc in self.fd:
				desc.flush()
			time.sleep(1.0)

if __name__ == '__main__':
	app = TS4App()
	exit(app.run(sys.argv))