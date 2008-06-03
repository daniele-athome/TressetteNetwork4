# -*- coding: utf-8 -*-
'''Oggetti della grafica di gioco.'''
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

from __future__ import division
import sys
import pygame,miscgui,deck

RECT=150			# dimensione rettangolo selezione posizione
BORDER=20			# bordo rettangolo selezione e rettangolo casella di testo
OFFSET=10			# distanza tra i pulsanti di selezione (usato anche in TableReplay -- distanza fra le carte)
TEXTBOX=30			# dimensione (in pixel) del font della textbox
TEXTBOX2=20			# dimensione (in pixel) del font delle textbox per gli accusi
TITLE=40			# dimensione (in pixel) del font del titolo della casella di testo
LINE=12				# spessore della linea che separa titolo da testo nella casella di testo
CARD_OFFSET=2		# distanza tra le carte (solo per SIDE_BOTTOM)
BTN_SIZE=(100,30,30)# grandezza pulsante (width,height,font) (MessageBox)
BTN_OFFSET=5		# distanza tra i pulsanti (MessageBox)
BTN_BORDER=7		# bordo pulsante

class TextLabel(pygame.sprite.Sprite):
	'''Una scritta da poter mettere dove si vuole.'''

	def __init__(self, color, text = '', position = (0,0), rightbottom = (None, None), rightlimit = False, size = TEXTBOX, center = (None,None)):
		pygame.sprite.Sprite.__init__(self)

		self.color = color
		self.text = text
		self.size = size
		self.font = miscgui.create_font(size)

		self.stop_animation()

		self.set_position(position,rightbottom,rightlimit,center)
		self.update()

	def set_text(self,text):
		self.stop_animation()
		self.text = text

	def get_text(self):
		return self.text

	def set_color(self,color):
		self.color = color
		self.stop_animation()

	def update(self,more_space=False,bgcolor=(0,0,0)):

		if self._anim:
			tick = (pygame.time.get_ticks() - self._start)/500*4.0
			if tick > 1.0:
				self._start = pygame.time.get_ticks()

				# cambia colore
				if self.current_color != self.hl_color:
					self.current_color = self.hl_color
				else:
					self.current_color = self.color

				self._times = self._times + 1
				if self._times >= 6:
					self.stop_animation()

		self._make_text(more_space,bgcolor)

	def set_position(self, xy, rightbottom = (None, None), rightlimit = False, center = (None,None)):
		self.position = xy
		self.rightbottom = rightbottom
		self.rightlimit = rightlimit
		self.center = center

	def _make_text(self,more_space=False,bgcolor=(0,0,0)):
		self.image = miscgui.draw_text(self.text,self.size,self.current_color,font=self.font,more_space=more_space,bgcolor=bgcolor)
		self.rect = self.image.get_rect()

		self.rect.topleft = self.position

		if self.rightbottom[0] != None:
			self.rect.right = self.rightbottom[0]

		if self.rightbottom[1] != None:
			self.rect.bottom = self.rightbottom[1]

		if self.rightlimit:
			self.rect.right = self.rightlimit

		if self.center[0] != None:
			self.rect.centerx = self.center[0]

		if self.center[1] != None:
			self.rect.centery = self.center[1]

	def animate_highlight(self,hl_color):
		'''Lampeggia la scritta nel colore dato per 3 volte.'''

		self.hl_color = hl_color
		self._anim = True
		self._times = 0
		self._start = pygame.time.get_ticks()

	def stop_animation(self):
		'''Ferma l'animazione del lampeggio.'''

		self._anim = False
		self.hl_color = None
		self.current_color = self.color

