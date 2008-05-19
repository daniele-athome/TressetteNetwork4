# -*- coding: utf-8 -*-
'''Miscellaneous networking functions.

Basic networking functions, mainly for object serialization and transfer.
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

import cPickle
import socket,select

def _recv_timeout(the_socket,timeout=2,flags=0):
	data=''
	rd,wr,er = select.select([the_socket],[],[the_socket],timeout)

	if len(rd) > 0:
		data = the_socket.recv(8192,flags)
		if len(data) == 0:
			return None

	# errorino :D
	if len(er) > 0:
		return None
	return data

_End="sb."
def _recv_end(the_socket,the_timeout=-1):
	total_data=[];data=''
	while True:
		if the_timeout < 0:
			data=the_socket.recv(8192,socket.MSG_PEEK)
			#print "Data:",data
			if len(data) == 0:
				# connessione chiusa... porco zio!
				raise socket.error,"connessione chiusa."
		else:
			#print "timing out receiving..."
			data=_recv_timeout(the_socket,the_timeout,socket.MSG_PEEK)
			if data == None:
				# connessione chiusa... porco zio (e 2)!
				raise socket.error,"connessione chiusa."
			elif len(data) == 0:
				break
		if _End in data:
			total_data.append(data[:(data.find(_End)+len(_End))])
			#print "START",str(data[:(data.find(End)+len(End))]),"END"
			the_socket.recv(len(data[:(data.find(_End)+len(_End))]))
			break
		else:
			the_socket.recv(len(data))
		total_data.append(data)
		"""
		if len(total_data)>1:
			#check if end_of_data was split
			last_pair=total_data[-2]+total_data[-1]
			if End in last_pair:
				total_data[-2]=last_pair[:last_pair.find(End)]
				total_data.pop()
				break
		"""
	return ''.join(total_data)

def receive_pickable(sock,timeout=0):
	'''Receives a pickable object and returns it unpickled.

	If timeout is 0, waits forever until an object is received.
	'''
	s = _recv_end(sock,timeout)
	#print s
	#if s != '':
	try:
		return cPickle.loads(s)
	except:
		return None

# pickla un oggetto e lo invia
def send_pickable(sock,obj):
	'''Serialize an object and send it.'''
	totalsent = 0
	msg = cPickle.dumps(obj)
	while totalsent < len(msg):
		sent = sock.send(msg[totalsent:])
		if sent == 0:
			# connessione chiusa... porco zio!
			raise socket.error, "connessione chiusa."
		totalsent = totalsent + sent
	return totalsent
