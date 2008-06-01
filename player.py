# -*- coding: utf-8 -*-
'''Classe per gestire un singolo giocatore.'''
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

import netframework
from netframework import interfaces
import protocol,deck

# controllo dell'interfaccia
STATE_WAIT=0			# in attesa degli altri giocatori
STATE_WAITCARDS=1		# tutti i giocatori connessi - in attesa delle carte
# controllo del Player
STATE_GAMESTART=2		# inizio partita - calcolo accusi
STATE_TURNWAIT=3		# in gioco -- in attesa del proprio turno
STATE_TURN=4			# in gioco -- in turno

class Player:
	'''Classe generica per un singolo giocatore.

	Metodi comuni sia per il server che per il client.
	'''

	def __init__(self,name,position,conn,state=STATE_WAIT):
		self.name = name
		self.position = position
		self.conn = conn
		self.state = state
		self.mycards = []

		self._register_methods()

	def _register_methods(self):
		pass

	def _unregister_methods(self):
		pass

	def set_state(self,state):
		'''Imposta lo stato.

		Gestisce solo i seguenti stati:
		- STATE_WAIT
		- STATE_WAITCARDS
		'''

		if state == STATE_WAIT:
			# resetta tutto!
			self.mycards = None

		elif state == STATE_WAITCARDS:
			# in attesa di carte...
			self.mycards = []

		self.state = state

	def set_cards(self,cards):
		self.mycards = list(cards)

	def get_cards(self):
		return tuple(self.mycards)

class ServerPlayer(Player):
	def __init__(self,name,position,conn,state=STATE_WAIT):
		Player.__init__(self,name,position,conn,state)

		self.chat_pending = False	# indica se abbiamo ricevuto una richiesta di chat da un giocatore

	def set_server(self,server):
		'''Imposta l'interfaccia server con cui comunicare.'''
		self.server = server

	def _register_methods(self):
		self.conn.register_method(protocol.THROW_CARD,self._card_thrown)
		self.conn.register_method(protocol.CHAT,self._chat)
		self.conn.register_method(protocol.REQ_CHAT,self._req_chat)

	def _card_thrown(self,conn,card_num):
		'''Callback carta gettata a terra da un giocatore.'''

		# controlla che la carta sia effettivamente nelle mani del giocatore e che sia il nostro turno
		if card_num in self.mycards and self.state == STATE_TURN:

			if self.server.verify_card(self.mycards,card_num):

				# rimuovi la carta dalle mani
				self.mycards.remove(card_num)

				# diffondi a tutti la carta
				self.server.conn.send_all(interfaces.NetMethod(protocol.THROW_CARD,self.position,card_num))

				# passa il turno al successivo
				self.server.turn_next(card_num)

				return

		conn.send(interfaces.NetMethod(protocol.THROW_CARD,self.position,card_num,protocol.ERR_REFUSED))

	def _req_chat(self,conn):
		'''Callback richiesta di chat.'''
		print "(SERVER PLAYER) Chat request!",conn.user_data['player'].position,self.server.current_order

		if conn.user_data['player'].position != self.server.current_order[0]:

			np = self.server.current_order[0]
			self.server.players[np].conn.send(interfaces.NetMethod(protocol.REQ_CHAT,self.position))
			self.server.players[np].chat_pending = True

	def _chat(self,conn,message):
		'''Callback messaggio di chat broadcast.'''

		# spedisci a tutti con prefisso
		print "Chat:",self.state,self.chat_pending,self.server.table.count(0)
		print "Data:",self.name,message
		if self.state == STATE_TURN or self.server.table.count(0) >= 3 or self.chat_pending:
			self.chat_pending = False
			self.conn.server.send_all(interfaces.NetMethod(protocol.CHAT,self.name,message))

		else:
			conn.send(interfaces.NetMethod(protocol.CHAT,self.name,message,protocol.ERR_REFUSED))

	def set_state(self,state):
		# richiama il super prima di tutto
		Player.set_state(self,state)

		# gestisce gli stati non gestiti da Player
		if state == STATE_GAMESTART:

			# controlla accusi
			self.accusations = self._check_accusations()

			# passa subito in attesa del turno, tanto il GAMESTART serve solo a noi per gestire gli annunci iniziali
			self.state = STATE_TURNWAIT

		elif state == STATE_TURN:
			self.server.conn.send_all(interfaces.NetMethod(protocol.TURN,self.position))

		# sincronizza con il client
		self.conn.send(interfaces.NetMethod(protocol.STATE,self.state))

	def cancel_chat_pending(self):
		self.chat_pending = False

	def set_cards(self,cards):
		Player.set_cards(self,cards)

		# sincronizza con il client
		self.conn.send(interfaces.NetMethod(protocol.CARDS_DISTRIB,self.mycards))

	def _check_accusations(self):

		ret = []

		napoli_seems = [0, 0, 0, 0]
		# un elemento rappresenta una carta da tressette, con il seme che manca (-1 se accuso da 4)
		accuse_seems = [ [False, False, False, False], [False, False, False, False], [False, False, False, False] ]

		for c in self.mycards:
			s,n = deck.get_card(c)

			#print "(SERVER PLAYER) Evaluating card, seem",s,"value",n
			if n >= 1 and n <= 3:
				#print "(SERVER PLAYER) Tressette card!"
				napoli_seems[s] = napoli_seems[s] + 1
				accuse_seems[n-1][s] = True

		# napoli: tre carte da tressette dello stesso seme
		for i in range(0,4):

			if napoli_seems[i] >= 3:
				ret.append(('napoli',i))

		#accuso: tre o quattro carte dello stesso valore nominale
		for i in range(0,3):

			tcount = 0

			# conto quanti True ci sono
			for j in range(0,4):
				if accuse_seems[i][j]:
					tcount = tcount + 1

			if tcount == 3:
				ret.append(('accuse',i+1,accuse_seems[i].index(False)))

			elif tcount == 4:
				ret.append(('accuse',i+1,-1))

		return ret