class TextEntry(TextLabel):
	'''Una TextLabel modificabile dall'utente.'''
	def __init__(self, color, text = '', position = (0,0), rightbottom = (None, None), rightlimit = False, size = TEXTBOX,show_cursor = True,bg_color=(0,0,0)):

		self.bg_color = bg_color
		self._cursor = 0
		self.show_cursor(show_cursor)

		# separatori di parola
		self.sep = (' ', '/', '-', '+', ',', '.', ';', ':' )

		TextLabel.__init__(self,color,text,position,rightbottom,rightlimit,size)

	def set_cursor(self,n):
		if n >= 0 and n <= len(self.text):
			self._cursor = n

	def cursor_offset(self,offset):
		'''Somma l'offset alla posizione del cursore.'''
		self.set_cursor(self._cursor + offset)

	def cursor_next(self):
		'''Avanza il cursore al carattere successivo.'''
		self.cursor_offset(1)

	def cursor_prev(self):
		'''Ritorna il cursore al carattere precedente.'''
		self.cursor_offset(-1)

	def cursor_start(self):
		'''Imposta il cursore all'inizio.'''
		self.set_cursor(0)

	def cursor_end(self):
		'''Imposta il cursore alla fine.'''
		self.set_cursor(len(self.text))

	def cursor_next_word(self):
		'''Imposta il cursore alla prossima parola.'''

		ind = self._find_sep()

		if ind >= 0:
			self.set_cursor(ind)
		else:
			self.cursor_end()

	def cursor_prev_word(self):
		'''Imposta il cursore alla parola precedente.'''

		ind = self._find_sep(True)

		if ind >= 0:
			self.set_cursor(ind)
		else:
			self.cursor_start()

	def _find_sep(self,backward=False,custom_cursor=-1):
		'''Restituisce l'indice della prossima/precedente parola dal cursore.'''

		if custom_cursor < 0:
			custom_cursor = self._cursor

		for c in self.sep:
			ind = -1
			if backward:
				cur = custom_cursor
				if cur > 0: cur = cur - 1
				ind = self.text.rfind(c,0,cur)
			else:
				ind = self.text.find(c,custom_cursor)

			if ind >= 0:
				# trovato qualcosa
				# FIXME non funziona in caso di spazi multipli
				return ind + 1

		return -1

	def show_cursor(self,bshow):
		'''Nasconde/mostra il cursore.'''
		self._cursor_draw = bshow

	def insert_text(self,text):
		'''Inserisce il testo alla posizione del cursore.'''
		txt = self.text[:self._cursor]+text+self.text[self._cursor:]
		#print "(GFX) Final text:",txt

		TextLabel.set_text(self,txt)
		self.cursor_offset(len(text))

	def delete(self,backspace=False):
		'''Rimuove un carattere alla destra del cursore.

		Se backspace e' True, rimuove il carattere alla sinistra del cursore.
		'''

		if backspace:
			if self._cursor == 0: return
			txt = self.text[:self._cursor-1]+self.text[self._cursor:]
			self.cursor_offset(-1)

		else:
			if self._cursor == len(self.text): return
			txt = self.text[:self._cursor]+self.text[self._cursor+1:]

		TextLabel.set_text(self,txt)

	def update(self):
		TextLabel.update(self,5,self.bg_color)

		# disegna cursore
		if self._cursor_draw:

			# trova posizione dato il cursore
			w,h = self.font.size(self.text[:self._cursor])

			start = (w,0)
			end = (w,h)

			pygame.draw.line(self.image,self.color,start,end,2)

	def process_event(self,event):
		'''Processa l'evento della tastiera passato.

		Restituisce False se l'evento non e' stato processato.
		'''

		if not self._cursor_draw: return False

		blacklist = ( "\t", "\n", "\r", "\b" )

		ret = False
		if event.key == pygame.K_BACKSPACE:
			self.delete(True)
			ret = True

		elif event.key == pygame.K_DELETE:
			self.delete(False)
			ret = True

		elif event.key == pygame.K_LEFT:

			if event.mod & pygame.KMOD_CTRL:
				if sys.platform == "darwin":
					# modificatori Mac OS X
					# TODO
					pass
				else:
					self.cursor_prev_word()

			else:
				self.cursor_prev()
			ret = True

		elif event.key == pygame.K_RIGHT:

			if event.mod & pygame.KMOD_CTRL:
				if sys.platform == "darwin":
					# modificatori Mac OS X
					# TODO
					pass
				else:
					self.cursor_next_word()

			else:
				self.cursor_next()
			ret = True

		elif event.key == pygame.K_END:
			self.cursor_end()
			ret = True

		elif event.key == pygame.K_HOME:
			self.cursor_start()
			ret = True

		else:
			if len(event.unicode) == 1:
				if event.unicode not in blacklist:
					self.insert_text(event.unicode)
					ret = True

		return ret

