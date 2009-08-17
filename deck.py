# -*- coding: utf-8 -*-
'''Gestione del mazzo di carte.'''
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

import random

DEFAULT_SEEMS=4
DEFAULT_NUM_PER_SEEM=10

# nomi dei semi
SEEMS_NAMES = [ 'bastoni', 'denara', 'spade', 'coppe' ]
# nomi delle carte
CARDS_NAMES = [ 'asso', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto', 'nove', 'dieci' ]
# nomi delle carte al plurale (se None prendere da CARD_NAMES)
PLURAL_NAMES = [ 'assi', None, None, None, None, None, None, None, None, None ]

class Deck:
	'''Gestione di un mazzo di carte.'''

	def __init__(self,seems=DEFAULT_SEEMS,num_per_seem=DEFAULT_NUM_PER_SEEM):
		'''Crea un mazzo di carte ordinato.

		seems: numero di semi/pali
		num_per_seem: numero di carte per seme/palo.

		In questo modo permette di gestire qualsiasi tipo di mazzo.
		'''

		self.seems = seems
		self.num_per_seem = num_per_seem
		self.deck = map(lambda x: x+1,range(0,seems*num_per_seem))

	def shuffle(self):
		'''Mischia il mazzo.'''

		random.shuffle(self.deck)

	def extract(self,count=1):
		'''Estrae <count> carte dal mazzo.

		Le carte estratte vengono prelevate dalla prima in lista.'''

		if count > len(self.deck):
			return ()

		# preleva la carte
		c = self.deck[:count]

		# cancella la parte di mazzo estratta
		del self.deck[:count]

		return tuple(c)

BASE_PATH="data/cards/piacentine"
BASE_EXT=".jpg"

def get_card_image_path(card_num,num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Restituisce il percorso dell'immagine della carta.'''

	# un gioco da ragazzi :P (ma va a cagare!)
	return ''.join( (BASE_PATH,str(card_num+1),BASE_EXT) )

def get_card(card_num,num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Restituisce una tupla contenente il numero del seme ed il valore nominale della carta.'''

	# seme: card_num / num_per_seem
	seem = card_num // num_per_seem

	# valore: card_num % num_per_seem
	value = card_num % num_per_seem
	if value == 0:
		seem = seem - 1
		value = 10

	return seem,value

def get_card_name(card_value, plural = False):
	'''Restituisce il nome del valore della carta.'''

	ret = CARDS_NAMES[card_value - 1]

	if plural:
		if PLURAL_NAMES[card_value - 1] != None:
			ret = PLURAL_NAMES[card_value - 1]

	return ret

def sort_cards(cards):
	'''Ordine la carte passate per seme e poi per valore.'''

	# un gioco da ragazzi :P (ma va a cagare n'altra volta!)
	return sorted(cards)

def seem_cards(cards,ref_card,num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Restituisce le carte con il seme dato.'''

	ret = []
	ref = get_card(ref_card)

	for c in cards:
		ext = get_card(c)
		if ext[0] == ref[0]:
			ret.append(c)

	return ret

def get_values(cards,num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Restituisce i valori nominali delle carte.'''

	ret = []
	for c in cards:
		n = c % num_per_seem
		if n == 0: n = 10
		ret.append(n)

	return ret

def get_tressette_cards(cards,num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Restituisce una lista con le carte da tressette.

	Nota: cards contiene solo i valori nominali!!!
	'''

	ret = []
	for c in cards:
		if c in (1,2,3):
			ret.append(c)

	return ret

def can_abort(cards, num_per_seem=DEFAULT_NUM_PER_SEEM):
	'''Determina se possiamo mandare a monte per poverello.'''

	fig_count = 0
	for c in cards:
		if c in (1,2,3):
			return False

		if c in (8,9,10):
			fig_count = fig_count + 1
			if (fig_count >= 4):
				return False

	return True

if __name__ == '__main__':
	a = Deck(4,10)

	for a in a.deck:
		print "Seem:",get_card(a)[0],"value",get_card(a)[1]
