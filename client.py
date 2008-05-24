# -*- coding: utf-8 -*-
'''Giocare TressetteNetwork4 come client.'''
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

import pygame,sys,os,signal
import netframework,protocol,main,player,graphics,objects
from netframework import interfaces,connection

class TS4Client(interfaces.NetEvents):

	def __init__(self,app,name,server,size):

		self.app = app
		self.server = server
		self.name = name
		self.conn = connection.NetConnection(self,self.game_loop)
		self.player = None
		self.join_sent = False
		self.plist = ['','','','']
		self._ending = False		# flag interno -- indica se stiamo finendo la partita

		self.display = graphics.Display(size,' v'.join((main.NAME,main.VERSION)))
		self.current_menu = self.display

		# registra unix signal handler
		signal.signal(signal.SIGTERM,self.sig_term)

	def sig_term(self,signum,stack=None):
		main.output_command('client','terminate')
		# bad exit... :S
		os._exit(1)

	def run(self):
		self.conn.register_method(protocol.VERSION_INFO,self.version_info)
		self.conn.register_method(protocol.VERSION_CHECK,self.version_check)
		self.conn.register_method(protocol.JOIN,self.join_player)
		self.conn.register_method(protocol.PART,self.part_player)
		self.conn.register_method(protocol.READY_DISTRIB,self.ready_distrib)

		# connetti al server di gioco
		err = ''
		if self.conn.connect(self.server[0],self.server[1]):
			ret = self.conn.run()

			if ret == netframework.EXIT_CONN_CLOSED:
				err = 'connection-closed'
			elif ret == netframework.EXIT_CONN_REFUSED:
				err = 'connection-refused'
			elif ret == netframework.EXIT_CONN_ERROR:
				err = 'connect-error'
			elif ret == netframework.EXIT_CONN_TIMEOUT:
				err = 'connect-timeout'
			elif ret == netframework.EXIT_SYS_ERROR:
				err = 'sys-error'

		else:
			err = 'connect-error'

		if len(err) > 0:
			main.output_command('client',err)
			return main.EXIT_FAILURE

		return main.EXIT_SUCCESS

	def connected(self,conn):
		print "(CLIENT) Connected!",conn

	def closed(self,conn):
		print "(CLIENT) Connection closed!",conn

	def error(self,conn,detail):
		print "(CLIENT) Error:",conn,detail

	def version_info(self,conn,sw_name,sw_version):
		print "(CLIENT) Version:",sw_name,sw_version

		conn.send(interfaces.NetMethod(protocol.VERSION_INFO,main.NAME,main.VERSION))

	def version_check(self,conn,check):
		print "(CLIENT) Version check:",check

		if check:
			self.goto_menu('selector', self._position_pressed, "Scegli la posizione digitando il numero corrispondente, oppure cliccaci sopra.")

	def _get_position(self):
		if self.player == None:
			return -1

		return self.player.position

	def _update_plist(self,name,pos):
		self.plist[pos] = name

	def _position_pressed(self,num,mousepos=None):
		if mousepos != None:
			# calcolo con il mouse
			num = self.current_menu.get_mouse_over(mousepos)
			
		if num > 0 and num <= 4:
			self.conn.send(interfaces.NetMethod(protocol.JOIN,self.name,num-1))
			self.join_sent = True
			self.activate_keyboard(None)
			self.set_status("Un momento...")

	def join_player(self,conn,name,position,error=None):
		print "(CLIENT) Join",name,"position",position,"error",error

		if error == None:
			self._update_plist(name,position)

			if name == self.name:
				if self.join_sent and self.player == None:
					# abbiamo il posto! possiamo creare il Player in stato WAIT...
					self.player = player.ClientPlayer(self.name,position,self.conn)
					self.player.set_gui(self)

				else:
					# posto occupato
					self.current_menu.set_status(u"Il nome scelto è già in uso da un altro giocatore.")

			self._update_selector(position, name, True)

		else:
			print "(CLIENT) Join error",error
			if self.player == None:

				if error == protocol.ERR_NAME_BUSY:
					self.current_menu.set_status(u"Il nome scelto è già in uso da un altro giocatore.")
				elif error == protocol.ERR_POS_BUSY:
					self.current_menu.set_status(u"La posizione scelta è già in uso da un altro giocatore.")

				# riattiva la tastiera
				self.activate_keyboard(self._position_pressed)

	def part_player(self,conn,name):
		print "(CLIENT) Player",name,"left."

		# indice del nome
		index = self.plist.index(name)

		# cancella dalla plist
		self._update_plist('',index)

		if isinstance(self.current_menu,graphics.SelectorMenu):

			# aggiorna il selettore
			self._update_selector(index, '', False)

		elif isinstance(self.current_menu,graphics.GameTable):

			# in gioco, annulla partita
			if not self._ending:
				self.goto_menu("exit")

	def _update_selector(self, position, name, busy):
		# se siamo nel selector aggiorniamolo
		if isinstance(self.current_menu,graphics.SelectorMenu):

			mine = False
			if name == self.name:
				mine = True

			self.current_menu.update_button(position, name, busy, mine)

			if self.join_sent:
				self.current_menu.set_status("Attendo gli altri giocatori...")

	def get_position_from_name(self, name):
		'''Restituisce la posizione di un giocatore dato il nome.'''

		return self.plist.index(name)

	def get_name_from_position(self, position):
		'''Restituisce il nome di un giocatore data la posizione.'''

		return self.plist[position]

	def ready_distrib(self, conn, error=None):
		print "(CLIENT) Ready for cards distribution. Error:",error

		if error == None:
			self.activate_keyboard(self._spacebar_pressed)

			status = "Premi la barra spaziatrice per "
			if self._ending:
					status = status + "vedere i risultati."
					self.player._unregister_methods()
					self.conn.unregister_method(protocol.VERSION_INFO)
					self.conn.unregister_method(protocol.VERSION_CHECK)
					self.conn.unregister_method(protocol.JOIN)
					self.conn.unregister_method(protocol.PART)
					self.conn.unregister_method(protocol.READY_DISTRIB)

			else:
					status = status + "iniziare!"

			self.current_menu.set_status(status)

	# funzione hackata (vedi mousepos) per ricominciare la partita
	def _spacebar_pressed(self, key, mousepos = None):
		if key == 'space':
			self.activate_keyboard(None)

			if self._ending:
				self.goto_menu('statistics',None,self.player.stats)

			else:
				self.current_menu.set_status("Attendo che gli altri giocatori comincino...")
				self.conn.send(interfaces.NetMethod(protocol.CARDS_DISTRIB))

	def game_loop(self):
		'''Questa funzione viene chiamata tutte le volte dal loop degli eventi.

		Gestisce il cambio di menu.
		'''

		goto = self.current_menu.menu()

		if goto != None:

			if goto[0] == 'exit':
				self.conn.close()

			elif goto[0] == 'selector':
				self.current_menu = graphics.SelectorMenu(*goto[1])

			elif goto[0] == 'game-table':
				self.current_menu = graphics.GameTable(*goto[1])

			elif goto[0] == 'statistics':
				self.current_menu = graphics.StatisticsMenu(*goto[1])

	def activate_keyboard(self, callback):
		'''Attiva la ricezione di eventi da tastiera.

		Passare None come argomento per disattivare gli eventi da tastiera.
		'''

		self.current_menu.set_callback(callback)

	''' Funzioni chiamate da ClientPlayer '''

	def goto_menu(self,menu,*args):
		'''Passa al menu <menu>.

		Gli argomenti saranno preceduti dagli argomenti predefiniti:
		 - screen
		'''

		self.current_menu.goto_menu(menu,self.display.screen,*args)

	def reveal_card(self,position,card_num):
		'''Rivela una carta nella posizione data.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.reveal_card(position,card_num)

	def throw_card(self,position,card_num):
		'''Mette una carta al centro del tavolo.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.throw_card(position,card_num)

	def back_all_cards(self,position):
		'''Torna le carte in tavola verso il giocatore in position.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.add_timeout(2000,self.current_menu.back_all_cards,position)

	def set_status(self,status):
		'''Imposta lo stato del menu corrente.'''

		self.current_menu.set_status(status)

	def set_player_subtitle(self,position,text):
		'''Imposta un testo sotto il nome.'''

		if isinstance(self.current_menu,graphics.GameTable):
			return self.current_menu.set_subtitle(position,text)

	def get_card_from_mousepos(self,mousepos):
		'''Restituisce il valore della carta data la posizione del mouse.

		Questo metodo funziona solo per le nostre carte ovviamente.
		'''

		if isinstance(self.current_menu,graphics.GameTable):
			return self.current_menu.get_mouse_over(mousepos)

		return 0

	def highlight_position(self,position):
		'''Disegna una linea rossa vicino alle carte della posizione data.

		Passare -1 per rimuovere tutte le linee.

		Rimuove ogni highlight precedente.
		'''

		if isinstance(self.current_menu,graphics.GameTable):

			for i in (0,1,2,3):
				self.current_menu.highlight(i,(i == position))

	def highlight_name(self,position,disable=False):
		'''Evidenzia il nome in position.

		Se disable e' True, disattiva l'evidenziazione.
		'''

		if isinstance(self.current_menu,graphics.GameTable):

			for i in range(0,4):
				if i == position:
					self.current_menu.highlight_name(i,not disable)

				else:
					self.current_menu.highlight_name(i,False)

	def update_score_board(self,team_points=None):
		'''Aggiorna la tabella punteggi.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.show_score(team_points)

	def toggle_last(self,cards,last=-1):
		'''Mostra/nasconde la visualizzazione delle ultime 4 carte.'''

		if isinstance(self.current_menu,graphics.GameTable):

			cd = cards
			if self.current_menu.last in self.current_menu.updater:
				cd = None

			self.current_menu.show_last(cd,last)

	def end_game(self):
		'''Segna la fine della partita.'''

		self._ending = True
		self.ready_distrib(None,None)

	def get_side_from_position(self, position):
		'''Restituisce il lato data la posizione.'''

		if isinstance(self.current_menu,graphics.GameTable):
			return self.current_menu.get_side_from_position(position)

		return -1

	def update_miniscore(self,points):
		'''Aggiorna il miniscore.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.update_miniscore((points[0][0],points[1][0]))

	def set_chat(self,text):
		'''Imposta il messaggio della chat.'''

		if isinstance(self.current_menu,graphics.GameTable):
			self.current_menu.set_chat(text)