class StatusText(TextLabel):
	'''Una scritta di stato in basso a destra.'''

	def __init__(self, color, screen_size, text = ''):

		self.screen_size = screen_size
		TextLabel.__init__(self, color, text)

	def _make_text(self,more_space=False,bgcolor=None):
		TextLabel._make_text(self)
		self.rect.bottom = self.screen_size[1]
		self.rect.right = self.screen_size[0]-5

class PositionButton(pygame.sprite.Sprite):
	'''Un singolo pulsante per il selettore di posizione.'''

	def __init__(self, bg_color, index, bl_color):
		pygame.sprite.Sprite.__init__(self)

		self.index = index
		self.size = RECT
		self.bg_color = bg_color

		self.old_color = bl_color
		self.color = bl_color
		self.name = ''

		# crea superficie per il disegno
		self.image = pygame.surface.Surface((self.size,self.size))
		self.rect = self.image.get_rect()

	def update(self):
		self._make_rect()
		self._make_number()
		self._make_name()

	def _make_name(self):
		surf = miscgui.draw_text(self.name,30,self.color)
		rect = surf.get_rect()
		rect.centerx = int(self.rect.width/2)
		rect.centery = self.rect.height-35
		self.image.blit(surf,rect)

	def _make_number(self):
		surf = miscgui.draw_text(str(self.index+1),80,self.color)
		rect = surf.get_rect()
		rect.center = (int(self.rect.width/2), int(self.rect.height/2))
		self.image.blit(surf,rect)

	def _make_rect(self):
		self.image.fill(self.bg_color)
		miscgui.draw_rect(self.image,self.size,self.size,self.bg_color,self.color,BORDER)

	def set_state(self, name = '', busy=False, mine=False):
		'''Imposta lo stato del pulsante.

		Viene valutato prima busy poi mine, se entrambi False viene preso il colore di default LGREEN.
		'''

		self.color = self.old_color

		if busy:
			self.color = (255, 255, 255)

		if mine:
			self.color = (255, 0, 0)

		self.name = name

	def get_state(self):
		'''Restituisce True se busy o mine e' True.'''

		return (self.color == (255, 255, 255) or self.color == (255,0,0))

# posizioni in senso antiorario
SIDE_BOTTOM=0
SIDE_RIGHT=1
SIDE_TOP=2
SIDE_LEFT=3

CARD_SIZE=62,120

