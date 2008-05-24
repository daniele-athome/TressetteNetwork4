# -*- coding: utf-8 -*-
'''Definizioni del protocollo di rete di TressetteNetwork4.'''
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

VERSION_INFO='version-info'					# scambio version info
VERSION_CHECK='version-check'				# responso verifica versione

STATE='state'								# cambio di stato dal server
ACCUSE_COUNT='accuse-count'					# notifica di quanti accusi
ACCUSATIONS='accusations'					# notifica accusi

JOIN='join'									# login giocatore
PART='part'									# logout giocatore

READY_DISTRIB='ready-distribution'		# pronti per cominciare la distribuzione delle carte!
CARDS_DISTRIB='cards-distribution'		# richiedi carte/invio delle carte a un giocatore
CHAT='chat'								# manda/ricevi messaggio di chat (in ricezione la stringa contiene anche nome:)

THROW_CARD='throw-card'					# getta carta a terra! questo comando ha l'argomento position in piu' quando viene spedito dal server
TURN='turn'								# il turno e' del giocatore position
TAKES='takes'							# il giocatore position prende la mano
POINTS='points'							# aggiornamento punteggio delle squadre
END_HAND='end-hand'						# fine mano
GAME_POINTS='game-points'				# aggiornamento punteggio partita delle squadre
END_GAME='end-game'						# fine partita (vincitore, se < 0 parita')

ERR_NAME_BUSY='error-name-busy'					# nome in uso
ERR_POS_BUSY='error-pos-busy'					# posizione occupata
ERR_ARG_INVALID='error-invalid-argument'		# argomento non valido
ERR_REFUSED='error-refused'						# richiesta rifiutata
