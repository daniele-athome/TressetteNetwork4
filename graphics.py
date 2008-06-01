# -*- coding: utf-8 -*-
'''Gestisce la grafica di gioco.'''
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

import pygame,time,deck
import miscgui,objects

BLACK=(0,0,0)
WHITE=(255,255,255)
GREEN=(0,180,0)
LGREEN=(123,240,123)
RED=(255,0,0)

HELP_TEXT = (
	("F1","mostra questa schermata"),
	("F2","mostra l'ultima mano"),
	("F3","richiama il giocatore di mano")
)

# responsi/testi pulsanti
MB_YES=u"Sì"
MB_NO="No"
MB_OK="OK"
MB_CANCEL="Annulla"

# pulsanti
MB_YESNO=(MB_YES,MB_NO)
MB_OK=(MB_OK,)
MB_OKCANCEL=(MB_OK,MB_CANCEL)

class Menu:
	'''Classe di base per tutti i menu.'''

	def __init__(self, screen, callback = None, status_text = ''):
		# prossima destinazione
		self.goto = None

		# screen surface
		self.screen = screen

		# testo di stato
		self.status = objects.StatusText(BLACK, self.screen.get_size(), status_text)

		# callback
		self.callback = callback

		# timeout (lista di (millisecondi,callback,args,start_time))
		self.timeouts = []

		self.clock = pygame.time.Clock()

	def add_timeout(self,millisecs,callback,*args):
		'''Aggiunge una funzione richiamata ogni millisecondi dati.

		Se il callback restituisce False, non sara' piu' chiamato.
		'''

		self.timeouts.append( [millisecs,callback,args,pygame.time.get_ticks()] )

	def message_box(self,text,title,buttons):
		'''Restituisce una nuova MessageBox.'''

		return objects.MessageBox(GREEN, LGREEN, BLACK, title, self.get_center(), text, buttons)

	def get_center(self):
		return (self.screen.get_size()[0]//2,self.screen.get_size()[1]//2)

	def menu(self):
		'''Chiamare alla fine del menu surclassato.

		Resetta il goto e lo restituisce.
		'''

		# processa i timeout
		delete = []
		for t in self.timeouts:
			cur = pygame.time.get_ticks()

			# timeout valido?
			if t[0] > 0:
				# tempo scaduto!
				if (cur - t[3]) >= t[0]:

					# ripeti callback
					if t[1](*t[2]):
						t[3] = pygame.time.get_ticks()
					# segna cancellazione
					else:
						t[0] = 0
						delete.append(self.timeouts.index(t))

		for i in delete:
			del self.timeouts[i]

		self.clock.tick(100)

		tmp = self.goto
		self.goto = None
		return tmp

	def goto_menu(self,menu,*args):
		'''Dirotta al menu <menu>, passando args come argomenti al costruttore.'''

		print "(GFX) Going to menu",menu
		self.goto = (menu,args)

	def set_callback(self,callback):
		'''Imposta il callback degli eventi.'''
		self.callback = callback

	def set_status(self,text):
		'''Imposta il testo di stato.'''
		self.status.set_text(text)

	def status_highlight(self):
		'''Anima il testo di stato.'''
		self.status.animate_highlight(RED)

class Display(Menu):
	'''Menu schermo bianco (verde in effetti).'''

	def __init__(self,size,title):
		# ora che e' tutto a posto, inizializza pygame
		pygame.init()

		# crea lo schermo
		Menu.__init__(self,pygame.display.set_mode(size))
		pygame.display.set_caption(title)
		pygame.key.set_repeat(400,50)

	def _update(self):
		'''Questa funzione viene eseguita nel passaggio da un menu ad un altro.

		Il suo compito e' semplicemente pulire lo schermo con il green table.
		'''

		pygame.display.update(self.screen.fill(GREEN))

	def menu(self):
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				return ("exit",)

		self._update()

		return Menu.menu(self)

class SelectorMenu(Menu):

	def __init__(self, screen, callback = None, status_text = ''):
		Menu.__init__(self, screen, callback, status_text)

		# ambiente gruppo di sprite
		self.updater = pygame.sprite.OrderedUpdates()

		bg = self.screen.fill(GREEN)
		pygame.display.update(bg)

		self.bg = pygame.Surface(self.screen.get_size())
		self.bg.fill(GREEN)
		self.screen.blit(self.bg,(0,0))

		# TODO: due scritte con due linee per dividere le squadre

		# crea 4 sprite con i quadratini
		self.cubes = []
		for i in range(0,4):

			self.cubes.append(objects.PositionButton(GREEN, self.screen.get_size(), i, LGREEN))
			self.updater.add(self.cubes[i])

		# aggiungi la scritta di stato
		self.updater.add(self.status)

	def get_mouse_over(self,mousepos):
		'''Restituisce il valore del pulsante cliccato.'''

		for s in self.cubes:
			if s.rect.collidepoint(mousepos): return self.cubes.index(s)+1

		return 0

	def update_button(self,index, name, busy, mine):
		'''Aggiorna un pulsante.'''

		self.cubes[index].set_state(name, busy, mine)

	def menu(self):
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				return ("exit",)

			if self.callback:

				if event.type == pygame.KEYDOWN:

					key = None
					# premuto numero
					if event.key >= pygame.K_0 and event.key <= pygame.K_9:
						key = event.key - pygame.K_0
						#print "(GFX) Pressed number",key

					if event.key == pygame.K_SPACE:
						key = 'space'
						#print "(GFX) Pressed spacebar"

					if key: self.callback(key)

				elif event.type == pygame.MOUSEBUTTONDOWN:

					self.callback(event.button,event.pos)

		self.updater.clear(self.screen, self.bg)
		self.updater.update()
		pygame.display.update(self.updater.draw(self.screen))

		return Menu.menu(self)

class GameTable(Menu):

	def __init__(self, screen, callback = None, status_text = '', my_position = 0, my_cards = [], plist = ('','','',''), show_cursor = False):
		'''Crea un tavolo da gioco.

		my_position: posizione globale del nostro client
		my_cards: carte del nostro client
		'''
		Menu.__init__(self, screen, callback, status_text)

		self.position = my_position
		self.cards = my_cards

		# ambiente gruppo di sprite
		self.updater = pygame.sprite.OrderedUpdates()
		self.groups = []

		self.plist = plist
		names = self._rotate(plist,self.position)

		# crea le carte
		for i in range(0,4):
			cards = map(lambda x: 0, range(0, 10))
			if i == 0: cards = my_cards

			grp = objects.CardGroup(i,screen,GREEN,cards,names[i])
			self.groups.append(grp)
			self.updater.add(grp)

		bg = self.screen.fill(GREEN)
		pygame.display.update(bg)

		self.bg = pygame.Surface(self.screen.get_size())
		self.bg.fill(GREEN)
		self.screen.blit(self.bg,(0,0))

		# sfondo trasparente
		self.bgdark = pygame.sprite.Sprite()
		self.bgdark.image = pygame.Surface(screen.get_size())
		self.bgdark.rect = self.bgdark.image.get_rect()
		self.bgdark.image.fill(BLACK)
		self.bgdark.image.set_alpha(150)

		# aggiungi la scritta di stato
		self.updater.add(self.status)

		self.score = objects.MultilineText((400,400),GREEN,LGREEN,BLACK,"Punteggio","",(self.screen.get_size()[0]//2,self.screen.get_size()[1]//2))
		self.last = objects.TableReplay(GREEN,LGREEN,BLACK,"Ultime carte",(self.screen.get_size()[0]//2,self.screen.get_size()[1]//2))

		self.help = objects.MultilineText((400,400),GREEN,LGREEN,BLACK,"Aiuto",HELP_TEXT,
		 (self.screen.get_size()[0]//2,self.screen.get_size()[1]//2),objects.TEXTBOX2)

		self.miniscore = (objects.TextLabel(WHITE,'',(5,5),size=objects.TEXTBOX-5),
						objects.TextLabel(WHITE,'',(5,5+objects.TEXTBOX2),size=objects.TEXTBOX-5))
		self.updater.add(*self.miniscore)
		self.update_miniscore()

		# chat (name label, chat entry)
		name_label = objects.TextLabel(WHITE,'',(3,0),(None,self.screen.get_size()[1]-2),size=objects.TEXTBOX)
		chat_entry = objects.TextEntry(WHITE,'',(name_label.rect.left+name_label.rect.width+5,0),(None,self.screen.get_size()[1]-2),
		 size=objects.TEXTBOX,show_cursor=show_cursor,bg_color=GREEN)
		self.chat = (name_label,chat_entry)
		self.updater.add(*self.chat)

	def set_chat(self,name=None,chat=None):
		if name != None:
			if len(name) > 0:
				self.chat[0].set_text(name+": ")
			else:
				self.chat[0].set_text("")
			self.chat[0].update()

		if chat != None:
			self.chat[1].set_text(chat)

		# aggiusta posizione chat entry
		self.chat[1].position = (self.chat[0].rect.left + self.chat[0].rect.width,self.chat[1].position[1])

	def chat_entry(self):
		'''Restituisce la sprite della chat entry.'''

		return self.chat[1]

	def update_miniscore(self,points=(0,0)):
		'''Aggiorna il miniscore.'''

		self.miniscore[0].set_text(self.plist[0]+"/"+self.plist[2]+": "+str(points[0]))
		self.miniscore[1].set_text(self.plist[1]+"/"+self.plist[3]+": "+str(points[1]))

	def reveal_card(self, position, card_num):
		'''Rivela una carta dell'avversario nella posizione data.

		L'indice della carta e' preso a caso (il primo in effetti ;)
		'''

		side = self.get_side_from_position(position)

		# ovviamente operiamo solo se non siamo noi ;)
		if side != objects.SIDE_BOTTOM:
			if side == objects.SIDE_TOP:
				sprite = self.groups[side].cards[0]
			else:
				sprite = self.groups[side].cards[-1]

			sprite.set_card_num(card_num)

	def throw_card(self, position, card_num):
		'''Rimuove una carta dalla mano e la mette in campo.

		position: posizione globale da dove prelevare la carta
		card_num: valore della carta
		'''

		side = self.get_side_from_position(position)

		sprite = self.groups[side].remove(card_num)

		if sprite != None:
			# mette al centro
			if not sprite.table:
				sprite.table = True
				sprite.animate_to_center(side)
				self.updater.add(sprite)

	def back_card(self, position, card_num):
		'''Fa ritornare la carta alla posizione data.'''
		side = self.get_side_from_position(position)
		sprite = None

		for s in self.updater.sprites:
			if isinstance(s,objects.Card):
				if s.card_num == card_num:
					sprite = s

		if sprite != None:
			# mette al centro
			if sprite.table:
				sprite.animate_to_side(side)
				self.updater.add(sprite)

	def back_all_cards(self, position):
		'''Fa ritornare tutte le carte in tavola alla posizione data.'''

		side = self.get_side_from_position(position)

		for s in self.updater:

			if isinstance(s,objects.Card):
				if s.table:
					s.animate_to_side(side)
					self.updater.add(s)

		# hack per il timeout dopo protocol.TAKES
		return False

	def get_side_from_position(self, position):
		'''Restituisce il lato del tavolo data la posizione *globale* nel gioco.'''

		copy = self._rotate([0, 1, 2, 3],self.position)

		#print "(GFX) Side for position",position,"is",copy.index(position)
		return copy.index(position)

	def _rotate(self, seq, n=1):
		n = n % len(seq)
		return seq[n:] + seq[:n]

	def highlight(self, position, value):
		'''Disegna una linea rossa vicino alle carte della posizione data.'''

		side = self.get_side_from_position(position)

		sp = self.groups[side].get_highlight()

		if value:
			self.updater.add(sp)

		else:
			sp.kill()

	def highlight_name(self, position, value):
		'''Setta il nome nella posizione data in rosso.'''

		side = self.get_side_from_position(position)

		if value:
			self.groups[side].title.set_color(RED)

		else:
			self.groups[side].title.set_color(BLACK)

	def get_mouse_over(self,mousepos):
		'''Restituisce il valore della carta con il mouse sopra.'''

		# carte nostre ovviamente
		grp = self.groups[0]

		for s in grp:
			if isinstance(s,objects.Card):
				if s.rect.collidepoint(mousepos): return s.card_num

		return 0

	def set_subtitle(self, position, text):

		# splitta il testo con l'accapo
		newline = text.split('\n')

		self.groups[self.get_side_from_position(position)].set_subtitle(newline)

	def show_score(self, points = None):
		'''Mostra lo score.

		points: ( ( team1, team2 ), ( team1, team2 ), ... )
		'''

		if points == None:
			self.score.kill()

		else:
			cumul = [0, 0]
			final = [ (self.plist[0],self.plist[1]), (self.plist[2],self.plist[3]) ]
			for i in range(0,len(points)):

				final.append( (str(points[i][0]),str(points[i][1])) )
				cumul[0] = cumul[0] + points[i][0]
				cumul[1] = cumul[1] + points[i][1]

			final.append('-')
			final.append( (str(cumul[0]),str(cumul[1])) )

			self.score.set_text(final)
			self.updater.add(self.score)

	def show_help(self, bshow = True):
		'''Mostra/nasconde l'aiuto veloce.'''

		if bshow:
			self.updater.add(self.bgdark)
			self.updater.add(self.help)

		else:
			self.help.kill()

			for sp in self.updater.sprites():
				if isinstance(sp,objects.MultilineText) and sp != self.score:
					# se troviamo un'altra multilinetext (ad eccezione dello score) non leviamo il background
					return

			self.bgdark.kill()

	def show_last(self, cards = None, last = -1):
		'''Mostra le ultime 4 carte dell'ultimo giro.'''

		if cards == None:
			self.last.kill()

			for sp in self.updater.sprites():
				if isinstance(sp,objects.MultilineText) and sp != self.score:
					# se troviamo un'altra multilinetext (ad eccezione dello score) non leviamo il background
					return

			self.bgdark.kill()

		else:
			self.last.set_cards(cards,self.get_side_from_position(last))
			self.updater.add(self.bgdark)
			self.updater.add(self.last)

	def add_messagebox(self,text,title,buttons):
		'''Crea e mostra una messagebox con il dark background.'''

		self.updater.add(self.bgdark)

		msgbox = Menu.message_box(self,text,title,buttons)
		self.updater.add(msgbox)

		return msgbox

	def cancel_multilines(self):
		'''Rimuove tutti i MultilineText (tranne le MessageBox) e l'eventuale dark background.'''

		for sp in self.updater.sprites():
			if isinstance(sp,objects.MultilineText) and not isinstance(sp,objects.MessageBox):
				sp.kill()

			if sp == self.bgdark: sp.kill()

	def menu(self):
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				return ("exit",)

			if self.callback:

				if event.type == pygame.KEYDOWN:

					if not self.chat[1].process_event(event):

						key = None
						if event.key == pygame.K_ESCAPE:
							key = 'escape'

						elif event.key == pygame.K_F1:
							key = 'f1'

						elif event.key == pygame.K_F2:
							key = 'f2'

						elif event.key == pygame.K_F3:
							key = 'f3'

						elif event.key == pygame.K_RETURN:
							key = 'return'

						if key: self.callback(key)

				elif event.type == pygame.MOUSEBUTTONDOWN:

					self.callback(-event.button,event.pos)

				elif event.type == pygame.MOUSEBUTTONUP:

					self.callback(event.button,event.pos)

		self.updater.clear(self.screen, self.bg)
		self.updater.update()
		pygame.display.update(self.updater.draw(self.screen))

		return Menu.menu(self)

class StatisticsMenu(Menu):
	'''Resoconto statistiche della partita.

	Mostrato alla fine della partita.
	'''

	def __init__(self, screen, callback = None, stats = None):
		Menu.__init__(self, screen, callback, "Chiudi la finestra per uscire.")

		self.stats = stats

		bg = self.screen.fill(GREEN)
		pygame.display.update(bg)

		self.bg = pygame.Surface(self.screen.get_size())
		self.bg.fill(GREEN)
		self.screen.blit(self.bg,(0,0))

		# multiline text per le statistiche
		self.multitext = objects.MultilineText((600,500), GREEN, LGREEN, BLACK, "Fine partita", self._make_text(), (self.screen.get_size()[0]//2, self.screen.get_size()[1]//2))

		# ambiente gruppo di sprite
		self.updater = pygame.sprite.OrderedUpdates()
		self.updater.add(self.multitext)

		# aggiungi la scritta di stato
		self.updater.add(self.status)

	def _make_text(self):
		'''Ricostruisce il testo dalle statistiche.'''

		text = [ (self.stats.plist[0],self.stats.plist[1]), (self.stats.plist[2],self.stats.plist[3]), "-", ("Punti","Accusi","Punti","Accusi") ]

		for h in self.stats.hands:
			text.append( (str(h[0][0]),str(h[0][1]),str(h[1][0]),str(h[1][1])) )

		text.append('-')
		text.append( (str(self.stats.total_points[0]),str(self.stats.total_points[1])) )

		return text

	def menu(self):
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				return ("exit",)

		self.updater.clear(self.screen, self.bg)
		self.updater.update()
		pygame.display.update(self.updater.draw(self.screen))

		return Menu.menu(self)
if __name__ == '__main__':
	import sys,player

	def callback_ciao(num,pos=None):
		p.score.kill()

		if pos != None and hasattr(p,'msgbox'):
			#print p.msgbox._click(pos)
			p.msgbox._mousedown(pos)
			return

		if num == 'f1':
			p.msgbox = objects.MessageBox(GREEN,LGREEN,BLACK,"Avviso",(p.screen.get_size()[0]//2,p.screen.get_size()[1]//2),"Bella zio!",
			 ("OK","Annulla","Riprova"))
			p.updater.add(p.msgbox)

		if num:

			if not p.first:
				del cards[0]
				p.back_all_cards(p.num)
				p.status.animate_highlight(RED)
				#p.chat.insert_text("ciao")
				p.chat[1].delete(False)
				p.num = p.num + 1
				if p.num > 3: p.num = 0
				p.first = True

			else:
				if len(cards) > 0:
					p.highlight(0,True)
					p.highlight(1,True)
					p.highlight(2,True)
					p.highlight(3,True)
					p.set_subtitle(3,"Ciao1\nProva1\nProvone1\nProvolone1\nMinchiarola1\nMerda1")
					p.set_subtitle(2,"Ciao2\nProva2")
					p.set_subtitle(1,"Ciao3\nProva3")
					p.throw_card(0,cards[0])
					p.first = False

					card = d.extract()[0]
					p.reveal_card(1,card)
					p.throw_card(1,card)

					card = d.extract()[0]
					p.reveal_card(2,card)
					p.throw_card(2,card)

					card = d.extract()[0]
					p.reveal_card(3,card)
					p.throw_card(3,card)

				#else:
				#	p.updater.add(objects.MultilineText((400,400),GREEN,LGREEN,"Punteggio"))

			#print "Cards now:",cards

	a = Display((800,600),"Prova Pygame")
	p = None
	if len(sys.argv) > 1 and sys.argv[1] == 'stats':

			st = player.GameStats(("daniele","simone","ilaria","valerio"))
			st.hand_begin()
			st.hand_update(((7,0),(3,0)))
			st.hand_end((11,6),0)

			st.hand_begin()
			st.hand_update( ((2,0),(8,0)) )
			st.hand_end((7+11,8+6),0)

			p = StatisticsMenu(a.screen,None,st)

	else:

		d = deck.Deck()
		d.shuffle()
		cards = deck.sort_cards(d.extract(10))

		p = GameTable(a.screen,callback_ciao,"Prova testo",0,list(cards),("daniele","simone","ilaria","valerio"),show_cursor=True)
		p.first = True
		p.num = 0
		if len(sys.argv) > 1:
			if sys.argv[1] == 'replay':
				p.score = objects.TableReplay(GREEN,LGREEN,BLACK,"Ultime carte",(p.screen.get_size()[0]//2,p.screen.get_size()[1]//2),d.extract(4),0)
		else:
			p.score = objects.MultilineText((400,400),GREEN,LGREEN,BLACK,"Punteggio",(),(p.screen.get_size()[0]//2,p.screen.get_size()[1]//2))
			points = [23,15]
			p.score.set_text( ( ("Squadra 1-3","Squadra 2-4"), (str(points[0]),str(points[1])) ) )
		""" background nero
		sp = pygame.sprite.Sprite()
		sp.image = pygame.Surface(p.screen.get_size())
		sp.rect = sp.image.get_rect()
		sp.image.fill(BLACK)
		sp.image.set_alpha(150)
		p.updater.add(sp)
		"""
		p.set_chat("daniele","bella zio!")
		p.updater.add(p.score)

	while True:
		goto = p.menu()

		if goto != None:
			if goto[0] == 'exit':
				break
