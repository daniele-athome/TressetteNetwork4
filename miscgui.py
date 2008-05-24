import pygame

def create_font(size,bold=False,italic=False):
	f = pygame.font.Font(None,size)
	f.set_bold(bold)
	f.set_italic(italic)
	return f

def draw_text(text,size=20,color=(0,0,0),bold=False,italic=False,font=None,more_space=False,bgcolor=(0,0,0)):
	'''Disegna del testo sulla superficie.

	bgcolor considerato solo se more_space != False

	Restituisce la text_surface.
	'''

	# crea il font
	if font == None:
		font = create_font(size,bold,italic)

	# renderizza il testo
	surf2 = font.render(text,True,color)
	surf = surf2

	if more_space != False:
		surf = pygame.surface.Surface((surf2.get_width()+more_space,surf2.get_height()))
		surf.fill(bgcolor)
		surf.blit(surf2,surf2.get_rect())

	return surf

def draw_rect(surface,width,height,bgcolor=(0,0,0),color=(0,0,0),border=0):
	'''Disegna un rettangolo sulla superficie.'''

	pygame.draw.rect(surface,color,pygame.Rect([0,0],[width,height]),border)
