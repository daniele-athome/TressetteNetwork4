# -*- coding: utf-8 -*-
'''Giocare TressetteNetwork4 come server.'''
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

from threading import Thread
import sys,traceback,time
import netframework,protocol,main,player,deck
from netframework import interfaces,connection

PSTATE_CONNECTED=0		# connesso
PSTATE_VERCHECKED=1		# passato controllo versione
PSTATE_JOINED=2			# effettuato join
PSTATE_CARDS=3			# attesa carte
PSTATE_BEGIN=4			# passato controllo a ServerPlayer

CARDS_VALUE=[4,5,6,7,8,9,10,1,2,3]	# potere delle carte

ROUNDS=10				# numero di mani
MAX_POINTS=41			# soglia di fine partita

class TS4Server(Thread,interfaces.NetEvents):

	def __init__(self,app,name,server):
		Thread.__init__(self)

		self.app = app
		self.server = server
		self.name = name
		self.conn = connection.NetServer(self)

		# array di 4 ServerPlayer
		self.players = [None, None, None, None]

		# prepara e mischia il mazzo
		self._make_deck()

	def _make_deck(self):
		self.deck = deck.Deck()
		self.deck.shuffle()

	def start_blocking(self):
		return self.run()

	def run(self):
		# metti in ascolto
		self.conn.listen(self.server[1],self.server[0])
		return netframework.EXIT_SUCCESS

	def connected(self,conn):
		print "(SERVER) Connected!",conn

	def closed(self,conn):
		print "(SERVER) Connection closed!",conn

		try:
			self.players[conn.user_data['player'].position] = None

			# notifica logout
			self.conn.send_all(interfaces.NetMethod(protocol.PART,conn.user_data['player'].name))

			# se siamo arrivati qui vuol dire che il giocatore aveva fatto JOIN, quindi dobbiamo rimettere tutti in WAIT e rimischiare le carte
			for p in self.players: p.set_state(player.STATE_WAIT)
			self._make_deck()

		except:
			pass


	def error(self,conn,detail):
		print "(SERVER) Error:",conn,detail

	def accepted(self,conn):
		print "(SERVER) Incoming connection!",conn

		conn.register_method(protocol.VERSION_INFO,self.version_info)
		conn.register_method(protocol.JOIN,self.join)
		conn.register_method(protocol.CARDS_DISTRIB,self.cards_distrib)

		conn.user_data = {}
		conn.user_data['state'] = PSTATE_CONNECTED

		conn.send(interfaces.NetMethod(protocol.VERSION_INFO,main.NAME,main.VERSION))

	def version_info(self,conn,sw_name,sw_version):
		print "(SERVER) Version:",sw_name,sw_version

		# buggone!!! Qualcuno potrebbe usare lo stato verchecked per cambiare nick (richiede il join un'altra volta)
		if conn.user_data['state'] == PSTATE_CONNECTED:
			conn.user_data['state'] = PSTATE_VERCHECKED
			conn.send(interfaces.NetMethod(protocol.VERSION_CHECK,True))

			for p in self.players:
				if p != None:
					conn.send(interfaces.NetMethod(protocol.JOIN,p.name,p.position))

	def join(self,conn,name,position):
		print "(SERVER) Join game by",name,"using position",position

		if conn.user_data['state'] == PSTATE_VERCHECKED:
			try:
				# controlla la corretta posizione
				# in caso di out of bounds, l'eccezione evitera' il proseguimento del join
				if self.players[position] == None:

					if name not in self._build_external_plist():
						self.players[position] = player.ServerPlayer(name,position,conn)
						self.players[position].set_server(self)

						conn.user_data['state'] = PSTATE_JOINED
						conn.user_data['player'] = self.players[position]
						self.conn.send_all(interfaces.NetMethod(protocol.JOIN,name,position))

						# lista piena! Invia richiesta di pronti a tutti!
						if None not in self.players:
							self.init_game()
							self.conn.send_all(interfaces.NetMethod(protocol.READY_DISTRIB))

					else:
						conn.send(interfaces.NetMethod(protocol.JOIN,name,position,protocol.ERR_NAME_BUSY))

				else:
					conn.send(interfaces.NetMethod(protocol.JOIN,name,position,protocol.ERR_POS_BUSY))

			except:
				print "(SERVER) Invalid join request!"
				# dettagli sull'errore
				traceback.print_exc()

				# annulla il giocatore eventualmente creato
				self.players[position] = None
				conn.user_data['state'] = PSTATE_JOINED-1
				try:
					del conn.user_data['player']
				except KeyError:
					pass
				conn.send(interfaces.NetMethod(protocol.JOIN,name,position,protocol.ERR_ARG_INVALID))

	def cards_distrib(self,conn):
		'''Callback per richiedere le carte.

		Le carte saranno distribuite solo quando tutti avranno richiesto questo comando.
		'''

		try:
			if conn.user_data['state'] == PSTATE_JOINED:
				print "(SERVER) Player",conn.user_data['player'].name,"is ready for card distribution!"

				conn.user_data['state'] = PSTATE_CARDS
				conn.user_data['player'].set_state(player.STATE_WAITCARDS)

				# verifica se tutti sono pronti, spedisci le carte a tutti
				count = 0
				for p in self.players:
					if p.state == player.STATE_WAITCARDS:
						count = count + 1

				if count >= len(self.players):
					print "(SERVER) All players are ready, sending cards"
					for p in self.players:
						p.set_cards(self.deck.extract(10))
						p.set_state(player.STATE_GAMESTART)

					# verifica chi e' il primo
					self.start_game()

				return

		except:
			traceback.print_exc()

		conn.send(interfaces.NetMethod(protocol.CARDS_DISTRIB,None,protocol.ERR_REFUSED))

	def init_game(self):
		'''Procedure inizio partita.'''

		# punteggio delle squadre
		self.points = [0, 0]

	def start_game(self):
		'''Procedure inizio mano.'''

		self.turn_count = 0
		# primo elemento: punti interi; secondo elemento: terzi di punti
		self.hand_points = [[0,0], [0,0]]
		begin = None

		# determina il quattro a denara se necessario
		if self.points == [0, 0]:

			fourdenara = -1
			for p in self.players:

				for c in p.mycards:
					if c == 14:
						fourdenara = p.position
						break

				if fourdenara >= 0: break

			# imposta l'ex mazziere che non esiste
			self.ex_dealer = [0,1,2,3][fourdenara-1]

		print "(SERVER) Ex dealer is",self.ex_dealer
		self.ex_dealer = begin = [0,1,2,3][(self.ex_dealer + 1) - len(self.players)]

		# diffondi a tutti SOLO LA NOTIFICA di quanti accusi
		for p in self.players:
			if len(p.accusations) > 0:
				self.conn.send_all(interfaces.NetMethod(protocol.ACCUSE_COUNT,p.position,len(p.accusations)))

		self.turn(begin)

	def _rotate(self, seq, n=1):
		n = n % len(seq)
		return seq[n:] + seq[:n]

	def turn(self, position):
		'''Comincia il giro dal giocatore in position.'''

		# passa il turno al giocatore solo se puo' prenderlo
		if self.players[position].state == player.STATE_TURNWAIT:

			# carte sul tavolo
			self.table = [0, 0, 0, 0]
			self.current_order = self._rotate([0,1,2,3],position)
			self.players[position].set_state(player.STATE_TURN)

			# dichiara accusi del giocatore di mano (se all'inizio del gioco)
			if self.turn_count < 2 and len(self.players[position].accusations) > 0:
				self.conn.send_all(interfaces.NetMethod(protocol.ACCUSATIONS,position,self.players[position].accusations))

	def turn_next(self, card_num):
		'''Continua il giro al giocatore successivo.

		card_num: carta giocata in questo turno
		'''

		# rilascia il turno dal giocatore precedente
		position = self.current_order[len(self.table)-self.table.count(0)]
		self.players[position].set_state(player.STATE_TURNWAIT)

		self.table[position] = card_num

		print "(SERVER) Cards on table:",self.table

		if self.table.count(0) == 0:
			# fine giro, determina chi prende e dichiara
			print "(SERVER) End round!"

			primary = deck.get_card(self.table[self.current_order[0]])
			take = self.current_order[0]
			print "(SERVER) Commanding seem is",primary

			for c in self.table:
				s,v = deck.get_card(c)

				print "(SERVER) Card value:",(v,CARDS_VALUE.index(v)),(primary[1],CARDS_VALUE.index(primary[1]))
				if s == primary[0] and CARDS_VALUE.index(v) > CARDS_VALUE.index(primary[1]):
					print "(SERVER) Found major card:",c
					take = self.table.index(c)
					primary = s,v

			print "(SERVER) Position",take,"takes the head"
			# consegna i punti alla squdra del giocatore
			self._round_points_to_team(take,self.table)

			self.conn.send_all(interfaces.NetMethod(protocol.TAKES,take))
			self.conn.send_all(interfaces.NetMethod(protocol.POINTS,self.hand_points))

			self.turn_count = self.turn_count + 1
			if self.turn_count >= ROUNDS:
				# fine mano!
				print "(SERVER) End hand!"
				self._update_game_points(take)

				time.sleep(3.0)
				self.conn.send_all(interfaces.NetMethod(protocol.GAME_POINTS,self.points))

				if self.points[0] >= MAX_POINTS or self.points[1] >= MAX_POINTS:
					# fine partita! raggiunto 41...

					ret = self.points.index(max(self.points))
					if self.points[0] == self.points[1]:
						# mitici... solo voi ce potete riusci!
						ret = -1

					# dichiara fine partita...
					self.conn.send_all(interfaces.NetMethod(protocol.END_GAME,ret))

				else:
					self.conn.send_all(interfaces.NetMethod(protocol.END_HAND))

					# inizia nuova mano...
					# dovrebbe funzionare...
					self._make_deck()
					for p in self.players:
						p.conn.user_data['state'] = PSTATE_JOINED
						p.set_state(player.STATE_WAIT)

			else:
				# ricomincia giro dalla posizione di take
				time.sleep(3.0)
				self.turn(take)

		else:
			# dai il turno al giocatore successivo
			if position >= 3: position = -1

			# dichiarazione pubblica accusi
			if ( len(self.table) - self.table.count(0) ) == 1 and self.turn_count == 1:
				for p in self.players:
					if len(p.accusations) > 0: self.conn.send_all(interfaces.NetMethod(protocol.ACCUSATIONS,p.position,p.accusations))

			self.players[position+1].set_state(player.STATE_TURN)

	def _update_game_points(self,last):
		print "(SERVER) Current score:",self.points
		for i in range(0,len(self.points)):
			print "(SERVER) Adding",self.hand_points[i][0],"to team",i
			self.points[i] = self.points[i] + self.hand_points[i][0]

		# ultima mano :)
		self.points[last%2] = self.points[last%2] + 1

		print "(SERVER) Without accusations:",self.points
		print "(SERVER) Last took:",last

		accuse_points = [0, 0]
		# punteggio accusi
		for p in self.players:

			team = p.position % 2
			# verifica che la squadra non abbia avuto zero punti nella mano
			print "(SERVER) Verifying accusations for player",p.position,"team",team
			if self.hand_points[team][0] > 0 or (last % 2) == team:

				for a in p.accusations:
					print "(SERVER) Accusation:",a
					if a[0] == 'napoli':
						accuse_points[team] = accuse_points[team] + 3

					if a[0] == 'accuse':
						if a[2] < 0:
							accuse_points[team] = accuse_points[team] + 4
						else:
							accuse_points[team] = accuse_points[team] + 3

		# aggiorna il punteggio
		print "(SERVER) Accusations for team 0:",accuse_points[0]
		print "(SERVER) Accusations for team 1:",accuse_points[1]
		self.points[0] = self.points[0] + accuse_points[0]
		self.points[1] = self.points[1] + accuse_points[1]

		print "(SERVER) Results until last hand:",self.points

	def _round_points_to_team(self, position, cards):
		'''Consegna il punteggio delle carte alla squadra del giocatore in position.'''

		team = position % 2

		# calcola punteggio
		cumul = self.hand_points[team][0]
		third = self.hand_points[team][1]
		for c in cards:

			s,v = deck.get_card(c)

			if v == 1:
				cumul = cumul + 1

			if v == 2 or v == 3 or (v >= 8 and v <= 10):
				third = third + 1
				if third == 3:
					cumul = cumul + 1
					third = 0

		print "(SERVER) Giving",cumul,"points to team",team
		self.hand_points[team][0] = cumul
		self.hand_points[team][1] = third

	def _build_external_plist(self):
		tmp = []

		for p in self.players:
			if p != None:
				tmp.append(p.name)
			else:
				tmp.append('')

		return tuple(tmp)

	def verify_card(self,cards,card_num):
		'''Verifica se la carta card_num puo' essere giocata nel turno corrente.'''

		# di mano, carta valida
		if self.table.count(0) == len(self.table):
			return True

		# verifica se possiamo rispondere
		ver = []
		for c in cards:
			ver.append(deck.get_card(c)[0])

		prev = deck.get_card(self.table[self.current_order[0]])
		this = deck.get_card(card_num)

		# possiamo rispondere, verifica se la carta precedente e' dello stesso seme
		print "Verification seems:",ver,"starting seem of",self.table[self.current_order[0]],"is",prev[0],"my seem for card",card_num,"is",this[0]
		if prev[0] in ver:
			if prev[0] == this[0]:
				return True

		# non possiamo rispondere
		else:
			return True

		return False

if __name__ == '__main__':
		table = [3, 2, 1, 8]
		print "(SERVER) Table:",table

		primary = deck.get_card(table[0])
		take = 0
		print "Commanding:",primary

		for c in table:
			s,v = deck.get_card(c)

			print "(SERVER) Card value:",(v,CARDS_VALUE.index(v)),(primary[1],CARDS_VALUE.index(primary[1]))
			if s == primary[0] and CARDS_VALUE.index(v) > CARDS_VALUE.index(primary[1]):
				#print "(SERVER) Found major card:",c
				take = table.index(c)

		print "(SERVER) Position",take,"takes the head"

		team = take % 2

		# calcola punteggio
		cumul = 0
		third = 0
		print "(SERVER) Table:",table
		for c in table:

			s,v = deck.get_card(c)

			if v == 1:
				cumul = cumul + 1

			if v == 2 or v == 3 or (v >= 8 and v <= 10):
				third = third + 1
				print "Third:",third
				if third == 3:
					cumul = cumul + 1
					third = 0

		print "(SERVER) Giving",cumul,"points to team",team
