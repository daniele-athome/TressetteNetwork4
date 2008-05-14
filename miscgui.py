import pygame

def draw_text(text,size=20,color=(0,0,0),bold=False,italic=False):
	'''Disegna del testo sulla superficie.

	Restituisce la text_surface
	'''

	# crea il font
	font = pygame.font.SysFont(None,size,bold,italic)

	# renderizza il testo
	surf = font.render(text,True,color)

	return surf

def draw_rect(surface,width,height,bgcolor=(0,0,0),color=(0,0,0),border=0):
	'''Disegna un rettangolo sulla superficie.'''

	pygame.draw.rect(surface,color,pygame.Rect([0,0],[width,height]),border)
