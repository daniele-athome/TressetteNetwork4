# -*- coding: utf-8 -*-
'''Network events interfaces

This classes are implemented as callbacks.
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

class NetEvents:
	'''A class used for receiving events from connection.* classes.

	Method names are self-explainatory. 'accepted' is used only by server implementation.
	'''

	def connected(self,net):
		print "(NET) Connected!",net

	def closed(self,net):
		print "(NET) Connection closed!",net

	def error(self,net,detail):
		'''Handles an error.'''
		print "(NET) Error:",net,detail

	def accepted(self,net):
		'''Callback for an incoming connection.

		This is the perfect occasion for registering method callbacks.
		'''
		print "(NET) Accepted!",net

class NetMethod:
	'''A pickable class containing a method call.'''

	def __init__(self,name,*args):
		'''Creates a new method call.

		name: the method name
		args: an expanded list of arguments
		'''

		self.name = name
		self.args = args