class Card(pygame.sprite.Sprite):
	'''Oggetto carta singola.'''

	def __init__(self, card_num, screen, bg_color = (0,0,0), draw_rect = False):
		pygame.sprite.Sprite.__init__(self)

		self.set_card_num(card_num)
		self.rect = self.image.get_rect()

		self.screen = screen
		self._anim = False
		self._draw_rect = draw_rect
		self._bg_color = bg_color

	def set_card_num(self,card_num):
		self.card_num = card_num

		# costruisci path dell'immagine della carta
		image_path = deck.get_card_image_path(card_num)

		# crea sprite da immagine
		card = pygame.image.load(image_path)

		if hasattr(pygame.transform,"smoothscale"):
			self.image = pygame.transform.smoothscale(card,CARD_SIZE)
		else:
			self.image = pygame.transform.scale(card,CARD_SIZE)

	def set_draw_rect(self,value):
		self._draw_rect = value

	def get_draw_rect(self):
		return self._draw_rect

	def animate_to_center(self, side):
		'''Anima il movimento della carta verso il centro relativo al lato dato.'''

		self._A = self.rect.topleft
		rect = self.screen.get_rect()

		self._B = rect.center

		if side == SIDE_BOTTOM:
			self._B = rect.center

		elif side == SIDE_RIGHT:
			self._B = (rect.centerx+CARD_SIZE[0]+10,rect.centery-int(CARD_SIZE[1]/2))

		elif side == SIDE_LEFT:
			self._B = (rect.centerx-CARD_SIZE[0]-10,rect.centery-int(CARD_SIZE[1]/2))

		elif side == SIDE_TOP:
			self._B = (rect.centerx,rect.centery-CARD_SIZE[1]-10)

		self._start_anim()

	def animate_to_side(self, side):
		'''Anima il movimento della carta dal centro verso il lato dato.'''

		self._A = self.rect.topleft
		rect = self.screen.get_rect()

		if side == SIDE_BOTTOM:
			self._B = (rect.centerx,rect.height)

		elif side == SIDE_TOP:
			self._B = (rect.centerx,0)

		elif side == SIDE_RIGHT:
			self._B = (rect.width,rect.centery)

		elif side == SIDE_LEFT:
			self._B = (-CARD_SIZE[0]-2,rect.centery)

		self._start_anim(True)

	def _start_anim(self,delete=False):
		self._start = pygame.time.get_ticks()
		self._anim = True
		self._delete = delete

	def update(self):

		if self._anim:

			tick = (pygame.time.get_ticks() - self._start)/1000*4.0
			if tick > 1.0:
				self._anim = False
				if self._delete:
					self.kill()
				tick = 1.0

			x = (1 - tick) * self._A[0] + tick * self._B[0]
			y = (1 - tick) * self._A[1] + tick * self._B[1]

			self.rect.topleft = (x,y)

		if self._draw_rect:
			miscgui.draw_rect(self.image,self.rect.width,self.rect.height,self._bg_color,(255,0,0),border=5)

