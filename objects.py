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
import pygame,miscgui,deck

RECT=130			# dimensione rettangolo selezione posizione
BORDER=20			# bordo rettangolo selezione e rettangolo casella di testo
OFFSET=10			# distanza tra i pulsanti di selezione (usato anche in TableReplay -- distanza fra le carte)
TEXTBOX=30			# dimensione (in pixel) del font della textbox
TEXTBOX2=20			# dimensione (in pixel) del font delle textbox per gli accusi
TITLE=40			# dimensione (in pixel) del font del titolo della casella di testo
LINE=12				# spessore della linea che separa titolo da testo nella casella di testo

class TextLabel(pygame.sprite.Sprite):
	'''Una scritta da poter mettere dove si vuole.'''

	def __init__(self, color, text = '', position = (0,0), rightbottom = (None, None), rightlimit = False, size = TEXTBOX):
		pygame.sprite.Sprite.__init__(self)

		self.color = color
		self.text = text
		self.size = size
		self.font = miscgui.create_font(size)

		self.set_position(position,rightbottom,rightlimit)
		self.update()

	def set_text(self,text):
		self.text = text

	def get_text(self):
		return self.text

	def set_color(self,color):
		self.color = color

	def update(self,more_space=False,bgcolor=(0,0,0)):
		self._make_text(more_space,bgcolor)

	def set_position(self, xy, rightbottom = (None, None), rightlimit = False):
		self.position = xy
		self.rightbottom = rightbottom
		self.rightlimit = rightlimit

	def _make_text(self,more_space=False,bgcolor=(0,0,0)):
		self.image = miscgui.draw_text(self.text,self.size,self.color,font=self.font,more_space=more_space,bgcolor=bgcolor)
		self.rect = self.image.get_rect()

		self.rect.topleft = self.position

		if self.rightbottom[0] != None:
			self.rect.right = self.rightbottom[0]

		if self.rightbottom[1] != None:
			self.rect.bottom = self.rightbottom[1]

		if self.rightlimit:
			self.rect.right = self.rightlimit

class TextEntry(TextLabel):
	'''Una TextLabel modificabile dall'utente.'''
	def __init__(self, color, text = '', position = (0,0), rightbottom = (None, None), rightlimit = False, size = TEXTBOX,show_cursor = True,bg_color=(0,0,0)):

		self.bg_color = bg_color
		self._cursor = 0
		self.show_cursor(show_cursor)

		TextLabel.__init__(self,color,text,position,rightbottom,rightlimit,size)

	def set_cursor(self,n):
		if n >= 0 and n <= len(self.text):
			self._cursor = n

	def cursor_offset(self,offset):
		'''Somma l'offset alla posizione del cursore.'''
		self.set_cursor(self.cursor + offset)

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

	def __init__(self, bg_color, screen_size, index, bl_color):
		pygame.sprite.Sprite.__init__(self)

		self.screen_size = screen_size
		self.index = index
		self.size = 150
		self.bg_color = bg_color
		self.left = int(self.screen_size[0] / 2) - self.size*2 - int((BORDER+OFFSET)/2)

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
		self.rect.top = int(self.screen_size[1]/2-self.size/2)
		self.rect.left = self.left+self.size*self.index+OFFSET*self.index

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
					left = left + CARD_SIZE[0]+2

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
		for sp in self:

			if self.side == SIDE_BOTTOM:
				if hasattr(sp,'card_num'):
					#print "(GFX) Sprite card:",sp.card_num
					if sp.card_num == card_num:
						#print "(GFX) Found sprite for card",card_num
						sprite = sp
						break

			else:
				sprite = self.sprites()[index]

		if not isinstance(sprite,Card): sprite = None

		if sprite != None:

			# scala le carte se siamo al SIDE_BOTTOM
			if self.side == SIDE_BOTTOM:
				for i in range(self.sprites().index(sprite)+1,len(self.sprites())):
					sp = self.sprites()[i]
					sp.rect.left = sp.rect.left - CARD_SIZE[0] - 2
				
			# rimuovi la sprite dal gruppo
			sprite.kill()


		return sprite

class Line(pygame.sprite.Sprite):
	'''Il nome della classe parla da solo.'''

	def __init__(self, color, direction, length):
		pygame.sprite.Sprite.__init__(self)

		width = 4
		x = length
		y = 0
		start = (0,0)
		end = None
		wh = None

		if direction == 'h':
			wh = (x,width)
			end = (length,0)

		elif direction == 'v':
			wh = (width,x)
			end = (0,length)

		self.image = pygame.surface.Surface(wh)
		self.rect = pygame.draw.line(self.image,color,start,end,width)

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
		self.fontsize = fontsize

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
						surf = miscgui.draw_text(line[i],TEXTBOX,self.color)
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

		self.cards = []
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
