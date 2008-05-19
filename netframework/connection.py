# -*- coding: utf-8 -*-
'''Network framework connection

This file contains functions for managing a network connection and its loop.
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

import miscnet
import loop
import socket
from threading import Thread

import os,errno
if os.name == 'nt':
	_IsConnected = (10022, 10056)
	_ConnectBusy = (10035, )
else:
	_IsConnected = (0, errno.EISCONN)
	_ConnectBusy = (errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK)

class NetConnection:
	'''A network connection object.

	A network connection has two types of callbacks inside:
	- callbacks: a class inheriting from events.NetEvents, which receive events concerned to the global state of the connection (open, close, errors).
	- methods: a dictionary containing a callback for each remote method, where keys are the method names.

	This class contains blocking functions.
	Once connected, it will create a new loop.NetLoop and block into it.
	'''
	def __init__(self,callbacks,loop_func=None,prev_socket=None):
		'''Creates a new NetConnection object.

		callbacks: an interface class inherited from events.NetEvents which will only receive the connected event
		loop_func: function to be called at the end of each loop iteration (after processing network events)
		prev_socket: an already-connected socket (useful for servers)
		'''

		self.socket = prev_socket
		if self.socket != None:
			self.connected = True
		else:
			self.connected = False

		self.methods = {}
		self.callbacks = callbacks
		self.user_data = None
		self.loop = loop.NetLoop(self)
		self.loop.register_loop(loop_func)

	def connect(self,host,port):
		'''Use this connection object as tcp client.

		host: hostname or IP address to connect
		port: port number to connect

		Returns the socket on success.
		'''

		if self.socket != None:
			# hihi :P
			self.socket.close()
			self.connected = False
			self.socket = None

		try:
			self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

			self.socket.setblocking(False)

			# code taken from asyncore.py
			err = self.socket.connect_ex((host,port))
			print "Connect_ex errno:",err,errno.EISCONN,errno.EINPROGRESS

			# azzo gia' connesso!
			if err in _IsConnected:
				self.connected = True
				self.callbacks.connected(self)

			# errori normali
			elif err not in _ConnectBusy:
				raise socket.error, (err, errno.errorcode[err])

			self.socket.setblocking(True)

			return self.socket

		except socket.error,detail:
			print "(NET) Error!",detail
			self.callbacks.error(self,detail)

		return None

	def run(self):
		# entra e non uscire mai piu'!
		return self.loop.run()

	def close(self):
		'''Manual channel shutdown.'''

		# close the socket
		#print "Closing..."
		if self.socket != None:
			self.loop.stop()
			self.socket.close()
			self.connected = False

	def register_method(self,name,cb):
		'''Register a remote method callback.'''

		self.methods[name] = cb

	def unregister_method(self,name):
		'''Unregister a remote method callback.'''

		try: del(self.methods[name])
		except: pass

	def register_timeout(self,seconds,cb,*args):
		'''Register a callback called at the end of every timeout.

		Timeout is an integer in seconds.

		Returns a timeout object.'''

		to = loop.NetTimeout(seconds,cb,self,*args)
		to.start()
		return to

	def unregister_timeout(self,timeout):
		'''Unregister the given timeout object.'''

		timeout.stop()

	def set_callbacks(self,new_cb):
		self.callbacks = new_cb

	def receive(self,timeout=0):
		'''Receives a pickable object.'''

		return miscnet.receive_pickable(self.socket,timeout)

	def send(self,data):
		'''Send a pickable object.'''

		miscnet.send_pickable(self.socket,data)

class NetServer:
	'''A basic TCP server listener.

	Once connected, it will create a new thread and call for callbacks.accepted()
	'''

	def __init__(self,callbacks):
		'''Creates a new TCP server listener.

		callbacks: an interface class inherited from events.NetEvents which will only receive the connected event
		'''

		self.callbacks = callbacks
		self.threads = []
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	def listen(self,port,addr=''):
		'''Start listening on port and (optional) bind address.

		This is blocking function.
		'''

		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((addr, port))
		self.socket.listen(5)

		while True:
			(SocketClient, address) = self.socket.accept()
			print "(NET) Incoming connection from",SocketClient.getpeername()

			# creates a new NetConnection with the socket
			conn = NetConnection(self.callbacks,None,SocketClient)
			conn.server = self
			self.__class__.ListenerAccept(conn,self.threads).start()

	def stop_all(self):
		'''Stops all threads.'''

		while len(self.threads) > 0:
			self.threads[0].connection.close()
			self.threads[0].stop()
			# list element will be removed by the connection itself

	def send_all(self,data,except_list=()):
		'''Send data thru all open connections.

		except_list: a list af NetConnection for exclude.
		'''

		for th in self.threads:
			if th.connection not in except_list: th.connection.send(data)

	class ListenerAccept(Thread):
		def __init__(self,conn,th_list):
			Thread.__init__(self)

			self.connection = conn

			# accepted callback
			conn.callbacks.accepted(conn)

			conn.loop.register_atexit(self.delete_thread,th_list,self)
			th_list.append(self)

		def run(self):
			# running looped forever...
			self.connection.run()

		def delete_thread(self,conn,th_list,elem):
			#print "Deleting thread..."
			th_list.remove(elem)

		def stop(self):
			self.connection.loop.stop()
			self.join()
