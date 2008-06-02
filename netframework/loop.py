# -*- coding: utf-8 -*-
'''Network loop implementation

Here is what the real framework is: remote procedure call. Classes in this
file do the actual network receive and procedure call.
'''
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
#    StargateRPG - copyright (C) daniele_athome
#
#    StargateRPG is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    StargateRPG is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StargateRPG; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

import time,sys,socket,traceback
import miscnet,__init__
from threading import Thread

DEFAULT_TIMEOUT=30

class NetLoop:
	'''This thread is started by the NetConnection class.

	NetLoop does the actual network loop and carries out the procedure call.
	'''

	def __init__(self,netconnection):
		self.running = False
		self.connection = netconnection
		self.atexit = None
		self.loop_func = None
		self._return = None
		self.timeout = NetTimeout(DEFAULT_TIMEOUT,self._cb_timeout,self.connection)

	def _cb_timeout(self,conn):
		if not conn.connected:
			self._return = __init__.EXIT_CONN_TIMEOUT
			conn.close()

		return False

	def register_atexit(self,callback,*args):
		'''Register a method to be called at channel closure.

		Not very useful, used by NetServer.'''

		self.atexit = (callback,args)

	def register_loop(self,callback):
		'''Register a method to be called at the end of a loop.

		Useful if you want to insert additional tasks to the loop.

		Note: the connection will *not* be passed to this callback.
		'''

		self.loop_func = callback

	def run(self):
		self.running = True
		ret = __init__.EXIT_SUCCESS

		self._return = None
		self.timeout.start()

		while self.running:

			try:
				#print "(NET) Receiving..."
				data = self.connection.receive(0)
				#print "(NET) Got",data

				if data != None:
					# FIXME metodo inefficiente per verificare l'avvenuta connessione
					if not self.connection.connected:
						self.connection.connected = True
						self.connection.callbacks.connected(self.connection)

					self.connection.methods[data.name](self.connection,*data.args)

			except KeyError:
				print "(NET) No method registered for",data.name

			except TypeError:
				traceback.print_exc()
				print "(NET) Invalid method call",data.__class__.__name__

			except socket.error,detail:
				print "(NET) Channel closed!"
				try:
					self.connection.callbacks.closed(self.connection)
				except:
					pass

				if self.running:

					# FIXME metodo inefficiente per verificare se la connessione e' stata rifiutata
					if self.connection.connected:
						ret = __init__.EXIT_CONN_CLOSED
					else:
						ret = __init__.EXIT_CONN_REFUSED

				else:
					ret = __init__.EXIT_SUCCESS

				break

			except:
				traceback.print_exc()
				print "(NET) Error!",sys.exc_info()
				self.connection.callbacks.error(self.connection,sys.exc_info())
				break

			if self.loop_func:
				self.loop_func()
			else:
				time.sleep(0.05)

		#print "(NET) Checking termination callback..."
		if self.atexit: self.atexit[0](self.connection,*self.atexit[1])

		if self._return != None:
			ret = self._return

		return ret

	def stop(self):
		#print "(NET) Terminating loop..."
		self.running = False

class NetTimeout(Thread):
	'''Handles a function to be called at a given timeout.'''

	def __init__(self,seconds,callback,*args):
		'''Creates a new timeout callback.

		seconds: a timeout in seconds
		callback, args: a callback function (with arguments), that must return True if the timer should continue.
		'''
		Thread.__init__(self)

		self.seconds = seconds
		self.passed = 0
		self.cb = (callback,args)
		self.running = False

	def run(self):
		'''Use start() to start the timer.'''

		self.running = True
		self.passed = 0

		time.sleep(1.0)

		while self.running:
			self.passed = self.passed + 1

			if self.passed >= self.seconds:

				if self.cb[0](*self.cb[1]):
					self.passed = 0

				else:
					self.running = False

			time.sleep(1.0)

	def stop(self):
		'''Stops the timer.'''

		self.running = False
		self.join()