class ClientPlayer(Player):

	def __init__(self,name,position,conn,state=STATE_WAIT,manualchat=False):
		Player.__init__(self,name,position,conn,state)

		self.current_position = -1	# giocatore di turno
		self.hand_position = -1		# giocatore di mano
		self.last_hand_position = -1	# giocatore di mano giro precedente
		self.points = []			# punteggio mani
		self.stats = None			# statistiche mani
		self.last_team = -1			# squadra che ha preso per ultima
		self.last_cards = None		# replay ultimo giro
		self.current_last = [0, 0, 0, 0]
		self.manualchat = manualchat

	def set_gui(self,gui):
		'''Imposta l'interfaccia grafica con cui comunicare.'''
		self.gui = gui

	def _register_methods(self):
		Player._register_methods(self)

		self.conn.register_method(protocol.CARDS_DISTRIB,self._getting_cards)
		self.conn.register_method(protocol.STATE,self._remote_state)
		self.conn.register_method(protocol.ACCUSE_COUNT,self._has_accused)
		self.conn.register_method(protocol.ACCUSATIONS,self._accusations)
		self.conn.register_method(protocol.THROW_CARD,self._card_thrown)
		self.conn.register_method(protocol.TURN,self._turning)
		self.conn.register_method(protocol.TAKES,self._takes)
		self.conn.register_method(protocol.POINTS,self._update_points)
		self.conn.register_method(protocol.END_HAND,self._end_hand)
		self.conn.register_method(protocol.GAME_POINTS,self._game_points)
		self.conn.register_method(protocol.END_GAME,self._end_game)
		self.conn.register_method(protocol.CHAT,self._chat)
		self.conn.register_method(protocol.REQ_CHAT,self._req_chat)

	def _unregister_methods(self):
		self.conn.unregister_method(protocol.CARDS_DISTRIB)
		self.conn.unregister_method(protocol.STATE)
		self.conn.unregister_method(protocol.ACCUSE_COUNT)
		self.conn.unregister_method(protocol.ACCUSATIONS)
		self.conn.unregister_method(protocol.THROW_CARD)
		self.conn.unregister_method(protocol.TURN)
		self.conn.unregister_method(protocol.TAKES)
		self.conn.unregister_method(protocol.POINTS)
		self.conn.unregister_method(protocol.END_HAND)
		self.conn.unregister_method(protocol.GAME_POINTS)
		self.conn.unregister_method(protocol.END_GAME)
		self.conn.unregister_method(protocol.CHAT)
		self.conn.unregister_method(protocol.REQ_CHAT)

	def _req_chat(self,conn,position):
		'''Callback richiesta di chat da position.'''
		print "(CLIENT) Chat request by",position

		# abilita eventi chat entry
		self.gui.set_status(' '.join( (self.gui.get_name_from_position(position),"chiede che dice la carta.") ),True)
		self.gui.activate_chat(True,self._card_click)

	def _chat(self,conn,name,message,error=None):
		if error == None:
			self.gui.set_chat(name,message)

		else:
			print "(CLIENT) Chat refused!",error

	def _end_game(self,conn,winner_team):
		print "(CLIENT) Team",winner_team,"won this game!"
		self.gui.end_game()

	def _game_points(self,conn,points):
		print "(CLIENT) Game points:",points

		# termina mano nelle statistiche
		self.stats.hand_end(points,self.last_team)

		# aggiorna score board
		print "Client Points:",self.points
		old = [0, 0]
		for p in self.points:
			old[0] = old[0] + p[0]
			old[1] = old[1] + p[1]
		print "Olds:",old

		ptsdiff = (points[0]-old[0],points[1]-old[1])
		print "Points difference:",ptsdiff
		self.points.append(ptsdiff)
		self.gui.update_score_board(self.points)

	def _update_points(self,conn,points):
		print "(CLIENT) Score update:",points
		self.stats.hand_update(points)
		self.gui.update_miniscore(points)

	def _end_hand(self,conn):
		print "(CLIENT) End hand!"

		# rimuovi highlight
		self.gui.highlight_name(0,True)
		self.gui.highlight_position(-1)

		# rimuovi chat
		self.gui.set_chat("","")

		# rimuovi etichette accusi
		for i in range(0,4):
			self.gui.set_player_subtitle(i,"")

		# hack per ricominciare la mano
		self.gui.ready_distrib(None,None)

	def _takes(self,conn,position):
		print "(CLIENT) Position",position,"takes the head!"
		self.last_hand_position = self.hand_position
		self.hand_position = -1
		self.current_position = -1

		# aggiorna dati ultima mano
		self.last_team = position%2
		self.last_cards = self.current_last
		self.current_last = [0, 0, 0, 0]

		# dai carte a chi ha preso
		self.gui.back_all_cards(position)

		# disattiva chat entry
		self.gui.activate_chat(False)

	def _turning(self,conn,position):
		print "(CLIENT) It's time for position",position

		if self.hand_position < 0:
			self.hand_position = position
			self.gui.set_chat(self.gui.get_name_from_position(position),"")
			# highlight del giocatore di mano
			self.gui.highlight_name(position)

		self.gui.highlight_position(position)

		self.current_position = position

		# non siamo noi, setta stato
		if position != self.position:
			self.gui.set_status(' '.join((self.gui.get_name_from_position(position),"sta giocando..."))  )

		else:
			# siamo di mano, possiamo parlare
			if self.hand_position == self.position:
				self.gui.set_chat(self.name,"")

				# chat manuale
				if self.manualchat:
					self.gui.activate_chat(True)


	def _card_thrown(self,conn,position,card_num,error=None):
		print "(CLIENT PLAYER) Card thrown by",position,"card",card_num,"error",error

		if error != None:
			# errore... buahahah
			self.gui.set_status("Devi rispondere al seme.",True)

			# riprova
			self.gui.activate_keyboard(self._card_click)

		else:

			# non siamo noi, rivela la carta
			if position != self.position:
				self.gui.reveal_card(position,card_num)

			else:
				# parla se siamo di mano
				if self.hand_position == self.position:
					msg = ''
					if self.manualchat:
						msg = self.gui.get_chat()
						self.gui.activate_chat(False)
					else:
						msg = self.chat_message(card_num)

					conn.send(interfaces.NetMethod(protocol.CHAT,msg))

				# rimuovi la carta dalle mani
				self.mycards.remove(card_num)

			self.gui.throw_card(position,card_num)
			self.current_last[self.gui.get_side_from_position(position)] = card_num

	def chat_message(self,card_num):
		'''Costruisce un messaggio di chat automatico.'''

		# in caso di nessun caso :P
		ret = "non dice niente."

		# estrai tutte le carte di quel seme dalle carte in mano
		cd = deck.get_values(deck.seem_cards(self.mycards,card_num))
		print "(SERVER) Same seem list:",cd

		# conta le carte da tressette
		tscards = deck.get_tressette_cards(cd)
		print "(SERVER) Tressette list:",tscards

		# abbiamo altre carte di quel seme
		count = len(cd) - 1
		s,v = deck.get_card(card_num)

		# caso 1: carte finite
		if count <= 0:
			ret = "volo!"

		# caso 2: carte non finite, determina se dichiarare una carta da tressette
		else:

			try:
				# caso 2a: una sola carta da tressette, dichiarala se non la stiamo gettando
				if len(tscards) == 1:
					if v not in tscards:
						ret = "ho "
						if tscards[0] == 1:
							ret = ret + "l'"
						else:
							ret = ret + "il "

						ret = ret + deck.get_card_name(tscards[0]) + "."

					else:
						raise

				# caso 2b: due carte da tressette; diciamo quello ke vogliamo
				elif len(tscards) == 2:
					if tscards == [1,3] or tscards == [3,1]:
						ret = "voglio il "+deck.get_card_name(2)+"."
					elif tscards == [1,2] or tscards == [2,1]:
						ret = "voglio il "+deck.get_card_name(3)+"."
					elif tscards == [2,3] or tscards == [3,2]:
						ret = "voglio l'"+deck.get_card_name(1)+"."

				else:
					raise

			except:
				if count == 1:
					ret = "un'altra."

				else:
					ret = "altre "+str(count)+"."

		return ret

	def _accusations(self,conn,position,accuses):
		print "(CLIENT PLAYER) Position",position,"accuses:",accuses

		# costruisci stringa accusi
		acc_lines = "Accusa\n"

		for a in accuses:

			if a[0] == 'napoli':
				acc_lines = acc_lines + "napoli a " + deck.SEEMS_NAMES[a[1]]

			elif a[0] == 'accuse':

				# accuso da quattro... me cojoni!
				if a[2] < 0:
					acc_lines = acc_lines + "4 " + deck.get_card_name(a[1],True)

				# accuso da tre...
				else:
					acc_lines = acc_lines + "3 " + deck.get_card_name(a[1],True) + " mancante " + deck.SEEMS_NAMES[a[2]]

			acc_lines = acc_lines + "\n"

		self.gui.set_player_subtitle(position,acc_lines)

	def _has_accused(self,conn,position,count):
		print "(CLIENT PLAYER) Position",position,"accuses",count,"times."
		if count > 0:
			title = "Accuso!"

			if count == 2:
				title = "Doppio accuso!"

			if count == 3:
				title = "Triplo accuso!"

			if count > 3:
				title = "Accuso tutto!"

			self.gui.set_player_subtitle(position,title)

	def _remote_state(self,conn,state):
		print "(CLIENT PLAYER) State:",state
		Player.set_state(self,state)

		if state == STATE_TURNWAIT:

			# disabilita tastiera
			self.gui.activate_keyboard(None)

		elif state == STATE_TURN:

			# abilita tastiera
			if len(self.mycards) == 1:
				self._send_card(self.mycards[0])

			else:
				self.gui.activate_keyboard(self._card_click)
				self.gui.set_status("Scegli una carta da giocare.",True)

	def _getting_cards(self,conn,cards,error=None):
		print "(CLIENT PLAYER) My cards:",cards

		if error == None:
			Player.set_cards(self,deck.sort_cards(cards))

			if self.stats == None:
				self.stats = GameStats(self.gui.plist)
			self.stats.hand_begin()

			# vai al tavolo di gioco, mostrando la nostre carte sul tavolo
			self.gui.goto_menu('game-table',self._card_click,'',self.position,self.mycards,self.gui.plist,False)

			# nascondi lo score board (se presente)
			self.gui.update_score_board()

	def _card_click(self,button,position=None):

		if position != None:

			if button == -1:	# mousedown button 1

				self.gui.process_mousedown(position)

			elif button == 1:	# mouseup button 1

				if self.gui.process_mouseup(position):
					self.gui.remove_popups()

					card = self.gui.get_card_from_mousepos(position)
					print "(CLIENT PLAYER) Clicked card",card

					if card > 0 and self.current_position == self.position:
						self._send_card(card)
						self.gui.activate_keyboard(None)

		elif button == 'return':
			self.conn.send(interfaces.NetMethod(protocol.CHAT,self.gui.get_chat()))

			# se non siamo in turno disabilita la tastiera
			if self.state != STATE_TURN:
				self.gui.set_status(' '.join((self.gui.get_name_from_position(self.current_position),"sta giocando..."))  )
				self.gui.activate_chat(False)

		# multiline di aiuto
		elif button == 'f1':
			self.gui.toggle_help()

		# visualizza ultima
		elif button == 'f2':
			self.gui.toggle_last(self.last_cards,self.last_hand_position)

		# richiedi chat
		elif button == 'f3':
			self.conn.send(interfaces.NetMethod(protocol.REQ_CHAT))

		elif button == 'escape':
			self.gui.message_box(self._escape_response,"Terminare la partita?","Esci dal gioco",self.gui.get_buttons("MB_YESNO"))

	def _escape_response(self,msgbox,response):
		print "(CLIENT PLAYER) Response is",response

		if response == 0:		# yes!
			self.gui.goto_menu("exit")

	def _send_card(self,card_num):
			self.conn.send(interfaces.NetMethod(protocol.THROW_CARD,card_num))
			self.gui.set_status("Un momento...")

