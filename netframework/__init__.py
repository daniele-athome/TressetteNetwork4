# -*- coding: utf-8 -*-
'''Network framework module

A network framework for remote procedure calls.
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

# connection loop exit codes
EXIT_SUCCESS=0			# uscita normale dal loop
EXIT_CONN_CLOSED=1		# connessione chiusa (durante la connessione)
EXIT_CONN_REFUSED=2		# connessione rifiutata
EXIT_CONN_ERROR=3		# errore di connessione (anche host non risolto)
EXIT_SYS_ERROR=4		# errore di sistema/python exception