class CardGroup(pygame.sprite.OrderedUpdates):
	'''Gruppo di carte per un singolo giocatore.

	Il gruppo di carte e' modificabile, ma e' possibile solo rimuovere
	carte; quindi il metodo add() e' dummy!
	'''

	def __init__(self, side, screen, bg_color, cards = [], title = ''):
		pygame.sprite.OrderedUpdates.__init__(self)

		self.side = side
		self.screen = screen
		self.bg_color = bg_color

		# coordinate di partenza
		self._card_count = len(cards)
		self._build_coords(True)

		left = self.left
		top = self.top
		self.cards = []
		for c in cards:
			#print "(GFX) Adding sprite for card",c
			sp = Card(c,screen)
			sp.table = False
			# converti il pixel format
			sp.image = sp.image.convert(screen)

			# aggiusta posizione
			if side % 2 != 0:
				# carte orizzontali
				# non ruotare l'immagine (TEST) --- sp.image = pygame.transform.rotate(sp.image,90)
				sp.rect.top = top
				sp.rect.left = self.left
				top = top + CARD_SIZE[0]-CARD_SIZE[0]//2

			else:
				# carte verticali
				sp.rect.top = self.top
				sp.rect.left = left

				if side == SIDE_TOP:
					left = left + CARD_SIZE[0]-CARD_SIZE[0]//2
				else:
					left = left + CARD_SIZE[0]+CARD_OFFSET

			self.cards.append(sp)
			pygame.sprite.OrderedUpdates.add(self,sp)

		left = self.left
		top = self.top - TEXTBOX
		subleft = 0
		subtop = 0
		right = None
		bottom = None

		lrect = self.sprites()[-1].rect
		if side % 2 == 0:
			left = int(self.screen.get_size()[0]/2)

		if side == SIDE_TOP:
			top = self.top + CARD_SIZE[1] + 10

			subleft = lrect.left + lrect.width + 5
			subtop = self.top + 5

		elif side == SIDE_BOTTOM:
			top = top + 5

		elif side == SIDE_LEFT:
			left = left + 2

			subleft = lrect.left + lrect.width + 5
			subtop = self.sprites()[4].rect.top

		elif side == SIDE_RIGHT:

			right = self.sprites()[0].rect.left - 5
			bottom = self.sprites()[1].rect.bottom

		# sottotitolo per side != SIDE_BOTTOM

		if side != SIDE_BOTTOM:
			self.subtitle = []
			self.subtitle.append(TextLabel((255,255,0),'',(subleft,subtop),(right,bottom)))
			pygame.sprite.OrderedUpdates.add(self,self.subtitle[0])

			for i in range(1,4):
				# sottotitolo -- seconda linea
				if (right,bottom) != (None, None):
					right,bottom = right,bottom+TEXTBOX2-2
				subtop = subtop + TEXTBOX2 + 2
				self.subtitle.append(TextLabel((255,255,0),'',(subleft,subtop),(right,bottom),False,TEXTBOX2))

				pygame.sprite.OrderedUpdates.add(self,self.subtitle[i])

		right = False
		if side == SIDE_RIGHT: right = self.screen.get_size()[0]-5

		self.title = TextLabel((0,0,0),title,(left,top),(None,None),right)
		pygame.sprite.OrderedUpdates.add(self,self.title)

		# linea highlight
		self.line = Line((255,0,0),'h',self.title.rect.width+10)
		self.line.rect.center = (self.title.rect.centerx,self.title.rect.centery+self.title.rect.height//2)

	def set_title(self,text):
		self.title.set_text(text)

	def set_subtitle(self, textlist):
		if hasattr(self,'subtitle'):
			for i in range(0,len(self.subtitle)):
				if i < len(textlist):
					self.subtitle[i].set_text(textlist[i])
				else:
					self.subtitle[i].set_text('')

	def _build_coords(self, init = False):

		if self.side == SIDE_BOTTOM:
			self.top = self.screen.get_size()[1]-CARD_SIZE[1]-TEXTBOX
			if init: self.left = self.screen.get_size()[0]/self._card_count

		elif self.side == SIDE_RIGHT:

			self.left = self.screen.get_size()[0]-CARD_SIZE[0]

		elif self.side == SIDE_LEFT:

			self.left = 0

		if self.side == SIDE_TOP:

			self.top = 0
			self.left = self.screen.get_size()[0]/(self._card_count/2)+CARD_SIZE[0]

		# lati destro e sinistro: stesso Top
		if self.side % 2 != 0:

			self.top = self.screen.get_size()[1]/(self._card_count/2)

	def get_highlight(self):
		'''Restituisce la sprite dell'highlight per il gruppo di carte.'''

		return self.line

	def add(self,*sprites):
		pass

	def remove(self,card_num,index = 0):
		'''Rimuove la carta con il valore di carta dato.

		Il metodo remove e' diverso dall'implementazione di pygame.
		Viene passato il valore della carta, non la sprite.

		Se il lato del gruppo e' SIDE_BOTTOM, la sprite viene rimossa
		e tutte le sprite vengono unite adiacentemente. In questo caso l'argomento
		index e' ignorato.

		Se il lato del gruppo e' diverso da SIDE_BOTTOM, viene considerata la carta
		numero index delle carte coperte e viene rimossa.

		Restituisce la sprite della carta, cosi' da poter essere messa sul tavolo.
		'''

		# prima di tutto trova la sprite corrispondente
		sprite = None
		for sp in self.cards:

			#if self.side == SIDE_BOTTOM:
			if hasattr(sp,'card_num'):
					#print "(GFX) Sprite card:",sp.card_num
					if sp.card_num == card_num:
						#print "(GFX) Found sprite for card",card_num
						sprite = sp
						break

			else:
				sprite = self.cards[index]

		if sprite != None:

			# rimuovi la sprite dal gruppo
			sprite.kill()
			c = self.cards.index(sprite)
			self.cards.remove(sprite)

			# scala le carte se siamo al SIDE_BOTTOM
			if self.side == SIDE_BOTTOM:
				# TODO: centrare invece di scalare a sinistra
				start = (self.screen.get_size()[0] - (CARD_SIZE[0] * len(self.cards)) - (CARD_OFFSET * len(self.cards))) // 2
				for i in range(0,len(self.cards)):
					sp = self.cards[i]
					sp.rect.left = start + (i * CARD_SIZE[0]) + (CARD_OFFSET * i)

		return sprite

class Line(pygame.sprite.Sprite):
	'''Il nome della classe parla da solo.'''

	def __init__(self, color, direction, length, width = 4):
		pygame.sprite.Sprite.__init__(self)

		self.length = length
		self.width = width
		self.color = color
		wh = None

		if direction == 'h':
			wh = (length,width)
			self.end = (length,0)

		elif direction == 'v':
			wh = (width,length)
			self.end = (0,length)

		dummy = pygame.surface.Surface(wh)
		rect = pygame.draw.line(dummy,self.color,(0,0),self.end,self.width)
		self.image = pygame.surface.Surface((rect.width,rect.height))
		self.rect = pygame.draw.line(self.image,self.color,(0,0),self.end,self.width)

	def update(self):
		pygame.draw.line(self.image,self.color,(0,0),self.end,self.width)

	def set_color(self,color):
		self.color = color

class MultilineText(pygame.sprite.Sprite):
	'''Casella di testo multilinea.'''

	def __init__(self, size, bg_color, out_color, color, title, text = (), center = (0,0), fontsize = TEXTBOX):
		'''Crea una nuova casella di testo multilinea.

		size: tupla (width,height) per la dimensione (compreso il rect)
		bg_color: colore di sfondo del rect
		color: colore del titolo e del testo
		out_color: colore del rect e della linea sotto il titolo
		title: testo del titolo
		text: testo nel frame (lista di righe: (cella1, cella2, cella3,...))
		center: posizione del punto centrale del frame
		fontsize: dimensione del font del testo (titolo fisso a TITLE)
		'''
		pygame.sprite.Sprite.__init__(self)

		self.size = size
		self.bg_color = bg_color
		self.out_color = out_color
		self.color = color
		self.title = title
		self.text = text

		self.center = center
		self.font = miscgui.create_font(fontsize,False,False)

		# crea superficie per il disegno
		self.image = pygame.surface.Surface(size)
		self.rect = self.image.get_rect()
		self.rect.center = center

	def set_title(self,title):
		self.title = title

	def set_text(self, text):
		self.text = text

	def update(self):
		self._make_rect()
		self._make_title()
		self._make_text()

	def _make_rect(self):
		self.image.fill(self.bg_color)
		miscgui.draw_rect(self.image,self.size[0],self.size[1],self.bg_color,self.out_color,BORDER)

	def _make_title(self):
		if self.title != None:
			surf = miscgui.draw_text(self.title,TITLE,self.color)
			rect = surf.get_rect()
			rect.centerx = int(self.rect.width/2)
			rect.top = 20
			self.image.blit(surf,rect)

		# linea sotto il titolo
		pygame.draw.line(self.image,self.out_color,(BORDER*2,TITLE+BORDER),(self.size[0]-BORDER*2,TITLE+BORDER),LINE)

	def _make_text(self):
		top = TITLE+BORDER+LINE+10
		if self.text != None:

			for line in self.text:

				if line == '-':
					pygame.draw.line(self.image,self.out_color,(BORDER*2,top),(self.size[0]-BORDER*2,top),LINE//2)
					top = top + LINE
				else:

					for i in range(0,len(line)):
						surf = miscgui.draw_text(line[i],color=self.color,font=self.font)
						rect = surf.get_rect()
						rect.centerx = 25+(((self.rect.width-50)//len(line))*i)+((self.rect.width-50)//len(line)//2)
						rect.top = top
						self.image.blit(surf,rect)

					top = top + TEXTBOX2 + 5

class TableReplay(MultilineText):
	'''Mostra un giro di 4 carte giocate sul tavolo.

	Il costruttore e' leggermente diverso da MultilineText.
	'''

	def __init__(self, bg_color, out_color, color, title, center, cards = None, hand_side = -1):
		MultilineText.__init__(self, (CARD_SIZE[0]*5+50,CARD_SIZE[1]*3+50), bg_color, out_color, color, title, None, center)

		self.cards = None
		self.set_cards(cards,hand_side)

	def update(self):
		MultilineText.update(self)

		for sp in self.cards:
			sp.update()
			self.image.blit(sp.image,sp.rect)
			
	def set_cards(self,cards,hand_side=-1):
		if self.cards != None:
			# rimuovi le carte dallo schermo
			for s in self.cards: s.kill()

		self.cards = []
		if cards != None:
			for i in range(0,4):
				c = Card(cards[i],None,self.bg_color,(i == hand_side))

				if i % 2:
					c.rect.centery = self.rect.height//2
					if i == SIDE_RIGHT:
						c.rect.centerx = self.rect.width//2+CARD_SIZE[0]+OFFSET*2

					elif i == SIDE_LEFT:
						c.rect.centerx = self.rect.width//2-CARD_SIZE[0]-OFFSET*2

				else:
					c.rect.centerx = self.rect.width//2
					if i == SIDE_BOTTOM:
						c.rect.centery = self.rect.height//2+CARD_SIZE[1]//2+OFFSET

					elif i == SIDE_TOP:
						c.rect.centery = self.rect.height//2-CARD_SIZE[1]//2-OFFSET

				c.rect.top = c.rect.top + OFFSET*3
				self.cards.append(c)

class MessageBox(MultilineText):
	'''MessageBox costruita con il MultilineText.'''

	def __init__(self, bg_color, out_color, color, title, center = (0,0), text = '', buttons = ('OK',)):
		MultilineText.__init__(self, (500,200), bg_color, out_color, color, title, center=center)

		self.buttons = buttons
		self.rects = []
		self.selected = -1
		self.btn_font = miscgui.create_font(BTN_SIZE[2])
		self.set_text(text)

	def set_text(self,text):
		'''Converte da testo semplice a testo per MultilineText.'''

		dd = text.split("\n")
		tlist = []

		for line in dd:

			if len(line) == 0:
				tlist.append("-")

			else:
				tlist.append( (line,) )
			
		MultilineText.set_text(self,tuple(tlist))

	def update(self):
		MultilineText.update(self)

		# disegna pulsanti
		start = (self.size[0] - (BTN_SIZE[0]*len(self.buttons)) - (BTN_OFFSET*len(self.buttons)))//2

		for i in range(0,len(self.buttons)):

			sel = False
			if i == self.selected: sel = True

			r = self._make_button(i,self.buttons[i],start,sel)

			if len(self.rects) < len(self.buttons):
				self.rects.append(pygame.Rect(r.left+self.rect.left,r.top+self.rect.top,r.width,r.height))

	def _make_button(self,index,text,start,selected=False):
		'''Disegna un pulsante.

		index: indice del pulsante
		text: testo del pulsante
		start: coordinata X del punto di partenza del primo pulsante
		'''

		pos = (start + (index * BTN_SIZE[0]) + (index * (BTN_OFFSET*2)),self.size[1]-BTN_SIZE[1]-BTN_BORDER-20)
		bg = self.bg_color
		col = self.color
		if selected:
			bg = (255,0,0)
			col = (255,255,255)

		# disegna rettangolo
		trect = miscgui.draw_rect(self.image,BTN_SIZE[0],BTN_SIZE[1],bg,self.out_color,BTN_BORDER,pos)

		# disegna testo
		surf = miscgui.draw_text(text,color=col,font=self.btn_font)
		rect = surf.get_rect()
		rect.center = trect.center
		self.image.blit(surf,rect)

		return trect

	def _mousedown(self,pos):
		'''Event mouse down

		Gestisce l'highlight dei pulsanti premuti.
		'''

		self.selected = -1

		for i in range(0,len(self.rects)):
			if self.rects[i].collidepoint(pos):
				self.selected = i

	def _click(self,pos):
		'''Evento click

		Restituisce l'indice del pulsante premuto, altrimenti -1.
		'''

		for i in range(0,len(self.rects)):
			if self.rects[i].collidepoint(pos):
				return i

		self.selected = -1
		return -1