class GameStats:
	'''Contenitore delle statistiche di gioco.'''

	def __init__(self, plist):
		self.plist = plist

		# statistiche di mano; per ogni mano: ( team1: (punteggio,punti_accuso), team2: (punteggio,punti_accuso) )
		self.hands = []

		# punti totali delle squadre
		self.total_points = [0, 0]

	def hand_begin(self):
		'''Inizia le statistiche di una mano.'''

		self.hands.append( ([0,0], [0,0]) )

	def hand_update(self,points):
		'''Aggiorna il punteggio della mano corrente.

		points sovrascrive i punteggi precedenti.
		'''

		for i in range(0,2):
			self.hands[-1][i][0] = points[i][0]

	def hand_end(self,game_points,last_team):
		'''Termina la mano aggiornando i punti di accuso.

		game_points: lista punteggi intera da GAME_POINTS
		last_team: indice del team che ha preso l'ultima mano.
		'''

		''' game_points[team1, team2] contiene i punteggi globali delle mani.
		Per calcolare gli accusi fatti, dobbiamo detrarre da questi punti quelli dell'ultima mano e di questa mano,
		togliendo 1 punto alla squadra che ha preso l'ultima mano.
		'''

		for i in range(0,2):

			# aggiorna punteggio accusi

			previous = 0
			if len(self.hands) > 1:
				previous = self.hands[-2][i][0] + self.hands[-2][i][1]

			print "Gamepoints:",game_points[i],"previous:",previous,"Hands:",self.hands[-1][i][0]
			self.hands[-1][i][1] = game_points[i] - previous - self.hands[-1][i][0]

			# togli ultima mano
			print "Last team:",last_team,"index:",i
			if i == last_team:
				self.hands[-1][i][0] = self.hands[-1][i][0] + 1
				self.hands[-1][i][1] = self.hands[-1][i][1] - 1

			print "Accusation points for team",i,"is",self.hands[-1][i][1]

			# aggiorna punteggio totale
			self.total_points[i] = game_points[i]

if __name__ == '__main__':

	class GUI:
		def update_score_board(self,points):
			print "(GUI) Points:",points

	class Conn:
		def register_method(self,name,cb):
			pass

	c = Conn()
	p = ClientPlayer('daniele',0,c)
	p.set_gui(GUI())
	p.stats = GameStats(('daniele','ilaria','simone','valerio'))

	p.stats.hand_begin()
	p._update_points(c,( (2,1), (7,0) ))

	p._update_points(c,( (2,0), (8,1) ))
	p.last_team = 0

	p._game_points(c,(3,8))

	print "=============================================="

	p.stats.hand_begin()
	p._update_points(c,( (5,2), (3,1) ))

	p._update_points(c,( (5,0), (5,0) ))

	p.last_team = 1
	p._game_points(c,(8,14))
